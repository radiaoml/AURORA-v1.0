import requests
import os
import json

def download_assets():
    url = "https://valorant-api.com/v1/maps"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch map data: {response.status_code}")
        return

    data = response.json()
    os.makedirs("blueprints/official", exist_ok=True)
    
    # We want to map the display names to their icons
    # Some maps are "The Range" or "Skirmish", we'll filter for the 12 competitive ones
    target_maps = ["Ascent", "Bind", "Haven", "Split", "Icebox", "Breeze", "Fracture", "Pearl", "Lotus", "Sunset", "Abyss", "District"]
    
    for map_info in data['data']:
        name = map_info['displayName']
        if name in target_maps:
            icon_url = map_info.get('displayIcon')
            if not icon_url:
                # Some maps might not have displayIcon (like District sometimes in API)
                # Fallback to listViewIcon or just skip
                icon_url = map_info.get('listViewIcon')
                
            if icon_url:
                save_path = f"blueprints/official/{name.lower()}_minimap.png"
                print(f"[DOWNLOADING] {name} from {icon_url}...")
                img_data = requests.get(icon_url).content
                with open(save_path, 'wb') as f:
                    f.write(img_data)
                print(f"[SAVED] {save_path}")
            else:
                print(f"[WARN] No icon found for {name}")

    print("[SUCCESS] Official asset migration complete.")

if __name__ == "__main__":
    download_assets()
