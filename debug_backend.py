"""
Debug startup for AURORA backend with Valorant scraper
"""

import sys
import os
sys.path.insert(0, '.')

print("🔍 Debug: Starting AURORA backend...")

try:
    print("📦 Importing FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported")
    
    print("📦 Importing valorant scraper integration...")
    from valorant_scraper_integration import setup_valorant_scraper_routes
    print("✅ Valorant scraper integration imported")
    
    print("🏗️ Creating FastAPI app...")
    app = FastAPI(title="AURORA Neural Backend Debug")
    print("✅ FastAPI app created")
    
    print("🔧 Setting up valorant routes...")
    setup_valorant_scraper_routes(app)
    print("✅ Valorant routes setup complete")
    
    print("📋 Checking routes...")
    valorant_routes = [route for route in app.routes if 'valorant' in route.path]
    print(f"📊 Found {len(valorant_routes)} valorant routes:")
    for route in valorant_routes:
        print(f"  {route.path} - {list(route.methods)}")
    
    print("🚀 Starting server on port 8002...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
