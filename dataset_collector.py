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
            },
            "spatial_data": {
                "kill_locations": [{"x": "float", "y": "float", "area": "string"}],
                "player_positions": [{"agent": "string", "x": "float", "y": "float", "timestamp": "string"}],
                "movement_paths": [{"start_x": "float", "start_y": "float", "end_x": "float", "end_y": "float", "type": "string"}]
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
    
    def create_annotation_tool(self):
        """Create an interactive annotation tool"""
        annotation_tool = """
import cv2
import numpy as np
import json
from pathlib import Path

class ValorantAnnotationTool:
    def __init__(self, dataset_dir):
        self.dataset_dir = Path(dataset_dir)
        self.current_frame_idx = 0
        self.annotations = {}
        self.frame_paths = []
        
        # Load frame paths
        self.load_frame_paths()
        
        # Annotation categories
        self.categories = {
            'map': ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET'],
            'tactical_situation': ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank'],
            'formation': ['tight', 'balanced', 'spread', 'scattered'],
            'position_type': ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
        }
        
    def load_frame_paths(self):
        frames_dir = self.dataset_dir / "frames"
        for video_dir in frames_dir.iterdir():
            if video_dir.is_dir():
                for frame_path in video_dir.glob("*.jpg"):
                    self.frame_paths.append(str(frame_path))
        
        self.frame_paths.sort()
        print(f"Loaded {len(self.frame_paths)} frames for annotation")
    
    def annotate_frame(self, frame_path):
        """Annotate a single frame"""
        frame = cv2.imread(frame_path)
        if frame is None:
            return None
        
        # Display frame
        cv2.imshow('Valorant Annotation', frame)
        
        # Get annotation for this frame
        annotation = {
            'image_path': str(frame_path),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get user input for each category
        print(f"\\nAnnotating: {frame_path}")
        
        for category, options in self.categories.items():
            print(f"\\n{category}:")
            for i, option in enumerate(options):
                print(f"  {i+1}. {option}")
            
            while True:
                try:
                    choice = int(input(f"Select {category} (1-{len(options)}): ")) - 1
                    if 0 <= choice < len(options):
                        annotation[category] = options[choice]
                        break
                    else:
                        print("Invalid choice, try again")
                except ValueError:
                    print("Please enter a number")
        
        # Performance metrics
        print("\\nPerformance Metrics (1-5 scale or 0.0-1.0):")
        annotation['performance_metrics'] = {
            'entry_rating': self.get_float_input("Entry rating (1-5): ", 1, 5, int),
            'timing_gap': self.get_float_input("Timing gap (0.0-5.0s): ", 0.0, 5.0),
            'formation_score': self.get_float_input("Formation score (0.0-1.0): ", 0.0, 1.0),
            'planting_score': self.get_float_input("Planting score (0.0-1.0): ", 0.0, 1.0),
            'rotation_score': self.get_float_input("Rotation score (0.0-1.0): ", 0.0, 1.0),
            'win_rate': self.get_float_input("Win rate (0.0-1.0): ", 0.0, 1.0)
        }
        
        # Save annotation
        self.annotations[frame_path] = annotation
        cv2.destroyAllWindows()
        
        return annotation
    
    def get_float_input(self, prompt, min_val, max_val, value_type=float):
        """Get validated float input"""
        while True:
            try:
                value = value_type(input(prompt))
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"Value must be between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
    
    def save_annotations(self):
        """Save all annotations to JSON file"""
        output_file = self.dataset_dir / "annotations" / "manual_annotations.json"
        with open(output_file, 'w') as f:
            json.dump(self.annotations, f, indent=2)
        print(f"Saved {len(self.annotations)} annotations to {output_file}")
    
    def run(self):
        """Run the annotation tool"""
        print("Valorant Dataset Annotation Tool")
        print("Controls:")
        print("  'n' - Next frame")
        print("  'p' - Previous frame") 
        print("  's' - Skip frame")
        print("  'q' - Quit and save")
        print("  'a' - Annotate current frame")
        
        while self.current_frame_idx < len(self.frame_paths):
            frame_path = self.frame_paths[self.current_frame_idx]
            frame = cv2.imread(frame_path)
            
            if frame is not None:
                # Add frame number and annotation status
                status = "✓" if frame_path in self.annotations else "○"
                cv2.putText(frame, f"Frame {self.current_frame_idx+1}/{len(self.frame_paths)} {status}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow('Valorant Annotation', frame)
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('n'):  # Next frame
                self.current_frame_idx = min(self.current_frame_idx + 1, len(self.frame_paths) - 1)
            elif key == ord('p'):  # Previous frame
                self.current_frame_idx = max(self.current_frame_idx - 1, 0)
            elif key == ord('s'):  # Skip
                self.current_frame_idx += 1
            elif key == ord('a'):  # Annotate
                self.annotate_frame(frame_path)
            elif key == ord('q'):  # Quit
                break
        
        cv2.destroyAllWindows()
        self.save_annotations()

# Usage example:
# tool = ValorantAnnotationTool("valorant_dataset")
# tool.run()
        """
        
        # Save annotation tool
        tool_file = self.dataset_dir / "annotation_tool.py"
        with open(tool_file, 'w') as f:
            f.write(annotation_tool)
        
        print(f"Created annotation tool at {tool_file}")
    
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
                },
                'spatial_data': {
                    'kill_locations': [
                        {
                            'x': round(np.random.uniform(0, 1000), 0),
                            'y': round(np.random.uniform(0, 1000), 0),
                            'area': np.random.choice(['A Site', 'B Site', 'Mid', 'Spawn'])
                        } for _ in range(np.random.randint(0, 5))
                    ],
                    'player_positions': [
                        {
                            'agent': np.random.choice(self.annotation_schema['agents_detected']),
                            'x': round(np.random.uniform(0, 1000), 0),
                            'y': round(np.random.uniform(0, 1000), 0),
                            'timestamp': f"frame_{i}"
                        } for _ in range(np.random.randint(2, 6))
                    ],
                    'movement_paths': [
                        {
                            'start_x': round(np.random.uniform(0, 1000), 0),
                            'start_y': round(np.random.uniform(0, 1000), 0),
                            'end_x': round(np.random.uniform(0, 1000), 0),
                            'end_y': round(np.random.uniform(0, 1000), 0),
                            'type': np.random.choice(['entry', 'rotation', 'flank', 'retreat'])
                        } for _ in range(np.random.randint(1, 4))
                    ]
                }
            }
            synthetic_annotations.append(annotation)
        
        # Save synthetic data
        output_file = self.annotations_dir / "synthetic_annotations.json"
        with open(output_file, 'w') as f:
            json.dump(synthetic_annotations, f, indent=2)
        
        print(f"Generated {num_samples} synthetic annotations")
        
        # Create splits
        return self.create_dataset_splits(str(output_file))
    
    def setup_dataset_structure(self):
        """Create complete dataset structure"""
        print("Setting up Valorant dataset structure...")
        
        # Create annotation tool
        self.create_annotation_tool()
        
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
        print("2. Run the annotation tool: python annotation_tool.py")
        print("3. Train the deep learning model")
        
        return dataset_info

if __name__ == "__main__":
    # Setup dataset
    collector = ValorantDatasetCollector()
    dataset_info = collector.setup_dataset_structure()
    
    print("\\nDataset setup complete!")
    print(f"Dataset location: {collector.dataset_dir}")
    print(f"Total samples: {dataset_info['total_samples']}")
