import json
from pathlib import Path


class MetadataOracle:
    """
    The Spatial Intelligence Brain of the Map Agent.
    Matches Gemini Vision outputs directly to official Riot callout data.
    """

    def __init__(self, knowledge_base_path: str = "Map Agent/riot_official_data/index.json"):
        self.kb_path = Path(knowledge_base_path)
        self.kb = self._load_kb()

    def _load_kb(self):
        if not self.kb_path.exists():
            # Fallback to old KB
            old_path = Path("Map Agent/map_knowledge_base.json")
            if old_path.exists():
                print(f"⚠️  Using legacy knowledge base: {old_path}")
                with open(old_path, 'r') as f:
                    return json.load(f)
            print(f"❌ No knowledge base found at {self.kb_path}")
            return {}
        print(f"✅ Oracle loaded: {self.kb_path}")
        with open(self.kb_path, 'r') as f:
            return json.load(f)

    def lookup(self, map_name: str, location: str) -> dict:
        """
        Directly find coordinates and zone from a map name and location string.
        Both map_name and location come from Gemini Vision output (natural language).
        """
        if not map_name or map_name.upper() == "UNKNOWN":
            return self._fallback(map_name, location)

        # Find map in KB (case-insensitive, partial match)
        map_key = self._find_map_key(map_name)
        if not map_key:
            print(f"⚠️  Map '{map_name}' not in knowledge base. Keys: {list(self.kb.keys())}")
            return self._fallback(map_name, location)

        map_data = self.kb[map_key]
        callouts = map_data.get("callouts", [])

        if not callouts:
            return self._fallback(map_name, location)

        # Fuzzy match the location against callout region names
        matched = self._fuzzy_match_callout(location, callouts)

        if not matched:
            # Return map-level info only (no specific callout)
            return {
                "map": map_data.get("name", map_name),
                "tactical_description": map_data.get("tacticalDescription"),
                "lore_coordinates": map_data.get("coordinates"),
                "location": location,
                "super_region": None,
                "coordinates": None,
                "precise_z": None,
                "tactical_advice": self._generate_advice(map_name, location),
                "note": "Callout matched at map level only."
            }

        # Elevation labeling
        elevation_label = self._get_elevation_label(matched["z"], callouts, matched["region"])

        return {
            "map": map_data.get("name", map_name),
            "tactical_description": map_data.get("tacticalDescription"),
            "lore_coordinates": map_data.get("coordinates"),
            "location": matched["region"],
            "super_region": matched["super_region"],
            "coordinates": {
                "x": matched["x"],
                "y": matched["y"],
                "z": matched["z"]
            },
            "precise_z": matched["z"],
            "elevation_label": elevation_label,
            "tactical_advice": self._generate_advice(map_name, matched["region"]),
        }

    def _find_map_key(self, map_name: str) -> str | None:
        """Case-insensitive partial map key search."""
        target = map_name.strip().upper()
        for key in self.kb:
            if key.upper() == target:
                return key
        # Try partial match
        for key in self.kb:
            if target in key.upper() or key.upper() in target:
                return key
        return None

    def _fuzzy_match_callout(self, location: str, callouts: list) -> dict | None:
        """Find the best matching callout by checking word overlap."""
        if not location or location.upper() == "UNKNOWN":
            return None

        location_words = set(location.upper().replace("-", " ").split())
        best_match = None
        best_score = 0

        for callout in callouts:
            region = callout.get("region", "")
            super_region = callout.get("super_region", "")
            candidate_words = set((region + " " + super_region).upper().replace("-", " ").split())
            overlap = len(location_words & candidate_words)
            if overlap > best_score:
                best_score = overlap
                best_match = callout

        return best_match if best_score > 0 else None

    def _generate_advice(self, map_name: str, region: str) -> str:
        region_upper = region.upper()
        if "A SITE" in region_upper or "SITE" in region_upper and "A" in region_upper:
            return f"On {map_name} A Site: Establish crossfire. Smoke off aggressive angles. Fast-plant on contact."
        if "B SITE" in region_upper:
            return f"On {map_name} B Site: Prioritize lane control. Flashbang corners before entry."
        if "MID" in region_upper:
            return f"Mid on {map_name}: Contest for map control. Watch for flanks and rotations."
        if "SPAWN" in region_upper and "ATTACK" in region_upper:
            return f"Attacking on {map_name}: Coordinate split push timing. Don't over-commit early."
        if "SPAWN" in region_upper and "DEFEND" in region_upper:
            return f"Defending on {map_name}: Set up passive holds. Save info utility early round."
        return f"Currently on {map_name} - {region}. Maintain map awareness and communicate positions."

    def _fallback(self, map_name: str, location: str) -> dict:
        return {
            "map": map_name or "UNKNOWN",
            "location": location or "Unknown",
            "super_region": None,
            "coordinates": None,
            "elevation_label": None,
            "tactical_advice": f"On {map_name}: Maintain awareness and call positions clearly.",
        }

    def _get_elevation_label(self, z: float, callouts: list, region: str) -> str:
        """Categorizes Z-axis into human-readable labels based on map distribution."""
        z_values = [c["z"] for c in callouts if "z" in c]
        if not z_values:
            return "Ground Level"
        
        min_z = min(z_values)
        max_z = max(z_values)
        z_range = max_z - min_z
        
        if z_range == 0:
            return "Ground Level"
            
        percentile = (z - min_z) / z_range
        
        # Priority 1: Keyword matching
        region_upper = region.upper()
        if "HEAVEN" in region_upper or "TOWER" in region_upper or "RAFTERS" in region_upper:
            return "Heaven / Upper"
        if "GROUND" in region_upper or "BOTTOM" in region_upper or "FLOOR" in region_upper:
            return "Ground Level"
            
        # Priority 2: Range-based
        if percentile < 0.2:
            return "Lower Level / Ground"
        if percentile < 0.5:
            return "Mid Level"
        if percentile < 0.8:
            return "Upper Level"
        return "Heaven / High Point"

    def get_map_scalars(self, map_name: str) -> dict | None:
        """Returns the multipliers and scalars for pixel-to-world conversion."""
        map_key = self._find_map_key(map_name)
        if not map_key:
            return None
        
        data = self.kb[map_key]
        return {
            "xMultiplier": data.get("xMultiplier"),
            "yMultiplier": data.get("yMultiplier"),
            "xScalarToAdd": data.get("xScalarToAdd"),
            "yScalarToAdd": data.get("yScalarToAdd")
        }

    # Legacy support for old label-based lookup


if __name__ == "__main__":
    oracle = MetadataOracle()
    res = oracle.lookup("Split", "Attacker Side Spawn")
    print(json.dumps(res, indent=2))
