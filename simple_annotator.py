import cv2
import numpy as np
import json
from pathlib import Path

class SimpleValorantAnnotator:
    def __init__(self, dataset_dir="valorant_dataset"):
        self.dataset_dir = Path(dataset_dir)
        self.annotations = {}
        self.current_idx = 0
        
        # Load frame paths
        self.frame_paths = []
        frames_dir = self.dataset_dir / "frames"
        
        # Check for extracted frames
        if not frames_dir.exists():
            print(f"No frames directory found at {frames_dir}")
            print("Please run real_data_collector.py first to extract frames.")
            return
        
        for video_dir in frames_dir.iterdir():
            if video_dir.is_dir():
                for frame_path in video_dir.glob("*.jpg"):
                    self.frame_paths.append(str(frame_path))
        
        # Also check directly in frames_dir
        for frame_path in frames_dir.glob("*.jpg"):
            self.frame_paths.append(str(frame_path))
        
        self.frame_paths.sort()
        print(f"Found {len(self.frame_paths)} frames to annotate")
        
        # Annotation categories
        self.maps = ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET']
        self.situations = ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank']
        self.formations = ['tight', 'balanced', 'spread', 'scattered']
        self.positions = ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
    
    def get_choice(self, prompt, options):
        """Get user choice with validation"""
        print(f"\n{prompt}")
        for i, option in enumerate(options):
            print(f"  {i+1}. {option}")
        
        while True:
            try:
                choice = int(input("Select option (number): ")) - 1
                if 0 <= choice < len(options):
                    return options[choice]
                else:
                    print("Invalid choice, try again")
            except ValueError:
                print("Please enter a number")
    
    def get_number(self, prompt, min_val, max_val, data_type=float):
        """Get validated number input"""
        while True:
            try:
                value = data_type(input(prompt))
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"Value must be between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
    
    def annotate_frame(self, frame_path):
        """Annotate a single frame"""
        frame = cv2.imread(frame_path)
        if frame is None:
            return False
        
        cv2.imshow('Valorant Annotation', frame)
        
        print(f"\n=== ANNOTATING FRAME {self.current_idx + 1}/{len(self.frame_paths)} ===")
        print(f"Frame: {Path(frame_path).name}")
        
        # Get annotations
        annotation = {
            'image_path': frame_path,
            'frame_number': self.current_idx
        }
        
        # Map
        annotation['map'] = self.get_choice("MAP:", self.maps)
        
        # Tactical situation
        annotation['tactical_situation'] = self.get_choice("TACTICAL SITUATION:", self.situations)
        
        # Formation
        annotation['formation'] = self.get_choice("FORMATION:", self.formations)
        
        # Position type
        annotation['position_type'] = self.get_choice("POSITION TYPE:", self.positions)
        
        # Performance metrics
        print("\nPERFORMANCE METRICS:")
        annotation['performance_metrics'] = {
            'entry_rating': self.get_number("Entry rating (1-5): ", 1, 5, int),
            'timing_gap': self.get_number("Timing gap (0.0-5.0s): ", 0.0, 5.0, float),
            'formation_score': self.get_number("Formation score (0.0-1.0): ", 0.0, 1.0, float),
            'planting_score': self.get_number("Planting score (0.0-1.0): ", 0.0, 1.0, float),
            'rotation_score': self.get_number("Rotation score (0.0-1.0): ", 0.0, 1.0, float),
            'win_rate': self.get_number("Win rate (0.0-1.0): ", 0.0, 1.0, float)
        }
        
        # Save annotation
        self.annotations[frame_path] = annotation
        
        cv2.destroyAllWindows()
        return True
    
    def run(self):
        """Run the annotation process"""
        if not self.frame_paths:
            print("No frames found to annotate!")
            return
        
        print("=== VALORANT FRAME ANNOTATION TOOL ===")
        print("Controls:")
        print("  'n' - Annotate current frame")
        print("  's' - Skip current frame")
        print("  'q' - Quit and save annotations")
        print("  'h' - Show help")
        
        while self.current_idx < len(self.frame_paths):
            frame_path = self.frame_paths[self.current_idx]
            frame = cv2.imread(frame_path)
            
            if frame is not None:
                # Add frame info
                status = "✓" if frame_path in self.annotations else "○"
                cv2.putText(frame, f"Frame {self.current_idx+1}/{len(self.frame_paths)} {status}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'n' to annotate, 's' to skip, 'q' to quit", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                cv2.imshow('Valorant Annotation', frame)
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('n'):  # Annotate
                if self.annotate_frame(frame_path):
                    print(f"✅ Frame {self.current_idx + 1} annotated")
                    self.current_idx += 1
                else:
                    print(f"❌ Could not load frame {self.current_idx + 1}")
                    self.current_idx += 1
            elif key == ord('s'):  # Skip
                self.current_idx += 1
                print(f"⏭️ Skipped frame {self.current_idx}")
            elif key == ord('q'):  # Quit
                break
            elif key == ord('h'):  # Help
                print("\n=== ANNOTATION GUIDE ===")
                print("MAP: Which Valorant map is shown?")
                print("TACTICAL SITUATION: What's happening?")
                print("FORMATION: How are players positioned?")
                print("POSITION TYPE: What type of positioning?")
                print("PERFORMANCE: Rate the execution (1=poor, 5=excellent)")
                print("TIMING GAP: How fast/slow is the execution?")
                print("SCORES: Rate 0.0 (poor) to 1.0 (excellent)")
                print("WIN RATE: Estimated win probability")
        
        cv2.destroyAllWindows()
        self.save_annotations()
    
    def save_annotations(self):
        """Save annotations to file"""
        if not self.annotations:
            print("No annotations to save!")
            return
        
        # Create annotations directory if needed
        annotations_dir = self.dataset_dir / "annotations"
        annotations_dir.mkdir(exist_ok=True)
        
        # Save annotations
        output_file = annotations_dir / "real_annotations.json"
        with open(output_file, 'w') as f:
            json.dump(self.annotations, f, indent=2)
        
        print(f"\n✅ Saved {len(self.annotations)} annotations to {output_file}")
        
        # Create dataset splits
        print("Creating dataset splits...")
        annotations_list = list(self.annotations.values())
        
        # Shuffle and split
        import random
        random.shuffle(annotations_list)
        
        total = len(annotations_list)
        train_size = int(total * 0.7)
        val_size = int(total * 0.2)
        
        train_data = annotations_list[:train_size]
        val_data = annotations_list[train_size:train_size + val_size]
        test_data = annotations_list[train_size + val_size:]
        
        # Save splits
        splits_dir = self.dataset_dir / "splits"
        splits_dir.mkdir(exist_ok=True)
        
        for split_name, split_data in [('train', train_data), ('val', val_data), ('test', test_data)]:
            split_file = splits_dir / f"{split_name}_annotations.json"
            with open(split_file, 'w') as f:
                json.dump(split_data, f, indent=2)
            print(f"Created {split_name} split: {len(split_data)} samples")
        
        print(f"\n🎉 Dataset ready for training!")
        print(f"Total samples: {total}")
        print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")

if __name__ == "__main__":
    annotator = SimpleValorantAnnotator()
    annotator.run()
