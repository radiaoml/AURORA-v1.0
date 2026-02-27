import requests
import json
import os
from pathlib import Path

OUTPUT_DIR = Path("Map Agent/riot_official_data")
API_URL = "https://valorant-api.com/v1/maps"

# Image types to download per map
IMAGE_KEYS = {
    "displayIcon": "minimap.png",
    "listViewIcon": "listview.png",
    "listViewIconTall": "listview_tall.png",
    "splash": "splash.png",
    "stylizedBackgroundImage": "background.png",
}

def scrape():
    print("🛰️  AURORA // Riot Official Data Scraper")
    print("=" * 50)
    
    r = requests.get(API_URL, timeout=10)
    r.raise_for_status()
    maps = r.json()["data"]

    # Only standard playable maps (those with callouts and a displayIcon)
    playable = [m for m in maps if m.get("displayIcon") and m.get("callouts")]
    print(f"📦 Found {len(playable)} standard maps to scrape.\n")

    all_metadata = {}

    for m in playable:
        name = m["displayName"]
        safe_name = name.replace(" ", "_").lower()
        map_dir = OUTPUT_DIR / safe_name
        map_dir.mkdir(parents=True, exist_ok=True)

        print(f"🗺️  [{name}]")

        # Download each image type
        for key, filename in IMAGE_KEYS.items():
            url = m.get(key)
            if not url:
                continue
            dest = map_dir / filename
            if dest.exists():
                print(f"  ⏭️  Skipping (cached): {filename}")
                continue
            try:
                img = requests.get(url, timeout=10).content
                dest.write_bytes(img)
                print(f"  ✅ {filename} ({len(img)//1024}KB)")
            except Exception as e:
                print(f"  ❌ Failed {filename}: {e}")

        # Save callout metadata as JSON
        callouts = m.get("callouts", [])
        meta = {
            "uuid": m["uuid"],
            "name": name,
            "tacticalDescription": m.get("tacticalDescription"),
            "coordinates": m.get("coordinates"),
            "xMultiplier": m.get("xMultiplier"),
            "yMultiplier": m.get("yMultiplier"),
            "xScalarToAdd": m.get("xScalarToAdd"),
            "yScalarToAdd": m.get("yScalarToAdd"),
            "callouts": [
                {
                    "region": c["regionName"],
                    "super_region": c["superRegionName"],
                    "x": c["location"]["x"],
                    "y": c["location"]["y"],
                    "z": c["location"]["z"],
                }
                for c in callouts
            ],
            "images": {k: str((map_dir / v).relative_to(OUTPUT_DIR.parent)) for k, v in IMAGE_KEYS.items() if m.get(k)}
        }
        (map_dir / "metadata.json").write_text(json.dumps(meta, indent=2))
        all_metadata[name.upper()] = meta
        print(f"  📄 Saved {len(callouts)} callouts to metadata.json\n")

    # Master index
    (OUTPUT_DIR / "index.json").write_text(json.dumps(all_metadata, indent=2))
    print("=" * 50)
    print(f"✅ Done! {len(playable)} maps saved to: {OUTPUT_DIR.resolve()}")
    print(f"📁 Master index: {(OUTPUT_DIR / 'index.json').resolve()}")

if __name__ == "__main__":
    scrape()
