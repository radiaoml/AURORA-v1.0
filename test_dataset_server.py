"""
Test server for enhanced Valorant dataset integration
"""

from fastapi import FastAPI
from valorant_scraper_integration import setup_valorant_scraper_routes
from valorant_dataset_integration import setup_valorant_dataset_routes
import uvicorn

app = FastAPI(title="Enhanced Valorant Dataset Server")

# Setup routes
setup_valorant_scraper_routes(app)
setup_valorant_dataset_routes(app)

@app.get("/")
async def root():
    return {
        "message": "Enhanced Valorant Dataset Server", 
        "status": "running",
        "features": [
            "Live data scraping",
            "Dataset integration", 
            "VOD enhancement",
            "Training data export",
            "Comprehensive analytics"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Enhanced Valorant Dataset Server...")
    print("📊 Available endpoints:")
    
    # List all routes
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            if any(keyword in route.path for keyword in ['valorant', 'dataset']):
                print(f"  {list(route.methods)} {route.path}")
    
    print("\n🌐 Server will be available at: http://localhost:8003")
    
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
