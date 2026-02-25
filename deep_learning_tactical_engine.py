import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import numpy as np
import cv2
import os
import json
from typing import Dict, List, Tuple, Optional
import albumentations as A
from albumentations.pytorch import ToTensorV2

class ValorantTacticalDataset(Dataset):
    """Dataset for Valorant tactical analysis"""
    
    def __init__(self, data_dir: str, split: str = "train", transform=None):
        self.data_dir = data_dir
        self.split = split
        self.transform = transform
        
        # Load annotations
        annotations_file = os.path.join(data_dir, f"{split}_annotations.json")
        with open(annotations_file, 'r') as f:
            self.annotations = json.load(f)
        
        # Tactical categories
        self.tactical_labels = {
            'map': ['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX', 'BREEZE', 'FRACTURE', 'PEARL', 'LOTUS', 'SUNSET'],
            'agent': ['JETT', 'REYNA', 'RAZE', 'PHOENIX', 'NEON', 'YORU', 'OMEGA', 'SAGE', 'SKYE', 'KILLJOY', 'CYPER', 'CHAMBER', 'SOVA', 'BREACH', 'KAYO', 'FADE', 'VIPER', 'ASTRA', 'HARBOR', 'BRIMSTONE', 'OMEN', 'CLOUDE'],
            'tactical_situation': ['entry', 'post_plant', 'retake', 'eco', 'buy_round', 'force_buy', 'mid_control', 'flank'],
            'formation': ['tight', 'balanced', 'spread', 'scattered'],
            'position_type': ['aggressive', 'defensive', 'support', 'roaming', 'anchoring']
        }
        
        # Multi-label encoding
        self.label_encoders = self._create_label_encoders()
        
    def _create_label_encoders(self):
        """Create label encoders for multi-label classification"""
        encoders = {}
        for category, labels in self.tactical_labels.items():
            encoders[category] = {label: idx for idx, label in enumerate(labels)}
        return encoders
    
    def __len__(self):
        return len(self.annotations)
    
    def __getitem__(self, idx):
        annotation = self.annotations[idx]
        
        # Load image
        img_path = os.path.join(self.data_dir, annotation['image_path'])
        image = Image.open(img_path).convert('RGB')
        
        # Apply transforms
        if self.transform:
            image = self.transform(image=np.array(image))['image']
        
        # Multi-label targets
        targets = {}
        for category in self.tactical_labels:
            label = annotation.get(category, self.tactical_labels[category][0])
            targets[category] = self.label_encoders[category][label]
        
        return image, targets

class ValorantTacticalModel(nn.Module):
    """Multi-task EfficientNet model for Valorant tactical analysis"""
    
    def __init__(self, model_name: str = 'efficientnet_b0', num_classes: Dict = None):
        super(ValorantTacticalModel, self).__init__()
        
        # Load pretrained EfficientNet
        if model_name.startswith('efficientnet'):
            self.backbone = models.efficientnet_b0(pretrained=True)
            feature_dim = self.backbone.classifier[1].in_features
            # Remove classification head
            self.backbone.classifier = nn.Identity()
        elif model_name.startswith('resnet'):
            if model_name == 'resnet50':
                self.backbone = models.resnet50(pretrained=True)
            elif model_name == 'resnet101':
                self.backbone = models.resnet101(pretrained=True)
            feature_dim = self.backbone.fc.in_features
            # Remove classification head
            self.backbone.fc = nn.Identity()
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        
        # Multi-task heads
        self.task_heads = nn.ModuleDict({
            'map': nn.Sequential(
                nn.Linear(feature_dim, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, 10)  # 10 maps
            ),
            'agent': nn.Sequential(
                nn.Linear(feature_dim, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, 22)  # 22 agents
            ),
            'tactical_situation': nn.Sequential(
                nn.Linear(feature_dim, 256),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(256, 8)  # 8 tactical situations
            ),
            'formation': nn.Sequential(
                nn.Linear(feature_dim, 128),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(128, 4)  # 4 formation types
            ),
            'position_type': nn.Sequential(
                nn.Linear(feature_dim, 128),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(128, 5)  # 5 position types
            )
        })
        
        # Performance prediction head (regression)
        self.performance_head = nn.Sequential(
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 6)  # [entry_rating, timing_gap, formation_score, planting_score, rotation_score, win_rate]
        )
        
    def forward(self, x):
        features = self.backbone(x)
        
        # Classification outputs
        outputs = {}
        for task, head in self.task_heads.items():
            outputs[task] = head(features)
        
        # Regression outputs
        performance = self.performance_head(features)
        outputs['performance'] = performance
        
        return outputs

class ValorantTrainer:
    """Training pipeline for Valorant tactical model"""
    
    def __init__(self, model: ValorantTacticalModel, device: str = None):
        # Auto-detect device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        print(f"Using device: {self.device}")
        self.model = model.to(self.device)
        
        # Loss functions
        self.classification_criterion = nn.CrossEntropyLoss()
        self.regression_criterion = nn.MSELoss()
        
        # Optimizer
        self.optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=50)
        
        # Task weights (can be adjusted)
        self.task_weights = {
            'map': 1.0,
            'agent': 1.0,
            'tactical_situation': 1.5,
            'formation': 0.8,
            'position_type': 0.8,
            'performance': 1.2
        }
        
    def train_epoch(self, dataloader: DataLoader) -> Dict:
        self.model.train()
        epoch_loss = 0
        task_losses = {task: 0 for task in self.task_weights.keys()}
        task_losses['performance'] = 0
        
        for batch_idx, (images, targets) in enumerate(dataloader):
            images = images.to(self.device)
            
            # Move targets to device
            targets = {k: v.to(self.device) for k, v in targets.items()}
            
            # Forward pass
            outputs = self.model(images)
            
            # Calculate losses
            total_loss = 0
            
            # Classification losses
            for task in ['map', 'agent', 'tactical_situation', 'formation', 'position_type']:
                if task in outputs and task in targets:
                    loss = self.classification_criterion(outputs[task], targets[task])
                    total_loss += self.task_weights[task] * loss
                    task_losses[task] += loss.item()
            
            # Regression loss
            if 'performance' in outputs:
                # Normalize performance targets
                perf_targets = torch.stack([
                    targets.get('entry_rating', torch.zeros_like(targets['map'])),
                    targets.get('timing_gap', torch.zeros_like(targets['map'])),
                    targets.get('formation_score', torch.zeros_like(targets['map'])),
                    targets.get('planting_score', torch.zeros_like(targets['map'])),
                    targets.get('rotation_score', torch.zeros_like(targets['map'])),
                    targets.get('win_rate', torch.zeros_like(targets['map']))
                ], dim=1).float()
                
                loss = self.regression_criterion(outputs['performance'], perf_targets)
                total_loss += self.task_weights['performance'] * loss
                task_losses['performance'] += loss.item()
            
            # Backward pass
            self.optimizer.zero_grad()
            total_loss.backward()
            self.optimizer.step()
            
            epoch_loss += total_loss.item()
        
        # Calculate average losses
        num_batches = len(dataloader)
        avg_loss = epoch_loss / num_batches
        avg_task_losses = {task: loss / num_batches for task, loss in task_losses.items()}
        
        return {'total_loss': avg_loss, **avg_task_losses}
    
    def validate(self, dataloader: DataLoader) -> Dict:
        self.model.eval()
        val_loss = 0
        task_losses = {task: 0 for task in self.task_weights.keys()}
        task_losses['performance'] = 0
        
        with torch.no_grad():
            for images, targets in dataloader:
                images = images.to(self.device)
                targets = {k: v.to(self.device) for k, v in targets.items()}
                
                outputs = self.model(images)
                
                # Calculate losses (same as training)
                total_loss = 0
                
                for task in ['map', 'agent', 'tactical_situation', 'formation', 'position_type']:
                    if task in outputs and task in targets:
                        loss = self.classification_criterion(outputs[task], targets[task])
                        total_loss += self.task_weights[task] * loss
                        task_losses[task] += loss.item()
                
                if 'performance' in outputs:
                    perf_targets = torch.stack([
                        targets.get('entry_rating', torch.zeros_like(targets['map'])),
                        targets.get('timing_gap', torch.zeros_like(targets['map'])),
                        targets.get('formation_score', torch.zeros_like(targets['map'])),
                        targets.get('planting_score', torch.zeros_like(targets['map'])),
                        targets.get('rotation_score', torch.zeros_like(targets['map'])),
                        targets.get('win_rate', torch.zeros_like(targets['map']))
                    ], dim=1).float()
                    
                    loss = self.regression_criterion(outputs['performance'], perf_targets)
                    total_loss += self.task_weights['performance'] * loss
                    task_losses['performance'] += loss.item()
                
                val_loss += total_loss.item()
        
        num_batches = len(dataloader)
        avg_loss = val_loss / num_batches
        avg_task_losses = {task: loss / num_batches for task, loss in task_losses.items()}
        
        return {'total_loss': avg_loss, **avg_task_losses}
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, epochs: int = 50):
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            # Training
            train_metrics = self.train_epoch(train_loader)
            
            # Validation
            val_metrics = self.validate(val_loader)
            
            # Learning rate step
            self.scheduler.step()
            
            # Print metrics
            print(f"Epoch {epoch+1}/{epochs}")
            print(f"Train Loss: {train_metrics['total_loss']:.4f}")
            print(f"Val Loss: {val_metrics['total_loss']:.4f}")
            
            # Save best model
            if val_metrics['total_loss'] < best_val_loss:
                best_val_loss = val_metrics['total_loss']
                torch.save(self.model.state_dict(), 'best_valorant_model.pth')
                print("Saved best model!")
            
            print("-" * 50)

def create_data_transforms(image_size: int = 224):
    """Create data augmentation transforms"""
    train_transform = A.Compose([
        A.Resize(image_size, image_size),
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.3),
        A.GaussNoise(p=0.2),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])
    
    val_transform = A.Compose([
        A.Resize(image_size, image_size),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])
    
    return train_transform, val_transform

def create_sample_annotations():
    """Create sample annotations for testing"""
    sample_data = []
    
    # Sample annotations for demonstration
    for i in range(100):
        sample_data.append({
            'image_path': f'frames/frame_{i}.jpg',
            'map': np.random.choice(['ASCENT', 'BIND', 'HAVEN', 'SPLIT', 'ICEBOX']),
            'agent': np.random.choice(['JETT', 'REYNA', 'SOVA', 'OMEN', 'SAGE']),
            'tactical_situation': np.random.choice(['entry', 'post_plant', 'retake', 'mid_control']),
            'formation': np.random.choice(['tight', 'balanced', 'spread']),
            'position_type': np.random.choice(['aggressive', 'defensive', 'support']),
            'entry_rating': np.random.randint(1, 6),
            'timing_gap': np.random.uniform(0.5, 3.0),
            'formation_score': np.random.uniform(0.5, 1.0),
            'planting_score': np.random.uniform(0.5, 1.0),
            'rotation_score': np.random.uniform(0.5, 1.0),
            'win_rate': np.random.uniform(0.3, 0.9)
        })
    
    return sample_data

if __name__ == "__main__":
    # Configuration
    config = {
        'model_name': 'efficientnet_b0',  # or 'resnet50', 'resnet101'
        'image_size': 224,
        'batch_size': 32,
        'epochs': 50,
        'data_dir': 'valorant_dataset'
    }
    
    # Create transforms
    train_transform, val_transform = create_data_transforms(config['image_size'])
    
    # Create datasets (you'll need to create the actual dataset)
    # train_dataset = ValorantTacticalDataset(config['data_dir'], 'train', train_transform)
    # val_dataset = ValorantTacticalDataset(config['data_dir'], 'val', val_transform)
    
    # Create dataloaders
    # train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=True)
    # val_loader = DataLoader(val_dataset, batch_size=config['batch_size'], shuffle=False)
    
    # Create model
    model = ValorantTacticalModel(config['model_name'])
    
    # Create trainer
    trainer = ValorantTrainer(model)
    
    print(f"Created {config['model_name']} model for Valorant tactical analysis")
    print("Model parameters:", sum(p.numel() for p in model.parameters()))
    print("Trainable parameters:", sum(p.numel() for p in model.parameters() if p.requires_grad))
    
    # Train (uncomment when you have data)
    # trainer.train(train_loader, val_loader, config['epochs'])
