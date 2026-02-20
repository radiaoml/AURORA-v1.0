from video_analyzer import TacticalVisionEngine
import os

# Test with a known YouTube video (short one preferably, or just first few seconds)
TEST_URL = "https://youtu.be/-8F_oh" 

print(f"--- STARTING STANDALONE TEST FOR: {TEST_URL} ---")

try:
    # 1. Initialize Engine
    print("[1] Initializing Engine...")
    engine = TacticalVisionEngine(TEST_URL)
    print(f"    - Is URL: {engine.is_url}")
    print(f"    - Source: {engine.source}")
    
    # 2. Extract Frames
    print("[2] Extracting Frames...")
    frames, meta = engine.extract_tactical_frames(fps_sample=1)
    
    print(f"    - Extracted {len(frames)} frames")
    print(f"    - Meta: {meta}")
    
    if len(frames) > 0:
        print(f"    - First frame: {frames[0]}")
        if os.path.exists(frames[0]):
            print("    - [PASS] Frame file exists on disk")
        else:
            print("    - [FAIL] Frame file MISSING on disk")
    else:
        print("    - [FAIL] No frames extracted")

except Exception as e:
    print(f"!!! TEST FAILED WITH ERROR: {e}")
    import traceback
    traceback.print_exc()

print("--- TEST COMPLETE ---")
