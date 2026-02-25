import torch
import torch.nn as nn
from deep_learning_tactical_engine import ValorantTacticalModel

def simple_model_test():
    """Simple test of the model architecture"""
    print("🚀 Simple Valorant Model Test")
    print("=" * 40)
    
    # Create model
    model = ValorantTacticalModel('efficientnet_b0')
    print(f"✅ Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Test forward pass with random input
    print("\n🧪 Testing forward pass...")
    model.eval()
    
    # Create sample input (batch of 2 images)
    sample_input = torch.randn(2, 3, 224, 224)
    
    with torch.no_grad():
        outputs = model(sample_input)
    
    print("Model outputs:")
    for key, tensor in outputs.items():
        print(f"  {key}: {tensor.shape}")
    
    print("✅ Forward pass successful!")
    
    # Test individual outputs
    print("\n📊 Testing individual predictions...")
    
    # Map prediction (10 maps)
    map_probs = torch.softmax(outputs['map'], dim=1)
    predicted_map = torch.argmax(map_probs, dim=1)
    print(f"Predicted maps: {predicted_map.tolist()}")
    
    # Agent prediction (22 agents)
    agent_probs = torch.softmax(outputs['agent'], dim=1)
    predicted_agents = torch.argmax(agent_probs, dim=1)
    print(f"Predicted agents: {predicted_agents.tolist()}")
    
    # Performance metrics
    performance = outputs['performance']
    print(f"Performance predictions: {performance.shape}")
    print(f"Entry rating (normalized): {performance[0, 0].item():.3f}")
    print(f"Timing gap (normalized): {performance[0, 1].item():.3f}")
    print(f"Win rate (normalized): {performance[0, 5].item():.3f}")
    
    # Test a simple training step
    print("\n🏋️ Testing training step...")
    model.train()
    
    # Create dummy targets
    map_target = torch.tensor([3, 7])  # ASCENT, HAVEN
    agent_target = torch.tensor([0, 10])  # JETT, SOVA
    situation_target = torch.tensor([2, 1])  # post_plant, entry
    formation_target = torch.tensor([1, 2])  # balanced, spread
    position_target = torch.tensor([0, 3])  # aggressive, roaming
    
    # Performance targets (normalized)
    perf_target = torch.tensor([
        [0.8, 0.3, 0.7, 0.6, 0.8, 0.75],  # Sample 1
        [0.6, 0.5, 0.8, 0.7, 0.6, 0.65]   # Sample 2
    ])
    
    # Calculate losses
    map_loss = nn.CrossEntropyLoss()(outputs['map'], map_target)
    agent_loss = nn.CrossEntropyLoss()(outputs['agent'], agent_target)
    situation_loss = nn.CrossEntropyLoss()(outputs['tactical_situation'], situation_target)
    formation_loss = nn.CrossEntropyLoss()(outputs['formation'], formation_target)
    position_loss = nn.CrossEntropyLoss()(outputs['position_type'], position_target)
    perf_loss = nn.MSELoss()(outputs['performance'], perf_target)
    
    total_loss = map_loss + agent_loss + situation_loss + formation_loss + position_loss + perf_loss
    
    print(f"Losses:")
    print(f"  Map: {map_loss.item():.4f}")
    print(f"  Agent: {agent_loss.item():.4f}")
    print(f"  Situation: {situation_loss.item():.4f}")
    print(f"  Formation: {formation_loss.item():.4f}")
    print(f"  Position: {position_loss.item():.4f}")
    print(f"  Performance: {perf_loss.item():.4f}")
    print(f"  Total: {total_loss.item():.4f}")
    
    # Backward pass
    total_loss.backward()
    print("✅ Backward pass successful!")
    
    # Save model
    torch.save(model.state_dict(), 'simple_test_model.pth')
    print("💾 Model saved as 'simple_test_model.pth'")
    
    print("\n🎉 Model test complete!")
    print("\nModel capabilities:")
    print("✅ Multi-task learning (6 outputs)")
    print("✅ Classification (maps, agents, situations)")
    print("✅ Regression (performance metrics)")
    print("✅ EfficientNet backbone (6.3M parameters)")
    print("✅ Ready for training with real data")
    
    print("\nNext steps:")
    print("1. Collect real Valorant gameplay footage")
    print("2. Extract frames and annotate tactical data")
    print("3. Train on real dataset for better accuracy")
    print("4. Integrate into AURORA backend")

if __name__ == "__main__":
    simple_model_test()
