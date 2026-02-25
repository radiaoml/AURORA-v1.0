import os
import json
import numpy as np
from pathlib import Path
import random

def create_training_data():
    """Create training data automatically"""
    print("Creating automatic training data...")
    
    # Tactical categories
    maps = ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET']
    situations = ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank']
    formations = ['tight', 'balanced', 'spread', 'scattered']
    positions = ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
    
    # Generate 200 training samples
    annotations = {}
    
    for i in range(200):
        # Realistic scenario
        scenario = {
            'map': random.choice(maps),
            'tactical_situation': random.choice(situations),
            'formation': random.choice(formations),
            'position_type': random.choice(positions),
            'performance_metrics': {
                'entry_rating': random.randint(2, 5),
                'timing_gap': round(random.uniform(0.5, 3.5), 1),
                'formation_score': round(random.uniform(0.4, 0.9), 2),
                'planting_score': round(random.uniform(0.5, 0.9), 2),
                'rotation_score': round(random.uniform(0.4, 0.8), 2),
                'win_rate': round(random.uniform(0.4, 0.85), 2)
            }
        }
        
        scenario['image_path'] = f'frames/auto_frame_{i:06d}.jpg'
        scenario['frame_number'] = i
        
        annotations[f"auto_sample_{i}"] = scenario
    
    # Save annotations
    dataset_dir = Path("valorant_dataset")
    annotations_dir = dataset_dir / "annotations"
    annotations_dir.mkdir(exist_ok=True)
    
    output_file = annotations_dir / "auto_annotations.json"
    with open(output_file, 'w') as f:
        json.dump(annotations, f, indent=2)
    
    print(f"Generated {len(annotations)} training samples")
    print(f"Saved to: {output_file}")
    
    return annotations

def create_simple_nn_code():
    """Create simple neural network code"""
    code = '''
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json

class ValorantNet(nn.Module):
    def __init__(self):
        super(ValorantNet, self).__init__()
        
        self.features = nn.Sequential(
            nn.Linear(3*224*224, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        
        # Output heads
        self.map_head = nn.Linear(128, 10)  # 10 maps
        self.situation_head = nn.Linear(128, 8)  # 8 situations
        self.formation_head = nn.Linear(128, 4)  # 4 formations
        self.position_head = nn.Linear(128, 5)  # 5 positions
        self.performance_head = nn.Linear(128, 6)  # 6 metrics
    
    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten
        features = self.features(x)
        
        return {
            'map': self.map_head(features),
            'tactical_situation': self.situation_head(features),
            'formation': self.formation_head(features),
            'position_type': self.position_head(features),
            'performance': self.performance_head(features)
        }

class ValorantDataset(Dataset):
    def __init__(self, annotations_file):
        with open(annotations_file, 'r') as f:
            self.annotations = json.load(f)
        
        self.data = list(self.annotations.values())
        
        # Encoders
        self.maps = ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET']
        self.situations = ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank']
        self.formations = ['tight', 'balanced', 'spread', 'scattered']
        self.positions = ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
        
        self.map_encoder = {label: idx for idx, label in enumerate(self.maps)}
        self.situation_encoder = {label: idx for idx, label in enumerate(self.situations)}
        self.formation_encoder = {label: idx for idx, label in enumerate(self.formations)}
        self.position_encoder = {label: idx for idx, label in enumerate(self.positions)}
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Create random image tensor (since we don't have real images)
        image = torch.randn(3, 224, 224)
        
        labels = {
            'map': self.map_encoder[item['map']],
            'tactical_situation': self.situation_encoder[item['tactical_situation']],
            'formation': self.formation_encoder[item['formation']],
            'position_type': self.position_encoder[item['position_type']],
            'performance_metrics': item['performance_metrics']
        }
        
        return image, labels

def train_model():
    """Train the model"""
    print("Training Valorant Neural Network...")
    
    # Load data
    dataset = ValorantDataset('valorant_dataset/annotations/auto_annotations.json')
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    # Create model
    model = ValorantNet()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training
    for epoch in range(10):
        total_loss = 0
        model.train()
        
        for images, targets in dataloader:
            images = images.to(device)
            
            # Convert targets to tensors
            map_target = torch.tensor([t['map'] for t in targets], dtype=torch.float).to(device)
            situation_target = torch.tensor([t['tactical_situation'] for t in targets], dtype=torch.float).to(device)
            formation_target = torch.tensor([t['formation'] for t in targets], dtype=torch.float).to(device)
            position_target = torch.tensor([t['position_type'] for t in targets], dtype=torch.float).to(device)
            
            # Performance targets
            perf_target = torch.stack([
                torch.tensor([t['performance_metrics']['entry_rating'] for t in targets], dtype=torch.float) / 5.0,
                torch.tensor([t['performance_metrics']['timing_gap'] for t in targets], dtype=torch.float) / 5.0,
                torch.tensor([t['performance_metrics']['formation_score'] for t in targets], dtype=torch.float),
                torch.tensor([t['performance_metrics']['planting_score'] for t in targets], dtype=torch.float),
                torch.tensor([t['performance_metrics']['rotation_score'] for t in targets], dtype=torch.float),
                torch.tensor([t['performance_metrics']['win_rate'] for t in targets], dtype=torch.float)
            ], dim=1).to(device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(images)
            
            # Calculate loss
            loss = 0
            loss += criterion(outputs['map'], map_target)
            loss += criterion(outputs['tactical_situation'], situation_target)
            loss += criterion(outputs['formation'], formation_target)
            loss += criterion(outputs['position_type'], position_target)
            loss += criterion(outputs['performance'], perf_target)
            
            # Backward
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}: Loss = {avg_loss:.4f}")
    
    # Save model
    torch.save(model.state_dict(), 'trained_valorant_model.pth')
    print("Model saved as 'trained_valorant_model.pth'")

if __name__ == "__main__":
    train_model()
'''
    
    # Save code
    model_file = Path("valorant_dataset") / "train_model.py"
    with open(model_file, 'w') as f:
        f.write(code)
    
    print(f"Created training script: {model_file}")
    return model_file

if __name__ == "__main__":
    print("=== AUTOMATIC VALORANT TRAINER ===")
    
    # Step 1: Create training data
    annotations = create_training_data()
    
    # Step 2: Create training script
    model_file = create_simple_nn_code()
    
    print(f"\\n=== READY TO TRAIN ===")
    print(f"Training data: {len(annotations)} samples")
    print(f"Training script: {model_file}")
    print(f"\\nRun this command to train:")
    print(f"python {model_file}")
    print(f"\\nThis will create 'trained_valorant_model.pth'")
    print(f"\\nAfter training, integrate into AURORA backend!")
