import pandas as pd
import visualizer
import json
import aurora_advisor
import riot_auth_engine
import os

def simulate_api_metadata():
    """Simulates the type of metadata we would get from VAL-MATCH-V1 and ACCOUNT-V1."""
    metadata = {
        "match_info": {
            "match_id": "VAL-12345-PRO-SUMMIT",
            "map": "Ascent",
            "mode": "Competitive",
            "date": "2026-02-16"
        },
        "teams": {
            "ATK": ["Player_1", "Player_2", "Player_3", "Player_4", "Player_5"],
            "DEF": ["Player_6", "Player_7", "Player_8", "Player_9", "Player_10"]
        },
        "round_results": [
            {"round_id": 1, "winner": "ATK", "win_type": "Elimination"},
            {"round_id": 2, "winner": "DEF", "win_type": "Bomb Defused"}
        ]
    }
    return metadata

def run_dashboard_pipeline():
    print("\n--- AURORA MASTER DASHBOARD PIPELINE ---")
    
    # 1. Simulate API Data Ingestion
    print("[1/4] Fetching match metadata from Riot APIs...")
    api_data = simulate_api_metadata()
    with open('match_metadata.json', 'w') as f:
        json.dump(api_data, f, indent=4)
    print(f"      Match ID: {api_data['match_info']['match_id']} loaded.")
    
    # 2. Synchronize with Tactical Data (CV extracted)
    print("[2/4] Synchronizing with Computer Vision coordinate data...")
    if not os.path.exists('gameplay_data.csv'):
        print("      Error: gameplay_data.csv not found. Run generate_mock_data.py first.")
        return
        
    df = pd.read_csv('gameplay_data.csv')
    print(f"      Found {len(df)} tactical events to process.")

    # 3. Generate Visual Reports
    print("[3/5] Generating professional visual reports...")
    visualizer.create_visualizations('gameplay_data.csv')
    
    # 4. Authenticate Identity & Harvest Personal Data (New Phase 6)
    print("[4/5] Connecting to Riot Identity Services...")
    profile = riot_auth_engine.authenticate_riot_id("RadiantPlayer", "TOP1")
    if profile:
        riot_auth_engine.harvest_personal_metrics(profile)
    
    # 5. Run Decision Intelligence Advisor (Identity-Aware)
    print("[5/5] Activating AURORA Decision Intelligence Advisor...")
    advisor_file = aurora_advisor.generate_recommendations()
    print(f"      Recommendations generated in {advisor_file}")
    
    # Final Summary
    print("\n--- DASHBOARD DEPLOYMENT COMPLETE ---")
    print(f"Map: {api_data['match_info']['map']}")
    print("Assets Optimized:")
    print(" - match_metadata.json (Riot API)")
    print(" - tactical_kill_heatmap.png (CV Analysis)")
    print(" - round_1_trajectories.png (CV Analysis)")
    print(" - advisor_recommendations.json (LLM Reasoning)")
    print("--------------------------------------")

if __name__ == "__main__":
    run_dashboard_pipeline()
