"""
Complete AURORA Tactical System Test Server
Integrates all components: data collection, scraping, tactical analysis
"""

from fastapi import FastAPI
from valorant_scraper_integration import setup_valorant_scraper_routes
from valorant_dataset_integration import setup_valorant_dataset_routes
from aurora_tactical_api import setup_aurora_tactical_routes
import uvicorn

app = FastAPI(title="Complete AURORA Tactical System")

# Setup all routes
setup_valorant_scraper_routes(app)
setup_valorant_dataset_routes(app)
setup_aurora_tactical_routes(app)

@app.get("/")
async def root():
    return {
        "message": "Complete AURORA Tactical System", 
        "status": "fully_operational",
        "components": {
            "data_scraper": "active",
            "dataset_integration": "active", 
            "tactical_analysis": "active",
            "intelligence_system": "active"
        },
        "features": [
            "Live Valorant data scraping",
            "Enhanced dataset integration",
            "Tactical situation analysis",
            "VOD enhancement with insights",
            "Player profiling",
            "Meta trend analysis",
            "Predictive analytics",
            "Strategic recommendations"
        ]
    }

@app.get("/system/overview")
async def system_overview():
    """Get complete system overview"""
    return {
        "system_status": "fully_integrated",
        "data_sources": {
            "existing_dataset": "200 annotations",
            "live_scraping": "tracker.gg, blitz.gg, vct.gg",
            "vod_analysis": "enhanced with tactical insights",
            "player_intelligence": "real-time profiling"
        },
        "analytics_capabilities": {
            "tactical_analysis": "situation-based recommendations",
            "pattern_recognition": "historical success patterns",
            "meta_comparison": "current meta alignment",
            "predictive modeling": "win probability forecasting"
        },
        "integration_points": {
            "aurora_backend": "fully integrated",
            "n8n_workflows": "automation ready",
            "frontend_hud": "real-time display",
            "ml_training": "dataset export ready"
        },
        "performance_metrics": {
            "total_data_points": "400+ enhanced samples",
            "map_coverage": "10 competitive maps",
            "tactical_situations": "8 scenarios",
            "agent_coverage": "23 agents"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Complete AURORA Tactical System...")
    print("📊 Available endpoints:")
    
    # List all routes
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            if any(keyword in route.path for keyword in ['valorant', 'aurora', 'dataset', 'tactical']):
                print(f"  {list(route.methods)} {route.path}")
    
    print("\n🌐 System will be available at: http://localhost:8004")
    print("🎯 Features:")
    print("  • Live Valorant data scraping")
    print("  • Enhanced dataset integration")
    print("  • Tactical situation analysis")
    print("  • VOD enhancement with insights")
    print("  • Player profiling and recommendations")
    print("  • Meta trend analysis")
    print("  • Predictive analytics")
    
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")
