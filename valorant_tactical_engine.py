import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class MapType(Enum):
    ASCENT = "ASCENT"
    BIND = "BIND"
    HAVEN = "HAVEN"
    SPLIT = "SPLIT"
    ICEBOX = "ICEBOX"
    BREEZE = "BREEZE"
    FRACTURE = "FRACTURE"
    PEARL = "PEARL"
    LOTUS = "LOTUS"
    SUNSET = "SUNSET"
    ABYSS = "ABYSS"
    DISTRICT = "DISTRICT"

class AgentType(Enum):
    JETT = "JETT"
    REYNA = "REYNA"
    RAZE = "RAZE"
    PHOENIX = "PHOENIX"
    NEON = "NEON"
    YORU = "YORU"
    OMEGA = "OMEGA"
    
    SAGE = "SAGE"
    SKYE = "SKYE"
    KILLJOY = "KILLJOY"
    CYPER = "CYPER"
    CHAMBER = "CHAMBER"
    
    SOVA = "SOVA"
    BREACH = "BREACH"
    KAYO = "KAYO"
    FADE = "FADE"
    
    VIPER = "VIPER"
    Astra = "ASTRA"
    HARBOR = "HARBOR"
    
    BRIMSTONE = "BRIMSTONE"
    OMEN = "OMEN"
    CLOUDE = "CLOUDE"

class TacticalPattern(Enum):
    ENTRY = "entry"
    ROTATION = "rotation"
    FLANK = "flank"
    RETREAT = "retreat"
    POST_PLANT = "post_plant"
    ECO = "eco"
    BUY_ROUND = "buy_round"
    FORCE_BUY = "force_buy"

@dataclass
class MapCoordinate:
    x: float
    y: float
    area_name: str
    
@dataclass
class TacticalPosition:
    agent: str
    position: MapCoordinate
    timestamp: str
    action: str

@dataclass
class MovementPath:
    start: MapCoordinate
    end: MapCoordinate
    path_type: TacticalPattern
    duration: float

class ValorantTacticalEngine:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict:
        """Load comprehensive Valorant tactical knowledge"""
        return {
            "maps": {
                MapType.ASCENT.value: {
                    "callouts": [
                        "A Main", "A Tree", "A Heaven", "A Site", "Market", "Mid",
                        "B Main", "B Tree", "B Site", "B Heaven", "Pizza", "Spawn"
                    ],
                    "common_positions": {
                        "attackers": [(650, 350), (700, 300), (750, 250)],
                        "defenders": [(350, 700), (300, 650), (250, 600)]
                    },
                    "tactical_areas": {
                        "entry_points": ["A Main", "B Main", "Mid"],
                        "rotation_paths": ["Market to Pizza", "Mid to A/B"],
                        "post_plant_positions": ["A Heaven", "B Heaven", "Pizza"]
                    }
                },
                MapType.BIND.value: {
                    "callouts": [
                        "A Showers", "A Lamps", "A Site", "A Elbow", "A Fountain",
                        "B Showers", "B Lamps", "B Site", "B Elbow", "B Fountain",
                        "Hookah", "Long C", "Market", "Spawn"
                    ],
                    "common_positions": {
                        "attackers": [(800, 200), (850, 150), (200, 800)],
                        "defenders": [(500, 500), (450, 450), (400, 400)]
                    },
                    "tactical_areas": {
                        "entry_points": ["A Showers", "B Showers", "Long C"],
                        "rotation_paths": ["Hookah Connect", "Market Mid"],
                        "post_plant_positions": ["A Lamps", "B Lamps", "Hookah"]
                    }
                },
                MapType.HAVEN.value: {
                    "callouts": [
                        "A Site", "A Long", "A Short", "A Heaven", "A Hell",
                        "B Site", "B Long", "B Short", "B Heaven", "B Hell",
                        "C Site", "C Long", "C Short", "C Heaven", "C Hell",
                        "Garage", "Mid", "Spawn"
                    ],
                    "common_positions": {
                        "attackers": [(300, 300), (350, 250), (700, 700)],
                        "defenders": [(500, 500), (450, 450), (650, 650)]
                    },
                    "tactical_areas": {
                        "entry_points": ["A Long", "B Long", "C Long"],
                        "rotation_paths": ["Garage Mid", "Center Courtyard"],
                        "post_plant_positions": ["A Heaven", "B Heaven", "C Heaven"]
                    }
                }
            },
            "agents": {
                AgentType.JETT.value: {
                    "role": "duelist",
                    "abilities": ["Tailwind", "Cloudburst", "Updraft", "Blade Storm"],
                    "playstyle": "aggressive_entry",
                    "strengths": ["mobility", "one_shot_potential"],
                    "weaknesses": ["low_health", "utility_dependent"]
                },
                AgentType.REYNA.value: {
                    "role": "duelist",
                    "abilities": ["Leer", "Devour", "Dismiss", "Empress"],
                    "playstyle": "aggressive_entry",
                    "strengths": ["self_sufficiency", "entry_frags"],
                    "weaknesses": ["team_dependent", "predictable"]
                },
                AgentType.SOVA.value: {
                    "role": "initiator",
                    "abilities": ["Owl Drone", "Shock Bolt", "Recon Bolt", "Hunter's Fury"],
                    "playstyle": "information_gathering",
                    "strengths": ["recon", "area_denial"],
                    "weaknesses": ["slow_entry", "utility_timing"]
                },
                AgentType.OMEN.value: {
                    "role": "controller",
                    "abilities": ["Dark Cover", "Paranoia", "From the Shadows", "Shrouded Step"],
                    "playstyle": "map_control",
                    "strengths": ["smokes", "flank_potential"],
                    "weaknesses": ["direct_combat", "long_setup_time"]
                }
            },
            "tactics": {
                "entry_patterns": {
                    "default": ["Split A/B", "Rush A", "Rush B", "Mid Control"],
                    "ascent": ["A Main Push", "B Main Push", "Market Control", "Pizza Split"],
                    "bind": ["Showers Split", "Hookah Control", "Long C Rush"],
                    "haven": ["Triple Site Split", "Garage Control", "Mid Dominance"]
                },
                "post_plant": {
                    "default": ["Crossfire Setup", "Off-angle Holds", "Retake Preparation"],
                    "ascent": ["A Heaven Post-plant", "B Heaven Post-plant", "Pizza Control"],
                    "bind": ["Lamps Hold", "Fountain Control", "Hookah Denial"],
                    "haven": ["Heaven Holds", "Hell Positioning", "Garage Flank"]
                },
                "rotations": {
                    "default": ["Fast Rotate", "Slow Rotate", "Fake Rotate"],
                    "ascent": ["Market to Pizza", "Mid to A/B", "Spawn Rotation"],
                    "bind": ["Hookah Connect", "Market Rotation", "Teleporter Play"],
                    "haven": ["Garage to Sites", "Mid Courtyard", "Spawn to Sites"]
                }
            }
        }
    
    def analyze_position(self, agent: str, position: MapCoordinate, detected_map: str) -> Dict:
        """Analyze player position and provide tactical insights"""
        map_data = self.knowledge_base["maps"].get(detected_map, {})
        agent_data = self.knowledge_base["agents"].get(agent.upper(), {})
        
        # Find nearest callout
        nearest_callout = self._find_nearest_callout(position, map_data.get("callouts", []))
        
        # Determine tactical significance
        tactical_areas = map_data.get("tactical_areas", {})
        position_significance = self._analyze_position_significance(position, tactical_areas)
        
        return {
            "agent": agent,
            "position": position,
            "nearest_callout": nearest_callout,
            "tactical_significance": position_significance,
            "agent_role": agent_data.get("role", "unknown"),
            "recommended_action": self._get_position_recommendation(agent, position, detected_map)
        }
    
    def _find_nearest_callout(self, position: MapCoordinate, callouts: List[str]) -> str:
        """Find nearest callout to position"""
        # Simplified - would use actual coordinate mapping in production
        return callouts[0] if callouts else "Unknown"
    
    def _analyze_position_significance(self, position: MapCoordinate, tactical_areas: Dict) -> str:
        """Analyze tactical significance of position"""
        # Simplified logic - would use actual coordinate analysis
        if position.x > 600 and position.y < 400:
            return "Aggressive Entry Position"
        elif position.x < 400 and position.y > 600:
            return "Defensive Anchor Position"
        else:
            return "Mid Control Position"
    
    def _get_position_recommendation(self, agent: str, position: MapCoordinate, detected_map: str) -> str:
        """Get tactical recommendation for position"""
        agent_data = self.knowledge_base["agents"].get(agent.upper(), {})
        playstyle = agent_data.get("playstyle", "balanced")
        
        if playstyle == "aggressive_entry":
            return "Consider pushing for entry frag or using utility for space creation"
        elif playstyle == "information_gathering":
            return "Use recon abilities before committing to push"
        elif playstyle == "map_control":
            return "Set up smokes/screens to enable team push"
        else:
            return "Maintain crossfire positioning with team"
    
    def generate_tactical_analysis(self, 
                              positions: List[TacticalPosition], 
                              paths: List[MovementPath], 
                              detected_map: str) -> Dict:
        """Generate comprehensive tactical analysis"""
        
        map_analysis = self._analyze_map_control(positions, detected_map)
        movement_analysis = self._analyze_movement_patterns(paths, detected_map)
        agent_analysis = self._analyze_agent_composition(positions)
        
        return {
            "detected_map": detected_map,
            "map_control": map_analysis,
            "movement_patterns": movement_analysis,
            "agent_composition": agent_analysis,
            "tactical_recommendations": self._generate_recommendations(map_analysis, movement_analysis, agent_analysis),
            "performance_metrics": self._calculate_performance_metrics(positions, paths)
        }
    
    def _analyze_map_control(self, positions: List[TacticalPosition], detected_map: str) -> Dict:
        """Analyze team map control"""
        map_data = self.knowledge_base["maps"].get(detected_map, {})
        tactical_areas = map_data.get("tactical_areas", {})
        
        # Count positions in different areas
        area_control = {}
        for pos in positions:
            significance = self._analyze_position_significance(pos.position, tactical_areas)
            area_control[significance] = area_control.get(significance, 0) + 1
        
        return {
            "dominant_areas": area_control,
            "control_strength": len(set([p.agent for p in positions])) / 5.0,  # Assuming 5v5
            "map_coverage": self._calculate_coverage(positions)
        }
    
    def _analyze_movement_patterns(self, paths: List[MovementPath], detected_map: str) -> Dict:
        """Analyze team movement patterns"""
        path_types = [p.path_type.value for p in paths]
        path_durations = [p.duration for p in paths]
        
        return {
            "common_patterns": path_types,
            "average_rotation_time": sum(path_durations) / len(path_durations) if path_durations else 0,
            "rotation_efficiency": self._calculate_rotation_efficiency(paths),
            "predicted_next_moves": self._predict_next_movements(paths)
        }
    
    def _analyze_agent_composition(self, positions: List[TacticalPosition]) -> Dict:
        """Analyze agent composition and roles"""
        agents = [p.agent for p in positions]
        roles = {}
        
        for agent in agents:
            agent_data = self.knowledge_base["agents"].get(agent.upper(), {})
            role = agent_data.get("role", "unknown")
            roles[role] = roles.get(role, 0) + 1
        
        return {
            "agents": agents,
            "roles": roles,
            "composition_balance": self._evaluate_composition_balance(roles),
            "synergy_score": self._calculate_synergy_score(agents)
        }
    
    def _generate_recommendations(self, map_analysis: Dict, movement_analysis: Dict, agent_analysis: Dict) -> List[str]:
        """Generate tactical recommendations based on analysis"""
        recommendations = []
        
        # Map control recommendations
        if map_analysis.get("control_strength", 0) < 0.6:
            recommendations.append("Improve map spreading and area denial")
        
        # Movement recommendations
        if movement_analysis.get("average_rotation_time", 0) > 3.0:
            recommendations.append("Work on faster rotations - consider pre-aiming common angles")
        
        # Agent composition recommendations
        if agent_analysis.get("composition_balance", "balanced") != "balanced":
            recommendations.append("Consider agent composition adjustments for better utility coverage")
        
        # Default recommendations
        if not recommendations:
            recommendations.append("Maintain current tactical approach - good coordination observed")
        
        return recommendations
    
    def _calculate_performance_metrics(self, positions: List[TacticalPosition], paths: List[MovementPath]) -> Dict:
        """Calculate performance metrics"""
        return {
            "entry_rating": self._calculate_entry_rating(positions, paths),
            "timing_gap": self._calculate_timing_gap(paths),
            "formation_rating": self._calculate_formation_rating(positions),
            "planting_logic": self._calculate_planting_logic(positions),
            "rotation_latency": self._calculate_rotation_latency(paths),
            "win_rate_prediction": self._predict_win_rate(positions, paths)
        }
    
    def _calculate_entry_rating(self, positions: List[TacticalPosition], paths: List[MovementPath]) -> str:
        """Calculate entry rating"""
        entry_paths = [p for p in paths if p.path_type == TacticalPattern.ENTRY]
        if not entry_paths:
            return "C"
        
        avg_duration = sum(p.duration for p in entry_paths) / len(entry_paths)
        if avg_duration < 2.0:
            return "S"
        elif avg_duration < 3.0:
            return "A"
        elif avg_duration < 4.0:
            return "B"
        else:
            return "C"
    
    def _calculate_timing_gap(self, paths: List[MovementPath]) -> str:
        """Calculate timing gap"""
        if not paths:
            return "0.0s"
        
        avg_duration = sum(p.duration for p in paths) / len(paths)
        optimal_time = 2.0
        gap = avg_duration - optimal_time
        
        if gap > 0:
            return f"+{gap:.1f}s (Slow)"
        else:
            return f"{abs(gap):.1f}s (Fast)"
    
    def _calculate_formation_rating(self, positions: List[TacticalPosition]) -> str:
        """Calculate formation rating"""
        if len(positions) < 3:
            return "Poor Formation"
        
        # Calculate spread
        positions = [p.position for p in positions]
        avg_x = sum(p.x for p in positions) / len(positions)
        avg_y = sum(p.y for p in positions) / len(positions)
        
        # Calculate average distance from center
        avg_distance = sum(((p.x - avg_x)**2 + (p.y - avg_y)**2)**0.5 for p in positions) / len(positions)
        
        if avg_distance < 200:
            return "Tight Formation"
        elif avg_distance < 400:
            return "Balanced Formation"
        else:
            return "Spread Formation"
    
    def _calculate_planting_logic(self, positions: List[TacticalPosition]) -> str:
        """Calculate planting logic rating"""
        plant_positions = [p for p in positions if "plant" in p.action.lower()]
        if not plant_positions:
            return "No Plant Data"
        
        # Simplified - would analyze actual plant locations
        return "Optimal Spike Placement"
    
    def _calculate_rotation_latency(self, paths: List[MovementPath]) -> str:
        """Calculate rotation latency"""
        rotation_paths = [p for p in paths if p.path_type == TacticalPattern.ROTATION]
        if not rotation_paths:
            return "0.0s"
        
        avg_time = sum(p.duration for p in rotation_paths) / len(rotation_paths)
        return f"{avg_time:.1f}s"
    
    def _predict_win_rate(self, positions: List[TacticalPosition], paths: List[MovementPath]) -> str:
        """Predict win rate based on analysis"""
        entry_rating = self._calculate_entry_rating(positions, paths)
        formation = self._calculate_formation_rating(positions)
        
        # Simple heuristic calculation
        score = 0
        if entry_rating in ["S", "A"]:
            score += 30
        elif entry_rating == "B":
            score += 20
        else:
            score += 10
            
        if "Balanced" in formation:
            score += 20
        elif "Tight" in formation:
            score += 15
        else:
            score += 5
        
        win_rate = min(95, max(25, score + 40))  # Base 40% + adjustments
        return f"{win_rate}%"
    
    def _calculate_coverage(self, positions: List[TacticalPosition]) -> float:
        """Calculate map coverage"""
        if len(positions) < 2:
            return 0.0
        
        positions = [p.position for p in positions]
        max_distance = 0
        
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                distance = ((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)**0.5
                max_distance = max(max_distance, distance)
        
        return min(1.0, max_distance / 1000.0)  # Normalize to 0-1
    
    def _calculate_rotation_efficiency(self, paths: List[MovementPath]) -> str:
        """Calculate rotation efficiency"""
        if not paths:
            return "No Data"
        
        avg_time = sum(p.duration for p in paths) / len(paths)
        if avg_time < 2.0:
            return "Excellent"
        elif avg_time < 3.0:
            return "Good"
        elif avg_time < 4.0:
            return "Average"
        else:
            return "Poor"
    
    def _predict_next_movements(self, paths: List[MovementPath]) -> List[str]:
        """Predict next movements based on patterns"""
        if not paths:
            return ["Hold Position"]
        
        # Simplified prediction based on recent patterns
        recent_paths = paths[-3:] if len(paths) >= 3 else paths
        common_types = [p.path_type.value for p in recent_paths]
        
        if "rotation" in common_types:
            return ["Prepare for Site Retake", "Watch for Flank"]
        elif "entry" in common_types:
            return ["Post-plant Setup", "Anchor Position"]
        else:
            return ["Maintain Map Control"]
    
    def _evaluate_composition_balance(self, roles: Dict) -> str:
        """Evaluate team composition balance"""
        total = sum(roles.values())
        if total == 0:
            return "unknown"
        
        # Check for balanced composition
        has_duelist = roles.get("duelist", 0) > 0
        has_initiator = roles.get("initiator", 0) > 0
        has_controller = roles.get("controller", 0) > 0
        has_sentinel = roles.get("sentinel", 0) > 0
        
        balance_score = sum([has_duelist, has_initiator, has_controller, has_sentinel])
        
        if balance_score >= 3:
            return "balanced"
        elif balance_score >= 2:
            return "moderate"
        else:
            return "unbalanced"
    
    def _calculate_synergy_score(self, agents: List[str]) -> float:
        """Calculate team synergy score"""
        # Simplified synergy calculation
        agent_types = set(agents)
        
        # Bonus for diverse agent types
        synergy_bonus = min(1.0, len(agent_types) / 5.0)
        
        # Base synergy
        base_synergy = 0.7
        
        return min(1.0, base_synergy + synergy_bonus)

if __name__ == "__main__":
    # Test the tactical engine
    engine = ValorantTacticalEngine()
    
    # Test position analysis
    test_position = MapCoordinate(650, 350, "A Main")
    analysis = engine.analyze_position("JETT", test_position, "ASCENT")
    print("Position Analysis:", json.dumps(analysis, indent=2, default=str))
