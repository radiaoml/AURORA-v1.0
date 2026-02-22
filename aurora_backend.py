from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from video_analyzer import TacticalVisionEngine
from local_video_analyzer import LocalVideoAnalyzer
from aurora_agents import process_video_analysis
from aurora_advanced_agents import run_advanced_analysis
from n8n_integration import setup_n8n_routes

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
    """
    Real-time endpoint that triggers the Vision Engine and Gemini LLM.
    """
    try:
        print(f"[BACKEND] Received analysis request for: {request.source}")
        
        # DEMO MODE: Bypass engine and return high-fidelity mock data
        if request.type == "demo":
            print("[BACKEND] ACTIVATING DEMO MODE: Generating High-Fidelity Capture...")
            time.sleep(2) # Simulate processing
            
            # Rich Spatial Data (Mock)
            demo_critique = {
                "detected_map": "ASCENT",
                "map_confidence": "high",
                "detected_round": "07 (Buy Phase)",
                "entry_rating": "S (Radiant Tier)",
                "timing_gap": "+0.05s (Frame Perfect)",
                "formation_issue": "None. Perfect 'Phalanx' formation.",
                "planting_critique": "God-tier plant for 'Heaven' execution.",
                "rotation_latency": "0.4s (Instant)",
                "win_rate_prediction": "99.9%",
                "tactical_suggestion": "Flawless execution detected. Maintain pressure on Mid-Link.",
                "kill_locations": [
                    {"x": 650, "y": 350, "area": "A Main"}, # Attackers
                    {"x": 620, "y": 400, "area": "A Main"},
                    {"x": 350, "y": 300, "area": "Pizza"}, # Mid
                    {"x": 300, "y": 700, "area": "B Main"},
                    {"x": 320, "y": 680, "area": "B Main"}
                ],
                "player_positions": [
                    {"x": 750, "y": 250, "agent": "Jett"},
                    {"x": 700, "y": 300, "agent": "Sova"},
                    {"x": 200, "y": 800, "agent": "Killjoy"},
                    {"x": 450, "y": 450, "agent": "Omen"}
                ],
                "movement_paths": [
                    {"start_x": 800, "start_y": 100, "end_x": 600, "end_y": 400, "type": "entry"}, # A Push
                    {"start_x": 500, "start_y": 500, "end_x": 300, "end_y": 300, "type": "rotation"} # Mid Rotate
                ],
                "detected_agents": ["JETT", "SOVA", "KILLJOY", "OMEN"]
            }
            
            # Use demo critique for visualization
            raw_critique = demo_critique
            critique = demo_critique
            
            # Skip engine
            frames = [] 
            engine = None
        else:
            # 1. Initialize the Local Analysis Engine
            local_analyzer = LocalVideoAnalyzer()
            
            # 2. Extract Frames (using existing TacticalVisionEngine for frame extraction)
            temp_engine = TacticalVisionEngine(request.source)
            frames, source_meta = temp_engine.extract_tactical_frames()
            
            # 3. Use Local Intelligence Engine for analysis
            raw_critique = local_analyzer.analyze_frames(frames)
        
        # 4. Neural Spatial Sync: Generate CUSTOM graphics for this analysis
        detected_map = "ASCENT"
        if isinstance(raw_critique, dict):
            detected_map = raw_critique.get("detected_map", "ASCENT").upper()

        # Generate unique filenames to prevent caching and cross-talk
        ts = int(time.time())
        heatmap_name = f"analysis_heatmap_{ts}.png"
        pathing_name = f"analysis_pathing_{ts}.png"
        
        # Extract spatial data from analysis
        spatial_data = {}
        if isinstance(raw_critique, dict):
            spatial_data = {
                "kill_locations": raw_critique.get("kill_locations", []),
                "player_positions": raw_critique.get("player_positions", []),
                "movement_paths": raw_critique.get("movement_paths", []),
                "detected_agents": raw_critique.get("detected_agents", [])
            }
        
        # 5. Multi-Agent Processing: Process through Aurora Agent System
        if request.type != "demo" and isinstance(raw_critique, dict):
            print("[BACKEND] Starting Aurora Multi-Agent Processing...")
            
            # Prepare data for multi-agent system
            agent_input = {
                "source_id": request.source,
                "video_analysis": raw_critique,
                "spatial_data": spatial_data,
                "raw_frames": frames if 'frames' in locals() else []
            }
            
            # Run multi-agent pipeline
            agent_results = process_video_analysis(agent_input)
            
            # Run advanced analysis (CoachBot + OracleBot)
            advanced_results = run_advanced_analysis(
                agent_results["cleaned_data"], 
                agent_results["analysis_results"]
            )
            
            # Update critique with agent insights
            raw_critique.update({
                "agent_analysis": agent_results["analysis_results"],
                "coach_recommendations": advanced_results["coach_analysis"],
                "oracle_predictions": advanced_results["oracle_predictions"]
            })
            
            print("[BACKEND] Multi-Agent Processing Complete")
        
        # Use final critique for visualization
        critique = raw_critique
        
        # Log what spatial data we received
        if spatial_data["kill_locations"]:
            print(f"[BACKEND] Received {len(spatial_data['kill_locations'])} kill locations from analysis")
        if spatial_data["player_positions"]:
            print(f"[BACKEND] Received {len(spatial_data['player_positions'])} player positions from analysis")
        if spatial_data["movement_paths"]:
            print(f"[BACKEND] Received {len(spatial_data['movement_paths'])} movement paths from analysis")
        if spatial_data["detected_agents"]:
            print(f"[BACKEND] Detected Agents: {spatial_data['detected_agents']}")
        
        # Transform player_positions into live_coords for the HUD
        live_coords = []
        if spatial_data.get("player_positions"):
            for pos in spatial_data["player_positions"]:
                live_coords.append({
                    "agent": pos.get("agent", "Unknown"),
                    "x": pos.get("x", 0),
                    "y": pos.get("y", 0),
                    "event": pos.get("timestamp", "Live")
                })
        else:
            # Fallback to mock if no positions detected
            live_coords = [
                {"agent": "Jett", "x": 1250, "y": 800, "event": "Entry"},
                {"agent": "Omen", "y": 450, "x": 900, "event": "Smoke"}
            ]

        spatial_payload = {
            "map_id": detected_map,
            "heatmap_url": heatmap_name,
            "trajectories_url": pathing_name,
            "detected_agents": spatial_data.get("detected_agents", []),
            "live_coords": live_coords
        }

        # Trigger High-Fidelity Blueprint Projection with detected map and REAL spatial data
        try:
            BLUEPRINT_MAP = {
                "ASCENT": "blueprints/official/ascent_minimap.png",
                "BIND": "blueprints/official/bind_minimap.png",
                "HAVEN": "blueprints/official/haven_minimap.png",
                "SPLIT": "blueprints/official/split_minimap.png",
                "ICEBOX": "blueprints/official/icebox_minimap.png",
                "BREEZE": "blueprints/official/breeze_minimap.png",
                "FRACTURE": "blueprints/official/fracture_minimap.png",
                "PEARL": "blueprints/official/pearl_minimap.png",
                "LOTUS": "blueprints/official/lotus_minimap.png",
                "SUNSET": "blueprints/official/sunset_minimap.png",
                "ABYSS": "blueprints/official/abyss_minimap.png",
                "DISTRICT": "blueprints/official/district_minimap.png"
            }
            blueprint_path = BLUEPRINT_MAP.get(detected_map)
            
            if blueprint_path and not os.path.exists(blueprint_path):
                print(f"[WARN] Blueprint not found for {detected_map} at {blueprint_path}")
                blueprint_path = None # Fallback to no-blueprint if file doesn't exist yet

            print(f"[BACKEND] Generating live tactical viz for {detected_map} with blueprint: {blueprint_path}")
            generate_pro_viz(
                detected_map, 
                heatmap_name, 
                pathing_name,
                blueprint_path=blueprint_path,
                spatial_data=spatial_data  # Pass REAL gameplay data to visualization
            )
            print(f"[BACKEND] Projected Intelligence synchronization active for {detected_map}")
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

# Setup n8n integration routes
setup_n8n_routes(app)

if __name__ == "__main__":
    # In production, run with uvicorn aurora_backend:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
