import json
from pathlib import Path

class ConsoleValorantAnnotator:
    def __init__(self, dataset_dir="valorant_dataset"):
        self.dataset_dir = Path(dataset_dir)
        self.annotations = {}
        self.current_idx = 0
        
        # Load frame paths
        self.frame_paths = []
        frames_dir = self.dataset_dir / "frames"
        
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
        print(f"\n{'='*60}")
        print(f"ANNOTATING FRAME {self.current_idx + 1}/{len(self.frame_paths)}")
        print(f"{'='*60}")
        print(f"Frame: {Path(frame_path).name}")
        
        # Get annotations
        annotation = {
            'image_path': frame_path,
            'frame_number': self.current_idx
        }
        
        # Map
        print(f"\n📍 MAP DETECTION:")
        print("Look at the frame and identify which Valorant map is shown.")
        annotation['map'] = self.get_choice("Which map is this?", self.maps)
        
        # Tactical situation
        print(f"\n⚔️ TACTICAL SITUATION:")
        print("What tactical situation is shown in this frame?")
        annotation['tactical_situation'] = self.get_choice("What's happening?", self.situations)
        
        # Formation
        print(f"\n👥 FORMATION ANALYSIS:")
        print("How are the players positioned relative to each other?")
        annotation['formation'] = self.get_choice("Formation type:", self.formations)
        
        # Position type
        print(f"\n🎯 POSITION TYPE:")
        print("What type of positioning is demonstrated?")
        annotation['position_type'] = self.get_choice("Position type:", self.positions)
        
        # Performance metrics
        print(f"\n📊 PERFORMANCE METRICS:")
        print("Rate the tactical execution shown in this frame.")
        
        annotation['performance_metrics'] = {
            'entry_rating': self.get_number("Entry rating (1=poor, 5=excellent): ", 1, 5, int),
            'timing_gap': self.get_number("Timing gap in seconds (0.0-5.0): ", 0.0, 5.0, float),
            'formation_score': self.get_number("Formation score (0.0=poor, 1.0=excellent): ", 0.0, 1.0, float),
            'planting_score': self.get_number("Planting score (0.0=poor, 1.0=excellent): ", 0.0, 1.0, float),
            'rotation_score': self.get_number("Rotation score (0.0=poor, 1.0=excellent): ", 0.0, 1.0, float),
            'win_rate': self.get_number("Estimated win rate (0.0-1.0): ", 0.0, 1.0, float)
        }
        
        # Save annotation
        self.annotations[frame_path] = annotation
        
        print(f"\n✅ Frame {self.current_idx + 1} annotated successfully!")
        return True
    
    def run(self):
        """Run the annotation process"""
        if not self.frame_paths:
            print("No frames found to annotate!")
            return
        
        print("=== CONSOLE VALORANT ANNOTATION TOOL ===")
        print("Instructions:")
        print("1. Open the frame image in your image viewer")
        print("2. Answer the questions based on what you see")
        print("3. Be consistent with your ratings")
        print("4. Press Enter to continue, Ctrl+C to quit")
        
        try:
            input("\nPress Enter to start annotating...")
        except KeyboardInterrupt:
            print("\nAnnotation cancelled.")
            return
        
        while self.current_idx < len(self.frame_paths):
            frame_path = self.frame_paths[self.current_idx]
            
            print(f"\n{'='*60}")
            print(f"FRAME {self.current_idx + 1}/{len(self.frame_paths)}")
            print(f"{'='*60}")
            print(f"Open this image in your viewer: {frame_path}")
            
            try:
                choice = input("\nOptions: [n]ext frame, [s]kip, [q]uit: ").lower()
                
                if choice == 'n':  # Annotate
                    if self.annotate_frame(frame_path):
                        self.current_idx += 1
                elif choice == 's':  # Skip
                    self.current_idx += 1
                    print(f"⏭️ Skipped frame {self.current_idx}")
                elif choice == 'q':  # Quit
                    break
                else:
                    print("Invalid choice, try again")
                    
            except KeyboardInterrupt:
                print("\nAnnotation interrupted.")
                break
        
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
        
        # Training instructions
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Run this command to train the model:")
        print(f"   python train_real_model.py")
        print(f"2. The model will learn from your annotations")
        print(f"3. Test the trained model with new videos")

if __name__ == "__main__":
    annotator = ConsoleValorantAnnotator()
    annotator.run()
