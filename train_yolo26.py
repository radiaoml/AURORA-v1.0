"""Utility script for training the Valorant enemy/weapon detector on dataset2 using YOLO26 (Ultralytics YOLOv8).

Run from the repository root:

    python train_yolo26.py --epochs 80 --imgsz 640

This script expects the Roboflow-exported dataset in dataset2/ with the canonical data.yaml file.
"""
from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path
from typing import Optional

try:
    from ultralytics import YOLO  # type: ignore
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "Ultralytics is required for YOLO26 training. Install it with 'pip install ultralytics>=8.1.0'."
    ) from exc

LOGGER = logging.getLogger("aurora.yolo26")
logging.basicConfig(level=logging.INFO)

DEFAULT_DATA_YAML = Path("dataset2/data.yaml")
DEFAULT_MODEL_NAME = "yolov8m.pt"
DEFAULT_OUTPUT_MODEL = Path("models/aurora_yolo26_detector.pt")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLO26 detector on the Roboflow dataset2 export")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_YAML, help="Path to data.yaml")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_NAME,
        help="Ultralytics checkpoint to fine-tune (e.g., yolov8s.pt, yolov8m.pt)",
    )
    parser.add_argument("--epochs", type=int, default=60, help="Training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size for training/validation")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument(
        "--device",
        default=None,
        help="CUDA device string (e.g., 0, 0,1) or 'cpu'. Defaults to autodetect",
    )
    parser.add_argument(
        "--project",
        default="runs/aurora_yolo26",
        help="Directory that will contain Ultralytics run artifacts",
    )
    parser.add_argument("--name", default="valorant-detector", help="Name of the training run")
    parser.add_argument(
        "--export-formats",
        nargs="*",
        default=["onnx"],
        help="Additional export formats to produce once training finishes",
    )
    parser.add_argument(
        "--output-weights",
        type=Path,
        default=DEFAULT_OUTPUT_MODEL,
        help="Where to copy the best weights for inference",
    )
    return parser.parse_args()


def train_detector(args: argparse.Namespace) -> Path:
    if not args.data.exists():
        raise FileNotFoundError(f"Cannot find dataset yaml at {args.data}")

    model = YOLO(args.model)
    LOGGER.info("Starting YOLO26 training on %s", args.data)
    results = model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        device=args.device,
        pretrained=True,
        exist_ok=True,
        verbose=True,
    )

    trainer = getattr(model, "trainer", None)
    save_dir: Optional[Path] = None
    best_weights: Optional[Path] = None

    if trainer and getattr(trainer, "best", None):
        best_weights = Path(trainer.best)
        save_dir = Path(trainer.save_dir)
    elif hasattr(results, "save_dir"):
        save_dir = Path(results.save_dir)
        candidate = save_dir / "weights" / "best.pt"
        if candidate.exists():
            best_weights = candidate

    if not best_weights or not best_weights.exists():
        raise FileNotFoundError("Ultralytics did not emit best.pt. Check the training logs for errors.")

    args.output_weights.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best_weights, args.output_weights)
    LOGGER.info("Best weights copied to %s", args.output_weights)

    LOGGER.info("Running validation on the held-out split...")
    model.val(data=str(args.data), imgsz=args.imgsz, batch=args.batch, device=args.device, project=args.project)

    for export_format in args.export_formats:
        try:
            LOGGER.info("Exporting detector as %s", export_format)
            model.export(format=export_format, imgsz=args.imgsz)
        except Exception as export_exc:  # pylint: disable=broad-except
            LOGGER.warning("Failed to export format %s: %s", export_format, export_exc)

    return args.output_weights


def main() -> None:
    args = parse_args()
    output_path = train_detector(args)
    LOGGER.info("Training complete. You can now point AURORA_YOLO26_WEIGHTS at %s", output_path)


if __name__ == "__main__":
    main()
