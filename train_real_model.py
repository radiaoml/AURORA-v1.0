import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import numpy as np
import json
import os
from pathlib import Path
from deep_learning_tactical_engine import ValorantTacticalModel

class RealValorantDataset(Dataset):
    """Dataset for real Valorant annotations"""
    
    def __init__(self, annotations_file, transform=None):
        self.transform = transform
        
        # Load annotations
        with open(annotations_file, 'r') as f:
            self.annotations = json.load(f)
        
        # Label encoders
        self.maps = ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET']
        self.situations = ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank']
        self.formations = ['tight', 'balanced', 'spread', 'scattered']
        self.positions = ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
        
        # Create encoders
        self.map_encoder = {label: idx for idx, label in enumerate(self.maps)}
        self.situation_encoder = {label: idx for idx, label in enumerate(self.situations)}
        self.formation_encoder = {label: idx for idx, label in enumerate(self.formations)}
        self.position_encoder = {label: idx for idx, label in enumerate(self.positions)}
        
        print(f"Loaded {len(self.annotations)} annotations from {annotations_file}")
    
    def __len__(self):
        return len(self.annotations)
    
    def __getitem__(self, idx):
        annotation = self.annotations[idx]
        
        # Load image
        img_path = annotation['image_path']
        if not os.path.exists(img_path):
            # Create a dummy image if file doesn't exist
            image = Image.new('RGB', (224, 224), color='black')
        else:
            image = Image.open(img_path).convert('RGB')
        
        # Apply transforms
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

def train_real_model():
    """Train model on real Valorant data"""
    print("🚀 Training Valorant Model on Real Data")
    print("=" * 50)
    
    # Check for real annotations
    annotations_file = "valorant_dataset/annotations/real_annotations.json"
    if not os.path.exists(annotations_file):
        print(f"❌ No real annotations found at {annotations_file}")
        print("Please run the annotation tool first:")
        print("python console_annotator.py")
        return
    
    # Configuration
    config = {
        'model_name': 'efficientnet_b0',
        'batch_size': 8,  # Smaller batch for real data
        'epochs': 20,     # More epochs for real data
        'learning_rate': 1e-4
    }
    
    print(f"Configuration:")
    print(f"  Model: {config['model_name']}")
    print(f"  Batch size: {config['batch_size']}")
    print(f"  Epochs: {config['epochs']}")
    print(f"  Learning rate: {config['learning_rate']}")
    
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
    print(f"\n📊 Creating datasets...")
    
    train_file = "valorant_dataset/splits/train_annotations.json"
    val_file = "valorant_dataset/splits/val_annotations.json"
    
    if not os.path.exists(train_file):
        print(f"❌ No train split found. Please annotate more data.")
        return
    
    train_dataset = RealValorantDataset(train_file, train_transform)
    val_dataset = RealValorantDataset(val_file, val_transform) if os.path.exists(val_file) else None
    
    print(f"✅ Train dataset: {len(train_dataset)} samples")
    if val_dataset:
        print(f"✅ Validation dataset: {len(val_dataset)} samples")
    else:
        print(f"⚠️ No validation dataset found")
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config['batch_size'], shuffle=False) if val_dataset else None
    
    # Create model
    print(f"\n🧠 Creating model...")
    model = ValorantTacticalModel(config['model_name'])
    
    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    print(f"Using device: {device}")
    
    # Optimizer and loss
    optimizer = optim.AdamW(model.parameters(), lr=config['learning_rate'], weight_decay=1e-4)
    
    # Loss functions
    classification_criterion = nn.CrossEntropyLoss()
    regression_criterion = nn.MSELoss()
    
    # Training loop
    print(f"\n🏋️ Starting training...")
    print("-" * 50)
    
    best_val_loss = float('inf')
    
    for epoch in range(config['epochs']):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (images, targets) in enumerate(train_loader):
            images = images.to(device)
            
            # Move targets to device
            map_targets = torch.tensor([t['map'] for t in targets]).to(device)
            situation_targets = torch.tensor([t['tactical_situation'] for t in targets]).to(device)
            formation_targets = torch.tensor([t['formation'] for t in targets]).to(device)
            position_targets = torch.tensor([t['position_type'] for t in targets]).to(device)
            
            # Performance targets
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
            
            # Classification losses
            map_loss = classification_criterion(outputs['map'], map_targets)
            situation_loss = classification_criterion(outputs['tactical_situation'], situation_targets)
            formation_loss = classification_criterion(outputs['formation'], formation_targets)
            position_loss = classification_criterion(outputs['position_type'], position_targets)
            
            loss += map_loss + situation_loss + formation_loss + position_loss
            
            # Regression loss
            perf_loss = regression_criterion(outputs['performance'], perf_targets)
            loss += perf_loss
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
            # Calculate accuracy
            _, map_pred = torch.max(outputs['map'], 1)
            train_correct += (map_pred == map_targets).sum().item()
            train_total += map_targets.size(0)
        
        # Validation
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        if val_loader:
            model.eval()
            with torch.no_grad():
                for images, targets in val_loader:
                    images = images.to(device)
                    
                    map_targets = torch.tensor([t['map'] for t in targets]).to(device)
                    situation_targets = torch.tensor([t['tactical_situation'] for t in targets]).to(device)
                    formation_targets = torch.tensor([t['formation'] for t in targets]).to(device)
                    position_targets = torch.tensor([t['position_type'] for t in targets]).to(device)
                    
                    perf_targets = torch.stack([
                        torch.tensor([t['performance_metrics']['entry_rating'] for t in targets]).float() / 5.0,
                        torch.tensor([t['performance_metrics']['timing_gap'] for t in targets]).float() / 5.0,
                        torch.tensor([t['performance_metrics']['formation_score'] for t in targets]).float(),
                        torch.tensor([t['performance_metrics']['planting_score'] for t in targets]).float(),
                        torch.tensor([t['performance_metrics']['rotation_score'] for t in targets]).float(),
                        torch.tensor([t['performance_metrics']['win_rate'] for t in targets]).float()
                    ], dim=1).to(device)
                    
                    outputs = model(images)
                    
                    # Calculate validation loss
                    loss = 0
                    loss += classification_criterion(outputs['map'], map_targets)
                    loss += classification_criterion(outputs['tactical_situation'], situation_targets)
                    loss += classification_criterion(outputs['formation'], formation_targets)
                    loss += classification_criterion(outputs['position_type'], position_targets)
                    loss += regression_criterion(outputs['performance'], perf_targets)
                    
                    val_loss += loss.item()
                    
                    # Calculate accuracy
                    _, map_pred = torch.max(outputs['map'], 1)
                    val_correct += (map_pred == map_targets).sum().item()
                    val_total += map_targets.size(0)
        
        # Print metrics
        train_acc = train_correct / train_total if train_total > 0 else 0
        val_acc = val_correct / val_total if val_total > 0 else 0
        
        print(f"Epoch {epoch+1:2d}/{config['epochs']}: "
              f"Train Loss: {train_loss/len(train_loader):.4f}, Acc: {train_acc:.3f} | "
              f"Val Loss: {val_loss/len(val_loader) if val_loader else 0:.4f}, Acc: {val_acc:.3f}")
        
        # Save best model
        if val_loader and val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), 'best_real_valorant_model.pth')
            print(f"  💾 Saved best model (val_loss: {val_loss/len(val_loader):.4f})")
    
    # Save final model
    torch.save(model.state_dict(), 'final_real_valorant_model.pth')
    print(f"\n✅ Training complete!")
    print(f"💾 Models saved:")
    print(f"  - best_real_valorant_model.pth (best validation)")
    print(f"  - final_real_valorant_model.pth (final epoch)")
    
    # Test the model
    print(f"\n🧪 Testing trained model...")
    model.eval()
    
    # Test with a sample
    if len(train_dataset) > 0:
        sample_image, sample_labels = train_dataset[0]
        sample_image = sample_image.unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(sample_image)
        
        # Convert predictions back to labels
        map_pred = torch.argmax(outputs['map'], dim=1).item()
        situation_pred = torch.argmax(outputs['tactical_situation'], dim=1).item()
        
        print(f"Sample predictions:")
        print(f"  Map: {train_dataset.maps[map_pred]} (actual: {train_dataset.maps[sample_labels['map']]})")
        print(f"  Situation: {train_dataset.situations[situation_pred]} (actual: {train_dataset.situations[sample_labels['tactical_situation']]})")
    
    print(f"\n🎉 Model ready for integration!")
    print(f"\nNext steps:")
    print(f"1. Test the model with new Valorant videos")
    print(f"2. Integrate into AURORA backend")
    print(f"3. Enjoy AI-powered tactical analysis!")

if __name__ == "__main__":
    train_real_model()
