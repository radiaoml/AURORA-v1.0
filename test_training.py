import torch
import json
from deep_learning_tactical_engine import ValorantTacticalModel, ValorantTrainer, ValorantTacticalDataset, create_data_transforms
from torch.utils.data import DataLoader
import numpy as np

def create_mock_dataset(num_samples=100):
    """Create a simple mock dataset for testing"""
    # Create mock image data (random images)
    mock_images = torch.randn(num_samples, 3, 224, 224)
    
    # Create mock labels
    mock_labels = []
    for i in range(num_samples):
        labels = {
            'map': torch.randint(0, 10, (1,)).item(),  # 10 maps
            'agent': torch.randint(0, 22, (1,)).item(),  # 22 agents
            'tactical_situation': torch.randint(0, 8, (1,)).item(),  # 8 situations
            'formation': torch.randint(0, 4, (1,)).item(),  # 4 formations
            'position_type': torch.randint(0, 5, (1,)).item(),  # 5 position types
            'entry_rating': torch.randint(1, 6, (1,)).item(),
            'timing_gap': torch.rand(1).item() * 3.0,
            'formation_score': torch.rand(1).item(),
            'planting_score': torch.rand(1).item(),
            'rotation_score': torch.rand(1).item(),
            'win_rate': torch.rand(1).item() * 0.6 + 0.3  # 0.3-0.9
        }
        mock_labels.append(labels)
    
    return list(zip(mock_images, mock_labels))

def test_model_training():
    """Test the model with mock data"""
    print("🚀 Testing Valorant Tactical Model Training")
    print("=" * 50)
    
    # Configuration
    config = {
        'model_name': 'efficientnet_b0',
        'batch_size': 16,
        'epochs': 3,  # Quick test
        'learning_rate': 1e-4
    }
    
    print(f"Model: {config['model_name']}")
    print(f"Batch size: {config['batch_size']}")
    print(f"Epochs: {config['epochs']}")
    print()
    
    # Create model
    model = ValorantTacticalModel(config['model_name'])
    print(f"✅ Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Create trainer
    trainer = ValorantTrainer(model)
    print("✅ Trainer initialized")
    
    # Create mock dataset
    print("📊 Creating mock dataset...")
    train_data = create_mock_dataset(80)
    val_data = create_mock_dataset(20)
    
    # Create simple dataset class
    class SimpleDataset(torch.utils.data.Dataset):
        def __init__(self, data):
            self.data = data
        
        def __len__(self):
            return len(self.data)
        
        def __getitem__(self, idx):
            image, labels = self.data[idx]
            return image, labels
    
    # Create dataloaders
    train_dataset = SimpleDataset(train_data)
    val_dataset = SimpleDataset(val_data)
    
    train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config['batch_size'], shuffle=False)
    
    print(f"✅ Dataset created: {len(train_dataset)} train, {len(val_dataset)} val samples")
    
    # Test forward pass
    print("\n🧪 Testing forward pass...")
    model.eval()
    with torch.no_grad():
        sample_image = torch.randn(1, 3, 224, 224)
        outputs = model(sample_image)
        
        print("Model outputs:")
        for key, tensor in outputs.items():
            print(f"  {key}: {tensor.shape}")
    
    print("✅ Forward pass successful")
    
    # Test training step
    print("\n🏋️ Testing training step...")
    model.train()
    
    # Get a batch
    images, labels = next(iter(train_loader))
    
    # Forward pass
    outputs = model(images)
    
    # Calculate losses
    total_loss = 0
    task_losses = {}
    
    # Classification losses
    for task in ['map', 'agent', 'tactical_situation', 'formation', 'position_type']:
        if task in outputs:
            target = torch.tensor([l[task] for l in labels])
            loss = torch.nn.CrossEntropyLoss()(outputs[task], target)
            total_loss += loss
            task_losses[task] = loss.item()
    
    # Regression loss
    if 'performance' in outputs:
        perf_targets = torch.stack([
            torch.stack([l['entry_rating'] for l in labels]).float() / 5.0,  # Normalize
            torch.stack([l['timing_gap'] for l in labels]).float() / 3.0,  # Normalize
            torch.stack([l['formation_score'] for l in labels]),
            torch.stack([l['planting_score'] for l in labels]),
            torch.stack([l['rotation_score'] for l in labels]),
            torch.stack([l['win_rate'] for l in labels])
        ], dim=1)
        
        loss = torch.nn.MSELoss()(outputs['performance'], perf_targets)
        total_loss += loss
        task_losses['performance'] = loss.item()
    
    print(f"Total loss: {total_loss.item():.4f}")
    for task, loss in task_losses.items():
        print(f"  {task}: {loss:.4f}")
    
    print("✅ Training step successful")
    
    # Quick training loop
    print(f"\n🎯 Running {config['epochs']} epochs of training...")
    
    for epoch in range(config['epochs']):
        # Training
        model.train()
        epoch_loss = 0
        num_batches = 0
        
        for batch_images, batch_labels in train_loader:
            # Forward pass
            outputs = model(batch_images)
            
            # Calculate loss
            total_loss = 0
            
            # Classification losses
            for task in ['map', 'agent', 'tactical_situation', 'formation', 'position_type']:
                if task in outputs:
                    target = torch.tensor([l[task] for l in batch_labels])
                    loss = torch.nn.CrossEntropyLoss()(outputs[task], target)
                    total_loss += loss
            
            # Regression loss
            if 'performance' in outputs:
                perf_targets = torch.stack([
                    torch.stack([l['entry_rating'] for l in batch_labels]).float() / 5.0,
                    torch.stack([l['timing_gap'] for l in batch_labels]).float() / 3.0,
                    torch.stack([l['formation_score'] for l in batch_labels]),
                    torch.stack([l['planting_score'] for l in batch_labels]),
                    torch.stack([l['rotation_score'] for l in batch_labels]),
                    torch.stack([l['win_rate'] for l in batch_labels])
                ], dim=1)
                
                loss = torch.nn.MSELoss()(outputs['performance'], perf_targets)
                total_loss += loss
            
            # Backward pass
            trainer.optimizer.zero_grad()
            total_loss.backward()
            trainer.optimizer.step()
            
            epoch_loss += total_loss.item()
            num_batches += 1
        
        avg_loss = epoch_loss / num_batches
        print(f"Epoch {epoch+1}/{config['epochs']}: Loss = {avg_loss:.4f}")
    
    print("✅ Training complete!")
    
    # Test inference
    print("\n🔍 Testing inference...")
    model.eval()
    with torch.no_grad():
        test_image = torch.randn(1, 3, 224, 224)
        outputs = model(test_image)
        
        # Convert outputs to predictions
        predictions = {}
        
        # Classification predictions
        for task in ['map', 'agent', 'tactical_situation', 'formation', 'position_type']:
            if task in outputs:
                pred_idx = torch.argmax(outputs[task], dim=1).item()
                predictions[task] = pred_idx
        
        # Regression predictions
        if 'performance' in outputs:
            perf = outputs['performance'][0]
            predictions['entry_rating'] = int(perf[0].item() * 5)
            predictions['timing_gap'] = perf[1].item() * 3.0
            predictions['formation_score'] = perf[2].item()
            predictions['planting_score'] = perf[3].item()
            predictions['rotation_score'] = perf[4].item()
            predictions['win_rate'] = perf[5].item()
        
        print("Sample predictions:")
        for key, value in predictions.items():
            print(f"  {key}: {value}")
    
    print("✅ Inference successful!")
    
    # Save model
    torch.save(model.state_dict(), 'test_valorant_model.pth')
    print("💾 Model saved as 'test_valorant_model.pth'")
    
    print("\n🎉 Training environment setup complete!")
    print("\nNext steps:")
    print("1. Add real Valorant VODs to extract frames")
    print("2. Annotate the frames with tactical data")
    print("3. Train on real data for better performance")
    print("4. Integrate trained model into AURORA backend")

if __name__ == "__main__":
    test_model_training()
