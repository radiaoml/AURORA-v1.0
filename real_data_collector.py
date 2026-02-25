import os
import json
from pathlib import Path
from dataset_collector_simple import ValorantDatasetCollector
from video_analyzer import TacticalVisionEngine

class ValorantDataCollector:
    """Enhanced data collector for real Valorant footage"""
    
    def __init__(self):
        self.collector = ValorantDatasetCollector()
        self.vod_urls = [
            "https://youtu.be/E4517INnHII?si=rqlSBD-gFFkwW4eM",
            "https://youtu.be/7gMwkCTbHMs?si=K20nmoKyWurq25HL",
            "https://youtu.be/2LnFuREmbpk?si=FtMcNS9qihdEFypF"
        ]
        
    def extract_frames_from_youtube_vods(self):
        """Extract frames from your YouTube VODs"""
        print("🎬 Extracting frames from YouTube VODs...")
        print("=" * 50)
        
        all_frames = []
        vod_data = {}
        
        for i, url in enumerate(self.vod_urls):
            print(f"\n📹 Processing VOD {i+1}/{len(self.vod_urls)}")
            print(f"URL: {url}")
            
            try:
                # Use existing video analyzer to download and extract frames
                engine = TacticalVisionEngine(url)
                frames, source_meta = engine.extract_tactical_frames(fps_sample=2)  # Extract 2 fps
                
                if frames:
                    vod_id = f"vod_{i+1}"
                    vod_data[vod_id] = {
                        'url': url,
                        'frames': frames,
                        'source_meta': source_meta,
                        'frame_count': len(frames)
                    }
                    all_frames.extend(frames)
                    print(f"✅ Extracted {len(frames)} frames")
                else:
                    print(f"❌ No frames extracted")
                    
            except Exception as e:
                print(f"❌ Error processing VOD {i+1}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"Total VODs processed: {len(vod_data)}")
        print(f"Total frames extracted: {len(all_frames)}")
        
        # Save VOD metadata
        metadata_file = self.collector.dataset_dir / "vod_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(vod_data, f, indent=2)
        
        print(f"✅ VOD metadata saved to {metadata_file}")
        return all_frames, vod_data
    
    def create_annotation_interface(self):
        """Create a simple annotation interface"""
        annotation_script = '''
import cv2
import numpy as np
import json
from pathlib import Path

class SimpleAnnotationTool:
    def __init__(self, dataset_dir):
        self.dataset_dir = Path(dataset_dir)
        self.annotations = {}
        self.current_idx = 0
        
        # Load frame paths
        self.frame_paths = []
        frames_dir = self.dataset_dir / "frames"
        for video_dir in frames_dir.iterdir():
            if video_dir.is_dir():
                for frame_path in video_dir.glob("*.jpg"):
                    self.frame_paths.append(str(frame_path))
        
        self.frame_paths.sort()
        print(f"Found {len(self.frame_paths)} frames to annotate")
        
        # Annotation categories
        self.categories = {
            'map': ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET'],
            'tactical_situation': ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank'],
            'formation': ['tight', 'balanced', 'spread', 'scattered'],
            'position_type': ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
        }
    
    def get_user_input(self, prompt, options):
        """Get user input with validation"""
        print(f"\\n{prompt}")
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
    
    def get_performance_input(self):
        """Get performance metrics input"""
        print("\\n📊 Performance Metrics:")
        metrics = {}
        
        metrics['entry_rating'] = self.get_numeric_input("Entry rating (1-5): ", 1, 5, int)
        metrics['timing_gap'] = self.get_numeric_input("Timing gap (0.0-5.0s): ", 0.0, 5.0, float)
        metrics['formation_score'] = self.get_numeric_input("Formation score (0.0-1.0): ", 0.0, 1.0, float)
        metrics['planting_score'] = self.get_numeric_input("Planting score (0.0-1.0): ", 0.0, 1.0, float)
        metrics['rotation_score'] = self.get_numeric_input("Rotation score (0.0-1.0): ", 0.0, 1.0, float)
        metrics['win_rate'] = self.get_numeric_input("Win rate (0.0-1.0): ", 0.0, 1.0, float)
        
        return metrics
    
    def get_numeric_input(self, prompt, min_val, max_val, value_type):
        """Get validated numeric input"""
        while True:
            try:
                value = value_type(input(prompt))
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"Value must be between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
    
    def annotate_current_frame(self):
        """Annotate the current frame"""
        if self.current_idx >= len(self.frame_paths):
            print("All frames annotated!")
            return False
        
        frame_path = self.frame_paths[self.current_idx]
        frame = cv2.imread(frame_path)
        
        if frame is None:
            print(f"Could not load frame: {frame_path}")
            self.current_idx += 1
            return True
        
        # Display frame
        cv2.imshow('Valorant Frame Annotation', frame)
        
        print(f"\\n🎯 Annotating Frame {self.current_idx + 1}/{len(self.frame_paths)}")
        print(f"Path: {frame_path}")
        
        # Get annotations
        annotation = {
            'image_path': str(frame_path),
            'frame_number': self.current_idx
        }
        
        # Get categorical annotations
        for category, options in self.categories.items():
            annotation[category] = self.get_user_input(f"📍 {category.upper()}", options)
        
        # Get performance metrics
        annotation['performance_metrics'] = self.get_performance_input()
        
        # Save annotation
        self.annotations[frame_path] = annotation
        
        cv2.destroyAllWindows()
        self.current_idx += 1
        
        print(f"✅ Frame annotated successfully")
        return True
    
    def run_annotation(self):
        """Run the annotation process"""
        print("🏷️ Valorant Frame Annotation Tool")
        print("=" * 40)
        print("Controls:")
        print("  'n' - Next frame (annotate)")
        print("  's' - Skip frame")
        print("  'q' - Quit and save")
        print("  'h' - Show help")
        
        while self.current_idx < len(self.frame_paths):
            frame_path = self.frame_paths[self.current_idx]
            frame = cv2.imread(frame_path)
            
            if frame is not None:
                # Add frame info
                status = "✓" if frame_path in self.annotations else "○"
                cv2.putText(frame, f"Frame {self.current_idx+1}/{len(self.frame_paths)} {status}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'n' to annotate, 's' to skip, 'q' to quit", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow('Valorant Annotation', frame)
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('n'):  # Annotate
                if not self.annotate_current_frame():
                    break
            elif key == ord('s'):  # Skip
                self.current_idx += 1
                print(f"⏭️ Skipped frame {self.current_idx}")
            elif key == ord('q'):  # Quit
                break
            elif key == ord('h'):  # Help
                print("\\n📖 Annotation Guide:")
                print("• Map: Which Valorant map is shown?")
                print("• Tactical Situation: What's happening in the round?")
                print("• Formation: How are players positioned?")
                print("• Position Type: What type of positioning is shown?")
                print("• Performance: Rate the tactical execution (1-5 or 0.0-1.0)")
        
        cv2.destroyAllWindows()
        self.save_annotations()
    
    def save_annotations(self):
        """Save annotations to file"""
        output_file = self.dataset_dir / "annotations" / "real_annotations.json"
        with open(output_file, 'w') as f:
            json.dump(self.annotations, f, indent=2)
        
        print(f"\\n💾 Saved {len(self.annotations)} annotations to {output_file}")
        
        # Create dataset splits
        from dataset_collector_simple import ValorantDatasetCollector
        collector = ValorantDatasetCollector()
        collector.create_dataset_splits(str(output_file))

if __name__ == "__main__":
    # Run annotation tool
    tool = SimpleAnnotationTool("valorant_dataset")
    tool.run_annotation()
'''
        
        # Save annotation tool
        tool_file = self.collector.dataset_dir / "real_annotation_tool.py"
        with open(tool_file, 'w') as f:
            f.write(annotation_script)
        
        print(f"✅ Annotation tool created at {tool_file}")
        return tool_file
    
    def setup_real_data_pipeline(self):
        """Setup the complete real data collection pipeline"""
        print("🚀 Setting up Real Valorant Data Pipeline")
        print("=" * 50)
        
        # Step 1: Extract frames from YouTube VODs
        print("\n📹 Step 1: Extracting frames from your YouTube VODs...")
        all_frames, vod_data = self.extract_frames_from_youtube_vods()
        
        if not all_frames:
            print("❌ No frames extracted. Please check your YouTube URLs.")
            return None
        
        # Step 2: Create annotation tool
        print("\n🏷️ Step 2: Creating annotation tool...")
        annotation_tool = self.create_annotation_interface()
        
        # Step 3: Provide instructions
        print(f"\n📋 Step 3: Annotation Instructions")
        print("=" * 30)
        print(f"1. Run the annotation tool:")
        print(f"   python {annotation_tool}")
        print(f"\\n2. Annotate at least 100 frames for good results")
        print(f"\\n3. Focus on diverse situations:")
        print(f"   - Different maps (ASCENT, BIND, HAVEN, etc.)")
        print(f"   - Different tactical situations (entry, post-plant, retake)")
        print(f"   - Different formations (tight, balanced, spread)")
        print(f"\\n4. Rate performance honestly:")
        print(f"   - Entry rating: 1 (poor) to 5 (excellent)")
        print(f"   - Timing gap: How fast/slow is the execution?")
        print(f"   - Win rate: Estimated win probability")
        
        print(f"\n🎯 Tips for Good Annotations:")
        print("• Be consistent with your ratings")
        print("• Include a variety of tactical situations")
        print("• Annotate different maps and agents")
        print("• Focus on key moments (entry, post-plant, retakes)")
        
        print(f"\n✅ Data pipeline setup complete!")
        print(f"📁 Dataset location: {self.collector.dataset_dir}")
        print(f"📊 Frames extracted: {len(all_frames)}")
        print(f"🎬 VODs processed: {len(vod_data)}")
        
        return {
            'frames': all_frames,
            'vod_data': vod_data,
            'annotation_tool': annotation_tool,
            'dataset_dir': self.collector.dataset_dir
        }

if __name__ == "__main__":
    collector = ValorantDataCollector()
    pipeline_result = collector.setup_real_data_pipeline()
    
    if pipeline_result:
        print(f"\n🎉 Ready to start annotating!")
        print(f"Run this command to begin:")
        print(f"python {pipeline_result['annotation_tool']}")
    else:
        print(f"\n❌ Pipeline setup failed. Please check the errors above.")
