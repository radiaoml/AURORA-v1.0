from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from video_analyzer import TacticalVisionEngine

app = FastAPI(title="AURORA Neural Backend")

# Enable CORS for the local HUD
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    source: str
    type: str  # 'cloud_stream', 'local_path', or 'local_upload'

@app.get("/")
async def root():
    return {"status": "AURORA_BACKEND_ONLINE", "version": "1.0.0"}

import json
import time
from generate_high_fidelity_mocks import generate_pro_viz

@app.post("/analyze-vod")
async def analyze_vod(request: AnalysisRequest):
    """
    Real-time endpoint that triggers the Vision Engine and Gemini LLM.
    """
    try:
        print(f"[BACKEND] Received analysis request for: {request.source}")
        
        # 1. Initialize the Engine
        engine = TacticalVisionEngine(request.source)
        
        # 2. Extract Frames
        frames, source_meta = engine.extract_tactical_frames()
        
        # 3. Call the Multimodal Brain (Gemini 1.5 Pro)
        raw_critique = engine.get_multimodal_critique(frames, source_meta=source_meta)
        
        # Parse the JSON if it's a string
        critique = raw_critique
        if isinstance(raw_critique, str):
            try:
                # Remove markdown code blocks if Gemini includes them
                json_str = raw_critique.replace("```json", "").replace("```", "").strip()
                critique = json.loads(json_str)
            except:
                print("[WARNING] Failed to parse Gemini response as JSON.")
                critique = {"raw": raw_critique}

        # 4. Neural Spatial Sync: Generate CUSTOM graphics for this analysis
        detected_map = "ASCENT"
        if isinstance(critique, dict):
            detected_map = critique.get("detected_map", "ASCENT").upper()

        # Generate unique filenames to prevent caching and cross-talk
        ts = int(time.time())
        heatmap_name = f"analysis_heatmap_{ts}.png"
        pathing_name = f"analysis_pathing_{ts}.png"
        
        print(f"[BACKEND] Generating live tactical viz for {detected_map}...")
        generate_pro_viz(detected_map, heatmap_name, pathing_name)
        
        spatial_payload = {
            "map_id": detected_map,
            "heatmap_url": heatmap_name,
            "trajectories_url": pathing_name,
            "live_coords": [
                {"agent": "Jett", "x": 1250, "y": 800, "event": "Entry"},
                {"agent": "Omen", "y": 450, "x": 900, "event": "Smoke"}
            ]
        }

        # Trigger High-Fidelity Blueprint Projection
        try:
            BLUEPRINT_MAP = {
                "ASCENT": "blueprints/ascent_blueprint.png",
                "BIND": "blueprints/bind_blueprint.png",
                "HAVEN": "blueprints/haven_blueprint.png",
                "SPLIT": "blueprints/split_blueprint.png",
                "ICEBOX": "blueprints/icebox_blueprint.png",
                "BREEZE": "blueprints/breeze_blueprint.png",
                "FRACTURE": "blueprints/fracture_blueprint.png",
                "PEARL": "blueprints/pearl_blueprint.png",
                "LOTUS": "blueprints/lotus_blueprint.png",
                "SUNSET": "blueprints/sunset_blueprint.png",
                "ABYSS": "blueprints/abyss_blueprint.png",
                "DISTRICT": "blueprints/district_blueprint.png"
            }
            blueprint_path = BLUEPRINT_MAP.get(spatial_payload["map_id"])
            if blueprint_path and not os.path.exists(blueprint_path):
                blueprint_path = None # Fallback to no-blueprint if file doesn't exist yet

            generate_pro_viz(
                spatial_payload["map_id"], 
                spatial_payload["heatmap_url"], 
                spatial_payload["trajectories_url"],
                blueprint_path=blueprint_path
            )
            print(f"[BACKEND] Projected Intelligence synchronization active for {spatial_payload['map_id']}")
        except Exception as e:
            print(f"[ERROR] Visualization Projection Failed: {e}")
        
        return {
            "status": "SUCCESS",
            "source_id": request.source,
            "analysis": critique,
            "spatial_data": spatial_payload
        }
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # In production, run with uvicorn aurora_backend:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
