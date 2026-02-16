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

@app.post("/analyze-vod")
async def analyze_vod(request: AnalysisRequest):
    """
    Real-time endpoint that triggers the Vision Engine and Gemini LLM.
    """
    try:
        print(f"[BACKEND] Received analysis request for: {request.source}")
        
        # 1. Initialize the Engine
        engine = TacticalVisionEngine(request.source)
        
        # 2. Extract Frames (Real logic)
        frames, source_meta = engine.extract_tactical_frames()
        
        # 3. Call the Multimodal Brain (Gemini 1.5 Pro)
        critique = engine.get_multimodal_critique(frames, source_meta=source_meta)
        
        # 4. Neural Spatial Sync: Fetch coordinates based on detected context
        # In production, this would query a real database or the .csv
        spatial_payload = {
            "map_id": "ASCENT",
            "heatmap_url": "tactical_kill_heatmap.png",
            "trajectories_url": "round_1_trajectories.png",
            "live_coords": [
                {"agent": "Jett", "x": 1250, "y": 800, "event": "Entry"},
                {"agent": "Omen", "y": 450, "x": 900, "event": "Smoke"}
            ]
        }
        
        # Override based on detected map (Simulation of dynamic lookup)
        if isinstance(critique, dict):
            detected_map = critique.get("detected_map", "Unknown").upper()
            if "BIND" in detected_map:
                spatial_payload["map_id"] = "BIND"
                spatial_payload["heatmap_url"] = "bind_heatmap_pro.png"
                spatial_payload["trajectories_url"] = "bind_pathing_pro.png"
            elif "HAVEN" in detected_map:
                spatial_payload["map_id"] = "HAVEN"
                spatial_payload["heatmap_url"] = "haven_heatmap_pro.png"
                spatial_payload["trajectories_url"] = "haven_pathing_pro.png"
            else:
                spatial_payload["map_id"] = "ASCENT"
                spatial_payload["heatmap_url"] = "ascent_heatmap_pro.png"
                spatial_payload["trajectories_url"] = "ascent_pathing_pro.png"
        
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
