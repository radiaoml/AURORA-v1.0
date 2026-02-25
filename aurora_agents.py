"""
AURORA Multi-Agent System
Implements the 5-agent architecture from Aurora Pipeline specification
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import sqlite3
import duckdb
from datetime import datetime

class AuroraAgent(ABC):
    """Base class for all Aurora agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.data_warehouse = "aurora_datawarehouse.db"
        
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data and return results"""
        pass
    
    def log_activity(self, activity: str, data: Dict[str, Any]):
        """Log agent activity for audit trail"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "agent": self.name,
            "timestamp": timestamp,
            "activity": activity,
            "data_summary": str(data)[:100]
        }
        print(f"[{self.name}] {activity} at {timestamp}")

class CleanerBot(AuroraAgent):
    """Data engineering and ingestion agent"""
    
    def __init__(self):
        super().__init__("CleanerBot")
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize incoming data"""
        self.log_activity("Starting data cleaning", data)
        
        # Extract video analysis data
        video_analysis = data.get("video_analysis", {})
        spatial_data = data.get("spatial_data", {})
        
        # Normalize data structure
        cleaned_data = {
            "match_id": data.get("source_id", f"match_{datetime.now().timestamp()}"),
            "timestamp": datetime.now().isoformat(),
            "detected_map": video_analysis.get("detected_map", "UNKNOWN"),
            "detected_agents": video_analysis.get("detected_agents", []),
            "entry_rating": video_analysis.get("entry_rating", "C"),
            "timing_gap": video_analysis.get("timing_gap", "0.0s"),
            "formation_issue": video_analysis.get("formation_issue", "None"),
            "planting_critique": video_analysis.get("planting_critique", "Standard"),
            "rotation_latency": video_analysis.get("rotation_latency", "0.0s"),
            "win_rate_prediction": video_analysis.get("win_rate_prediction", "50%"),
            "tactical_suggestion": video_analysis.get("tactical_suggestion", "No analysis"),
            "spatial_coordinates": {
                "kill_locations": spatial_data.get("kill_locations", []),
                "player_positions": spatial_data.get("player_positions", []),
                "movement_paths": spatial_data.get("movement_paths", [])
            },
            "raw_video_data": data.get("raw_frames", [])
        }
        
        # Validate data integrity
        validation_result = self._validate_data(cleaned_data)
        cleaned_data["validation_status"] = validation_result
        
        # Store in data warehouse
        self._store_in_warehouse(cleaned_data)
        
        self.log_activity("Data cleaning complete", cleaned_data)
        return cleaned_data
    
    def _validate_data(self, data: Dict[str, Any]) -> str:
        """Validate data integrity and schema compliance"""
        required_fields = ["match_id", "detected_map", "detected_agents", "entry_rating"]
        
        for field in required_fields:
            if not data.get(field):
                return f"Missing required field: {field}"
        
        # Validate map
        valid_maps = ["ASCENT", "BIND", "HAVEN", "SPLIT", "ICEBOX", "BREEZE", "FRACTURE", "PEARL", "LOTUS", "SUNSET"]
        if data["detected_map"] not in valid_maps:
            return f"Invalid map: {data['detected_map']}"
        
        # Validate agents
        valid_agents = ["JETT", "REYNA", "SOVA", "OMEN", "SAGE", "PHOENIX", "RAZE", "BREACH", "CYPER", "KILLJOY", "VIPER", "ASTRA", "SKYE", "YORU", "KAY/O", "CHAMBER", "NEON", "FADE", "HARBOR", "DEADLOCK"]
        for agent in data["detected_agents"]:
            if agent not in valid_agents:
                return f"Invalid agent: {agent}"
        
        return "VALID"
    
    def _store_in_warehouse(self, data: Dict[str, Any]):
        """Store cleaned data in SQLite data warehouse"""
        conn = sqlite3.connect(self.data_warehouse)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT UNIQUE,
                timestamp TEXT,
                detected_map TEXT,
                detected_agents TEXT,
                entry_rating TEXT,
                timing_gap TEXT,
                formation_issue TEXT,
                planting_critique TEXT,
                rotation_latency TEXT,
                win_rate_prediction TEXT,
                tactical_suggestion TEXT,
                validation_status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spatial_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                kill_locations TEXT,
                player_positions TEXT,
                movement_paths TEXT,
                FOREIGN KEY (match_id) REFERENCES match_analysis (match_id)
            )
        ''')
        
        # Insert match analysis
        cursor.execute('''
            INSERT OR REPLACE INTO match_analysis 
            (match_id, timestamp, detected_map, detected_agents, entry_rating, 
             timing_gap, formation_issue, planting_critique, rotation_latency, 
             win_rate_prediction, tactical_suggestion, validation_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["match_id"], data["timestamp"], data["detected_map"],
            json.dumps(data["detected_agents"]), data["entry_rating"],
            data["timing_gap"], data["formation_issue"], data["planting_critique"],
            data["rotation_latency"], data["win_rate_prediction"],
            data["tactical_suggestion"], data["validation_status"]
        ))
        
        # Insert spatial data
        spatial = data["spatial_coordinates"]
        cursor.execute('''
            INSERT OR REPLACE INTO spatial_data 
            (match_id, kill_locations, player_positions, movement_paths)
            VALUES (?, ?, ?, ?)
        ''', (
            data["match_id"], json.dumps(spatial["kill_locations"]),
            json.dumps(spatial["player_positions"]), json.dumps(spatial["movement_paths"])
        ))
        
        conn.commit()
        conn.close()

class AnalystBot(AuroraAgent):
    """Tactical analysis and KPI calculation agent"""
    
    def __init__(self):
        super().__init__("AnalystBot")
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform tactical analysis and calculate KPIs"""
        self.log_activity("Starting tactical analysis", data)
        
        # Calculate KPIs
        kpis = self._calculate_kpis(data)
        
        # Perform tactical audit
        tactical_audit = self._perform_tactical_audit(data)
        
        # Generate insights
        insights = self._generate_insights(data, kpis, tactical_audit)
        
        analysis_results = {
            "match_id": data["match_id"],
            "kpis": kpis,
            "tactical_audit": tactical_audit,
            "insights": insights,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        self.log_activity("Tactical analysis complete", analysis_results)
        return analysis_results
    
    def _calculate_kpis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key performance indicators"""
        # Extract numeric values
        timing_gap = float(data.get("timing_gap", "0.0s").replace("s", ""))
        rotation_latency = float(data.get("rotation_latency", "0.0s").replace("s", ""))
        win_rate = float(data.get("win_rate_prediction", "50%").replace("%", ""))
        
        # Calculate OVR (Overall Valorant Rating) - proprietary metric
        ovr_score = self._calculate_ovr(data, timing_gap, rotation_latency, win_rate)
        
        # Calculate tactical efficiency
        tactical_efficiency = self._calculate_tactical_efficiency(data)
        
        return {
            "ovr_score": ovr_score,
            "tactical_efficiency": tactical_efficiency,
            "timing_performance": max(0, 100 - timing_gap * 10),  # Lower is better
            "rotation_performance": max(0, 100 - rotation_latency * 8),  # Lower is better
            "win_probability": win_rate,
            "agent_synergy": self._calculate_agent_synergy(data.get("detected_agents", []))
        }
    
    def _calculate_ovr(self, data: Dict[str, Any], timing: float, rotation: float, win_rate: float) -> float:
        """Calculate proprietary OVR score"""
        # Base score from win rate
        base_score = win_rate
        
        # Timing penalty
        timing_penalty = min(20, timing * 5)
        
        # Rotation penalty
        rotation_penalty = min(15, rotation * 3)
        
        # Entry rating bonus
        entry_bonus = {"A": 10, "B": 5, "C": 0, "D": -5, "F": -10}.get(data.get("entry_rating", "C"), 0)
        
        # Agent composition bonus
        agent_bonus = len(data.get("detected_agents", [])) * 2
        
        ovr = base_score + entry_bonus + agent_bonus - timing_penalty - rotation_penalty
        return max(0, min(100, ovr))
    
    def _calculate_tactical_efficiency(self, data: Dict[str, Any]) -> float:
        """Calculate tactical efficiency score"""
        factors = []
        
        # Formation efficiency
        if data.get("formation_issue") == "None":
            factors.append(100)
        elif "Enhanced" in data.get("formation_issue", ""):
            factors.append(85)
        else:
            factors.append(70)
        
        # Planting efficiency
        if "Enhanced" in data.get("planting_critique", ""):
            factors.append(90)
        else:
            factors.append(75)
        
        # Spatial utilization
        spatial = data.get("spatial_coordinates", {})
        if spatial.get("kill_locations") and spatial.get("movement_paths"):
            factors.append(85)
        else:
            factors.append(60)
        
        return sum(factors) / len(factors)
    
    def _calculate_agent_synergy(self, agents: List[str]) -> float:
        """Calculate agent team synergy score"""
        if len(agents) < 2:
            return 50
        
        # Define synergistic agent pairs
        synergies = {
            ("JETT", "REYNA"): 95,
            ("OMEN", "VAULT"): 90,
            ("SAGE", "PHOENIX"): 85,
            ("SOVA", "BREACH"): 90,
            ("KILLJOY", "CYPER"): 95
        }
        
        synergy_scores = []
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                pair = tuple(sorted([agent1, agent2]))
                synergy_scores.append(synergies.get(pair, 75))
        
        return sum(synergy_scores) / len(synergy_scores) if synergy_scores else 75
    
    def _perform_tactical_audit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform tactical audit to identify weaknesses"""
        weaknesses = []
        strengths = []
        
        # Timing analysis
        timing = float(data.get("timing_gap", "0.0s").replace("s", ""))
        if timing > 2.0:
            weaknesses.append("Slow entry timing - coordination issues detected")
        elif timing < 1.0:
            strengths.append("Excellent entry timing - aggressive coordination")
        
        # Rotation analysis
        rotation = float(data.get("rotation_latency", "0.0s").replace("s", ""))
        if rotation > 3.0:
            weaknesses.append("Slow rotations - map control issues")
        elif rotation < 1.5:
            strengths.append("Fast rotations - good map awareness")
        
        # Formation analysis
        formation = data.get("formation_issue", "")
        if "None" in formation:
            strengths.append("Solid team formation")
        else:
            weaknesses.append(f"Formation issues: {formation}")
        
        return {
            "weaknesses": weaknesses,
            "strengths": strengths,
            "overall_tactical_score": max(0, 100 - len(weaknesses) * 15)
        }
    
    def _generate_insights(self, data: Dict[str, Any], kpis: Dict[str, Any], audit: Dict[str, Any]) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        # OVR-based insights
        if kpis["ovr_score"] > 80:
            insights.append("Excellent overall performance - professional level tactics")
        elif kpis["ovr_score"] > 60:
            insights.append("Good performance with room for improvement")
        else:
            insights.append("Significant tactical improvements needed")
        
        # Timing-based insights
        if kpis["timing_performance"] < 70:
            insights.append("Focus on improving entry coordination and timing")
        
        # Agent synergy insights
        if kpis["agent_synergy"] < 80:
            insights.append("Consider agent composition adjustments for better synergy")
        
        # Tactical audit insights
        if audit["weaknesses"]:
            insights.append(f"Priority weaknesses: {', '.join(audit['weaknesses'][:2])}")
        
        return insights

# Initialize agents
cleaner_bot = CleanerBot()
analyst_bot = AnalystBot()

def process_video_analysis(video_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main pipeline function to process video analysis through agents"""
    print("🚀 Starting Aurora Multi-Agent Pipeline")
    
    # Step 1: CleanerBot processes raw video analysis
    cleaned_data = cleaner_bot.process(video_data)
    
    # Step 2: AnalystBot performs tactical analysis
    analysis_results = analyst_bot.process(cleaned_data)
    
    return {
        "status": "SUCCESS",
        "pipeline": "AURORA Multi-Agent System",
        "cleaned_data": cleaned_data,
        "analysis_results": analysis_results,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test the multi-agent system
    test_data = {
        "source_id": "test_match_001",
        "video_analysis": {
            "detected_map": "HAVEN",
            "detected_agents": ["JETT", "REYNA", "SOVA", "OMEN", "SAGE"],
            "entry_rating": "B",
            "timing_gap": "1.5s",
            "formation_issue": "Enhanced Formation Analysis - Entry Phase",
            "planting_critique": "Enhanced Planting Assessment - Entry Context",
            "rotation_latency": "2.1s",
            "win_rate_prediction": "65%",
            "tactical_suggestion": "Enhanced AI Analysis: Entry detected with 3/5 tactical execution"
        },
        "spatial_data": {
            "kill_locations": [{"x": 300, "y": 850, "area": "Enhanced Entry Zone"}],
            "player_positions": [{"agent": "JETT", "x": 330, "y": 880, "timestamp": "Enhanced"}],
            "movement_paths": [{"start_x": 300, "start_y": 850, "end_x": 500, "end_y": 500, "type": "Enhanced Entry"}]
        }
    }
    
    result = process_video_analysis(test_data)
    print("✅ Multi-Agent Processing Complete!")
    print(f"Status: {result['status']}")
    print(f"OVR Score: {result['analysis_results']['kpis']['ovr_score']:.1f}")
    print(f"Tactical Efficiency: {result['analysis_results']['kpis']['tactical_efficiency']:.1f}%")
