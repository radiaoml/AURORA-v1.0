"""
AURORA Intelligence Integration
Integrates public intelligence data with existing AURORA multi-agent system
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime
from public_intelligence import get_player_intelligence, intelligence_aggregator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligenceRequest(BaseModel):
    """Request model for player intelligence"""
    riot_id: str
    username: Optional[str] = None
    include_patterns: bool = True
    include_meta: bool = True

class EnhancedAnalysisRequest(BaseModel):
    """Enhanced analysis request with player context"""
    source: str
    type: str
    player_riot_id: Optional[str] = None
    player_username: Optional[str] = None
    intelligence_request: Optional[IntelligenceRequest] = None

class IntelligenceEnhancedAnalysis:
    """Enhanced analysis with player intelligence"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    def enhance_analysis_with_intelligence(self, analysis_data: Dict[str, Any], 
                                     player_intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance VOD analysis with player intelligence"""
        if "error" in player_intelligence:
            logger.warning(f"No player intelligence available: {player_intelligence['error']}")
            return analysis_data
        
        profile = player_intelligence.get("profile", {})
        patterns = player_intelligence.get("patterns", {})
        meta_trends = player_intelligence.get("meta_trends", [])
        
        # Enhanced metrics calculation
        enhanced_analysis = {
            **analysis_data,
            "player_context": {
                "rank": profile.get("rank", "Unknown"),
                "tier": profile.get("tier", 0),
                "skill_level": profile.get("skill_level", "Unknown"),
                "main_agents": profile.get("main_agents", []),
                "playstyle": profile.get("playstyle", "Unknown"),
                "win_rate": profile.get("win_rate", 0.0),
                "kd_ratio": profile.get("kd_ratio", 0.0)
            },
            "enhanced_metrics": self.calculate_enhanced_metrics(analysis_data, profile, patterns),
            "personalized_recommendations": self.generate_personalized_recommendations(
                analysis_data, profile, patterns, meta_trends
            ),
            "performance_benchmarks": self.generate_performance_benchmarks(profile, patterns),
            "meta_analysis": self.analyze_meta_relevance(profile, meta_trends)
        }
        
        return enhanced_analysis
    
    def calculate_enhanced_metrics(self, analysis_data: Dict[str, Any], 
                                profile: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate enhanced metrics with player context"""
        base_metrics = analysis_data.get("tactical_metrics", {})
        
        # Rank-adjusted performance scores
        rank_multiplier = self.get_rank_multiplier(profile.get("rank", "Gold"))
        
        enhanced = {
            "rank_adjusted_ovr": base_metrics.get("ovr_score", 50) * rank_multiplier,
            "skill_level_score": self.calculate_skill_level_score(profile),
            "playstyle_efficiency": self.calculate_playstyle_efficiency(
                base_metrics, profile.get("playstyle", "")
            ),
            "agent_mastery_bonus": self.calculate_agent_mastery_bonus(
                base_metrics, profile.get("main_agents", [])
            ),
            "consistency_score": patterns.get("consistency", "Unknown"),
            "adaptability_score": patterns.get("adaptability", "Unknown"),
            "team_contribution": patterns.get("team_contribution", "Unknown"),
            "aggression_level": patterns.get("aggression_level", "Unknown"),
            "improvement_potential": patterns.get("improvement_potential", "Unknown")
        }
        
        return enhanced
    
    def get_rank_multiplier(self, rank: str) -> float:
        """Get rank-based performance multiplier"""
        multipliers = {
            "Iron": 0.8,
            "Bronze": 0.85,
            "Silver": 0.9,
            "Gold": 1.0,
            "Platinum": 1.1,
            "Diamond": 1.2,
            "Immortal": 1.3,
            "Radiant": 1.4
        }
        return multipliers.get(rank, 1.0)
    
    def calculate_skill_level_score(self, profile: Dict[str, Any]) -> float:
        """Calculate skill level score"""
        skill_scores = {
            "Beginner": 20,
            "Intermediate": 40,
            "Advanced": 60,
            "Expert": 80,
            "Professional": 95
        }
        return skill_scores.get(profile.get("skill_level", "Intermediate"), 50)
    
    def calculate_playstyle_efficiency(self, metrics: Dict[str, Any], playstyle: str) -> float:
        """Calculate playstyle efficiency based on metrics"""
        base_score = metrics.get("tactical_efficiency", 50)
        
        # Playstyle-specific adjustments
        if playstyle == "Aggressive":
            # Reward high kills and entry fragging
            kills_bonus = min(metrics.get("kills", 0) * 0.5, 20)
            return min(base_score + kills_bonus, 100)
        elif playstyle == "Supportive":
            # Reward assists and team play
            assists_bonus = min(metrics.get("assists", 0) * 0.8, 15)
            return min(base_score + assists_bonus, 100)
        elif playstyle == "Conservative":
            # Reward survival and K/D ratio
            kd_bonus = min(metrics.get("kd_ratio", 1.0) * 10, 15)
            return min(base_score + kd_bonus, 100)
        else:
            return base_score
    
    def calculate_agent_mastery_bonus(self, metrics: Dict[str, Any], main_agents: List[str]) -> float:
        """Calculate agent mastery bonus"""
        if not main_agents:
            return 0
        
        # Bonus for playing main agents
        current_agent = metrics.get("current_agent", "")
        if current_agent in main_agents:
            return 15  # Significant bonus for main agent
        elif any(agent_type in current_agent for agent_type in ["Jett", "Reyna", "Sova"]):
            return 5  # Small bonus for similar agent type
        
        return 0
    
    def generate_personalized_recommendations(self, analysis_data: Dict[str, Any],
                                        profile: Dict[str, Any],
                                        patterns: Dict[str, Any],
                                        meta_trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on player intelligence"""
        recommendations = []
        
        # Rank-based recommendations
        rank = profile.get("rank", "Gold")
        if rank in ["Iron", "Bronze", "Silver"]:
            recommendations.append({
                "type": "rank_focused",
                "priority": "high",
                "title": "Fundamental Improvement",
                "description": f"Focus on basic mechanics and game sense to reach {self.get_next_rank(rank)}",
                "actions": ["Aim training", "Map knowledge", "Economy management"]
            })
        elif rank in ["Platinum", "Diamond"]:
            recommendations.append({
                "type": "advanced_tactics",
                "priority": "medium",
                "title": "Advanced Strategy",
                "description": f"Develop advanced tactics to compete at {self.get_next_rank(rank)} level",
                "actions": ["Advanced utility usage", "Team coordination", "Counter-strategies"]
            })
        
        # Playstyle-based recommendations
        playstyle = profile.get("playstyle", "")
        if playstyle == "Aggressive" and patterns.get("team_contribution") == "Low":
            recommendations.append({
                "type": "playstyle_adjustment",
                "priority": "medium",
                "title": "Balance Aggression",
                "description": "Consider more team-oriented play to improve win rate",
                "actions": ["Trade fragging", "Support team entries", "Economy consideration"]
            })
        
        # Agent mastery recommendations
        main_agents = profile.get("main_agents", [])
        if len(main_agents) < 2:
            recommendations.append({
                "type": "agent_diversity",
                "priority": "low",
                "title": "Expand Agent Pool",
                "description": "Learn more agents to improve team flexibility",
                "actions": ["Learn 1-2 new agents", "Practice different roles", "Adapt to team needs"]
            })
        
        # Meta-based recommendations
        if meta_trends:
            top_agents = sorted(meta_trends, key=lambda x: x.get("pick_rate", 0), reverse=True)[:3]
            if not any(agent["agent"] in main_agents for agent in top_agents):
                recommendations.append({
                    "type": "meta_awareness",
                    "priority": "medium",
                    "title": "Meta Adaptation",
                    "description": "Consider learning meta agents for competitive advantage",
                    "actions": [f"Practice {agent['agent']}" for agent in top_agents[:2]]
                })
        
        # Improvement potential recommendations
        if patterns.get("improvement_potential") == "High":
            recommendations.append({
                "type": "improvement_focus",
                "priority": "high",
                "title": "High Improvement Potential",
                "description": "You have significant room for improvement with focused practice",
                "actions": ["VOD review", "Targeted practice", "Coaching"]
            })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def get_next_rank(self, current_rank: str) -> str:
        """Get next rank in progression"""
        rank_order = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Immortal", "Radiant"]
        try:
            current_index = rank_order.index(current_rank)
            return rank_order[current_index + 1] if current_index < len(rank_order) - 1 else "Radiant"
        except ValueError:
            return "Gold"
    
    def generate_performance_benchmarks(self, profile: Dict[str, Any], 
                                    patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance benchmarks based on player profile"""
        rank = profile.get("rank", "Gold")
        
        # Rank-based benchmarks
        benchmarks = {
            "Iron": {"kills": 10, "deaths": 15, "assists": 3, "win_rate": 45},
            "Bronze": {"kills": 12, "deaths": 14, "assists": 4, "win_rate": 48},
            "Silver": {"kills": 14, "deaths": 13, "assists": 5, "win_rate": 50},
            "Gold": {"kills": 16, "deaths": 12, "assists": 6, "win_rate": 52},
            "Platinum": {"kills": 18, "deaths": 11, "assists": 7, "win_rate": 54},
            "Diamond": {"kills": 20, "deaths": 10, "assists": 8, "win_rate": 56},
            "Immortal": {"kills": 22, "deaths": 9, "assists": 9, "win_rate": 58},
            "Radiant": {"kills": 25, "deaths": 8, "assists": 10, "win_rate": 60}
        }
        
        rank_benchmarks = benchmarks.get(rank, benchmarks["Gold"])
        
        # Compare with player's recent performance
        recent_matches = profile.get("recent_performance", [])
        if recent_matches:
            avg_kills = sum(match.get("kills", 0) for match in recent_matches) / len(recent_matches)
            avg_deaths = sum(match.get("deaths", 0) for match in recent_matches) / len(recent_matches)
            avg_assists = sum(match.get("assists", 0) for match in recent_matches) / len(recent_matches)
            
            performance_comparison = {
                "kills_above_benchmark": avg_kills - rank_benchmarks["kills"],
                "deaths_below_benchmark": rank_benchmarks["deaths"] - avg_deaths,
                "assists_above_benchmark": avg_assists - rank_benchmarks["assists"],
                "win_rate_above_benchmark": profile.get("win_rate", 0) - rank_benchmarks["win_rate"]
            }
        else:
            performance_comparison = {}
        
        return {
            "rank_benchmarks": rank_benchmarks,
            "performance_comparison": performance_comparison,
            "areas_for_improvement": self.identify_improvement_areas(performance_comparison)
        }
    
    def identify_improvement_areas(self, performance_comparison: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement"""
        areas = []
        
        if performance_comparison.get("kills_above_benchmark", 0) < -2:
            areas.append("Increase kill participation")
        
        if performance_comparison.get("deaths_below_benchmark", 0) < -2:
            areas.append("Reduce deaths - improve positioning")
        
        if performance_comparison.get("assists_above_benchmark", 0) < -1:
            areas.append("Increase team support")
        
        if performance_comparison.get("win_rate_above_benchmark", 0) < -5:
            areas.append("Focus on game impact and decision making")
        
        return areas
    
    def analyze_meta_relevance(self, profile: Dict[str, Any], 
                            meta_trends: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze player's relevance to current meta"""
        main_agents = profile.get("main_agents", [])
        
        if not meta_trends:
            return {"meta_relevance_score": 0, "analysis": "No meta data available"}
        
        # Calculate meta relevance score
        total_pick_rate = sum(trend.get("pick_rate", 0) for trend in meta_trends)
        player_pick_rate = 0
        
        for agent in main_agents:
            for trend in meta_trends:
                if trend.get("agent") == agent:
                    player_pick_rate += trend.get("pick_rate", 0)
        
        meta_relevance_score = (player_pick_rate / total_pick_rate * 100) if total_pick_rate > 0 else 0
        
        # Meta analysis
        if meta_relevance_score > 60:
            meta_analysis = "Strong meta relevance - playing optimal agents"
        elif meta_relevance_score > 30:
            meta_analysis = "Moderate meta relevance - some optimization possible"
        else:
            meta_analysis = "Low meta relevance - consider meta agents for competitive advantage"
        
        recommended_meta_agents = [trend["agent"] for trend in 
                               sorted(meta_trends, key=lambda x: x.get("pick_rate", 0), reverse=True)[:3]]
        
        return {
            "meta_relevance_score": meta_relevance_score,
            "analysis": meta_analysis,
            "recommended_meta_agents": recommended_meta_agents
        }

# Global instance
intelligence_enhancer = IntelligenceEnhancedAnalysis()

def enhance_analysis_with_intelligence(analysis_data: Dict[str, Any], 
                                   riot_id: str = None, 
                                   username: str = None) -> Dict[str, Any]:
    """Enhance analysis with player intelligence"""
    if not riot_id and not username:
        return analysis_data
    
    try:
        player_intelligence = get_player_intelligence(riot_id, username)
        return intelligence_enhancer.enhance_analysis_with_intelligence(analysis_data, player_intelligence)
    except Exception as e:
        logger.error(f"Error enhancing analysis with intelligence: {e}")
        return analysis_data

def setup_intelligence_routes(app: FastAPI):
    """Setup intelligence integration routes"""
    
    @app.post("/intelligence/player", tags=["Player Intelligence"])
    async def get_player_intelligence_endpoint(request: IntelligenceRequest):
        """Get comprehensive player intelligence"""
        try:
            intelligence = get_player_intelligence(request.riot_id, request.username)
            return intelligence
        except Exception as e:
            logger.error(f"Error getting player intelligence: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/intelligence/enhance-analysis", tags=["Player Intelligence"])
    async def enhance_analysis_endpoint(request: EnhancedAnalysisRequest):
        """Enhance VOD analysis with player intelligence"""
        try:
            # Get base analysis (existing logic)
            base_analysis = get_base_analysis(request.source, request.type)
            
            # Enhance with intelligence if player data provided
            if request.player_riot_id or request.player_username:
                enhanced_analysis = enhance_analysis_with_intelligence(
                    base_analysis, request.player_riot_id, request.player_username
                )
                return enhanced_analysis
            else:
                return base_analysis
                
        except Exception as e:
            logger.error(f"Error enhancing analysis: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/intelligence/meta-trends", tags=["Player Intelligence"])
    async def get_meta_trends():
        """Get current meta trends"""
        try:
            trends = intelligence_aggregator.get_meta_trends()
            return {"meta_trends": trends}
        except Exception as e:
            logger.error(f"Error getting meta trends: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/intelligence/patterns/{riot_id}", tags=["Player Intelligence"])
    async def get_player_patterns(riot_id: str):
        """Get player behavior patterns"""
        try:
            patterns = intelligence_aggregator.analyze_player_patterns(riot_id)
            return {"patterns": patterns}
        except Exception as e:
            logger.error(f"Error getting player patterns: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/intelligence/status", tags=["Player Intelligence"])
    async def get_intelligence_status():
        """Get intelligence system status"""
        return {
            "status": "active",
            "data_sources": ["public_aggregation", "ai_synthesis", "pattern_analysis"],
            "cache_enabled": True,
            "supported_features": [
                "player_profiles",
                "behavior_patterns",
                "meta_trends",
                "performance_benchmarks",
                "personalized_recommendations"
            ]
        }

def get_base_analysis(source: str, analysis_type: str) -> Dict[str, Any]:
    """Get base analysis (placeholder for existing logic)"""
    # This would integrate with your existing analysis system
    return {
        "source": source,
        "type": analysis_type,
        "tactical_metrics": {
            "ovr_score": 60,
            "tactical_efficiency": 75,
            "kills": 18,
            "deaths": 12,
            "assists": 6,
            "kd_ratio": 1.5,
            "current_agent": "Jett"
        },
        "analysis_timestamp": datetime.now().isoformat()
    }
