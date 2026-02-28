"""FastAPI service that predicts Valorant weapons from video clips and enriches results with weapon stats."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import requests
import torch
from PIL import Image
from fastapi import APIRouter, Body, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from torchvision import transforms
from transformers import CLIPModel, CLIPProcessor
try:
    import tensorflow as tf  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    tf = None

from weapon_classifier import build_model, build_transforms

logger = logging.getLogger("weapon_prediction_api")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

MODEL_WEIGHTS_ENV = "WEAPON_CLASSIFIER_WEIGHTS"
DEFAULT_MODEL_PATH = Path("models/valorant_weapon_classifier.pt")
VALORANT_API_URL = "https://valorant-api.com/v1/weapons"
API_NAME_BY_LABEL = {
    "Classic": "Classic",
    "Ghost": "Ghost",
    "Guardian": "Guardian",
    "Knife": "Melee",
    "Missing": None,
    "Phantom": "Phantom",
    "Sheriff": "Sheriff",
    "Vandal": "Vandal",
}


def normalize_weapon_label(label: str) -> str:
    canonical = label.strip()
    if canonical in API_NAME_BY_LABEL:
        return canonical
    title_case = canonical.title()
    if title_case in API_NAME_BY_LABEL:
        return title_case
    upper_case = canonical.capitalize()
    if upper_case in API_NAME_BY_LABEL:
        return upper_case
    return canonical

ALLOW_MOCK_SERVICE = os.getenv("WEAPON_INTEL_ALLOW_MOCK", "1").lower() not in {"0", "false", "no"}
ALLOW_CLIP_FALLBACK = os.getenv("WEAPON_INTEL_ALLOW_CLIP", "1").lower() not in {"0", "false", "no"}
CLIP_MODEL_NAME = os.getenv("WEAPON_INTEL_CLIP_MODEL", "openai/clip-vit-base-patch32")
TEACHABLE_MODEL_DIR = Path(os.getenv("WEAPON_TF_MODEL_DIR", "models/weapons_model"))
TEACHABLE_MODEL_PATH = Path(
    os.getenv("WEAPON_TF_MODEL_PATH", str(TEACHABLE_MODEL_DIR / "keras_model.h5"))
)
TEACHABLE_LABELS_PATH = Path(
    os.getenv("WEAPON_TF_LABELS_PATH", str(TEACHABLE_MODEL_DIR / "labels.txt"))
)
FRAME_STRIDE = max(1, int(os.getenv("WEAPON_FRAME_STRIDE", "6")))
MAX_FRAMES = int(os.getenv("WEAPON_MAX_FRAMES", "64"))


def sample_video_frames(
    video_path: Path,
    frame_stride: int = 6,
    max_frames: int = 64,
) -> List[np.ndarray]:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        capture.release()
        raise ValueError(f"Unable to open video: {video_path}")
    frames: List[np.ndarray] = []
    sample_index = 0
    try:
        while len(frames) < max_frames:
            success, frame = capture.read()
            if not success:
                break
            if sample_index % frame_stride == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(rgb_frame)
            sample_index += 1
    finally:
        capture.release()
    if not frames:
        raise ValueError("Video did not contain readable frames")
    return frames


class WeaponClassifierInference:
    def __init__(self, weights_path: Path, device: Optional[torch.device] = None) -> None:
        if not weights_path.exists():
            raise FileNotFoundError(f"Model weights not found: {weights_path}")
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(weights_path, map_location=self.device)
        self.label_names: List[str] = checkpoint["label_names"]
        config = checkpoint.get("config", {})
        image_size = int(config.get("image_size", 224))
        self.transform = build_transforms(image_size=image_size, train=False)
        self.model = build_model(len(self.label_names), pretrained=False)
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.to(self.device)
        self.model.eval()

    def predict_frames(self, frames: List[np.ndarray], top_k: int = 3) -> Dict[str, object]:
        summary, _ = self.summarize_frames(frames, top_k=top_k)
        return summary

    def summarize_frames(
        self, frames: List[np.ndarray], top_k: int = 3
    ) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        mean_probs, per_frame = self._predict_probabilities(frames)
        summary = self._build_summary(mean_probs, top_k)
        per_frame_dicts: List[Dict[str, float]] = []
        for probs in per_frame:
            probs_cpu = probs.detach().cpu()
            per_frame_dicts.append(
                {label: float(probs_cpu[idx].item()) for idx, label in enumerate(self.label_names)}
            )
        return summary, per_frame_dicts

    def frame_distributions(self, frames: List[np.ndarray]) -> List[Dict[str, float]]:
        _, per_frame = self.summarize_frames(frames)
        return per_frame

    def _frame_to_tensor(self, frame: np.ndarray) -> torch.Tensor:
        image = transforms.ToPILImage()(frame)
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        return tensor

    def _predict_probabilities(self, frames: List[np.ndarray]) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        if not frames:
            raise ValueError("No frames provided for prediction")
        probability_tensors: List[torch.Tensor] = []
        with torch.no_grad():
            for frame in frames:
                tensor = self._frame_to_tensor(frame)
                logits = self.model(tensor)
                probs = torch.softmax(logits, dim=1)
                probability_tensors.append(probs.squeeze(0))
        mean_probs = torch.stack(probability_tensors).mean(dim=0)
        return mean_probs, probability_tensors

    def _build_summary(self, mean_probs: torch.Tensor, top_k: int) -> Dict[str, object]:
        top_k = min(top_k, len(self.label_names))
        top_values, top_indices = torch.topk(mean_probs, k=top_k)
        distribution = {label: float(mean_probs[idx].item()) for idx, label in enumerate(self.label_names)}
        top_predictions = [
            {"label": self.label_names[idx], "confidence": float(value.item())}
            for idx, value in zip(top_indices.tolist(), top_values)
        ]
        return {
            "top_prediction": top_predictions[0],
            "alternatives": top_predictions[1:],
            "probabilities": distribution,
        }


class ValorantWeaponStatsClient:
    def __init__(self, cache_path: Path = Path("cache/valorant_weapon_stats.json")) -> None:
        self.cache_path = cache_path
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._weapon_index: Dict[str, Dict[str, object]] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        if self.cache_path.exists():
            try:
                cached = json.loads(self.cache_path.read_text(encoding="utf-8"))
                self._weapon_index = {entry["displayName"]: entry for entry in cached}
            except (json.JSONDecodeError, KeyError):
                self._weapon_index = {}
        if not self._weapon_index:
            self.refresh(force=True)

    def refresh(self, force: bool = False) -> None:
        if self._weapon_index and not force:
            return
        try:
            response = requests.get(VALORANT_API_URL, timeout=15)
            response.raise_for_status()
            data = response.json().get("data", [])
            self._weapon_index = {entry["displayName"]: entry for entry in data}
            self.cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except requests.RequestException as exc:
            if not self._weapon_index:
                raise RuntimeError("Unable to fetch Valorant weapon stats") from exc

    def list_available_weapons(self) -> List[str]:
        return sorted(self._weapon_index.keys())

    def get_weapon_stats(self, label: str) -> Optional[Dict[str, object]]:
        api_name = API_NAME_BY_LABEL.get(label, label)
        if not api_name:
            return None
        entry = self._weapon_index.get(api_name)
        if not entry:
            self.refresh(force=True)
            entry = self._weapon_index.get(api_name)
        if not entry:
            return None
        return self._summarize_entry(entry)

    def _summarize_entry(self, entry: Dict[str, object]) -> Dict[str, object]:
        stats = entry.get("weaponStats") or {}
        shop = entry.get("shopData") or {}
        damage_ranges = stats.get("damageRanges") or []
        return {
            "display_name": entry.get("displayName"),
            "category": shop.get("categoryText"),
            "cost": shop.get("cost"),
            "fire_rate": stats.get("fireRate"),
            "magazine_size": stats.get("magazineSize"),
            "reload_time_seconds": stats.get("reloadTimeSeconds"),
            "first_bullet_accuracy": stats.get("firstBulletAccuracy"),
            "run_speed_multiplier": stats.get("runSpeedMultiplier"),
            "wall_penetration": stats.get("wallPenetration"),
            "feature": shop.get("featureText"),
            "damage_ranges": [
                {
                    "range_start_meters": dr.get("rangeStartMeters"),
                    "range_end_meters": dr.get("rangeEndMeters"),
                    "head_damage": dr.get("headDamage"),
                    "body_damage": dr.get("bodyDamage"),
                    "leg_damage": dr.get("legDamage"),
                }
                for dr in damage_ranges
            ],
        }


class WeaponPredictionService:
    def __init__(self, weights_path: Path) -> None:
        self.classifier = WeaponClassifierInference(weights_path)
        self.stats_client = ValorantWeaponStatsClient()
        self.is_mock = False

    def predict(self, video_path: Path) -> Dict[str, object]:
        frames = sample_video_frames(video_path, frame_stride=FRAME_STRIDE, max_frames=MAX_FRAMES)
        prediction, _ = self._predict_with_frames(frames)
        return prediction

    def supported_labels(self) -> List[str]:
        return self.classifier.label_names

    def predict_from_frames(self, frames: List[np.ndarray]) -> Dict[str, object]:
        prediction, _ = self._predict_with_frames(frames)
        return prediction

    def analyze_frames(self, frames: List[np.ndarray]) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        return self._predict_with_frames(frames)

    def _predict_with_frames(
        self, frames: List[np.ndarray]
    ) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        prediction, per_frame = self.classifier.summarize_frames(frames)
        prediction["frames_analyzed"] = len(frames)
        label = normalize_weapon_label(prediction["top_prediction"]["label"])
        stats = self.stats_client.get_weapon_stats(label)
        prediction["weapon_stats"] = stats
        return prediction, per_frame


class TeachableWeaponClassifier:
    def __init__(self, model_path: Path, labels_path: Path) -> None:
        if tf is None:
            raise RuntimeError(
                "TensorFlow is required for the Teachable Machine model. Install it with 'pip install tensorflow'."
            )
        if not model_path.exists():
            raise FileNotFoundError(f"Teachable Machine model not found at {model_path}")
        if not labels_path.exists():
            raise FileNotFoundError(f"Label file not found at {labels_path}")
        self.model = tf.keras.models.load_model(model_path, compile=False)
        self.label_names = self._load_labels(labels_path)
        input_shape = self.model.inputs[0].shape  # type: ignore[index]
        height = int(input_shape[1]) if input_shape[1] else 224
        width = int(input_shape[2]) if input_shape[2] else 224
        self.image_size = (height, width)

    @staticmethod
    def _load_labels(labels_path: Path) -> List[str]:
        labels: List[str] = []
        for line in labels_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split(maxsplit=1)
            label = parts[1] if len(parts) == 2 else parts[0]
            labels.append(label.strip())
        if not labels:
            raise ValueError(f"No labels parsed from {labels_path}")
        return labels

    def summarize_frames(
        self, frames: List[np.ndarray], top_k: int = 3
    ) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        if not frames:
            raise ValueError("No frames provided for prediction")
        per_frame_probs: List[np.ndarray] = []
        for frame in frames:
            tensor = self._preprocess(frame)
            preds = self.model(tensor, training=False)
            if isinstance(preds, tf.Tensor):
                preds = preds.numpy()
            per_frame_probs.append(preds.squeeze(0))
        mean_probs = np.stack(per_frame_probs, axis=0).mean(axis=0)
        summary = self._build_summary(mean_probs, top_k)
        per_frame_dicts = []
        for probs in per_frame_probs:
            per_frame_dicts.append({label: float(probs[idx]) for idx, label in enumerate(self.label_names)})
        return summary, per_frame_dicts

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        resized = cv2.resize(frame, (self.image_size[1], self.image_size[0]))
        tensor = resized.astype("float32") / 255.0
        return np.expand_dims(tensor, axis=0)

    def _build_summary(self, mean_probs: np.ndarray, top_k: int) -> Dict[str, object]:
        top_k = min(top_k, len(self.label_names))
        sorted_indices = np.argsort(mean_probs)[::-1][:top_k]
        top_predictions = [
            {"label": self.label_names[idx], "confidence": float(mean_probs[idx])}
            for idx in sorted_indices
        ]
        distribution = {label: float(mean_probs[idx]) for idx, label in enumerate(self.label_names)}
        return {
            "top_prediction": top_predictions[0],
            "alternatives": top_predictions[1:],
            "probabilities": distribution,
        }


class TeachableWeaponPredictionService:
    def __init__(self, model_path: Path, labels_path: Path) -> None:
        self.classifier = TeachableWeaponClassifier(model_path, labels_path)
        self.stats_client = ValorantWeaponStatsClient()
        self.frame_stride = FRAME_STRIDE
        self.max_frames = MAX_FRAMES
        self.is_mock = False

    def predict(self, video_path: Path) -> Dict[str, object]:
        frames = sample_video_frames(video_path, frame_stride=self.frame_stride, max_frames=self.max_frames)
        prediction, _ = self._predict_with_frames(frames)
        return prediction

    def predict_from_frames(self, frames: List[np.ndarray]) -> Dict[str, object]:
        prediction, _ = self._predict_with_frames(frames)
        return prediction

    def supported_labels(self) -> List[str]:
        return self.classifier.label_names

    def analyze_frames(self, frames: List[np.ndarray]) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        return self._predict_with_frames(frames)

    def _predict_with_frames(
        self, frames: List[np.ndarray]
    ) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        prediction, per_frame = self.classifier.summarize_frames(frames)
        prediction["frames_analyzed"] = len(frames)
        label = normalize_weapon_label(prediction["top_prediction"]["label"])
        prediction["weapon_stats"] = self.stats_client.get_weapon_stats(label)
        return prediction, per_frame
class ClipWeaponPredictionService:
    @staticmethod
    def _coerce_feature_tensor(features: object) -> torch.Tensor:
        if isinstance(features, torch.Tensor):
            return features
        if isinstance(features, tuple) and features and isinstance(features[0], torch.Tensor):
            return features[0]
        pooler_output = getattr(features, "pooler_output", None)
        if isinstance(pooler_output, torch.Tensor):
            return pooler_output
        image_embeds = getattr(features, "image_embeds", None)
        if isinstance(image_embeds, torch.Tensor):
            return image_embeds
        text_embeds = getattr(features, "text_embeds", None)
        if isinstance(text_embeds, torch.Tensor):
            return text_embeds
        last_hidden = getattr(features, "last_hidden_state", None)
        if isinstance(last_hidden, torch.Tensor):
            return last_hidden[:, 0, :] if last_hidden.ndim == 3 else last_hidden
        raise RuntimeError(f"Unsupported CLIP feature output type: {type(features)!r}")

    def __init__(self) -> None:
        if not ALLOW_CLIP_FALLBACK:
            raise RuntimeError("CLIP fallback disabled by configuration")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CLIPModel.from_pretrained(CLIP_MODEL_NAME).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
        self.model.eval()
        self.label_names = [name for name in API_NAME_BY_LABEL.keys() if name != "Missing"]
        prompts = [f"A high-resolution Valorant screenshot focusing on the {label} weapon." for label in self.label_names]
        with torch.no_grad():
            text_inputs = self.processor(text=prompts, return_tensors="pt", padding=True).to(self.device)
            text_embeds = self._coerce_feature_tensor(self.model.get_text_features(**text_inputs))
            self.text_embeds = torch.nn.functional.normalize(text_embeds, dim=-1)
        self.stats_client = ValorantWeaponStatsClient()
        self.frame_stride = 8
        self.max_frames = 40
        self.is_mock = False

    def predict(self, video_path: Path) -> Dict[str, object]:
        frames = sample_video_frames(video_path, frame_stride=self.frame_stride, max_frames=self.max_frames)
        prediction, _ = self._predict_with_frames(frames)
        return prediction

    def supported_labels(self) -> List[str]:
        return self.label_names

    def predict_from_frames(self, frames: List[np.ndarray]) -> Dict[str, object]:
        prediction, _ = self._predict_with_frames(frames)
        return prediction

    def analyze_frames(self, frames: List[np.ndarray]) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        return self._predict_with_frames(frames)

    def _predict_with_frames(
        self, frames: List[np.ndarray]
    ) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        if not frames:
            raise ValueError("No frames extracted for CLIP inference")
        per_frame_probs = self._compute_probabilities(frames)
        stacked = torch.stack(per_frame_probs, dim=0)
        mean_probs = stacked.mean(dim=0)
        topk = torch.topk(mean_probs, k=min(3, len(self.label_names)))
        top_predictions = [
            {"label": self.label_names[idx], "confidence": float(value.item())}
            for idx, value in zip(topk.indices.tolist(), topk.values)
        ]
        distribution = {self.label_names[i]: float(mean_probs[i].item()) for i in range(len(self.label_names))}
        stats = self.stats_client.get_weapon_stats(top_predictions[0]["label"])
        per_frame_dicts: List[Dict[str, float]] = []
        for probs in per_frame_probs:
            probs_cpu = probs.detach().cpu()
            per_frame_dicts.append(
                {self.label_names[idx]: float(probs_cpu[idx].item()) for idx in range(len(self.label_names))}
            )
        prediction = {
            "top_prediction": top_predictions[0],
            "alternatives": top_predictions[1:],
            "probabilities": distribution,
            "weapon_stats": stats,
            "frames_analyzed": len(frames),
        }
        return prediction, per_frame_dicts

    def _compute_probabilities(self, frames: List[np.ndarray]) -> List[torch.Tensor]:
        batch_size = 8
        per_frame: List[torch.Tensor] = []
        with torch.no_grad():
            for idx in range(0, len(frames), batch_size):
                batch = frames[idx : idx + batch_size]
                images = [Image.fromarray(frame) for frame in batch]
                inputs = self.processor(images=images, return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                feats = self._coerce_feature_tensor(self.model.get_image_features(**inputs))
                feats = torch.nn.functional.normalize(feats, dim=-1)
                scores = feats @ self.text_embeds.T
                probs = torch.softmax(scores, dim=-1)
                per_frame.extend(probs)
        return per_frame


class MockWeaponPredictionService:
    def __init__(self) -> None:
        self.is_mock = True
        self.label_names = [name for name in API_NAME_BY_LABEL.keys() if name != "Missing"]
        try:
            self.stats_client = ValorantWeaponStatsClient()
        except RuntimeError as exc:
            logger.warning("Valorant stats unavailable for mock mode: %s", exc)
            self.stats_client = None

    def predict(self, video_path: Path) -> Dict[str, object]:
        prediction, _ = self._generate_prediction(str(video_path), frame_count=0)
        return prediction

    def supported_labels(self) -> List[str]:
        return self.label_names

    def predict_from_frames(self, frames: List[np.ndarray]) -> Dict[str, object]:
        prediction, _ = self._generate_prediction("frames", frame_count=len(frames))
        return prediction

    def analyze_frames(self, frames: List[np.ndarray]) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        return self._generate_prediction("frames", frame_count=len(frames))

    def _generate_prediction(
        self, seed_source: str, frame_count: int
    ) -> Tuple[Dict[str, object], List[Dict[str, float]]]:
        seed = abs(hash(seed_source)) or random.randint(1, 1_000_000)
        random.seed(seed)
        primary_idx = seed % len(self.label_names)
        primary_label = self.label_names[primary_idx]
        alt_labels = [self.label_names[(primary_idx + i) % len(self.label_names)] for i in range(1, 3)]
        primary_conf = round(random.uniform(0.55, 0.85), 3)
        alt_conf = max(0.0, round(1.0 - primary_conf, 3))
        stats = None
        if self.stats_client:
            stats = self.stats_client.get_weapon_stats(primary_label)
        probabilities = {label: 0.0 for label in self.label_names}
        probabilities[primary_label] = primary_conf
        probabilities[alt_labels[0]] = round(alt_conf * 0.65, 3)
        probabilities[alt_labels[1]] = round(alt_conf * 0.35, 3)
        per_frame = [probabilities.copy() for _ in range(max(frame_count, 1))]
        prediction = {
            "top_prediction": {"label": primary_label, "confidence": primary_conf},
            "alternatives": [
                {"label": alt_labels[0], "confidence": probabilities[alt_labels[0]]},
                {"label": alt_labels[1], "confidence": probabilities[alt_labels[1]]},
            ],
            "probabilities": probabilities,
            "frames_analyzed": frame_count,
            "weapon_stats": stats,
        }
        return prediction, per_frame




def _download_video_from_url(source_url: str) -> Path:
    try:
        import yt_dlp  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "yt-dlp is required for URL ingestion. Install it with 'pip install yt-dlp'."
        ) from exc

    tmp_dir = Path(tempfile.mkdtemp(prefix="weapon_url_"))
    output_template = tmp_dir / "clip.%(ext)s"
    ydl_opts = {
        "outtmpl": str(output_template),
        "quiet": True,
        "no_warnings": True,
        "format": "mp4/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "retries": 3,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source_url, download=True)
            downloaded_path = Path(ydl.prepare_filename(info))
        if not downloaded_path.exists():
            matches = list(tmp_dir.glob("clip.*"))
            if not matches:
                raise RuntimeError("Video download completed but file not found.")
            downloaded_path = matches[0]
        return downloaded_path
    except Exception as exc:  # pylint: disable=broad-except
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to ingest video from URL: {exc}") from exc


async def _save_upload_to_temp(upload: UploadFile, default_suffix: str = ".mp4") -> Path:
    suffix = Path(upload.filename or f"upload{default_suffix}").suffix or default_suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            tmp_file.write(chunk)
        tmp_path = Path(tmp_file.name)
    await upload.close()
    return tmp_path


def _cleanup_temp_artifact(path: Optional[Path]) -> None:
    if not path:
        return
    if path.exists() and path.is_file():
        try:
            path.unlink()
        except OSError:
            pass
    parent = path.parent
    if parent.exists() and parent.name.startswith("weapon_url_"):
        shutil.rmtree(parent, ignore_errors=True)


def _decode_image_bytes(payload: bytes) -> np.ndarray:
    array = np.frombuffer(payload, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image payload")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def _format_prediction_response(prediction: Dict[str, object]) -> WeaponPredictionResponse:
    weapon_stats = prediction.get("weapon_stats")
    return WeaponPredictionResponse(
        top_prediction=PredictionScore(**prediction["top_prediction"]),
        alternatives=[PredictionScore(**alt) for alt in prediction.get("alternatives", [])],
        frames_analyzed=prediction.get("frames_analyzed", 0),
        probabilities=prediction.get("probabilities", {}),
        weapon_stats=WeaponStatsModel(**weapon_stats) if weapon_stats else None,
    )


def _build_improvement_notes(
    summary: DetectionSummaryModel,
    weapon_prediction: Optional[WeaponPredictionResponse],
) -> List[str]:
    notes: List[str] = []
    enemy_pressure = summary.agent_counts.get("enemy", 0) + summary.agent_counts.get("enemy behind wall", 0)
    ally_pressure = summary.agent_counts.get("ally", 0) + summary.agent_counts.get("ally behind wall", 0)
    if enemy_pressure > ally_pressure:
        notes.append("Enemy presence outweighs team positioning; delay peaks or rotate to regain numbers.")
    if summary.weapon_presence < 0.25:
        notes.append("Weapon is rarely visible; capture longer POV clips to reinforce the detector.")
    if summary.spike_detected:
        notes.append("Spike spotted in-frame—tighten post-plant spacing and call rotations sooner.")
    if weapon_prediction and weapon_prediction.top_prediction.confidence < 0.6:
        notes.append(
            f"Weapon prediction confidence is {weapon_prediction.top_prediction.confidence:.2f}; record clearer spray sequences."
        )
    if not notes:
        notes.append("Solid capture—keep diversifying angles to continue improving the model.")
    return notes


class DamageRangeModel(BaseModel):
    range_start_meters: Optional[float]
    range_end_meters: Optional[float]
    head_damage: Optional[float]
    body_damage: Optional[float]
    leg_damage: Optional[float]


class WeaponStatsModel(BaseModel):
    display_name: Optional[str]
    category: Optional[str]
    cost: Optional[int]
    fire_rate: Optional[float]
    magazine_size: Optional[int]
    reload_time_seconds: Optional[float]
    first_bullet_accuracy: Optional[float]
    run_speed_multiplier: Optional[float]
    wall_penetration: Optional[str]
    feature: Optional[str]
    damage_ranges: List[DamageRangeModel] = Field(default_factory=list)


class PredictionScore(BaseModel):
    label: str
    confidence: float


class WeaponPredictionResponse(BaseModel):
    top_prediction: PredictionScore
    alternatives: List[PredictionScore]
    frames_analyzed: int
    probabilities: Dict[str, float]
    weapon_stats: Optional[WeaponStatsModel]


class DetectionInstanceModel(BaseModel):
    label: str
    confidence: float
    frame_index: int
    area_pct: float
    agent_name: Optional[str] = None


class DetectionSummaryModel(BaseModel):
    frames_evaluated: int
    total_detections: int
    weapon_detections: int
    weapon_presence: float
    agent_counts: Dict[str, int]
    named_agent_counts: Dict[str, int]
    spike_detected: bool
    detections: List[DetectionInstanceModel]


class WeaponAgentInsightResponse(BaseModel):
    weapon_prediction: Optional[WeaponPredictionResponse]
    selected_weapon: Optional[str]
    selected_weapon_stats: Optional[WeaponStatsModel]
    dominant_agent: Optional[str]
    detection_summary: DetectionSummaryModel
    improvement_notes: List[str]


class URLPredictionRequest(BaseModel):
    source_url: str = Field(..., description="Direct video URL or supported YouTube link")


app = FastAPI(title="Valorant Weapon Predictor", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

weapon_router = APIRouter()

_SERVICE: Optional[object] = None
_STATS_CLIENT: Optional[ValorantWeaponStatsClient] = None


def _resolve_model_path() -> Path:
    env_path = os.getenv(MODEL_WEIGHTS_ENV)
    if env_path:
        return Path(env_path)
    return DEFAULT_MODEL_PATH


def _resolve_teachable_paths() -> Tuple[Path, Path]:
    return TEACHABLE_MODEL_PATH, TEACHABLE_LABELS_PATH


def get_stats_client() -> ValorantWeaponStatsClient:
    global _STATS_CLIENT
    if _STATS_CLIENT is None:
        _STATS_CLIENT = ValorantWeaponStatsClient()
    return _STATS_CLIENT


def get_service() -> object:
    global _SERVICE
    if _SERVICE is None:
        try:
            teachable_model, teachable_labels = _resolve_teachable_paths()
            _SERVICE = TeachableWeaponPredictionService(teachable_model, teachable_labels)
            return _SERVICE
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Teachable weapon model unavailable (%s). Trying Torch checkpoint...", exc)

        weights_path = _resolve_model_path()
        try:
            _SERVICE = WeaponPredictionService(weights_path)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Primary weapon classifier unavailable (%s).", exc)
            if ALLOW_CLIP_FALLBACK:
                try:
                    logger.info("Initializing CLIP zero-shot fallback (%s)...", CLIP_MODEL_NAME)
                    _SERVICE = ClipWeaponPredictionService()
                    return _SERVICE
                except Exception as clip_exc:  # pylint: disable=broad-except
                    logger.warning("CLIP fallback failed: %s", clip_exc)
            if not ALLOW_MOCK_SERVICE:
                raise
            logger.warning("Falling back to mock weapon predictions.")
            _SERVICE = MockWeaponPredictionService()
    return _SERVICE


@weapon_router.get("/healthz")
def health() -> Dict[str, object]:
    model_ready = False
    error: Optional[str] = None
    try:
        service = get_service()
        model_ready = service is not None
    except Exception as exc:  # pylint: disable=broad-except
        error = str(exc)
    return {"status": "ok", "model_ready": model_ready, "error": error}


@weapon_router.get("/weapons")
def list_weapons() -> Dict[str, object]:
    labels = sorted(name for name in API_NAME_BY_LABEL.keys() if name and name != "Missing")

    try:
        api_weapons = get_stats_client().list_available_weapons()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "labels": labels,
        "api_weapons": api_weapons,
    }


@weapon_router.get("/weapons/stats/{weapon_label}", response_model=WeaponStatsModel)
def get_weapon_stats(weapon_label: str) -> WeaponStatsModel:
    normalized = normalize_weapon_label(weapon_label)
    try:
        stats = get_stats_client().get_weapon_stats(normalized)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not stats:
        raise HTTPException(status_code=404, detail=f"Weapon stats not found for '{weapon_label}'.")
    return WeaponStatsModel(**stats)


@weapon_router.post("/predict", response_model=WeaponPredictionResponse)
async def predict_weapon(file: UploadFile = File(...)) -> WeaponPredictionResponse:
    if file.content_type and not file.content_type.startswith("video"):
        raise HTTPException(status_code=415, detail="Please upload a video file.")
    try:
        service = get_service()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    tmp_path: Optional[Path] = None
    try:
        tmp_path = await _save_upload_to_temp(file)
        prediction = service.predict(tmp_path)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected weapon prediction error")
        raise HTTPException(status_code=500, detail="Unexpected weapon prediction error.") from exc
    finally:
        _cleanup_temp_artifact(tmp_path)

    return _format_prediction_response(prediction)


@weapon_router.post("/predict-by-url", response_model=WeaponPredictionResponse)
async def predict_weapon_by_url(payload: URLPredictionRequest = Body(...)) -> WeaponPredictionResponse:
    source_url = payload.source_url.strip()
    if not source_url:
        raise HTTPException(status_code=422, detail="source_url must be provided")
    try:
        service = get_service()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if getattr(service, "is_mock", False):
        video_path = Path(f"mock_url_{abs(hash(source_url)) % 10_000}.mp4")
    else:
        try:
            video_path = _download_video_from_url(source_url)
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        prediction = service.predict(video_path)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected URL-based weapon prediction error")
        raise HTTPException(status_code=500, detail="Unexpected URL-based weapon prediction error.") from exc
    finally:
        _cleanup_temp_artifact(video_path)

    return _format_prediction_response(prediction)


@weapon_router.post(
    "/insights/analyze",
    response_model=WeaponAgentInsightResponse,
    summary="Upload a video, still image, or YouTube clip for combined weapon + agent stats.",
)
async def analyze_weapon_and_agents(
    video_file: Optional[UploadFile] = File(None),
    image_file: Optional[UploadFile] = File(None),
    youtube_url: Optional[str] = Form(None),
    selected_weapon: Optional[str] = Form(None),
) -> WeaponAgentInsightResponse:
    provided = sum(bool(item) for item in (video_file, image_file, youtube_url))
    if provided == 0:
        raise HTTPException(status_code=422, detail="Provide a video_file, image_file, or youtube_url.")
    if provided > 1:
        raise HTTPException(status_code=422, detail="Submit only one media source at a time.")

    try:
        service = get_service()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    frames: List[np.ndarray] = []
    weapon_prediction_raw: Optional[Dict[str, object]] = None
    per_frame_distributions: List[Dict[str, float]] = []
    temp_paths: List[Path] = []
    selected_weapon_name: Optional[str] = None
    selected_weapon_stats_model: Optional[WeaponStatsModel] = None

    try:
        if video_file is not None:
            tmp_path = await _save_upload_to_temp(video_file)
            temp_paths.append(tmp_path)
            frames = sample_video_frames(
                tmp_path,
                frame_stride=FRAME_STRIDE,
                max_frames=MAX_FRAMES,
            )
            weapon_prediction_raw, per_frame_distributions = service.analyze_frames(frames)
        elif youtube_url:
            url = youtube_url.strip()
            if not url:
                raise HTTPException(status_code=422, detail="youtube_url must not be empty.")
            tmp_path = _download_video_from_url(url)
            temp_paths.append(tmp_path)
            frames = sample_video_frames(
                tmp_path,
                frame_stride=FRAME_STRIDE,
                max_frames=MAX_FRAMES,
            )
            weapon_prediction_raw, per_frame_distributions = service.analyze_frames(frames)
        else:
            if image_file is None:
                raise HTTPException(status_code=422, detail="image_file is required for still-frame analysis.")
            payload = await image_file.read()
            await image_file.close()
            if not payload:
                raise HTTPException(status_code=422, detail="Image payload is empty.")
            frame = _decode_image_bytes(payload)
            frames = [frame]
            weapon_prediction_raw, per_frame_distributions = service.analyze_frames(frames)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected media analysis error")
        raise HTTPException(status_code=500, detail="Unexpected analysis failure.") from exc
    finally:
        for tmp in temp_paths:
            _cleanup_temp_artifact(tmp)

    if not frames:
        raise HTTPException(status_code=422, detail="No frames extracted for insights analysis.")

    weapon_prediction_model = (
        _format_prediction_response(weapon_prediction_raw) if weapon_prediction_raw else None
    )
    if selected_weapon and selected_weapon.strip():
        selected_weapon_name = normalize_weapon_label(selected_weapon.strip())
        try:
            chosen_stats = get_stats_client().get_weapon_stats(selected_weapon_name)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        if not chosen_stats:
            raise HTTPException(
                status_code=404,
                detail=f"Weapon stats not found for '{selected_weapon.strip()}'.",
            )
        selected_weapon_stats_model = WeaponStatsModel(**chosen_stats)

    detections: List[DetectionInstanceModel] = []
    confident_hits = 0
    for idx, distribution in enumerate(per_frame_distributions):
        if not distribution:
            continue
        label, confidence = max(distribution.items(), key=lambda item: item[1])
        detections.append(
            DetectionInstanceModel(
                label=label,
                confidence=confidence,
                frame_index=idx,
                area_pct=1.0,
                agent_name=None,
            )
        )
        if confidence >= 0.4:
            confident_hits += 1

    weapon_presence = confident_hits / max(1, len(per_frame_distributions))
    summary_model = DetectionSummaryModel(
        frames_evaluated=len(frames),
        total_detections=len(detections),
        weapon_detections=confident_hits,
        weapon_presence=weapon_presence,
        agent_counts={},
        named_agent_counts={},
        spike_detected=False,
        detections=detections[:40],
    )
    improvement_notes = _build_improvement_notes(summary_model, weapon_prediction_model)

    return WeaponAgentInsightResponse(
        weapon_prediction=weapon_prediction_model,
        selected_weapon=selected_weapon_name,
        selected_weapon_stats=selected_weapon_stats_model,
        dominant_agent=None,
        detection_summary=summary_model,
        improvement_notes=improvement_notes,
    )


app.include_router(weapon_router)
