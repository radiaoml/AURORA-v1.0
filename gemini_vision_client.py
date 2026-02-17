import os
import time
import google.generativeai as genai
from typing import List

class GeminiVisionClient:
    def __init__(self):
        # In production, the user would set this env variable
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None
            print("[WARNING] GEMINI_API_KEY not found. Vision reasoning will be simulated.")

    def analyze_gameplay_vod(self, frames: List[str], source_info: str = "Unknown"):
        """
        Sends sampled frames to Gemini 1.5 Pro for deep tactical analysis.
        """
        if not self.model:
            print("[SIMULATION_MODE] No API key. Falling back to dynamic mock.")
            return self._get_dynamic_mock_analysis(source_info)

        print(f"[BRAIN] Sending {len(frames)} frames to Gemini 1.5 Pro Neural Engine...")
        
        try:
            # Prepare images for Gemini
            images = []
            for frame_path in frames:
                if os.path.exists(frame_path):
                    # In production, we'd use PIL or raw bytes
                    # For this prototype, we're assuming frames are saved to disk
                    img = genai.upload_file(path=frame_path, display_name=f"TacticalFrame_{os.path.basename(frame_path)}")
                    images.append(img)
            
            prompt = f"""
            You are analyzing frames from a Valorant competitive gameplay match (Source: {source_info}).
            
            CRITICAL TASK 1: Identify which Valorant map is being played from these frames.
            
            The 12 competitive maps are:
            - ASCENT (Italy, Venice-inspired, open mid, A-site has wine/garden)
            - BIND (Morocco, teleporters, hookah/showers)
            - HAVEN (Bhutan, 3 sites: A/B/C, garage, long C)
            - SPLIT (Japan/Tokyo, vertical map, ropes, mid mail)
            - ICEBOX (Arctic, vertical, yellow containers, kitchen)
            - BREEZE (Caribbean island, wide open, pyramids on A)
            - FRACTURE (New Mexico, H-shaped, attackers spawn both sides)
            - PEARL (Lisbon/Portugal, art gallery, mid plaza)
            - LOTUS (India, 3 sites: A/B/C, rotating doors)
            - SUNSET (Los Angeles, sunset lighting, market on B)
            - ABYSS (Norway, no boundaries/death drops, castle aesthetic)
            - DISTRICT (Team Deathmatch map, urban setting)
            
            Look for distinctive visual features:
            - Architecture style and color palette
            - Unique landmarks (teleporters, ropes, rotating doors, etc.)
            - Site layouts visible in the minimap
            - Environmental lighting and theme
            
            CRITICAL TASK 2: Extract SPATIAL GAMEPLAY DATA from the frames.
            
            Analyze the minimap (top-left corner) and gameplay footage to extract:
            
            1. KILL LOCATIONS: For each kill/death event visible:
               - Approximate map coordinates (0-1000 scale, where 0,0 is bottom-left, 1000,1000 is top-right)
               - Area name (e.g., "A-site", "B-long", "Mid", "Spawn")
               - If you can't see exact coordinates, estimate based on the area
            
            2. PLAYER POSITIONS: Sample 5-10 player positions throughout the visible gameplay:
               - Coordinates (x, y) on 0-1000 scale
               - Timestamp indicator (early/mid/late in the round)
               - Agent name if visible
            
            3. MOVEMENT PATHS: Identify 3-5 major movement corridors used:
               - Start position (x, y)
               - End position (x, y)
               - Path type (entry, rotation, flank, retreat)
            
            COORDINATE SYSTEM GUIDE:
            - Use the minimap as reference
            - Bottom-left corner of map = (0, 0)
            - Top-right corner of map = (1000, 1000)
            - A-site typically around (200-400, 600-800) depending on map
            - B-site typically around (600-800, 200-400) depending on map
            - Mid typically around (400-600, 400-600)
            
            Also analyze these tactical metrics:
            1. Match Context: Current round number if visible on HUD
            2. Entry Timing: Was entry synchronized with initiator utility?
            3. Team Formation: Is teammate spacing optimal for trades?
            4. Spike Planting: Is plant location strategically sound?
            5. Rotation Latency: How long did team rotate after contact?
            6. Win Rate Prediction: Estimated win rate for this round based on tactics
            
            Return ONLY valid JSON with these exact keys (no markdown, no code blocks):
            {{
                "detected_map": "MAP_NAME_IN_UPPERCASE",
                "map_confidence": "high/medium/low",
                "kill_locations": [
                    {{"x": 450, "y": 650, "area": "A-site"}},
                    {{"x": 520, "y": 380, "area": "Mid"}}
                ],
                "player_positions": [
                    {{"x": 300, "y": 400, "timestamp": "early", "agent": "Jett"}},
                    {{"x": 500, "y": 700, "timestamp": "mid", "agent": "Omen"}}
                ],
                "movement_paths": [
                    {{"start_x": 200, "start_y": 300, "end_x": 450, "end_y": 650, "type": "entry"}},
                    {{"start_x": 600, "start_y": 400, "end_x": 300, "end_y": 700, "type": "rotation"}}
                ],
                "detected_round": "round number or unknown",
                "entry_rating": "A+/A/A-/B+/B/B-/C+/C/D",
                "timing_gap": "description with seconds",
                "formation_issue": "analysis of team spacing",
                "planting_critique": "spike plant analysis",
                "rotation_latency": "time in seconds",
                "win_rate_prediction": "percentage",
                "tactical_suggestion": "professional critique"
            }}
            
            IMPORTANT: If you cannot extract exact coordinates, provide your best estimate based on the area names and typical map layouts.
            """

            response = self.model.generate_content([prompt, *images])
            
            # Clean up uploaded files (Production best practice)
            # for img in images: genai.delete_file(img.name)
            
            # Parse JSON response
            import json
            try:
                # Remove markdown code blocks if present
                response_text = response.text.strip()
                if response_text.startswith("```"):
                    # Extract JSON from code block
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                    response_text = response_text.strip()
                
                analysis = json.loads(response_text)
                
                # Ensure map name is uppercase and valid
                detected_map = analysis.get("detected_map", "UNKNOWN").upper()
                valid_maps = ["ASCENT", "BIND", "HAVEN", "SPLIT", "ICEBOX", "BREEZE", 
                             "FRACTURE", "PEARL", "LOTUS", "SUNSET", "ABYSS", "DISTRICT"]
                
                if detected_map not in valid_maps:
                    print(f"[WARN] Invalid map detected: {detected_map}, defaulting to ASCENT")
                    analysis["detected_map"] = "ASCENT"
                else:
                    analysis["detected_map"] = detected_map
                
                print(f"[VISION] Map detected: {analysis['detected_map']} (confidence: {analysis.get('map_confidence', 'unknown')})")
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse JSON response: {e}")
                print(f"[DEBUG] Raw response: {response.text[:500]}")
                return self._get_dynamic_mock_analysis(source_info)

        except Exception as e:
            print(f"[NEURAL_ERROR] {str(e)}")
            return self._get_dynamic_mock_analysis(source_info)

    def _get_dynamic_mock_analysis(self, source_info):
        """Generates varied tactical critiques based on the VOD source archetype."""
        time.sleep(2)
        
        print("[WARN] Using mock analysis fallback. Map detection may be inaccurate.")
        print("[INFO] For accurate map detection, ensure GEMINI_API_KEY is set and frames are being analyzed.")
        
        # Try to extract map from filename if possible
        detected_map = "UNKNOWN"
        source_upper = source_info.upper()
        
        # Simple filename parsing
        for map_name in ["ASCENT", "BIND", "HAVEN", "SPLIT", "ICEBOX", "BREEZE", 
                         "FRACTURE", "PEARL", "LOTUS", "SUNSET", "ABYSS", "DISTRICT"]:
            if map_name in source_upper:
                detected_map = map_name
                break
        
        # Determine archetype from source string (Simulation)
        if "YT_" in source_info or "cloud" in source_info.lower():
            # Archetype: Pro High-Level Meta
            return {
                "detected_map": detected_map if detected_map != "UNKNOWN" else "ASCENT",
                "map_confidence": "low (mock data)",
                "detected_round": "04",
                "entry_rating": "A-",
                "timing_gap": "+0.4s (Elite synchronization)",
                "formation_issue": "Flawless 'Diamond' formation detected.",
                "planting_critique": "Optimal Spike placement for 'Post-Plant Long'.",
                "rotation_latency": "1.8s (Elite-level reaction)",
                "win_rate_prediction": "88%",
                "tactical_suggestion": "Excellent map control. Consider 'False A' rotation next round."
            }
        elif "Ace" in source_info or "Clutch" in source_info:
            # Archetype: Individual Heroics / Trade Isolation
            return {
                "detected_map": detected_map if detected_map != "UNKNOWN" else "BIND",
                "map_confidence": "low (mock data)",
                "detected_round": "12",
                "entry_rating": "B",
                "timing_gap": "Variable (Heroic individual timing)",
                "formation_issue": "Isolated from team; High individual performance found.",
                "planting_critique": "Aggressive plant; Dependent on individual aim.",
                "rotation_latency": "4.1s (Delayed due to individual engagements)",
                "win_rate_prediction": "62%",
                "tactical_suggestion": "Great clutch, but average team spacing is low. Focus on trade-potential."
            }
        else:
            # Archetype: Strategic Gaps (Standard Learning Mode)
            return {
                "detected_map": detected_map if detected_map != "UNKNOWN" else "HAVEN",
                "map_confidence": "low (mock data)",
                "detected_round": "07",
                "entry_rating": "D",
                "timing_gap": "+2.8s (Delayed entry relative to smokes)",
                "formation_issue": "Fragmented; Teammates isolated behind site-entrance.",
                "planting_critique": "Vulnerable plant detected. No cover utility detected.",
                "rotation_latency": "6.5s (Critical delay in map-repositioning)",
                "win_rate_prediction": "31%",
                "tactical_suggestion": "Sync entry with Initiator utility. Hold smokes until cross-site logic clears."
            }

if __name__ == "__main__":
    client = GeminiVisionClient()
    print("Gemini Vision Client Initialized.")
