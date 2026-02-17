import matplotlib.pyplot as plt
import os

def create_schematic(map_name, output_path, sites):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    # Draw a stylized border
    ax.add_patch(plt.Rectangle((50, 50), 900, 900, fill=False, edgecolor='#334155', linewidth=2, linestyle='--'))
    
    # Draw "Structural" lines (Schematic look)
    ax.plot([100, 900], [500, 500], color='#1e293b', alpha=0.5, linewidth=1)
    ax.plot([500, 500], [100, 900], color='#1e293b', alpha=0.5, linewidth=1)
    
    # Draw site boxes
    for site_name, (x, y) in sites.items():
        # Large site indicator
        rect = plt.Rectangle((x-80, y-80), 160, 160, fill=True, color='#020617', alpha=0.8, edgecolor='#334155', zorder=1)
        ax.add_patch(rect)
        plt.text(x, y, site_name, color='#94a3b8', fontsize=40, ha='center', va='center', weight='bold', alpha=0.3, zorder=2)
    
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_axis_off()
    
    plt.text(500, 960, f"TACTICAL_SCHEMATIC // {map_name}", color='#64748b', fontsize=14, family='monospace', ha='center', weight='bold')
    plt.text(500, 40, "COORD_GRID: NORMALIZED_1000px", color='#334155', fontsize=8, family='monospace', ha='center')

    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=120, facecolor='#0f172a')
    plt.close()
    print(f"[SUCCESS] Created schematic for {map_name} at {output_path}")

if __name__ == "__main__":
    os.makedirs("blueprints", exist_ok=True)
    
    create_schematic("BIND", "blueprints/bind_blueprint.png", {
        "A": (700, 300),
        "B": (300, 700)
    })
    
    create_schematic("HAVEN", "blueprints/haven_blueprint.png", {
        "A": (800, 300),
        "B": (500, 500),
        "C": (200, 700)
    })
