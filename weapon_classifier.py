"""Utilities for training and loading a Valorant weapon image classifier."""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class WeaponDataset(Dataset):
    """Dataset that reads flattened CSV labels alongside raw image files."""

    def __init__(
        self,
        split_dir: Path,
        transform: Optional[transforms.Compose] = None,
        label_names: Optional[List[str]] = None,
    ) -> None:
        self.split_dir = split_dir
        csv_path = split_dir / "_classes.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing label file: {csv_path}")
        df = pd.read_csv(csv_path)
        df.columns = [c.strip() for c in df.columns]
        inferred_labels = [c for c in df.columns if c.lower() != "filename"]
        self.label_names = label_names or inferred_labels
        missing = [c for c in self.label_names if c not in df.columns]
        if missing:
            raise ValueError(f"Columns {missing} not present in {csv_path}")
        label_frame = df[["filename", *self.label_names]].copy()
        self.class_counts = label_frame[self.label_names].sum().to_dict()
        self.samples: List[Path] = []
        self.targets: List[int] = []
        for _, row in label_frame.iterrows():
            filename = str(row["filename"]).strip()
            image_path = split_dir / filename
            if not image_path.exists():
                continue
            label_vector = row[self.label_names].to_numpy(dtype=np.float32)
            label_idx = int(label_vector.argmax())
            self.samples.append(image_path)
            self.targets.append(label_idx)
        if not self.samples:
            raise RuntimeError(f"No samples discovered under {split_dir}")
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int]:
        image_path = self.samples[index]
        image = Image.open(image_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        else:
            image = transforms.ToTensor()(image)
        return image, self.targets[index]


def build_transforms(image_size: int = 224, train: bool = False) -> transforms.Compose:
    if train:
        ops = [
            transforms.Resize(int(image_size * 1.15)),
            transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15, hue=0.05),
        ]
    else:
        ops = [
            transforms.Resize(int(image_size * 1.15)),
            transforms.CenterCrop(image_size),
        ]
    ops.extend([transforms.ToTensor(), transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)])
    return transforms.Compose(ops)


def build_model(num_classes: int, pretrained: bool = True) -> nn.Module:
    try:
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        model = models.resnet18(weights=weights)
    except AttributeError:
        model = models.resnet18(pretrained=pretrained)
    in_features = model.fc.in_features  # type: ignore[attr-defined]
    model.fc = nn.Linear(in_features, num_classes)  # type: ignore[attr-defined]
    return model


@dataclass
class TrainHistoryItem:
    epoch: int
    train_loss: float
    val_loss: float
    val_accuracy: float


def create_dataloader(
    data_root: Path,
    split: str,
    label_names: Optional[List[str]],
    batch_size: int,
    train: bool,
    num_workers: int,
    image_size: int,
) -> Tuple[DataLoader, WeaponDataset]:
    dataset = WeaponDataset(
        split_dir=data_root / split,
        transform=build_transforms(image_size=image_size, train=train),
        label_names=label_names,
    )
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=train,
        num_workers=num_workers,
        pin_memory=True,
    )
    return loader, dataset


def compute_class_weights(label_names: List[str], counts: Dict[str, int]) -> torch.Tensor:
    values = torch.tensor([max(counts.get(name, 0), 1) for name in label_names], dtype=torch.float32)
    scale = values.sum() / float(len(label_names))
    weights = scale / values
    return weights


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device, criterion: nn.Module) -> Dict[str, float]:
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0
    with torch.no_grad():
        for images, targets in loader:
            images = images.to(device)
            if not torch.is_tensor(targets):
                targets = torch.tensor(targets)
            targets = targets.to(device)
            logits = model(images)
            loss = criterion(logits, targets)
            preds = torch.argmax(logits, dim=1)
            total_correct += (preds == targets).sum().item()
            total_samples += targets.size(0)
            total_loss += loss.item() * targets.size(0)
    return {
        "loss": total_loss / max(total_samples, 1),
        "accuracy": total_correct / max(total_samples, 1),
    }


def train_weapon_classifier(
    data_root: Path,
    output_path: Path,
    epochs: int = 20,
    batch_size: int = 32,
    learning_rate: float = 3e-4,
    weight_decay: float = 1e-4,
    image_size: int = 224,
    num_workers: int = 2,
    seed: int = 17,
    use_pretrained: bool = True,
) -> Dict[str, float]:
    if not data_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {data_root}")
    seed_everything(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_loader, train_dataset = create_dataloader(
        data_root=data_root,
        split="train",
        label_names=None,
        batch_size=batch_size,
        train=True,
        num_workers=num_workers,
        image_size=image_size,
    )
    val_loader, _ = create_dataloader(
        data_root=data_root,
        split="valid",
        label_names=train_dataset.label_names,
        batch_size=batch_size,
        train=False,
        num_workers=num_workers,
        image_size=image_size,
    )

    test_loader = None
    test_dir = data_root / "test"
    if test_dir.exists():
        test_loader, _ = create_dataloader(
            data_root=data_root,
            split="test",
            label_names=train_dataset.label_names,
            batch_size=batch_size,
            train=False,
            num_workers=num_workers,
            image_size=image_size,
        )

    model = build_model(len(train_dataset.label_names), pretrained=use_pretrained)
    model = model.to(device)

    class_weights = compute_class_weights(train_dataset.label_names, train_dataset.class_counts).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)

    history: List[TrainHistoryItem] = []
    best_state: Optional[Dict[str, torch.Tensor]] = None
    best_accuracy = 0.0

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        sample_count = 0
        for images, targets in train_loader:
            images = images.to(device)
            if not torch.is_tensor(targets):
                targets = torch.tensor(targets)
            targets = targets.to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * targets.size(0)
            sample_count += targets.size(0)
        train_loss = running_loss / max(sample_count, 1)

        val_metrics = evaluate(model, val_loader, device, criterion)
        scheduler.step(val_metrics["accuracy"])
        history.append(
            TrainHistoryItem(
                epoch=epoch,
                train_loss=train_loss,
                val_loss=val_metrics["loss"],
                val_accuracy=val_metrics["accuracy"],
            )
        )
        if val_metrics["accuracy"] > best_accuracy:
            best_accuracy = val_metrics["accuracy"]
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        print(
            f"Epoch {epoch:02d}/{epochs} - "
            f"train_loss={train_loss:.4f} val_loss={val_metrics['loss']:.4f} "
            f"val_acc={val_metrics['accuracy']:.3f}"
        )

    if best_state is None:
        best_state = model.state_dict()
    model.load_state_dict(best_state)

    test_metrics: Optional[Dict[str, float]] = None
    if test_loader is not None:
        test_metrics = evaluate(model, test_loader, device, criterion)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "state_dict": best_state,
        "label_names": train_dataset.label_names,
        "config": {
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "weight_decay": weight_decay,
            "image_size": image_size,
            "num_workers": num_workers,
            "seed": seed,
            "use_pretrained": use_pretrained,
        },
        "history": [history_item.__dict__ for history_item in history],
        "metrics": {
            "best_val_accuracy": best_accuracy,
            "test_accuracy": test_metrics["accuracy"] if test_metrics else None,
            "test_loss": test_metrics["loss"] if test_metrics else None,
        },
    }
    torch.save(checkpoint, output_path)
    metrics_path = output_path.with_suffix(".json")
    with metrics_path.open("w", encoding="utf-8") as fp:
        json.dump(checkpoint["metrics"], fp, indent=2)

    return checkpoint["metrics"]


def load_weapon_classifier(weights_path: Path, device: Optional[torch.device] = None) -> Tuple[nn.Module, List[str], Dict[str, object]]:
    if not weights_path.exists():
        raise FileNotFoundError(f"Weights not found: {weights_path}")
    device = device or torch.device("cpu")
    checkpoint = torch.load(weights_path, map_location=device)
    label_names: List[str] = checkpoint["label_names"]
    model = build_model(len(label_names), pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    model.eval()
    config = checkpoint.get("config", {})
    return model, label_names, config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the Valorant weapon classifier")
    parser.add_argument("--data-root", type=Path, default=Path("weapons_dataset"))
    parser.add_argument("--output", type=Path, default=Path("models/valorant_weapon_classifier.pt"))
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--no-pretrained", action="store_true", help="Disable ImageNet initialization")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics = train_weapon_classifier(
        data_root=args.data_root,
        output_path=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        image_size=args.image_size,
        num_workers=args.num_workers,
        seed=args.seed,
        use_pretrained=not args.no_pretrained,
    )
    print("Training finished:", metrics)


if __name__ == "__main__":
    main()
