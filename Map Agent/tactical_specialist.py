import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class TacticalSpecialist:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def get_tactical_advice(self, game_state: dict) -> str:
        """
        Generates expert Valorant tactical advice based on game state.
        
        Expected game_state keys:
        - map_name
        - location
        - score
        - time
        - phase
        - agent_name (optional)
        """
        map_name = game_state.get("map_name", "Unknown")
        location = game_state.get("location", "Unknown")
        score = game_state.get("score", "0-0")
        time = game_state.get("time", "Unknown")
        phase = game_state.get("phase", "Round")
        agent_name = game_state.get("agent_name", "current agent")

        prompt = f"""You are a professional Valorant Head Coach for a Tier 1 VCT team.
Your goal is to provide elite-level tactical advice based on the current game state.

CURRENT GAME STATE:
- Map: {map_name}
- Location: {location}
- Agent: {agent_name}
- Score: {score}
- Round Time: {time}
- Phase: {phase}

INSTRUCTIONS:
1. ECONOMY: Analyze the score/round to infer the economy (e.g., eco, force, or full buy).
2. STRATEGY: Provide 2-3 concise, high-impact tactical bullet points for the current map location.
3. AGENT TIPS: Give 1 specific utility or positioning tip for {agent_name} in this spot.
4. URGENCY: Factor in the time remaining (e.g., if there are 20 seconds left, prioritize the plant/defuse).

Keep the advice professional, punchy, and actionable. Use tactical terminology (e.g., "default", "rotate", "trade", "crossfire").

RESPONSE FORMAT:
One concise paragraph of expert analysis, followed by 2-3 bullet points."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Strategic analysis unavailable: {str(e)}"

if __name__ == "__main__":
    # Test case
    specialist = TacticalSpecialist()
    test_state = {
        "map_name": "Split",
        "location": "A Heaven",
        "score": "10-12",
        "time": "0:45",
        "phase": "Active Round",
        "agent_name": "Brimstone"
    }
    print(specialist.get_tactical_advice(test_state))
