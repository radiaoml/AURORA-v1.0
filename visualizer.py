import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_visualizations(data_path='gameplay_data.csv'):
    df = pd.read_csv(data_path)
    
    # Set style
    plt.style.use('dark_background')
    
    # 1. Kill Heatmap
    fig, ax = plt.subplots(figsize=(8, 8))
    kills = df[df['event_type'] == 'Kill']
    
    sns.kdeplot(
        x=kills['x'], y=kills['y'], 
        fill=True, thresh=0.05, levels=15, 
        cmap='rocket', alpha=0.8, ax=ax
    )
    
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_axis_off() # HUD looks better without axes
    
    plt.tight_layout()
    plt.savefig('tactical_kill_heatmap.png', dpi=150, transparent=True)
    plt.close()
    print("Generated tactical_kill_heatmap.png")
    
    # 2. Player Trajectories (Round 1 Example)
    fig, ax = plt.subplots(figsize=(8, 8))
    round_1 = df[df['round_id'] == 1]
    
    for player in round_1['player_id'].unique():
        player_data = round_1[round_1['player_id'] == player]
        color = '#00f5d4' if player_data['team'].iloc[0] == 'ATK' else '#ff4655'
        ax.plot(player_data['x'], player_data['y'], alpha=0.6, color=color, linewidth=2)
        
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_axis_off()
    
    plt.tight_layout()
    plt.savefig('round_1_trajectories.png', dpi=150, transparent=True)
    plt.close()
    print("Generated round_1_trajectories.png")

if __name__ == "__main__":
    create_visualizations()
