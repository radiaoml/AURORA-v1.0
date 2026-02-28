import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LoreGeographer:
    """
    Translates raw lore coordinates (Lat/Long) into real-world geographic context
     and provides tactical flavor text.
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        # Map of common coordinates to avoid unnecessary API calls for fixed data
        self.preset_lore = {
            "35°41'CD'N,139°41'WX'E": {
                "city": "Tokyo",
                "country": "Japan",
                "region_display": "Shinjuku, Tokyo, Japan (Sector 7)",
                "lore_snippet": "Split is a battle for the urban soul. High-density verticality requires tight team coordination. Watch the '02' tower skyline."
            },
            "27°28'A'N,89°38'WZ'E": {
                "city": "Thimphu",
                "country": "Bhutan",
                "region_display": "Thimphu, Bhutan (Eastern Himalayas)",
                "lore_snippet": "Haven't you heard? This base in the Himalayas features three distinct sites. Oxygen is thin; stay sharp."
            },
            "34°2'A'N,6°51'Z'W": {
                "city": "Rabat",
                "country": "Morocco",
                "region_display": "Rabat, Morocco (Maghreb Coast)",
                "lore_snippet": "Bind is a desert facility using stolen radianite technology. Teleporters provide instant rotation at the cost of sound cues."
            },
            "51°28'S'N,3°01'E'W": {
                 "city": "Bristol",
                 "country": "United Kingdom",
                 "region_display": "Bristol, UK (Kingdom HQ)",
                 "lore_snippet": "Ascent represents a floating piece of Venice. The architecture is classical, but the stakes are purely modern."
            }
        }

    def get_location_context(self, coordinates: str) -> dict:
        """
        Processes coordinates to return a rich geographic and lore context.
        """
        if not coordinates:
            return {
                "geographic_discovery": "Unknown Territory",
                "lore_report": "Tactical satellite link lost. Unable to triangulate lore data."
            }
            
        # Check presets first (Fast & Free)
        if coordinates in self.preset_lore:
            data = self.preset_lore[coordinates]
            return {
                "geographic_discovery": f"{data['region_display']}",
                "lore_report": data['lore_snippet']
            }

        # Fallback to Gemini for maps not in preset
        try:
            prompt = f"""
            You are a tactical geographer. Given these real-world coordinates: '{coordinates}', 
            identify the City, Country, and specific real-world region.
            Then, provide a 1-sentence 'Tactical Lore Report' in the style of a Valorant briefing.
            
            Return ONLY a JSON object:
            {{
                "geographic_discovery": "City, Country (Specific Region)",
                "lore_report": "Brief tactical lore snippet."
            }}
            """
            response = self.model.generate_content(prompt)
            import json
            # Extract JSON if Gemini adds markdown-backticks
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            data = json.loads(clean_text)
            return data
        except Exception as e:
            return {
                "geographic_discovery": f"Coordinates: {coordinates}",
                "lore_report": "Satellite imagery shows high Radianite interference. Ground-truth lore unavailable."
            }

if __name__ == "__main__":
    geographer = LoreGeographer()
    print(geographer.get_location_context("35°41'CD'N,139°41'WX'E"))
