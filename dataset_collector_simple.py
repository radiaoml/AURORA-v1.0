import cv2
import numpy as np
import json
import os
from typing import List, Dict, Tuple
from datetime import datetime
import shutil
from pathlib import Path

class ValorantDatasetCollector:
    """Collect and annotate Valorant gameplay data for deep learning"""
    
    def __init__(self, dataset_dir: str = "valorant_dataset"):
        self.dataset_dir = Path(dataset_dir)
        self.dataset_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.frames_dir = self.dataset_dir / "frames"
        self.annotations_dir = self.dataset_dir / "annotations"
        self.splits_dir = self.dataset_dir / "splits"
        
        for dir_path in [self.frames_dir, self.annotations_dir, self.splits_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Tactical annotation categories
        self.annotation_schema = {
            "image_path": "string",
            "map": ["ASCENT", "BIND", "HAVEN", "SPLIT", "ICEBOX", "BREEZE", "FRACTURE", "PEARL", "LOTUS", "SUNSET"],
            "agents_detected": ["JETT", "REYNA", "RAZE", "PHOENIX", "NEON", "YORU", "OMEGA", "SAGE", "SKYE", "KILLJOY", "CYPER", "CHAMBER", "SOVA", "BREACH", "KAYO", "FADE", "VIPER", "ASTRA", "HARBOR", "BRIMSTONE", "OMEN", "CLOUDE"],
            "tactical_situation": ["entry", "post_plant", "retake", "eco", "buy_round", "force_buy", "mid_control", "flank"],
            "formation": ["tight", "balanced", "spread", "scattered"],
            "position_type": ["aggressive", "defensive", "support", "roaming", "anchoring"],
            "performance_metrics": {
                "entry_rating": {"min": 1, "max": 5, "type": "int"},
                "timing_gap": {"min": 0.0, "max": 5.0, "type": "float"},
                "formation_score": {"min": 0.0, "max": 1.0, "type": "float"},
                "planting_score": {"min": 0.0, "max": 1.0, "type": "float"},
                "rotation_score": {"min": 0.0, "max": 1.0, "type": "float"},
                "win_rate": {"min": 0.0, "max": 1.0, "type": "float"}
            }
        }
        
    def extract_frames_from_video(self, video_path: str, fps_sample: int = 1) -> List[str]:
        """Extract frames from video for annotation"""
        video_name = Path(video_path).stem
        output_dir = self.frames_dir / video_name
        output_dir.mkdir(exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return []
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = int(fps / fps_sample) if fps_sample > 0 else 30
        
        frame_count = 0
        extracted_frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frame_path = output_dir / f"frame_{frame_count:06d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                extracted_frames.append(str(frame_path))
                
                # Limit to prevent too many frames
                if len(extracted_frames) >= 100:
                    break
            
            frame_count += 1
        
        cap.release()
        print(f"Extracted {len(extracted_frames)} frames from {video_name}")
        return extracted_frames
    
    def create_dataset_splits(self, annotations_file: str, train_ratio: float = 0.7, val_ratio: float = 0.2):
        """Create train/val/test splits"""
        with open(annotations_file, 'r') as f:
            annotations = json.load(f)
        
        # Get all annotation entries
        entries = list(annotations.values())
        
        # Shuffle entries
        np.random.shuffle(entries)
        
        # Calculate split sizes
        total = len(entries)
        train_size = int(total * train_ratio)
        val_size = int(total * val_ratio)
        test_size = total - train_size - val_size
        
        # Create splits
        train_entries = entries[:train_size]
        val_entries = entries[train_size:train_size + val_size]
        test_entries = entries[train_size + val_size:]
        
        # Save splits
        splits = {
            'train': train_entries,
            'val': val_entries,
            'test': test_entries
        }
        
        for split_name, split_data in splits.items():
            output_file = self.splits_dir / f"{split_name}_annotations.json"
            with open(output_file, 'w') as f:
                json.dump(split_data, f, indent=2)
            print(f"Created {split_name} split with {len(split_data)} samples")
        
        return splits
    
    def generate_synthetic_data(self, num_samples: int = 1000):
        """Generate synthetic training data for testing"""
        synthetic_annotations = []
        
        for i in range(num_samples):
            annotation = {
                'image_path': f'frames/synthetic/frame_{i:06d}.jpg',
                'map': np.random.choice(self.annotation_schema['map']),
                'agents_detected': np.random.choice(self.annotation_schema['agents_detected'], size=np.random.randint(1, 6), replace=False).tolist(),
                'tactical_situation': np.random.choice(self.annotation_schema['tactical_situation']),
                'formation': np.random.choice(self.annotation_schema['formation']),
                'position_type': np.random.choice(self.annotation_schema['position_type']),
                'performance_metrics': {
                    'entry_rating': np.random.randint(1, 6),
                    'timing_gap': round(np.random.uniform(0.5, 3.0), 1),
                    'formation_score': round(np.random.uniform(0.3, 1.0), 2),
                    'planting_score': round(np.random.uniform(0.3, 1.0), 2),
                    'rotation_score': round(np.random.uniform(0.3, 1.0), 2),
                    'win_rate': round(np.random.uniform(0.3, 0.9), 2)
                }
            }
            synthetic_annotations.append(annotation)
        
        # Save synthetic data as dict with keys
        synthetic_data = {f"sample_{i}": annotation for i, annotation in enumerate(synthetic_annotations)}
        output_file = self.annotations_dir / "synthetic_annotations.json"
        with open(output_file, 'w') as f:
            json.dump(synthetic_data, f, indent=2)
        
        print(f"Generated {num_samples} synthetic annotations")
        
        # Create splits
        return self.create_dataset_splits(str(output_file))
    
    def setup_dataset_structure(self):
        """Create complete dataset structure"""
        print("Setting up Valorant dataset structure...")
        
        # Generate synthetic data for testing
        self.generate_synthetic_data(1000)  # Generate 1000 synthetic samples
        
        # Create dataset info file
        dataset_info = {
            'name': 'Valorant Tactical Dataset',
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'description': 'Dataset for Valorant tactical analysis using deep learning',
            'categories': self.annotation_schema,
            'total_samples': 1000,
            'splits': {
                'train': 700,
                'val': 200,
                'test': 100
            }
        }
        
        info_file = self.dataset_dir / "dataset_info.json"
        with open(info_file, 'w') as f:
            json.dump(dataset_info, f, indent=2)
        
        print(f"Dataset structure created at {self.dataset_dir}")
        print("\\nNext steps:")
        print("1. Add your Valorant VODs to extract frames")
        print("2. Train the deep learning model")
        print("3. Test with synthetic data first")
        
        return dataset_info

if __name__ == "__main__":
    # Setup dataset
    collector = ValorantDatasetCollector()
    dataset_info = collector.setup_dataset_structure()
    
    print("\\nDataset setup complete!")
    print(f"Dataset location: {collector.dataset_dir}")
    print(f"Total samples: {dataset_info['total_samples']}")
