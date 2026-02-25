"""
AURORA Valorant Scraper Integration
Integrates Valorant data scraping with AURORA backend
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from valorant_scraper import ValorantDataScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapeRequest(BaseModel):
    """Request model for scraping operations"""
    player_name: Optional[str] = None
    player_tag: Optional[str] = None
    scrape_type: str = "full"  # full, player, meta, matches

class PlayerAnalysisRequest(BaseModel):
    """Request model for player analysis"""
    player_name: str
    player_tag: str
    include_trends: bool = True

class ValorantScraperIntegration:
    """Integration layer for Valorant scraping"""
    
    def __init__(self):
        self.scraper = ValorantDataScraper()
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if fresh"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        return None
    
    def cache_data(self, cache_key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[cache_key] = (data, datetime.now().timestamp())
    
    async def scrape_player_data(self, player_name: str, player_tag: str) -> Dict:
        """Scrape and analyze player data"""
        try:
            cache_key = f"player_{player_name}_{player_tag}"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            # Scrape player data
            player_data = self.scraper.scrape_tracker_gg_player(player_name, player_tag)
            
            if not player_data:
                return {"error": "Player data not found"}
            
            # Get trends
            trends = self.scraper.analyze_player_trends(player_name, player_tag)
            
            # Get meta comparison
            agent_meta = self.scraper.get_agent_meta()
            player_agents = player_data.get('agents_played', '').split(',')
            
            meta_comparison = {
                "player_agents": [agent.strip() for agent in player_agents if agent.strip()],
                "agent_performance": self.get_agent_performance(player_agents, agent_meta),
                "meta_relevance": self.calculate_meta_relevance(player_agents, agent_meta)
            }
            
            result = {
                "player_data": player_data,
                "trends": trends,
                "meta_comparison": meta_comparison,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            self.cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error scraping player data: {e}")
            return {"error": str(e)}
    
    def get_agent_performance(self, player_agents: List[str], agent_meta: List[Dict]) -> Dict:
        """Get performance data for player's agents"""
        performance = {}
        
        for agent in player_agents:
            for meta in agent_meta:
                if meta['agent_name'].lower() == agent.lower():
                    performance[agent] = {
                        "pick_rate": meta['pick_rate'],
                        "win_rate": meta['win_rate'],
                        "kd_average": meta['kd_average'],
                        "role": meta['role']
                    }
                    break
        
        return performance
    
    def calculate_meta_relevance(self, player_agents: List[str], agent_meta: List[Dict]) -> Dict:
        """Calculate how well player's agents align with meta"""
        if not agent_meta:
            return {"score": 0, "analysis": "No meta data available"}
        
        # Get top meta agents
        top_agents = sorted(agent_meta, key=lambda x: x['pick_rate'], reverse=True)[:10]
        top_agent_names = [agent['agent_name'].lower() for agent in top_agents]
        
        # Calculate relevance
        player_agent_names = [agent.lower() for agent in player_agents]
        matching_agents = set(player_agent_names) & set(top_agent_names)
        
        relevance_score = (len(matching_agents) / len(player_agent_names)) * 100 if player_agent_names else 0
        
        if relevance_score > 70:
            analysis = "Strong meta alignment"
        elif relevance_score > 40:
            analysis = "Moderate meta alignment"
        else:
            analysis = "Low meta alignment - consider meta agents"
        
        return {
            "score": relevance_score,
            "analysis": analysis,
            "matching_agents": list(matching_agents),
            "recommended_agents": top_agent_names[:3]
        }
    
    async def scrape_meta_data(self) -> Dict:
        """Scrape current meta data"""
        try:
            cache_key = "meta_data"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            # Scrape meta data
            meta_data = self.scraper.scrape_blitz_gg_meta()
            
            # Generate analysis
            report = self.scraper.generate_meta_report()
            
            result = {
                "agent_meta": meta_data,
                "meta_report": report,
                "scrape_timestamp": datetime.now().isoformat()
            }
            
            self.cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error scraping meta data: {e}")
            return {"error": str(e)}
    
    async def scrape_match_data(self) -> Dict:
        """Scrape recent match data"""
        try:
            cache_key = "match_data"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            # Scrape match data
            match_data = self.scraper.scrape_vct_matches()
            
            # Analyze matches
            analysis = self.analyze_matches(match_data)
            
            result = {
                "match_data": match_data,
                "match_analysis": analysis,
                "scrape_timestamp": datetime.now().isoformat()
            }
            
            self.cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error scraping match data: {e}")
            return {"error": str(e)}
    
    def analyze_matches(self, match_data: List[Dict]) -> Dict:
        """Analyze scraped match data"""
        if not match_data:
            return {"error": "No match data available"}
        
        # Map analysis
        map_stats = {}
        for match in match_data:
            map_name = match.get('map_name', 'Unknown')
            if map_name not in map_stats:
                map_stats[map_name] = {
                    'count': 0,
                    'total_duration': 0,
                    'scores': []
                }
            map_stats[map_name]['count'] += 1
            map_stats[map_name]['total_duration'] += match.get('duration', 0)
            
            score = match.get('score', '')
            if score:
                map_stats[map_name]['scores'].append(score)
        
        # Calculate averages
        for map_name, stats in map_stats.items():
            stats['average_duration'] = stats['total_duration'] / stats['count'] if stats['count'] > 0 else 0
        
        # Agent analysis from matches
        agent_stats = {}
        for match in match_data:
            try:
                player_stats = json.loads(match.get('player_stats', '[]'))
                for player in player_stats:
                    agent = player.get('agent', '')
                    if agent:
                        if agent not in agent_stats:
                            agent_stats[agent] = {
                                'total_kills': 0,
                                'total_deaths': 0,
                                'total_assists': 0,
                                'matches': 0
                            }
                        agent_stats[agent]['total_kills'] += player.get('kills', 0)
                        agent_stats[agent]['total_deaths'] += player.get('deaths', 0)
                        agent_stats[agent]['total_assists'] += player.get('assists', 0)
                        agent_stats[agent]['matches'] += 1
            except:
                continue
        
        # Calculate agent averages
        for agent, stats in agent_stats.items():
            if stats['matches'] > 0:
                stats['average_kills'] = stats['total_kills'] / stats['matches']
                stats['average_deaths'] = stats['total_deaths'] / stats['matches']
                stats['average_assists'] = stats['total_assists'] / stats['matches']
                stats['kd_ratio'] = stats['total_kills'] / max(stats['total_deaths'], 1)
        
        return {
            "map_statistics": map_stats,
            "agent_statistics": agent_stats,
            "total_matches": len(match_data),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def run_full_scrape(self) -> Dict:
        """Run complete scraping cycle"""
        try:
            logger.info("Starting full Valorant data scrape...")
            
            # Run full scrape
            report = self.scraper.run_full_scrape()
            
            # Get additional analysis
            meta_data = await self.scrape_meta_data()
            match_data = await self.scrape_match_data()
            
            result = {
                "scrape_report": report,
                "meta_data": meta_data,
                "match_data": match_data,
                "full_scrape_timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in full scrape: {e}")
            return {"error": str(e)}
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            cursor = self.scraper.db_conn.cursor()
            
            # Count records in each table
            cursor.execute("SELECT COUNT(*) FROM player_stats")
            player_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM agent_meta")
            agent_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM match_data")
            match_count = cursor.fetchone()[0]
            
            # Get data freshness
            freshness = self.scraper.get_data_freshness()
            
            return {
                "database_stats": {
                    "player_records": player_count,
                    "agent_records": agent_count,
                    "match_records": match_count
                },
                "data_freshness": freshness,
                "stats_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}

# Global instance
scraper_integration = ValorantScraperIntegration()

def setup_valorant_scraper_routes(app: FastAPI):
    """Setup Valorant scraper API routes"""
    
    @app.post("/valorant/scrape", tags=["Valorant Scraper"])
    async def scrape_valorant_data(request: ScrapeRequest):
        """Main scraping endpoint"""
        try:
            if request.scrape_type == "full":
                result = await scraper_integration.run_full_scrape()
            elif request.scrape_type == "player" and request.player_name and request.player_tag:
                result = await scraper_integration.scrape_player_data(request.player_name, request.player_tag)
            elif request.scrape_type == "meta":
                result = await scraper_integration.scrape_meta_data()
            elif request.scrape_type == "matches":
                result = await scraper_integration.scrape_match_data()
            else:
                raise HTTPException(status_code=400, detail="Invalid scrape type or missing parameters")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in scrape endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/valorant/player-analysis", tags=["Valorant Scraper"])
    async def analyze_player(request: PlayerAnalysisRequest):
        """Analyze specific player"""
        try:
            result = await scraper_integration.scrape_player_data(
                request.player_name, 
                request.player_tag
            )
            
            if "error" in result:
                raise HTTPException(status_code=404, detail=result["error"])
            
            return result
            
        except Exception as e:
            logger.error(f"Error in player analysis: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/valorant/meta", tags=["Valorant Scraper"])
    async def get_meta_data():
        """Get current meta data"""
        try:
            result = await scraper_integration.scrape_meta_data()
            return result
        except Exception as e:
            logger.error(f"Error getting meta data: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/valorant/matches", tags=["Valorant Scraper"])
    async def get_match_data():
        """Get recent match data"""
        try:
            result = await scraper_integration.scrape_match_data()
            return result
        except Exception as e:
            logger.error(f"Error getting match data: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/valorant/stats", tags=["Valorant Scraper"])
    async def get_database_statistics():
        """Get database statistics"""
        try:
            result = scraper_integration.get_database_stats()
            return result
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/valorant/status", tags=["Valorant Scraper"])
    async def get_scraper_status():
        """Get scraper system status"""
        return {
            "status": "active",
            "data_sources": ["tracker.gg", "blitz.gg", "vct.gg"],
            "cache_enabled": True,
            "database": "SQLite",
            "supported_operations": [
                "player_scraping",
                "meta_analysis",
                "match_scraping",
                "trend_analysis",
                "full_scrape"
            ],
            "last_update": datetime.now().isoformat()
        }
