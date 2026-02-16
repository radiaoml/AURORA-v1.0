import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def generate_pro_viz(map_name, prefix):
    # Set dark style
    plt.style.use('dark_background')
    
    # Generate random data points for the heatmap
    np.random.seed(42 if map_name == "ASCENT" else 1337)
    
    # --- 1. PRO HEATMAP (KDE Style) ---
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#0b0e14')
    ax.set_facecolor('#0b0e14')
    
    # Create clusters of data
    x = np.concatenate([np.random.normal(loc, 100, 100) for loc in [200, 500, 800]])
    y = np.concatenate([np.random.normal(loc, 150, 100) for loc in [300, 600, 200]])
    
    sns.kdeplot(
        x=x, y=y, 
        fill=True, thresh=0, levels=20, 
        cmap='rocket', alpha=1.0, ax=ax,
        cbar=False
    )
    
    # Add Grid
    ax.grid(color='#1e293b', linestyle='--', linewidth=0.5, alpha=0.3)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_axis_off()
    
    # Add tactical annotations
    plt.text(20, 950, f"NEURAL_HEATMAP // {map_name}", color='#00f5d4', fontsize=12, family='monospace', weight='bold')
    plt.text(20, 920, "SCAN_DENSITY: ALPHA_STABLE", color='#94a3b8', fontsize=8, family='monospace')
    
    plt.tight_layout()
    heatmap_path = f"{prefix}_heatmap_pro.png"
    plt.savefig(heatmap_path, dpi=120, facecolor='#0b0e14')
    plt.close()
    
    # --- 2. PRO TRAJECTORIES (Neural Web Style) ---
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#0b0e14')
    ax.set_facecolor('#0b0e14')
    
    # Generate dense lines
    for _ in range(40):
        # Start and end points
        start_x, start_y = np.random.randint(100, 900), np.random.randint(100, 900)
        end_x, end_y = start_x + np.random.normal(0, 200), start_y + np.random.normal(0, 200)
        
        # Color based on direction or random
        color = '#ff4655' if np.random.rand() > 0.5 else '#00f5d4'
        ax.plot([start_x, end_x], [start_y, end_y], color=color, alpha=0.4, linewidth=1)
        
        # Add some middle nodes
        if np.random.rand() > 0.7:
            ax.scatter([start_x], [start_y], color=color, s=2, alpha=0.6)

    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_axis_off()
    
    plt.text(20, 950, f"PATHING_SYNC // {map_name}", color='#ff4655', fontsize=12, family='monospace', weight='bold')
    plt.text(20, 920, "COORD_STREAM: RESOLVED", color='#94a3b8', fontsize=8, family='monospace')
    
    plt.tight_layout()
    path_path = f"{prefix}_pathing_pro.png"
    plt.savefig(path_path, dpi=120, facecolor='#0b0e14')
    plt.close()
    
    print(f"[SUCCESS] Generated Pro Viz for {map_name}")

if __name__ == "__main__":
    generate_pro_viz("ASCENT", "ascent")
    generate_pro_viz("BIND", "bind")
    generate_pro_viz("HAVEN", "haven")
