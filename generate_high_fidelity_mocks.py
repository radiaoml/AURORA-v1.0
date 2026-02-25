import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def generate_pro_viz(map_name, heatmap_path, path_path, blueprint_path=None, spatial_data=None):
    # Set dark style
    plt.style.use('dark_background')
    
    import time
    seed = int(time.time() * 1000) % 2**32
    np.random.seed(seed)
    
    # Load Blueprint if available
    bg_img = None
    if blueprint_path and os.path.exists(blueprint_path):
        try:
            bg_img = plt.imread(blueprint_path)
        except Exception as e:
            print(f"[WARN] Failed to load blueprint: {e}")

    # --- 1. PRO HEATMAP (Projected over Blueprint) ---
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#0b0e14')
    ax.set_facecolor('#0b0e14')
    
    # Draw Blueprint as Background
    if bg_img is not None:
        ax.imshow(bg_img, extent=[0, 1000, 0, 1000], alpha=0.9, zorder=0)
    
    # Use REAL spatial data if available, otherwise fallback to mock
    if spatial_data and "kill_locations" in spatial_data and len(spatial_data["kill_locations"]) > 0:
        print(f"[VIZ] Using REAL kill location data: {len(spatial_data['kill_locations'])} kills detected")
        kill_coords = spatial_data["kill_locations"]
        x = [k["x"] for k in kill_coords]
        y = [k["y"] for k in kill_coords]
        
        # Add player positions to the heatmap for more density
        if "player_positions" in spatial_data and len(spatial_data["player_positions"]) > 0:
            print(f"[VIZ] Adding {len(spatial_data['player_positions'])} player positions to heatmap")
            player_coords = spatial_data["player_positions"]
            x.extend([p["x"] for p in player_coords])
            y.extend([p["y"] for p in player_coords])
    else:
        print(f"[VIZ] No real spatial data available, using mock data")
        # Fallback to mock data
        x = np.concatenate([np.random.normal(loc, 80, 100) for loc in [300, 500, 700]])
        y = np.concatenate([np.random.normal(loc, 120, 100) for loc in [400, 700, 200]])
    
    sns.kdeplot(
        x=x, y=y, 
        fill=True, thresh=0.1, levels=15, 
        cmap='rocket', alpha=0.5 if bg_img is not None else 1.0, 
        ax=ax, cbar=False, zorder=1
    )
    
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_axis_off()
    
    plt.text(20, 970, f"NEURAL_PROJECTION // {map_name}", color='#00f5d4', fontsize=12, family='monospace', weight='bold', zorder=5)
    plt.text(20, 940, "STATUS: BLUEPRINT_OVERLAY_ACTIVE", color='#94a3b8', fontsize=8, family='monospace', zorder=5)
    
    plt.tight_layout(pad=0)
    plt.savefig(heatmap_path, dpi=120, facecolor='#0b0e14')
    plt.close()
    
    # --- 2. PRO TRAJECTORIES (Projected over Blueprint) ---
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#0b0e14')
    ax.set_facecolor('#0b0e14')
    
    if bg_img is not None:
        ax.imshow(bg_img, extent=[0, 1000, 0, 1000], alpha=0.9, zorder=0)
    
    # Use REAL movement paths if available
    if spatial_data and "movement_paths" in spatial_data and len(spatial_data["movement_paths"]) > 0:
        print(f"[VIZ] Using REAL movement path data: {len(spatial_data['movement_paths'])} paths detected")
        paths = spatial_data["movement_paths"]
        
        for path in paths:
            start_x, start_y = path["start_x"], path["start_y"]
            end_x, end_y = path["end_x"], path["end_y"]
            path_type = path.get("type", "unknown")
            
            # Color based on path type
            if path_type == "entry":
                color = '#ff4655'  # Red for aggressive entry
            elif path_type == "rotation":
                color = '#ffa500'  # Orange for rotations
            elif path_type == "flank":
                color = '#9d4edd'  # Purple for flanks
            else:
                color = '#00f5d4'  # Cyan for other movements
            
            ax.plot([start_x, end_x], [start_y, end_y], color=color, alpha=0.7, linewidth=2, zorder=1)
            ax.scatter([start_x], [start_y], color=color, s=8, alpha=0.9, zorder=2)
    else:
        print(f"[VIZ] No real movement path data, using mock trajectories")
        # Fallback to mock pathing webs
        for _ in range(40):
            start_x, start_y = np.random.randint(200, 800), np.random.randint(200, 800)
            end_x, end_y = start_x + np.random.normal(0, 150), start_y + np.random.normal(0, 150)
            
            color = '#ff4655' if np.random.rand() > 0.5 else '#00f5d4'
            ax.plot([start_x, end_x], [start_y, end_y], color=color, alpha=0.6, linewidth=1.5, zorder=1)
            
            if np.random.rand() > 0.7:
                ax.scatter([start_x], [start_y], color=color, s=4, alpha=0.8, zorder=2)

    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_axis_off()
    
    plt.text(20, 970, f"PATHING_PROJECTION // {map_name}", color='#ff4655', fontsize=12, family='monospace', weight='bold', zorder=5)
    plt.text(20, 940, "COORD_SYNC: CALIBRATED", color='#94a3b8', fontsize=8, family='monospace', zorder=5)
    
    plt.tight_layout(pad=0)
    plt.savefig(path_path, dpi=120, facecolor='#0b0e14')
    plt.close()
    
    print(f"[SUCCESS] Generated Project Viz for {map_name} at {heatmap_path}")

if __name__ == "__main__":
    # Test paths
    BLUEPRINT_DIR = "blueprints/official"
    ascent_bp = os.path.join(BLUEPRINT_DIR, "ascent_minimap.png")
    
    generate_pro_viz("ASCENT", "ascent_heatmap_pro.png", "ascent_pathing_pro.png", blueprint_path=ascent_bp)
    generate_pro_viz("BIND", "bind_heatmap_pro.png", "bind_pathing_pro.png", blueprint_path=os.path.join(BLUEPRINT_DIR, "bind_minimap.png"))
    generate_pro_viz("HAVEN", "haven_heatmap_pro.png", "haven_pathing_pro.png", blueprint_path=os.path.join(BLUEPRINT_DIR, "haven_minimap.png"))
