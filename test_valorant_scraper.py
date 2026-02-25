"""
Simple test for Valorant scraper functionality
"""

from valorant_scraper import ValorantDataScraper
from valorant_scraper_integration import ValorantScraperIntegration
import asyncio

async def test_scraper():
    print("🔍 Testing Valorant Scraper...")
    
    # Test basic scraper
    scraper = ValorantDataScraper()
    print("✅ Basic scraper initialized")
    
    # Test database freshness
    freshness = scraper.get_data_freshness()
    print(f"📊 Database freshness: {freshness}")
    
    scraper.close()
    
    # Test integration
    integration = ValorantScraperIntegration()
    print("✅ Integration initialized")
    
    # Test status endpoint
    status = integration.get_database_stats()
    print(f"📈 Integration stats: {status}")
    
    print("🎉 All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_scraper())
