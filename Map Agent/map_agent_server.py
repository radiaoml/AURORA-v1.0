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
from PIL import Image, ImageStat
import numpy as np

# Add Map Agent directory to path for metadata_oracle import
import numpy as np

# Optional OCR dependencies. If unavailable we gracefully fallback to UNKNOWN.
try:
    import cv2
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False
sys.path.insert(0, os.path.dirname(__file__))
from metadata_oracle import MetadataOracle
from lore_geographer import LoreGeographer
from tactical_specialist import TacticalSpecialist
from report_specialist import ReportSpecialist
from enemy_specialist import EnemySpecialist
from spike_specialist import SpikeSpecialist
from riot_id_specialist import RiotIDSpecialist

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("MapAgent_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
lore_agent = LoreGeographer()
tactical_agent = TacticalSpecialist()
report_agent = ReportSpecialist()
enemy_agent = EnemySpecialist()
spike_agent = SpikeSpecialist()
riot_agent = RiotIDSpecialist()
vision_model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI(title="AURORA Map Intelligence Agent v2")
oracle = MetadataOracle(knowledge_base_path="Map Agent/riot_official_data/index.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def ocr_minimap_text(image_bytes: bytes) -> str:
    """Attempt to extract text from the top-left minimap area.

    This function is intentionally conservative: it will try to crop the
    top-left portion of the image (where the minimap typically lives),
    apply simple binarization and OCR, and return the extracted text.
    If OCR libraries are not installed or extraction fails, returns "UNKNOWN".
    """
    if not OCR_AVAILABLE:
        return "UNKNOWN"

    try:
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return "UNKNOWN"

        h, w = img.shape[:2]

        # Heuristic minimap ROI: top-left corner. These ratios are conservative
        # and can be tuned per-stream resolution. We crop 0..0.28 width and 0..0.28 height.
        x1 = int(w * 0.0)
        x2 = max(1, int(w * 0.28))
        y1 = int(h * 0.0)
        y2 = max(1, int(h * 0.28))

        roi = img[y1:y2, x1:x2]
        if roi is None or roi.size == 0:
            return "UNKNOWN"

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # upscale to help OCR
        gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Use pytesseract to extract text. Use a forgiving page segmentation mode.
        text = pytesseract.image_to_string(thr, config='--psm 6')
        text = text.strip()
        if not text:
            return "UNKNOWN"

        # Clean up common OCR noise
        text = re.sub(r"[^A-Za-z0-9 '\-]", ' ', text).strip()
        return text if text else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

ANALYSIS_PROMPT = """You are an expert Valorant analyst with perfect map knowledge.
Analyze this gameplay screenshot and identify the map and location.

CRITICAL: STREAMER OVERLAYS & UI
- Ignore any webcams/facecams (usually square boxes in corners).
- Ignore colorful borders, stripes, or frames (e.g., orange/green stripes often denote streamer UI, NOT the map).
- Focus ONLY on the actual 3D game world and the Minimap.

IMPORTANT - Use this VERIFICATION WORKFLOW:
1. LIST ALL SITE LABELS: Scan the entire minimap. Which letters (A, B, C) do you see?
   - If you see A, B, AND C -> Strictly identify as Haven or Lotus.
   - If you see only A and B -> Most other maps.
2. OCR (Top-Left): Read the text label in the minimap (e.g., "A Garden").
3. LANDMARK CHECK: Look for THE "02" building (Split), Asian Monastery arches (Haven), or Desert murals (Bind).
4. SELF-CORRECTION: "I see A, B, and C sites, so I cannot choose Bind. This must be Haven."

EXACT MAP NAMES (use strictly one): Ascent, Bind, Breeze, Corrode, Fracture, Haven, Icebox, Lotus, Pearl, Split, Sunset, Abyss, District, Drift, Kasbah

Respond in STRICT JSON format only:
{
    "map": "<exact map name>",
    "location": "<specific callout visible in text>",
    "agent": "<name of the character being played, e.g. Brimstone, Jett>",
    "sites_observed": ["<list site letters seen>"],
    "round_context": {
        "score": "<current score e.g. 0-0>",
        "time": "<current round time e.g. 1:40>",
        "phase": "<Buy/Round/Post-Plant/End>"
    },
    "confidence": "<high/medium/low>",
    "visual_cues": "<brief explanation>"
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

    # Run OCR pre-step on the minimap region and surface the text to the LLM
    minimap_text = ocr_minimap_text(image_bytes)
    print(f"🔎 Minimap OCR result: '{minimap_text}' (OCR_AVAILABLE={OCR_AVAILABLE})")

    # Send to Gemini Vision
    try:
        image_part = {
            "inline_data": {
                "mime_type": file.content_type or "image/jpeg",
                "data": base64.b64encode(image_bytes).decode()
            }
        }
        print("🤖 Sending to Gemini Vision...")
        combined_prompt = ANALYSIS_PROMPT + "\n\nMINIMAP_OCR: '" + minimap_text + "'\n\n"
        response = vision_model.generate_content([combined_prompt, image_part])
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

    # 2. Attempt Precision Tracing and Minimap Crop for Enemy Detection
    minimap_img = None
    try:
        full_img = Image.open(io.BytesIO(image_bytes))
        w, h = full_img.size
        # Reuse standard crop from get_precision_coordinates logic
        sx, sy, sw, sh = int(w * 0.01), int(h * 0.015), int(w * 0.16), int(h * 0.28)
        minimap_img = full_img.crop((sx, sy, sx+sw, sy+sh))
    except Exception:
        pass

    precision_coords = get_precision_coordinates(image_bytes, detected_map)
    final_coords = precision_coords if precision_coords else oracle_data.get("coordinates")
    is_precision = precision_coords is not None

    # Apply Enemy Specialist
    tactical_state = {"status_msg": "🟢 SECTOR CLEAR", "enemy_count": 0, "threat_level": "NONE"}
    if minimap_img:
        tactical_state = enemy_agent.detect_enemies(minimap_img)

    # Apply Spike Specialist
    spike_status = {"status_msg": "🕒 PRE-PLANT", "is_planted": False}
    if minimap_img:
        try:
            full_img = Image.open(io.BytesIO(image_bytes))
            spike_status = spike_agent.detect_spike(full_img, minimap_img)
        except Exception:
            pass

    # Merge results
    result = {
        "map": detected_map,
        "location": detected_location,
        "sites_observed": gemini_data.get("sites_observed", []),
        "tactical_description": oracle_data.get("tactical_description"),
        "lore_coordinates": oracle_data.get("lore_coordinates"),
        "precise_z": oracle_data.get("precise_z"),
        "elevation_label": oracle_data.get("elevation_label"),
        "confidence": gemini_data.get("confidence", "unknown"),
        "visual_cues": gemini_data.get("visual_cues", ""),
        "round_context": gemini_data.get("round_context", {}),
        "agent": gemini_data.get("agent", "Unknown"),
        "coordinates": final_coords,
        "super_region": oracle_data.get("super_region"),
        "source": "Gemini Vision + Precision Tracer" if is_precision else "Gemini Vision + Oracle",
        "tactical_state": tactical_state,
        "spike_status": spike_status,
        "map_uuid": riot_agent.get_map_uuid(detected_map)
    }

    # Phase 6: Deep Tactical Analysis via Specialist Agent
    try:
        print(f"🧠 Tactical Specialist analyzing round state...")
        round_state = {
            "map_name": detected_map,
            "location": detected_location,
            "score": result["round_context"].get("score", "0-0"),
            "time": result["round_context"].get("time", "Unknown"),
            "phase": result["round_context"].get("phase", "Round"),
            "agent_name": result.get("agent", "Unknown")
        }
        result["tactical_advice"] = tactical_agent.get_tactical_advice(round_state)
    except Exception as tac_err:
        print(f"⚠️ Tactical Agent failed: {tac_err}")
        result["tactical_advice"] = oracle_data.get("tactical_advice", "Maintain awareness.")

    # Phase 7: Report Beautification (Structured JSON for UI)
    try:
        print(f"🎨 Report Specialist beautifying analysis...")
        result["tactical_advice_beautified"] = report_agent.beautify(result["tactical_advice"])
        result["visual_cues_beautified"] = report_agent.beautify(result["visual_cues"])
    except Exception as report_err:
        print(f"⚠️ Report Agent failed: {report_err}")
        result["tactical_advice_beautified"] = None
        result["visual_cues_beautified"] = None

    # Phase 4: Enrich with Lore Geographer Agent
    if result["lore_coordinates"]:
        try:
            print(f"🌍 Lore Agent analyzing: {result['lore_coordinates']}")
            lore_context = lore_agent.get_location_context(result["lore_coordinates"])
            result["lore_context"] = lore_context
        except Exception as lore_err:
            import traceback
            print(f"⚠️  Lore Agent failed: {lore_err}")
            traceback.print_exc()
            result["lore_context"] = {
                "geographic_discovery": f"Coordinates: {result['lore_coordinates']}",
                "lore_report": "Lore data temporarily unavailable."
            }

    print(f"✅ Final result: {json.dumps(result, indent=2)}")
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
