import os
import json
import re
import sys
import base64
import io
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
from PIL import Image
import numpy as np

# Add Map Agent directory to path for metadata_oracle import
sys.path.insert(0, os.path.dirname(__file__))
from metadata_oracle import MetadataOracle

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
vision_model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI(title="AURORA Map Intelligence Agent v2")
oracle = MetadataOracle(knowledge_base_path="Map Agent/riot_official_data/index.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ANALYSIS_PROMPT = """You are an expert Valorant analyst with perfect map knowledge.
Analyze this gameplay screenshot and identify the map and location.

CRITICAL: STREAMER OVERLAYS & UI
- Ignore any webcams/facecams (usually square boxes in corners).
- Ignore colorful borders, stripes, or frames (e.g., orange/green stripes often denote streamer UI, NOT the map).
- Focus ONLY on the actual 3D game world and the Minimap.

IMPORTANT - Use this PRIORITY ORDER for identification:
1. OCR (Top-Left): Check the minimap for a text label of the current location - this is ground truth.
2. GEOMETRY: Analyze the minimap shape and layout (e.g., three sites vs. two, verticality).
3. ENVIRONMENT: Use your native knowledge of Valorant map aesthetics (colors, architectural styles, unique landmarks) to confirm.

EXACT MAP NAMES (use strictly one): Ascent, Bind, Breeze, Corrode, Fracture, Haven, Icebox, Lotus, Pearl, Split, Sunset, Abyss, District, Drift, Kasbah

Respond in STRICT JSON format only:
{
  "map": "<exact map name>",
  "location": "<specific callout or region>",
  "confidence": "<high/medium/low>",
  "visual_cues": "<brief explanation of the game-world evidence found>"
}

If you cannot identify the map, use "UNKNOWN" for both fields."""

def get_precision_coordinates(image_bytes, map_name):
    """
    Experimental: Extracts the minimap, finds the player icon, 
    and converts to world coordinates.
    Assumes standard 16:9 1080p HUD for now.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        
        # 1. Minimap Box (Standard 1080p estimate: top-left corner)
        sx = int(width * 0.01) 
        sy = int(height * 0.015) 
        sw = int(width * 0.16) 
        sh = int(height * 0.28) 
        
        minimap = img.crop((sx, sy, sx+sw, sy+sh))
        
        # --- Safeguard: Check if this is a real Minimap ---
        # A real minimap has a circular or square frame with high variation.
        # Cinematics might have simple flat colors or gradients.
        stat = ImageStat.Stat(minimap)
        if sum(stat.stddev) < 20: # Low visual complexity = not a HUD
            return None
        # --------------------------------------------------

        # 2. Find Player Icon (White-ish arrow)
        gray = minimap.convert('L')
        arr = np.array(gray)
        
        # Find the max brightness
        max_val = np.max(arr)
        if max_val < 200: # Probably didn't find the icon
            return None
            
        # Get coordinates of bright spots
        y_indices, x_indices = np.where(arr >= max_val - 10)
        pixel_x = np.mean(x_indices)
        pixel_y = np.mean(y_indices)
        
        # 3. Get Scalars from Oracle
        scalars = oracle.get_map_scalars(map_name)
        if not scalars or not scalars.get("xMultiplier"):
            return None
            
        # 4. Transform (Standard Valorant API Formula)
        world_x = (pixel_x * scalars["xMultiplier"]) + scalars["xScalarToAdd"]
        world_y = (pixel_y * scalars["yMultiplier"]) + scalars["yScalarToAdd"]
        
        return {
            "x": world_x,
            "y": world_y,
            "pixel_x": pixel_x,
            "pixel_y": pixel_y,
            "is_precision": True
        }
    except Exception as e:
        print(f"⚠️ Tracer error: {e}")
        return None

@app.get("/")
async def root():
    return {"status": "AURORA_MAP_AGENT_ONLINE", "version": "2.0-GeminiVision"}

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    print(f"🔭 Received image: {file.filename} ({file.content_type})")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")

    # Send to Gemini Vision
    try:
        image_part = {
            "inline_data": {
                "mime_type": file.content_type or "image/jpeg",
                "data": base64.b64encode(image_bytes).decode()
            }
        }
        print("🤖 Sending to Gemini Vision...")
        response = vision_model.generate_content([ANALYSIS_PROMPT, image_part])
        raw_text = response.text.strip()
        print(f"📡 Gemini raw response: {raw_text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

    # Parse JSON from Gemini response
    try:
        clean = re.sub(r"```json|```", "", raw_text).strip()
        gemini_data = json.loads(clean)
    except Exception:
        gemini_data = {
            "map": "UNKNOWN",
            "location": "UNKNOWN",
            "confidence": "low",
            "visual_cues": raw_text[:200]
        }

    detected_map = gemini_data.get("map", "UNKNOWN").strip()
    detected_location = gemini_data.get("location", "UNKNOWN").strip()

    print(f"🗺️ Detected: {detected_map} / {detected_location}")

    # 1. Get Regional Data (Oracle)
    oracle_data = oracle.lookup(detected_map, detected_location)

    # 2. Attempt Precision Tracing
    precision_coords = get_precision_coordinates(image_bytes, detected_map)
    final_coords = precision_coords if precision_coords else oracle_data.get("coordinates")

    # Merge results
    result = {
        "map": detected_map,
        "location": detected_location,
        "confidence": gemini_data.get("confidence", "unknown"),
        "visual_cues": gemini_data.get("visual_cues", ""),
        "coordinates": final_coords,
        "super_region": oracle_data.get("super_region"),
        "tactical_advice": oracle_data.get("tactical_advice", "Maintain awareness."),
        "source": "Gemini Vision + Precision Tracer" if precision_coords else "Gemini Vision + Oracle"
    }
    print(f"✅ Final result: {json.dumps(result, indent=2)}")
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
