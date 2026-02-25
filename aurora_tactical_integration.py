"""
AURORA Tactical System Integration
Integrates enhanced Valorant dataset with tactical analysis and intelligence
"""

import json
import sqlite3
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from enhanced_valorant_collector import EnhancedValorantDataCollector
from valorant_scraper_integration import ValorantScraperIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AURORATacticalIntegration:
    """Main integration class for AURORA tactical system"""
    
    def __init__(self):
        self.collector = EnhancedValorantDataCollector()
        self.scraper_integration = ValorantScraperIntegration()
        self.setup_tactical_database()
        self.load_tactical_models()
        
    def setup_tactical_database(self):
        """Setup tactical analysis database"""
        cursor = self.collector.scraper.db_conn.cursor()
        
        # Tactical recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tactical_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                map_name TEXT,
                tactical_situation TEXT,
                formation TEXT,
                enemy_composition TEXT,
                recommended_strategy TEXT,
                confidence_score REAL,
                success_rate REAL,
                meta_relevance REAL,
                timestamp TIMESTAMP
            )
        ''')
        
        # Player tactical profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_tactical_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                player_tag TEXT,
                preferred_agents TEXT,
                playstyle TEXT,
                strengths TEXT,
                weaknesses TEXT,
                map_specialties TEXT,
                tactical_role TEXT,
                rank TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        # Match tactical analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_tactical_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                map_name TEXT,
                round_number INTEGER,
                tactical_situation TEXT,
                formation_analysis TEXT,
                utility_usage TEXT,
                positioning_analysis TEXT,
                outcome TEXT,
                effectiveness_score REAL,
                timestamp TIMESTAMP
            )
        ''')
        
        # Meta tactical trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_tactical_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patch_version TEXT,
                map_name TEXT,
                agent_name TEXT,
                tactical_role TEXT,
                popularity_trend REAL,
                effectiveness_trend REAL,
                counter_strategies TEXT,
                synergy_agents TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        self.collector.scraper.db_conn.commit()
        logger.info("Tactical database setup complete")
    
    def load_tactical_models(self):
        """Load or initialize tactical analysis models"""
        try:
            # Load existing ML models if available
            self.models = {
                'formation_analyzer': self.load_formation_model(),
                'tactical_predictor': self.load_tactical_model(),
                'meta_analyzer': self.load_meta_model()
            }
            logger.info("Tactical models loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load tactical models: {e}")
            self.models = {}
    
    def load_formation_model(self):
        """Load formation analysis model"""
        # Placeholder for actual ML model loading
        return {
            'type': 'formation_classifier',
            'features': ['player_positions', 'agent_types', 'map_zones'],
            'accuracy': 0.85
        }
    
    def load_tactical_model(self):
        """Load tactical prediction model"""
        # Placeholder for actual ML model loading
        return {
            'type': 'tactical_predictor',
            'features': ['economy', 'round_number', 'agent_composition', 'map_control'],
            'accuracy': 0.78
        }
    
    def load_meta_model(self):
        """Load meta analysis model"""
        # Placeholder for actual ML model loading
        return {
            'type': 'meta_analyzer',
            'features': ['pick_rates', 'win_rates', 'patch_changes'],
            'accuracy': 0.82
        }
    
    def analyze_tactical_situation(self, context: Dict) -> Dict:
        """Analyze current tactical situation with dataset insights"""
        try:
            cursor = self.collector.scraper.db_conn.cursor()
            
            # Extract context parameters
            map_name = context.get('map', 'Unknown')
            tactical_situation = context.get('tactical_situation', 'Unknown')
            formation = context.get('formation', 'Unknown')
            player_agents = context.get('agents_detected', [])
            
            # Get similar situations from dataset
            cursor.execute('''
                SELECT AVG(entry_rating), AVG(timing_gap), AVG(formation_score),
                       AVG(planting_score), AVG(rotation_score), AVG(win_rate),
                       COUNT(*) as sample_count
                FROM enhanced_player_analytics 
                WHERE map_name = ? AND tactical_situation = ? AND formation = ?
                GROUP BY map_name, tactical_situation, formation
            ''', (map_name, tactical_situation, formation))
            
            similar_situations = cursor.fetchone()
            
            if similar_situations and similar_situations[6] >= 5:  # Minimum 5 samples
                analysis = {
                    "situation_analysis": {
                        "map": map_name,
                        "tactical_situation": tactical_situation,
                        "formation": formation,
                        "sample_count": similar_situations[6],
                        "confidence": min(similar_situations[6] / 50, 1.0)  # Confidence based on sample size
                    },
                    "performance_benchmarks": {
                        "avg_entry_rating": similar_situations[0],
                        "avg_timing_gap": similar_situations[1],
                        "avg_formation_score": similar_situations[2],
                        "avg_planting_score": similar_situations[3],
                        "avg_rotation_score": similar_situations[4],
                        "avg_win_rate": similar_situations[5]
                    },
                    "tactical_recommendations": self.generate_tactical_recommendations(
                        map_name, tactical_situation, formation, player_agents
                    )
                }
            else:
                # Fallback to general analysis
                analysis = {
                    "situation_analysis": {
                        "map": map_name,
                        "tactical_situation": tactical_situation,
                        "formation": formation,
                        "sample_count": 0,
                        "confidence": 0.3  # Low confidence without data
                    },
                    "performance_benchmarks": self.get_general_benchmarks(),
                    "tactical_recommendations": self.get_general_recommendations(
                        tactical_situation, formation
                    )
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing tactical situation: {e}")
            return {"error": str(e)}
    
    def generate_tactical_recommendations(self, map_name: str, tactical_situation: str, 
                                       formation: str, player_agents: List[str]) -> Dict:
        """Generate tactical recommendations based on dataset"""
        cursor = self.collector.scraper.db_conn.cursor()
        
        # Get successful strategies for similar situations
        cursor.execute('''
            SELECT agents_detected, entry_rating, timing_gap, formation_score,
                   planting_score, rotation_score, win_rate
            FROM enhanced_player_analytics 
            WHERE map_name = ? AND tactical_situation = ? AND formation = ?
            AND win_rate > 0.6
            ORDER BY win_rate DESC
            LIMIT 10
        ''', (map_name, tactical_situation, formation))
        
        successful_cases = cursor.fetchall()
        
        recommendations = {
            "agent_synergies": self.analyze_agent_synergies(player_agents, successful_cases),
            "positioning_advice": self.get_positioning_advice(tactical_situation, formation),
            "utility_usage": self.get_utility_recommendations(tactical_situation, player_agents),
            "timing_strategy": self.get_timing_recommendations(tactical_situation),
            "success_probability": self.calculate_success_probability(successful_cases)
        }
        
        # Store recommendations for learning
        self.store_tactical_recommendation(map_name, tactical_situation, formation, recommendations)
        
        return recommendations
    
    def analyze_agent_synergies(self, current_agents: List[str], successful_cases: List) -> Dict:
        """Analyze agent synergies based on successful cases"""
        agent_performance = {}
        
        for case in successful_cases:
            agents = json.loads(case[0] or "[]")
            entry_rating = case[1]
            timing_gap = case[2]
            formation_score = case[3]
            planting_score = case[4]
            rotation_score = case[5]
            win_rate = case[6]
            
            metrics = {
                "entry_rating": entry_rating,
                "timing_gap": timing_gap,
                "formation_score": formation_score,
                "planting_score": planting_score,
                "rotation_score": rotation_score
            }
            
            for agent in agents:
                if agent not in agent_performance:
                    agent_performance[agent] = {
                        "count": 0,
                        "avg_win_rate": 0,
                        "avg_entry_rating": 0
                    }
                
                agent_performance[agent]["count"] += 1
                agent_performance[agent]["avg_win_rate"] += win_rate
                agent_performance[agent]["avg_entry_rating"] += metrics.get("entry_rating", 0)
        
        # Calculate averages
        for agent, data in agent_performance.items():
            if data["count"] > 0:
                data["avg_win_rate"] /= data["count"]
                data["avg_entry_rating"] /= data["count"]
        
        # Find synergies with current agents
        synergies = {}
        for current_agent in current_agents:
            synergies[current_agent] = {
                "compatible_agents": [],
                "synergy_score": 0
            }
            
            for agent, performance in agent_performance.items():
                if agent != current_agent and performance["avg_win_rate"] > 0.65:
                    synergies[current_agent]["compatible_agents"].append({
                        "agent": agent,
                        "win_rate": performance["avg_win_rate"],
                        "entry_rating": performance["avg_entry_rating"]
                    })
        
        return synergies
    
    def get_positioning_advice(self, tactical_situation: str, formation: str) -> Dict:
        """Get positioning advice based on tactical situation"""
        positioning_strategies = {
            "entry": {
                "tight": "Focus on coordinated pushes through single choke points",
                "balanced": "Split pushes with trade coordination",
                "spread": "Wide map control with multiple entry points"
            },
            "retake": {
                "tight": "Stack and retake together with utility",
                "balanced": "Coordinate retake with trade frags",
                "spread": "Split retake to catch defenders off guard"
            },
            "post_plant": {
                "tight": "Group defense around spike",
                "balanced": "Balanced spike defense with rotations",
                "spread": "Wide spike defense with off-angle holds"
            }
        }
        
        return positioning_strategies.get(tactical_situation, {}).get(formation, 
            "Maintain map control and coordinate with team")
    
    def get_utility_recommendations(self, tactical_situation: str, agents: List[str]) -> List[str]:
        """Get utility usage recommendations"""
        utility_map = {
            "entry": [
                "Use smoke screens to block sightlines",
                "Flashbangs for aggressive pushes",
                "Molly/Incendiary for site clearing"
            ],
            "retake": [
                "Stun abilities for entry fragging",
                "Smoke screens to block defenders",
                "Recon abilities for information"
            ],
            "post_plant": [
                "Area denial utilities around spike",
                "Recon to detect defuse attempts",
                "Stun for post-plant aggression"
            ]
        }
        
        base_recommendations = utility_map.get(tactical_situation, [])
        
        # Agent-specific recommendations
        agent_utilities = {
            "JETT": ["Tailwind for repositioning", "Updraft for high ground"],
            "SOVA": ["Recon arrows for information", "Shock darts for area denial"],
            "VIPER": ["Poison cloud for area denial", "Snake bite for spike defense"],
            "KILLJOY": ["Turret for information", "Nanoswarm for spike defense"]
        }
        
        for agent in agents:
            if agent in agent_utilities:
                base_recommendations.extend(agent_utilities[agent])
        
        return base_recommendations[:5]  # Return top 5 recommendations
    
    def get_timing_recommendations(self, tactical_situation: str) -> Dict:
        """Get timing strategy recommendations"""
        timing_strategies = {
            "entry": {
                "coordinated_push": "Execute within 2-3 seconds",
                "staggered_push": "Space out entries by 1-2 seconds",
                "trade_setup": "First entry creates trade opportunity"
            },
            "retake": {
                "immediate": "Retake within 5 seconds of plant",
                "utility_first": "Use utilities before pushing",
                "split_time": "Coordinate split pushes"
            },
            "post_plant": {
                "immediate_pressure": "Pressure defuse immediately",
                "time_bank": "Use full time bank for advantage",
                "rotation_setup": "Pre-aim common rotation paths"
            }
        }
        
        return timing_strategies.get(tactical_situation, {
            "coordination": "Maintain team communication",
            "patience": "Wait for optimal timing",
            "adaptation": "Adjust based on enemy behavior"
        })
    
    def calculate_success_probability(self, successful_cases: List) -> float:
        """Calculate success probability based on historical data"""
        if not successful_cases:
            return 0.5  # Base probability
        
        total_win_rate = sum(case[2] for case in successful_cases)
        avg_win_rate = total_win_rate / len(successful_cases)
        
        # Weight by sample size
        sample_size_factor = min(len(successful_cases) / 20, 1.0)
        
        return avg_win_rate * 0.7 + sample_size_factor * 0.3
    
    def store_tactical_recommendation(self, map_name: str, tactical_situation: str, 
                                    formation: str, recommendations: Dict):
        """Store tactical recommendations for learning"""
        cursor = self.collector.scraper.db_conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tactical_recommendations 
            (map_name, tactical_situation, formation, recommended_strategy,
             confidence_score, success_rate, meta_relevance, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            map_name,
            tactical_situation,
            formation,
            json.dumps(recommendations),
            0.8,  # Confidence score
            recommendations.get("success_probability", 0.5),
            0.7,  # Meta relevance
            datetime.now()
        ))
        
        self.collector.scraper.db_conn.commit()
    
    def get_general_benchmarks(self) -> Dict:
        """Get general performance benchmarks"""
        return {
            "avg_entry_rating": 3.5,
            "avg_timing_gap": 2.0,
            "avg_formation_score": 0.65,
            "avg_planting_score": 0.70,
            "avg_rotation_score": 0.60,
            "avg_win_rate": 0.60
        }
    
    def get_general_recommendations(self, tactical_situation: str, formation: str) -> Dict:
        """Get general tactical recommendations"""
        return {
            "agent_synergies": "Focus on balanced agent composition",
            "positioning_advice": "Maintain map control and communication",
            "utility_usage": "Coordinate utility usage with team",
            "timing_strategy": "Focus on team coordination",
            "success_probability": 0.5
        }
    
    def enhance_vod_with_tactical_analysis(self, vod_analysis: Dict) -> Dict:
        """Enhance VOD analysis with tactical insights"""
        enhanced_analysis = {
            "original_analysis": vod_analysis,
            "tactical_insights": {},
            "dataset_comparisons": {},
            "recommendations": {}
        }
        
        # Process each frame
        if "frame_analysis" in vod_analysis:
            for frame_data in vod_analysis["frame_analysis"]:
                tactical_context = {
                    "map": frame_data.get("map", "Unknown"),
                    "tactical_situation": frame_data.get("tactical_situation", "Unknown"),
                    "formation": frame_data.get("formation", "Unknown"),
                    "agents_detected": frame_data.get("agents_detected", [])
                }
                
                tactical_analysis = self.analyze_tactical_situation(tactical_context)
                frame_data["tactical_analysis"] = tactical_analysis
        
        return enhanced_analysis
    
    def generate_tactical_report(self, match_context: Dict) -> Dict:
        """Generate comprehensive tactical report"""
        report = {
            "match_context": match_context,
            "analysis_timestamp": datetime.now().isoformat(),
            "tactical_overview": {},
            "performance_analysis": {},
            "recommendations": {},
            "meta_comparison": {}
        }
        
        # Analyze overall tactical performance
        if "rounds" in match_context:
            round_analyses = []
            for round_data in match_context["rounds"]:
                tactical_analysis = self.analyze_tactical_situation(round_data)
                round_analyses.append(tactical_analysis)
            
            report["tactical_overview"] = {
                "total_rounds": len(round_analyses),
                "avg_confidence": sum(r.get("situation_analysis", {}).get("confidence", 0) for r in round_analyses) / len(round_analyses),
                "success_patterns": self.identify_success_patterns(round_analyses)
            }
        
        return report
    
    def identify_success_patterns(self, round_analyses: List[Dict]) -> List[Dict]:
        """Identify successful tactical patterns"""
        successful_patterns = []
        
        for analysis in round_analyses:
            situation = analysis.get("situation_analysis", {})
            benchmarks = analysis.get("performance_benchmarks", {})
            
            if situation.get("confidence", 0) > 0.7 and benchmarks.get("avg_win_rate", 0) > 0.6:
                pattern = {
                    "map": situation.get("map"),
                    "tactical_situation": situation.get("tactical_situation"),
                    "formation": situation.get("formation"),
                    "success_rate": benchmarks.get("avg_win_rate"),
                    "sample_size": situation.get("sample_count")
                }
                successful_patterns.append(pattern)
        
        return successful_patterns
    
    def close(self):
        """Close database connections"""
        self.collector.close()

# Example usage
if __name__ == "__main__":
    integration = AURORATacticalIntegration()
    
    # Test tactical analysis
    test_context = {
        "map": "BIND",
        "tactical_situation": "entry",
        "formation": "tight",
        "agents_detected": ["JETT", "SOVA", "VIPER"]
    }
    
    analysis = integration.analyze_tactical_situation(test_context)
    print("🎯 Tactical Analysis:", json.dumps(analysis, indent=2, default=str))
    
    integration.close()
    print("🎉 Tactical integration test completed!")
