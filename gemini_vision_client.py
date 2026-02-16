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
            Analyze these frames from a Valorant gameplay match (Source: {source_info}). 
            Evaluate the following metrics:
            1. Map Identification: Which map is being played? (Ascent, Bind, Haven, etc.)
            2. Match Context: Identify the current round number if visible on the HUD.
            3. Entry Timing: Was the entry synchronized with initiator utility?
            4. Team Formation: Is the teammate spacing optimal for trades?
            5. Spike Planting: Is the plant location strategically sound?
            6. Rotation Latency: How long did it take the team to rotate after contact? (e.g., "3.2s")
            7. Win Rate Prediction: Based on this tactic, what is the estimated win rate for the round? (e.g., "75%")
            
            Provide a professional critique in JSON format with these exact keys: 
            detected_map, detected_round, entry_rating, timing_gap, formation_issue, planting_critique, rotation_latency, win_rate_prediction, tactical_suggestion.
            """

            response = self.model.generate_content([prompt, *images])
            
            # Clean up uploaded files (Production best practice)
            # for img in images: genai.delete_file(img.name)

            return response.text # Assuming JSON response from prompt instructions
            
        except Exception as e:
            print(f"[NEURAL_ERROR] {str(e)}")
            return self._get_dynamic_mock_analysis(source_info)

    def _get_dynamic_mock_analysis(self, source_info):
        """Generates varied tactical critiques based on the VOD source archetype."""
        time.sleep(2)
        
        # Determine archetype from source string (Simulation)
        if "YT_" in source_info or "cloud" in source_info.lower():
            # Archetype: Pro High-Level Meta
            return {
                "detected_map": "Ascent",
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
                "detected_map": "Bind",
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
                "detected_map": "Haven",
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
