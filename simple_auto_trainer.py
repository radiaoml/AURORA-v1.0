import os
import json
import numpy as np
from pathlib import Path
import random

class SimpleAutoTrainer:
    """Simplified automatic training data generation"""
    
    def __init__(self):
        self.dataset_dir = Path("valorant_dataset")
        
        # Tactical categories
        self.maps = ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET']
        self.situations = ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank']
        self.formations = ['tight', 'balanced', 'spread', 'scattered']
        self.positions = ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
    
    def generate_mock_training_data(self, num_samples=500):
        """Generate realistic mock training data"""
        print("🎲 Generating Mock Training Data")
        print("=" * 50)
        
        annotations = {}
        
        # Scenario patterns for realistic data
        scenarios = [
            {'map': 'ASCENT', 'situation': 'entry', 'formation': 'tight', 'position': 'aggressive', 'entry_rating': 4, 'timing': 1.2, 'win_rate': 0.75},
            {'map': 'BIND', 'situation': 'post_plant', 'formation': 'spread', 'position': 'defensive', 'entry_rating': 3, 'timing': 2.1, 'win_rate': 0.65},
            {'map': 'HAVEN', 'situation': 'retake', 'formation': 'balanced', 'position': 'support', 'entry_rating': 5, 'timing': 0.8, 'win_rate': 0.82},
            {'map': 'SPLIT', 'situation': 'mid_control', 'formation': 'scattered', 'position': 'roaming', 'entry_rating': 2, 'timing': 3.2, 'win_rate': 0.45},
            {'map': 'ICEBOX', 'situation': 'eco', 'formation': 'tight', 'position': 'anchoring', 'entry_rating': 2, 'timing': 4.1, 'win_rate': 0.35},
            {'map': 'BREEZE', 'situation': 'buy_round', 'formation': 'balanced', 'position': 'aggressive', 'entry_rating': 4, 'timing': 1.5, 'win_rate': 0.78},
            {'map': 'FRACTURE', 'situation': 'force_buy', 'formation': 'spread', 'position': 'support', 'entry_rating': 3, 'timing': 2.8, 'win_rate': 0.68},
            {'map': 'PEARL', 'situation': 'flank', 'formation': 'scattered', 'position': 'roaming', 'entry_rating': 4, 'timing': 1.0, 'win_rate': 0.72},
        ]
        
        for i in range(num_samples):
            # Pick a scenario and add variation
            scenario = random.choice(scenarios)
            
            # Add realistic variation
            entry_rating = max(1, min(5, scenario['entry_rating'] + random.randint(-1, 1)))
            timing_gap = max(0.0, min(5.0, scenario['timing'] + random.uniform(-0.5, 0.5)))
            win_rate = max(0.0, min(1.0, scenario['win_rate'] + random.uniform(-0.1, 0.1)))
            
            annotation = {
                'image_path': f'frames/mock_frame_{i:06d}.jpg',
                'frame_number': i,
                'map': scenario['map'],
                'tactical_situation': scenario['situation'],
                'formation': scenario['formation'],
                'position_type': scenario['position'],
                'performance_metrics': {
                    'entry_rating': entry_rating,
                    'timing_gap': round(timing_gap, 1),
                    'formation_score': round(random.uniform(0.4, 0.9), 2),
                    'planting_score': round(random.uniform(0.5, 0.9), 2),
                    'rotation_score': round(random.uniform(0.4, 0.8), 2),
                    'win_rate': round(win_rate, 2)
                }
            }
            
            annotations[f"mock_sample_{i}"] = annotation
        
        print(f"✅ Generated {num_samples} realistic training samples")
        return annotations
    
    def create_simple_model(self):
        """Create a simple neural network for testing"""
        print("🧠 Creating Simple Neural Network")
        
        model_code = '''
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

class SimpleValorantNet(nn.Module):
    def __init__(self):
        super(SimpleValorantNet, self).__init__()
        
        # Feature extractor
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(128 * 28 * 28, 512),  # Adjusted for 224x224 input
            nn.ReLU(),
            nn.Dropout(0.5)
        )
        
        # Classification heads
        self.map_head = nn.Linear(512, 10)  # 10 maps
        self.situation_head = nn.Linear(512, 8)  # 8 situations
        self.formation_head = nn.Linear(512, 4)  # 4 formations
        self.position_head = nn.Linear(512, 5)  # 5 positions
        
        # Performance regression head
        self.performance_head = nn.Linear(512, 6)  # 6 performance metrics
    
    def forward(self, x):
        features = self.features(x)
        
        return {
            'map': self.map_head(features),
            'tactical_situation': self.situation_head(features),
            'formation': self.formation_head(features),
            'position_type': self.position_head(features),
            'performance': self.performance_head(features)
        }

class SimpleValorantDataset(Dataset):
    def __init__(self, annotations):
        self.annotations = list(annotations.values())
        
        # Encoders
        self.maps = ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET']
        self.situations = ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank']
        self.formations = ['tight', 'balanced', 'spread', 'scattered']
        self.positions = ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
        
        self.map_encoder = {label: idx for idx, label in enumerate(self.maps)}
        self.situation_encoder = {label: idx for idx, label in enumerate(self.situations)}
        self.formation_encoder = {label: idx for idx, label in enumerate(self.formations)}
        self.position_encoder = {label: idx for idx, label in enumerate(self.positions)}
        
        # Transform
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def __len__(self):
        return len(self.annotations)
    
    def __getitem__(self, idx):
        annotation = self.annotations[idx]
        
        # Create dummy image (since we don't have real images)
        image = torch.randn(3, 224, 224)
        
        # Encode labels
        labels = {
            'map': self.map_encoder[annotation['map']],
            'tactical_situation': self.situation_encoder[annotation['tactical_situation']],
            'formation': self.formation_encoder[annotation['formation']],
            'position_type': self.position_encoder[annotation['position_type']],
            'performance_metrics': annotation['performance_metrics']
        }
        
        return image, labels

def train_simple_model(annotations):
    """Train the simple model"""
    print("🏋️ Training Simple Neural Network")
    print("=" * 50)
    
    # Create dataset
    dataset = SimpleValorantDataset(annotations)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    # Create model
    model = SimpleValorantNet()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    
    # Loss functions
    classification_criterion = nn.CrossEntropyLoss()
    regression_criterion = nn.MSELoss()
    
    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    epochs = 20
    print(f"Training for {epochs} epochs...")
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_idx, (images, targets) in enumerate(dataloader):
            images = images.to(device)
            
            # Move targets to device
            map_targets = torch.tensor([t['map'] for t in targets]).to(device)
            situation_targets = torch.tensor([t['tactical_situation'] for t in targets]).to(device)
            formation_targets = torch.tensor([t['formation'] for t in targets]).to(device)
            position_targets = torch.tensor([t['position_type'] for t in targets]).to(device)
            
            # Performance targets (normalized)
            perf_targets = torch.stack([
                torch.tensor([t['performance_metrics']['entry_rating'] for t in targets]).float() / 5.0,
                torch.tensor([t['performance_metrics']['timing_gap'] for t in targets]).float() / 5.0,
                torch.tensor([t['performance_metrics']['formation_score'] for t in targets]).float(),
                torch.tensor([t['performance_metrics']['planting_score'] for t in targets]).float(),
                torch.tensor([t['performance_metrics']['rotation_score'] for t in targets]).float(),
                torch.tensor([t['performance_metrics']['win_rate'] for t in targets]).float()
            ], dim=1).to(device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(images)
            
            # Calculate losses
            loss = 0
            loss += classification_criterion(outputs['map'], map_targets)
            loss += classification_criterion(outputs['tactical_situation'], situation_targets)
            loss += classification_criterion(outputs['formation'], formation_targets)
            loss += classification_criterion(outputs['position_type'], position_targets)
            loss += regression_criterion(outputs['performance'], perf_targets)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1:2d}/{epochs}: Loss = {avg_loss:.4f}")
    
    # Save model
    torch.save(model.state_dict(), 'simple_trained_valorant_model.pth')
    print(f"✅ Training complete! Model saved as 'simple_trained_valorant_model.pth'")
    
    return 'simple_trained_valorant_model.pth'

if __name__ == "__main__":
    # Load annotations
    with open('valorant_dataset/annotations/auto_annotations.json', 'r') as f:
        annotations = json.load(f)
    
    # Train model
    model_path = train_simple_model(annotations)
    
    print(f"\\n🎉 Simple Training Complete!")
    print(f"Model saved: {model_path}")
'''
        
        # Save the simple model code
        model_file = self.dataset_dir / "simple_model.py"
        with open(model_file, 'w') as f:
            f.write(model_code)
        
        print(f"✅ Created simple model at {model_file}")
        return model_file
    
    def run_complete_pipeline(self):
        """Run the complete automatic pipeline"""
        print("🚀 Starting Complete Automatic Pipeline")
        print("=" * 60)
        
        # Step 1: Generate training data
        annotations = self.generate_mock_training_data(500)
        
        # Step 2: Save annotations
        print(f"\n💾 Saving training data...")
        annotations_dir = self.dataset_dir / "annotations"
        annotations_dir.mkdir(exist_ok=True)
        
        output_file = annotations_dir / "auto_annotations.json"
        with open(output_file, 'w') as f:
            json.dump(annotations, f, indent=2)
        
        print(f"✅ Saved {len(annotations)} annotations to {output_file}")
        
        # Step 3: Create dataset splits
        print("Creating dataset splits...")
        annotations_list = list(annotations.values())
        
        # Shuffle and split
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
            split_file = splits_dir / f"auto_{split_name}_annotations.json"
            with open(split_file, 'w') as f:
                json.dump(split_data, f, indent=2)
            print(f"Created auto_{split_name} split: {len(split_data)} samples")
        
        # Step 4: Create simple model
        model_file = self.create_simple_model()
        
        print(f"\n🎉 Complete Pipeline Ready!")
        print(f"📁 Dataset: {self.dataset_dir}")
        print(f"📊 Samples: {len(annotations)}")
        print(f"🧠 Model: {model_file}")
        
        # Step 5: Train the model
        print(f"\n🏋️ Starting Model Training...")
        print(f"Run this command to train:")
        print(f"python {model_file}")
        
        return {
            'annotations_file': output_file,
            'model_file': model_file,
            'total_samples': len(annotations)
        }

if __name__ == "__main__":
    trainer = SimpleAutoTrainer()
    result = trainer.run_complete_pipeline()
    
    if result:
        print(f"\n🎯 Next Steps:")
        print(f"1. Train the model: python {result['model_file']}")
        print(f"2. Test trained model with new videos")
        print(f"3. Integrate into AURORA backend")
        print(f"4. Enjoy AI-powered tactical analysis!")
    else:
        print(f"\n❌ Pipeline failed. Please check errors above.")
