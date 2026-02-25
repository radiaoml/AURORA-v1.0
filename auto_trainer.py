import os
import json
import numpy as np
from pathlib import Path
from local_video_analyzer import LocalVideoAnalyzer
from dataset_collector_simple import ValorantDatasetCollector

class AutoValorantTrainer:
    """Automatic training data generation and model training"""
    
    def __init__(self):
        self.collector = ValorantDatasetCollector()
        self.local_analyzer = LocalVideoAnalyzer()
        
        # YouTube URLs for automatic processing
        self.vod_urls = [
            "https://youtu.be/E4517INnHII?si=rqlSBD-gFFkwW4eM",
            "https://youtu.be/7gMwkCTbHMs?si=K20nmoKyWurq25HL", 
            "https://youtu.be/2LnFuREmbpk?si=FtMcNS9qihdEFypF",
            "https://youtu.be/5XG9kC4j8oQ?si=mN9pLqR3wK7tT2a",
            "https://youtu.be/9Ym7dG4kL2p?si=vQ8hXmN3jL9sR3b"
        ]
    
    def generate_automatic_annotations(self):
        """Generate training data automatically using local analyzer"""
        print("🤖 Generating Automatic Training Data")
        print("=" * 50)
        
        all_annotations = {}
        frame_count = 0
        
        for vod_idx, url in enumerate(self.vod_urls):
            print(f"\n📹 Processing VOD {vod_idx+1}/{len(self.vod_urls)}")
            print(f"URL: {url}")
            
            try:
                # Extract frames using existing video analyzer
                from video_analyzer import TacticalVisionEngine
                engine = TacticalVisionEngine(url)
                frames, source_meta = engine.extract_tactical_frames(fps_sample=3)  # Extract 3 fps
                
                if not frames:
                    print(f"❌ No frames extracted from VOD {vod_idx+1}")
                    continue
                
                print(f"✅ Extracted {len(frames)} frames")
                
                # Analyze each frame with local analyzer
                for frame_idx, frame_path in enumerate(frames):
                    print(f"🧠 Analyzing frame {frame_idx+1}/{len(frames)}...")
                    
                    try:
                        # Get automatic analysis from local analyzer
                        analysis = self.local_analyzer.analyze_frames([frame_path])
                        
                        # Convert analysis to training annotation format
                        annotation = {
                            'image_path': frame_path,
                            'frame_number': frame_count,
                            'map': analysis.get('detected_map', 'ASCENT'),
                            'tactical_situation': self._infer_situation(analysis),
                            'formation': self._infer_formation(analysis),
                            'position_type': self._infer_position_type(analysis),
                            'performance_metrics': {
                                'entry_rating': self._extract_rating(analysis.get('entry_rating', 'C')),
                                'timing_gap': self._extract_timing(analysis.get('timing_gap', '1.5s')),
                                'formation_score': np.random.uniform(0.6, 0.9),  # Simulated
                                'planting_score': np.random.uniform(0.6, 0.9),  # Simulated
                                'rotation_score': np.random.uniform(0.6, 0.9),  # Simulated
                                'win_rate': self._extract_win_rate(analysis.get('win_rate_prediction', '65%'))
                            }
                        }
                        
                        all_annotations[f"sample_{frame_count}"] = annotation
                        frame_count += 1
                        
                    except Exception as e:
                        print(f"⚠️ Error analyzing frame {frame_idx}: {e}")
                        continue
                
                print(f"✅ Processed {len(frames)} frames from VOD {vod_idx+1}")
                
            except Exception as e:
                print(f"❌ Error processing VOD {vod_idx+1}: {e}")
                continue
        
        print(f"\n📊 Auto-annotation Summary:")
        print(f"Total VODs processed: {vod_idx+1}")
        print(f"Total frames analyzed: {frame_count}")
        print(f"Total annotations generated: {len(all_annotations)}")
        
        return all_annotations
    
    def _infer_situation(self, analysis):
        """Infer tactical situation from analysis"""
        recommendations = analysis.get('tactical_suggestion', '')
        
        if 'entry' in recommendations.lower():
            return 'entry'
        elif 'plant' in recommendations.lower():
            return 'post_plant'
        elif 'retake' in recommendations.lower():
            return 'retake'
        elif 'eco' in recommendations.lower():
            return 'eco'
        elif 'buy' in recommendations.lower():
            return 'buy_round'
        elif 'mid' in recommendations.lower():
            return 'mid_control'
        else:
            return np.random.choice(['entry', 'post_plant', 'retake', 'mid_control'])
    
    def _infer_formation(self, analysis):
        """Infer formation from analysis"""
        recommendations = analysis.get('tactical_suggestion', '')
        
        if 'tight' in recommendations.lower():
            return 'tight'
        elif 'spread' in recommendations.lower():
            return 'spread'
        elif 'balanced' in recommendations.lower():
            return 'balanced'
        else:
            return np.random.choice(['tight', 'balanced', 'spread'])
    
    def _infer_position_type(self, analysis):
        """Infer position type from analysis"""
        recommendations = analysis.get('tactical_suggestion', '')
        
        if 'aggressive' in recommendations.lower():
            return 'aggressive'
        elif 'defensive' in recommendations.lower():
            return 'defensive'
        elif 'support' in recommendations.lower():
            return 'support'
        elif 'roaming' in recommendations.lower():
            return 'roaming'
        else:
            return np.random.choice(['aggressive', 'defensive', 'support'])
    
    def _extract_rating(self, rating_str):
        """Extract numeric rating from string like 'A', 'B', 'C'"""
        rating_map = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1}
        return rating_map.get(rating_str.upper(), 3)
    
    def _extract_timing(self, timing_str):
        """Extract timing from string like '1.5s'"""
        try:
            return float(timing_str.replace('s', ''))
        except:
            return 1.5
    
    def _extract_win_rate(self, win_rate_str):
        """Extract win rate from string like '65%'"""
        try:
            return float(win_rate_str.replace('%', '')) / 100.0
        except:
            return 0.65
    
    def save_and_split_data(self, annotations):
        """Save annotations and create dataset splits"""
        print(f"\n💾 Saving automatic annotations...")
        
        # Create directories
        annotations_dir = self.collector.dataset_dir / "annotations"
        annotations_dir.mkdir(exist_ok=True)
        
        # Save annotations
        output_file = annotations_dir / "auto_annotations.json"
        with open(output_file, 'w') as f:
            json.dump(annotations, f, indent=2)
        
        print(f"✅ Saved {len(annotations)} annotations to {output_file}")
        
        # Create dataset splits
        print("Creating dataset splits...")
        annotations_list = list(annotations.values())
        
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
        splits_dir = self.collector.dataset_dir / "splits"
        splits_dir.mkdir(exist_ok=True)
        
        for split_name, split_data in [('train', train_data), ('val', val_data), ('test', test_data)]:
            split_file = splits_dir / f"auto_{split_name}_annotations.json"
            with open(split_file, 'w') as f:
                json.dump(split_data, f, indent=2)
            print(f"Created auto_{split_name} split: {len(split_data)} samples")
        
        return {
            'train_file': splits_dir / "auto_train_annotations.json",
            'val_file': splits_dir / "auto_val_annotations.json", 
            'test_file': splits_dir / "auto_test_annotations.json"
        }
    
    def train_model_automatically(self, split_files):
        """Train model on automatically generated data"""
        print(f"\n🏋️ Training Model on Automatic Data")
        print("=" * 50)
        
        # Import training modules
        from deep_learning_tactical_engine import ValorantTacticalModel, ValorantTrainer
        from torch.utils.data import DataLoader
        import torch
        import torchvision.transforms as transforms
        from PIL import Image
        
        # Create dataset class for auto data
        class AutoValorantDataset(torch.utils.data.Dataset):
            def __init__(self, annotations_file, transform=None):
                with open(annotations_file, 'r') as f:
                    self.annotations = json.load(f)
                self.transform = transform
                
                # Label encoders
                self.maps = ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET']
                self.situations = ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank']
                self.formations = ['tight', 'balanced', 'spread', 'scattered']
                self.positions = ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
                
                self.map_encoder = {label: idx for idx, label in enumerate(self.maps)}
                self.situation_encoder = {label: idx for idx, label in enumerate(self.situations)}
                self.formation_encoder = {label: idx for idx, label in enumerate(self.formations)}
                self.position_encoder = {label: idx for idx, label in enumerate(self.positions)}
            
            def __len__(self):
                return len(self.annotations)
            
            def __getitem__(self, idx):
                annotation = list(self.annotations.values())[idx]
                
                # Load image
                img_path = annotation['image_path']
                if os.path.exists(img_path):
                    image = Image.open(img_path).convert('RGB')
                else:
                    image = Image.new('RGB', (224, 224), color='black')
                
                if self.transform:
                    image = self.transform(image)
                
                # Encode labels
                labels = {
                    'map': self.map_encoder[annotation['map']],
                    'tactical_situation': self.situation_encoder[annotation['tactical_situation']],
                    'formation': self.formation_encoder[annotation['formation']],
                    'position_type': self.position_encoder[annotation['position_type']],
                    'performance_metrics': annotation['performance_metrics']
                }
                
                return image, labels
        
        # Create transforms
        train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Create datasets
        print("Creating datasets...")
        train_dataset = AutoValorantDataset(split_files['train_file'], train_transform)
        val_dataset = AutoValorantDataset(split_files['val_file'], val_transform) if os.path.exists(split_files['val_file']) else None
        
        print(f"Train dataset: {len(train_dataset)} samples")
        if val_dataset:
            print(f"Validation dataset: {len(val_dataset)} samples")
        
        # Create dataloaders
        train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False) if val_dataset else None
        
        # Create model
        print("Creating model...")
        model = ValorantTacticalModel('efficientnet_b0')
        
        # Device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = model.to(device)
        print(f"Using device: {device}")
        
        # Create trainer
        trainer = ValorantTrainer(model, device)
        
        # Train for fewer epochs on auto data
        epochs = 10
        print(f"Training for {epochs} epochs...")
        
        for epoch in range(epochs):
            # Training
            train_metrics = trainer.train_epoch(train_loader)
            
            # Validation
            val_metrics = trainer.validate(val_loader) if val_loader else {'total_loss': 0}
            
            print(f"Epoch {epoch+1}/{epochs}: "
                  f"Train Loss: {train_metrics['total_loss']:.4f} | "
                  f"Val Loss: {val_metrics['total_loss']:.4f}")
        
        # Save model
        torch.save(model.state_dict(), 'auto_trained_valorant_model.pth')
        print(f"\n✅ Auto-training complete!")
        print(f"💾 Model saved as 'auto_trained_valorant_model.pth'")
        
        return 'auto_trained_valorant_model.pth'
    
    def run_automatic_pipeline(self):
        """Run complete automatic training pipeline"""
        print("🚀 Starting Automatic Valorant Training Pipeline")
        print("=" * 60)
        
        # Step 1: Generate automatic annotations
        annotations = self.generate_automatic_annotations()
        
        if not annotations:
            print("❌ No annotations generated. Cannot continue.")
            return None
        
        # Step 2: Save and split data
        split_files = self.save_and_split_data(annotations)
        
        # Step 3: Train model automatically
        model_path = self.train_model_automatically(split_files)
        
        print(f"\n🎉 Automatic Training Complete!")
        print(f"📁 Dataset: {self.collector.dataset_dir}")
        print(f"🤖 Model: {model_path}")
        print(f"📊 Samples: {len(annotations)}")
        
        # Step 4: Test model
        print(f"\n🧪 Testing automatically trained model...")
        self.test_trained_model(model_path)
        
        return model_path
    
    def test_trained_model(self, model_path):
        """Test the automatically trained model"""
        try:
            import torch
            from deep_learning_tactical_engine import ValorantTacticalModel
            from PIL import Image
            import torchvision.transforms as transforms
            
            # Load model
            model = ValorantTacticalModel('efficientnet_b0')
            model.load_state_dict(torch.load(model_path, map_location='cpu'))
            model.eval()
            
            # Test with a sample frame
            test_frames = list(Path("valorant_dataset/frames").glob("*.jpg"))
            if test_frames:
                test_image = Image.open(test_frames[0]).convert('RGB')
                
                # Transform
                transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
                
                input_tensor = transform(test_image).unsqueeze(0)
                
                # Get prediction
                with torch.no_grad():
                    outputs = model(input_tensor)
                
                # Convert predictions to readable format
                maps = ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET']
                situations = ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank']
                
                map_pred = maps[torch.argmax(outputs['map']).item()]
                situation_pred = situations[torch.argmax(outputs['tactical_situation']).item()]
                
                print(f"✅ Model test successful!")
                print(f"  Predicted map: {map_pred}")
                print(f"  Predicted situation: {situation_pred}")
                print(f"  Performance metrics shape: {outputs['performance'].shape}")
                
                return True
            else:
                print("⚠️ No test frames found")
                return False
                
        except Exception as e:
            print(f"❌ Error testing model: {e}")
            return False

if __name__ == "__main__":
    # Run automatic training pipeline
    auto_trainer = AutoValorantTrainer()
    model_path = auto_trainer.run_automatic_pipeline()
    
    if model_path:
        print(f"\n🎯 Next Steps:")
        print(f"1. Test model with new YouTube videos")
        print(f"2. Integrate into AURORA backend")
        print(f"3. Enjoy AI-powered tactical analysis!")
    else:
        print(f"\n❌ Automatic training failed. Please check errors above.")
