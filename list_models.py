import google.generativeai as genai
import os

key = os.getenv("GEMINI_API_KEY")
print(f"Checking models for key: {key[:10]}...")
genai.configure(api_key=key)

try:
    print("Listing available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
