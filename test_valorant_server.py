"""
Simple test server for Valorant scraper API
"""

from fastapi import FastAPI
from valorant_scraper_integration import setup_valorant_scraper_routes
import uvicorn

app = FastAPI(title="Valorant Scraper Test Server")

# Setup Valorant scraper routes
setup_valorant_scraper_routes(app)

@app.get("/")
async def root():
    return {"message": "Valorant Scraper Test Server", "status": "running"}

if __name__ == "__main__":
    print("🚀 Starting Valorant Scraper Test Server...")
    print("📊 Available endpoints:")
    print("  GET  /")
    print("  POST /valorant/scrape")
    print("  POST /valorant/player-analysis") 
    print("  GET  /valorant/meta")
    print("  GET  /valorant/matches")
    print("  GET  /valorant/stats")
    print("  GET  /valorant/status")
    print("\n🌐 Server will be available at: http://localhost:8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
