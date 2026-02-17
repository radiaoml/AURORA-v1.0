import matplotlib.pyplot as plt
import os

def create_schematic(map_name, output_path, sites):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#0b0e14') # Deep obsidian
    ax.set_facecolor('#0b0e14')

    # Draw "Playable Area" (Gray Pathways)
    # Generic representation for current mock/schematic
    # In a real implementation, this would use polygons from game data
    path_color = '#d1d5db' # Light Gray
    
    # Base layout "Skeleton"
    rects = [
        (100, 450, 800, 100), # Main Horizontal (Mid)
        (450, 100, 100, 800), # Main Vertical (Mid)
        (650, 250, 150, 150), # A Site Area
        (200, 650, 150, 150), # B Site Area
    ]
    
    for r in rects:
        ax.add_patch(plt.Rectangle((r[0], r[1]), r[2], r[3], fill=True, color=path_color, alpha=0.9, zorder=1))

    # Draw sites with Red "Drop Pins"
    for site_name, (x, y) in sites.items():
        # Draw Pin Head (Red Circle)
        ax.scatter([x], [y+30], color='#ff4655', s=800, zorder=10)
        # Draw Pin Stem/Indicator
        ax.plot([x, x], [y, y+30], color='#ff4655', linewidth=4, zorder=9)
        # Site Letter
        plt.text(x, y+30, site_name, color='white', fontsize=20, ha='center', va='center', weight='bold', zorder=11)
        
        # Site Base shading
        ax.add_patch(plt.Circle((x, y), 50, color='#ff4655', alpha=0.3, zorder=2))

    # Draw Callout Labels (e.g., "MID", "LONG")
    callouts = [
        ("MID", (500, 500)),
        ("A MAIN", (700, 400)),
        ("B MAIN", (300, 600)),
    ]
    for label, (lx, ly) in callouts:
        plt.text(lx, ly, label, color='black', fontsize=8, family='monospace', weight='bold',
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3'), zorder=5)

    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_axis_off()
    
    plt.text(500, 960, f"OFFICIAL_TACTICAL_DATA // {map_name}", color='#64748b', fontsize=12, family='monospace', ha='center', weight='bold')
    plt.text(500, 40, "HUD_SYNC: STABLE", color='#334155', fontsize=8, family='monospace', ha='center')

    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=120, facecolor='#0b0e14')
    plt.close()
    print(f"[SUCCESS] Generated Stylized Blueprint for {map_name} at {output_path}")

if __name__ == "__main__":
    os.makedirs("blueprints", exist_ok=True)
    
    MAP_DATA = {
        "ASCENT": {"A": (700, 300), "B": (300, 700)},
        "BIND": {"A": (700, 300), "B": (300, 700)},
        "HAVEN": {"A": (800, 300), "B": (500, 500), "C": (200, 700)},
        "SPLIT": {"A": (750, 350), "B": (250, 650)},
        "ICEBOX": {"A": (300, 200), "B": (700, 800)},
        "BREEZE": {"A": (800, 400), "B": (200, 600)},
        "FRACTURE": {"A": (700, 200), "B": (700, 800)},
        "PEARL": {"A": (200, 300), "B": (800, 700)},
        "LOTUS": {"A": (850, 300), "B": (500, 400), "C": (150, 700)},
        "SUNSET": {"A": (750, 250), "B": (250, 750)},
        "ABYSS": {"A": (800, 200), "B": (200, 800)},
        "DISTRICT": {"MID": (500, 500)}
    }
    
    for map_name, sites in MAP_DATA.items():
        create_schematic(map_name, f"blueprints/{map_name.lower()}_blueprint.png", sites)
