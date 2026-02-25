import asyncio
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from aurora_backend import analyze_vod, AnalysisRequest

async def test_demo_integration():
    print("Testing Backend Demo Integration...")
    req = AnalysisRequest(source="demo_test", type="demo")
    
    try:
        result = await analyze_vod(req)
        
        spatial = result.get("spatial_data", {})
        agents = spatial.get("detected_agents", [])
        
        print(f"[TEST] Status: {result.get('status')}")
        print(f"[TEST] Detected Agents: {agents}")
        
        # Check if agents we added to demo data are present
        if "JETT" in agents and "OMEN" in agents:
            print("[TEST] SUCCESS: Detected agents found in response")
        else:
            print("[TEST] FAILURE: Expected agents not found")
            exit(1)
            
        # Check live coords
        live_coords = spatial.get("live_coords", [])
        print(f"[TEST] Live Coords Count: {len(live_coords)}")
        
        if len(live_coords) > 0:
            print("[TEST] SUCCESS: Live Coords populated")
        else:
             print("[TEST] FAILURE: Live Coords missing")
             exit(1)
             
    except Exception as e:
        print(f"[TEST] EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    asyncio.run(test_demo_integration())
