import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class ReportSpecialist:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        # Using 1.5-flash for speed and cost
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def beautify(self, raw_text: str) -> list:
        """
        Transforms raw text into a structured JSON list of report blocks.
        STRICTLY preserves the original wording.
        """
        if not raw_text or len(raw_text) < 10:
            return [{"type": "paragraph", "content": raw_text}]

        prompt = f"""You are a UI/UX Content Architect.
Your task is to take a raw tactical report and structure it into a beautiful, organized JSON format for a dashboard.

STRICT RULES:
1. DO NOT change, add, or remove any words from the original text.
2. DO NOT summarize.
3. Your only job is to categorize segments of the text into block types.

BLOCK TYPES:
- "header": A short title or high-level category (e.g., "TACTICAL OVERVIEW").
- "paragraph": Standard text blocks.
- "bullet": Specific actionable items or observations.
- "tip": Specialized advice (e.g., agent-specific tips).
- "warning": Urgent or high-priority tactical info.

RAW TEXT:
{raw_text}

RESPONSE FORMAT (Strict JSON list of objects):
[
  {{ "type": "header", "content": "..." }},
  {{ "type": "paragraph", "content": "..." }},
  {{ "type": "bullet", "content": "..." }},
  ...
]"""

        try:
            response = self.model.generate_content(prompt)
            clean_json = re.sub(r"```json|```", "", response.text).strip()
            structured_data = json.loads(clean_json)
            return structured_data
        except Exception as e:
            print(f"⚠️ Report Specialist failed: {e}")
            # Fallback to a single paragraph block
            return [{"type": "paragraph", "content": raw_text}]

if __name__ == "__main__":
    # Test case
    specialist = ReportSpecialist()
    test_text = "Alright team, pistol round. We need to focus. * **Mid Control:** Let's default towards mid. Sova, use your drone. **Jett Tip:** Jett, use your Cloudbursts strategically."
    print(json.dumps(specialist.beautify(test_text), indent=2))
