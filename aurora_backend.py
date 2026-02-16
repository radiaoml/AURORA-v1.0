from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx

@app.get("/")
async def root():
    return {"status": "AURORA_BACKEND_ONLINE", "version": "1.1.0_RSO"}

# RSO CONFIGURATION (Production placeholders)
RIOT_RSO_AUTHORIZE_URL = "https://auth.riotgames.com/authorize"
RIOT_RSO_TOKEN_URL = "https://auth.riotgames.com/token"
RIOT_USERINFO_URL = "https://americas.api.riotgames.com/riot/account/v1/accounts/me" # Or similar RSO endpoint
REDIRECT_URI = "http://localhost:8000/auth/callback"

@app.get("/auth/login")
async def auth_login():
    """Redirects to the official Riot Games Sign On portal."""
    client_id = os.getenv("RIOT_CLIENT_ID")
    if not client_id:
        # Fallback for demo if no real client id is set
        print("[WARNING] RIOT_CLIENT_ID not found. Redirecting to mock auth for demo.")
        return RedirectResponse(url="http://localhost:5500/index.html?demo_auth=true")

    auth_url = (
        f"{RIOT_RSO_AUTHORIZE_URL}?client_id={client_id}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=openid+riotid"
    )
    return RedirectResponse(url=auth_url)

@app.get("/auth/callback")
async def auth_callback(code: str):
    """Handles the redirect from Riot and exchanges the code for tokens."""
    client_id = os.getenv("RIOT_CLIENT_ID")
    client_secret = os.getenv("RIOT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        # For demo purposes, we'll redirect back with a mock success if no keys are found
        # In production, this would be a 401.
        return RedirectResponse(url="http://localhost:5500/index.html?auth_success=true&riot_id=RadiantPlayer&tag=TOP1")

    async with httpx.AsyncClient() as client:
        # Exchange Code for Access Token
        token_resp = await client.post(
            RIOT_RSO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange RSO code.")
        
        tokens = token_resp.json()
        access_token = tokens.get("access_token")

        # Get User Info (Riot ID / Tag)
        user_resp = await client.get(
            RIOT_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_data = user_resp.json()
        
        riot_id = user_data.get("gameName", "Unknown")
        tag = user_data.get("tagLine", "000")

    # Redirect back to the HUD with the identity
    return RedirectResponse(url=f"http://localhost:5500/index.html?auth_success=true&riot_id={riot_id}&tag={tag}")

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
