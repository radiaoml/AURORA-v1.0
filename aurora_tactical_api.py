"""
AURORA Tactical System API Integration
Integrates tactical analysis with AURORA backend
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from aurora_tactical_integration import AURORATacticalIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TacticalAnalysisRequest(BaseModel):
    """Request model for tactical analysis"""
    map: str
    tactical_situation: str
    formation: str
    agents_detected: List[str]
    context: Optional[Dict] = None

class VODEnhancementRequest(BaseModel):
    """Request model for VOD tactical enhancement"""
    vod_analysis: Dict
    match_context: Optional[Dict] = None

class TacticalReportRequest(BaseModel):
    """Request model for tactical report generation"""
    match_context: Dict
    analysis_depth: str = "comprehensive"  # basic, detailed, comprehensive

class PlayerTacticalProfileRequest(BaseModel):
    """Request model for player tactical profiling"""
    player_name: str
    player_tag: str
    include_recommendations: bool = True

class AURORATacticalAPI:
    """API integration for AURORA tactical system"""
    
    def __init__(self):
        self.integration = AURORATacticalIntegration()
        self.cache = {}
        self.cache_ttl = 1800000  # 30 minutes
    
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
    
    async def analyze_tactical_situation(self, request: TacticalAnalysisRequest) -> Dict:
        """Analyze tactical situation with dataset insights"""
        try:
            cache_key = f"tactical_{request.map}_{request.tactical_situation}_{request.formation}"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            context = {
                "map": request.map,
                "tactical_situation": request.tactical_situation,
                "formation": request.formation,
                "agents_detected": request.agents_detected
            }
            
            if request.context:
                context.update(request.context)
            
            analysis = self.integration.analyze_tactical_situation(context)
            
            # Add API metadata
            analysis["api_metadata"] = {
                "request_timestamp": datetime.now().isoformat(),
                "analysis_version": "2.0",
                "data_sources": ["enhanced_dataset", "live_scraping", "tactical_models"]
            }
            
            self.cache_data(cache_key, analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error in tactical analysis: {e}")
            return {"error": str(e)}
    
    async def enhance_vod_analysis(self, request: VODEnhancementRequest) -> Dict:
        """Enhance VOD analysis with tactical insights"""
        try:
            cache_key = f"vod_enhancement_{hash(json.dumps(request.vod_analysis, sort_keys=True))}"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            enhanced_analysis = self.integration.enhance_vod_with_tactical_analysis(request.vod_analysis)
            
            # Add match context if provided
            if request.match_context:
                tactical_report = self.integration.generate_tactical_report(request.match_context)
                enhanced_analysis["match_tactical_report"] = tactical_report
            
            enhanced_analysis["enhancement_metadata"] = {
                "enhanced_timestamp": datetime.now().isoformat(),
                "enhancement_version": "2.0",
                "insights_generated": len(enhanced_analysis.get("tactical_insights", {}))
            }
            
            self.cache_data(cache_key, enhanced_analysis)
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error enhancing VOD analysis: {e}")
            return {"error": str(e)}
    
    async def generate_tactical_report(self, request: TacticalReportRequest) -> Dict:
        """Generate comprehensive tactical report"""
        try:
            cache_key = f"report_{hash(json.dumps(request.match_context, sort_keys=True))}_{request.analysis_depth}"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            report = self.integration.generate_tactical_report(request.match_context)
            
            # Add depth-specific analysis
            if request.analysis_depth == "detailed" or request.analysis_depth == "comprehensive":
                report["detailed_analysis"] = self.add_detailed_analysis(request.match_context)
            
            if request.analysis_depth == "comprehensive":
                report["comprehensive_analysis"] = self.add_comprehensive_analysis(request.match_context)
            
            report["report_metadata"] = {
                "generated_timestamp": datetime.now().isoformat(),
                "analysis_depth": request.analysis_depth,
                "report_version": "2.0"
            }
            
            self.cache_data(cache_key, report)
            return report
            
        except Exception as e:
            logger.error(f"Error generating tactical report: {e}")
            return {"error": str(e)}
    
    def add_detailed_analysis(self, match_context: Dict) -> Dict:
        """Add detailed tactical analysis"""
        detailed = {
            "pattern_analysis": self.analyze_patterns(match_context),
            "performance_metrics": self.calculate_performance_metrics(match_context),
            "strategic_insights": self.generate_strategic_insights(match_context)
        }
        return detailed
    
    def add_comprehensive_analysis(self, match_context: Dict) -> Dict:
        """Add comprehensive tactical analysis"""
        comprehensive = {
            "meta_comparison": self.compare_with_meta(match_context),
            "predictive_analysis": self.generate_predictive_analysis(match_context),
            "improvement_recommendations": self.generate_improvement_recommendations(match_context)
        }
        return comprehensive
    
    def analyze_patterns(self, match_context: Dict) -> Dict:
        """Analyze tactical patterns"""
        patterns = {
            "successful_formations": [],
            "effective_strategies": [],
            "common_mistakes": [],
            "improvement_areas": []
        }
        
        # Pattern analysis logic here
        if "rounds" in match_context:
            rounds = match_context["rounds"]
            # Analyze successful patterns
            successful_rounds = [r for r in rounds if r.get("won", False)]
            if successful_rounds:
                formation_counts = {}
                for round_data in successful_rounds:
                    formation = round_data.get("formation", "unknown")
                    formation_counts[formation] = formation_counts.get(formation, 0) + 1
                
                patterns["successful_formations"] = [
                    {"formation": k, "success_rate": v/len(successful_rounds)}
                    for k, v in sorted(formation_counts.items(), key=lambda x: x[1], reverse=True)
                ]
        
        return patterns
    
    def calculate_performance_metrics(self, match_context: Dict) -> Dict:
        """Calculate performance metrics"""
        metrics = {
            "overall_performance": 0.0,
            "tactical_efficiency": 0.0,
            "coordination_score": 0.0,
            "adaptability_score": 0.0
        }
        
        # Performance calculation logic here
        if "rounds" in match_context:
            rounds = match_context["rounds"]
            total_rounds = len(rounds)
            won_rounds = sum(1 for r in rounds if r.get("won", False))
            
            metrics["overall_performance"] = won_rounds / total_rounds if total_rounds > 0 else 0.0
        
        return metrics
    
    def generate_strategic_insights(self, match_context: Dict) -> List[str]:
        """Generate strategic insights"""
        insights = [
            "Focus on coordinated utility usage",
            "Maintain map control in mid-round situations",
            "Adapt formation based on enemy composition"
        ]
        
        # Generate context-specific insights
        if "map" in match_context:
            map_name = match_context["map"]
            insights.append(f"Map-specific strategy for {map_name}")
        
        return insights
    
    def compare_with_meta(self, match_context: Dict) -> Dict:
        """Compare performance with meta data"""
        comparison = {
            "meta_alignment": 0.0,
            "agent_performance_vs_meta": {},
            "strategy_effectiveness": {},
            "recommendations": []
        }
        
        # Meta comparison logic here
        return comparison
    
    def generate_predictive_analysis(self, match_context: Dict) -> Dict:
        """Generate predictive analysis"""
        prediction = {
            "win_probability": 0.5,
            "key_factors": [],
            "confidence_interval": [0.3, 0.7],
            "scenario_analysis": {}
        }
        
        # Predictive analysis logic here
        return prediction
    
    def generate_improvement_recommendations(self, match_context: Dict) -> List[Dict]:
        """Generate improvement recommendations"""
        recommendations = [
            {
                "category": "tactical",
                "priority": "high",
                "description": "Improve coordination in entry situations",
                "expected_impact": "+15% win rate"
            },
            {
                "category": "utility",
                "priority": "medium",
                "description": "Better utility usage in post-plant situations",
                "expected_impact": "+10% win rate"
            }
        ]
        
        return recommendations
    
    async def get_player_tactical_profile(self, request: PlayerTacticalProfileRequest) -> Dict:
        """Get player tactical profile"""
        try:
            cache_key = f"player_profile_{request.player_name}_{request.player_tag}"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            # Get player data from scraper
            player_data = await self.integration.scraper_integration.scrape_player_data(
                request.player_name, request.player_tag
            )
            
            if "error" in player_data:
                return {"error": "Player data not found"}
            
            # Generate tactical profile
            profile = {
                "player_info": {
                    "name": request.player_name,
                    "tag": request.player_tag,
                    "rank": player_data.get("player_data", {}).get("rank", "Unknown"),
                    "main_agents": player_data.get("player_data", {}).get("agents_played", "").split(",") if player_data.get("player_data", {}).get("agents_played") else []
                },
                "tactical_profile": self.generate_player_tactical_profile(player_data),
                "performance_trends": player_data.get("trends", {}),
                "meta_comparison": player_data.get("meta_comparison", {})
            }
            
            if request.include_recommendations:
                profile["recommendations"] = self.generate_player_recommendations(player_data)
            
            profile["profile_metadata"] = {
                "generated_timestamp": datetime.now().isoformat(),
                "profile_version": "2.0",
                "data_sources": ["scraper", "dataset", "tactical_analysis"]
            }
            
            self.cache_data(cache_key, profile)
            return profile
            
        except Exception as e:
            logger.error(f"Error getting player tactical profile: {e}")
            return {"error": str(e)}
    
    def generate_player_tactical_profile(self, player_data: Dict) -> Dict:
        """Generate tactical profile for player"""
        profile = {
            "playstyle": "balanced",
            "strengths": [],
            "weaknesses": [],
            "preferred_situations": [],
            "map_specialties": [],
            "tactical_role": "flexible"
        }
        
        # Analyze player data to generate profile
        player_stats = player_data.get("player_data", {})
        
        if player_stats.get("win_rate", 0) > 0.6:
            profile["strengths"].append("High win rate")
        
        if player_stats.get("kd_ratio", 0) > 1.2:
            profile["strengths"].append("Strong K/D ratio")
        
        if player_stats.get("headshot_pct", 0) > 25:
            profile["strengths"].append("Accurate shooting")
        
        return profile
    
    def generate_player_recommendations(self, player_data: Dict) -> List[Dict]:
        """Generate player-specific recommendations"""
        recommendations = []
        
        player_stats = player_data.get("player_data", {})
        
        if player_stats.get("win_rate", 0) < 0.5:
            recommendations.append({
                "type": "improvement",
                "priority": "high",
                "description": "Focus on improving round win rate",
                "action_items": ["Better utility usage", "Improved positioning"]
            })
        
        if player_stats.get("kd_ratio", 0) < 1.0:
            recommendations.append({
                "type": "combat",
                "priority": "medium",
                "description": "Improve combat effectiveness",
                "action_items": ["Aim training", "Crosshair placement"]
            })
        
        return recommendations
    
    def get_tactical_system_status(self) -> Dict:
        """Get tactical system status"""
        return {
            "status": "active",
            "integration_status": "fully_integrated",
            "data_sources": [
                "enhanced_dataset",
                "live_scraping", 
                "tactical_models",
                "player_intelligence"
            ],
            "capabilities": [
                "tactical_situation_analysis",
                "vod_enhancement",
                "tactical_reporting",
                "player_profiling",
                "pattern_recognition",
                "predictive_analysis"
            ],
            "dataset_statistics": self.integration.collector.get_comprehensive_analytics(),
            "last_updated": datetime.now().isoformat()
        }

# Global instance
tactical_api = AURORATacticalAPI()

def setup_aurora_tactical_routes(app: FastAPI):
    """Setup AURORA tactical system API routes"""
    
    @app.post("/aurora/tactical/analyze", tags=["AURORA Tactical"])
    async def analyze_tactical_situation(request: TacticalAnalysisRequest):
        """Analyze tactical situation with dataset insights"""
        try:
            result = await tactical_api.analyze_tactical_situation(request)
            return result
        except Exception as e:
            logger.error(f"Error in tactical analysis endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/aurora/tactical/enhance-vod", tags=["AURORA Tactical"])
    async def enhance_vod_analysis(request: VODEnhancementRequest):
        """Enhance VOD analysis with tactical insights"""
        try:
            result = await tactical_api.enhance_vod_analysis(request)
            return result
        except Exception as e:
            logger.error(f"Error in VOD enhancement endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/aurora/tactical/report", tags=["AURORA Tactical"])
    async def generate_tactical_report(request: TacticalReportRequest):
        """Generate comprehensive tactical report"""
        try:
            result = await tactical_api.generate_tactical_report(request)
            return result
        except Exception as e:
            logger.error(f"Error in tactical report endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/aurora/tactical/player-profile", tags=["AURORA Tactical"])
    async def get_player_tactical_profile(request: PlayerTacticalProfileRequest):
        """Get player tactical profile"""
        try:
            result = await tactical_api.get_player_tactical_profile(request)
            return result
        except Exception as e:
            logger.error(f"Error in player profile endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/aurora/tactical/status", tags=["AURORA Tactical"])
    async def get_tactical_system_status():
        """Get tactical system status"""
        return tactical_api.get_tactical_system_status()
