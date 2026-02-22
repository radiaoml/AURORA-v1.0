"""
AURORA CoachBot and OracleBot
Advanced AI agents for strategy recommendations and predictions
"""
from typing import Dict, List, Any, Optional
import json
import numpy as np
from datetime import datetime
import sqlite3
import pickle
import os

from aurora_rag_system import get_professional_strategies
from aurora_agents import AuroraAgent

class CoachBot(AuroraAgent):
    """AI Strategic Agent with RAG capabilities"""
    
    def __init__(self):
        super().__init__("CoachBot")
        self.memory_cache = {}
        self.strategy_history = []
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic recommendations using RAG"""
        self.log_activity("Starting strategic analysis", data)
        
        # Get professional strategies from RAG system
        strategy_recommendations = get_professional_strategies(data)
        
        # Generate tactical synthesis
        tactical_synthesis = self._generate_tactical_synthesis(data, strategy_recommendations)
        
        # Create actionable recommendations
        recommendations = self._create_actionable_recommendations(data, strategy_recommendations)
        
        # Update strategy memory
        self._update_strategy_memory(data, strategy_recommendations)
        
        coach_results = {
            "match_id": data.get("match_id", "unknown"),
            "strategy_recommendations": strategy_recommendations,
            "tactical_synthesis": tactical_synthesis,
            "actionable_recommendations": recommendations,
            "confidence_score": self._calculate_confidence(data, strategy_recommendations),
            "coach_timestamp": datetime.now().isoformat()
        }
        
        self.log_activity("Strategic analysis complete", coach_results)
        return coach_results
    
    def _generate_tactical_synthesis(self, data: Dict[str, Any], strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meta-contextual tactical synthesis"""
        context = data.get("analysis_results", {})
        kpis = context.get("kpis", {})
        audit = context.get("tactical_audit", {})
        
        # Analyze current performance
        performance_level = self._assess_performance_level(kpis)
        
        # Identify key areas for improvement
        improvement_areas = self._identify_improvement_areas(audit, kpis)
        
        # Synthesize strategy recommendations
        synthesis = {
            "current_performance": {
                "level": performance_level,
                "ovr_score": kpis.get("ovr_score", 0),
                "tactical_efficiency": kpis.get("tactical_efficiency", 0),
                "agent_synergy": kpis.get("agent_synergy", 0)
            },
            "improvement_priorities": improvement_areas,
            "strategic_focus": self._determine_strategic_focus(data, strategies),
            "team_composition_analysis": self._analyze_team_composition(data),
            "meta_context": self._generate_meta_context(data, strategies)
        }
        
        return synthesis
    
    def _assess_performance_level(self, kpis: Dict[str, Any]) -> str:
        """Assess overall performance level"""
        ovr_score = kpis.get("ovr_score", 0)
        
        if ovr_score >= 85:
            return "Professional"
        elif ovr_score >= 70:
            return "Advanced"
        elif ovr_score >= 55:
            return "Intermediate"
        elif ovr_score >= 40:
            return "Beginner"
        else:
            return "Developing"
    
    def _identify_improvement_areas(self, audit: Dict[str, Any], kpis: Dict[str, Any]) -> List[str]:
        """Identify key areas for improvement"""
        areas = []
        
        # Check tactical audit weaknesses
        weaknesses = audit.get("weaknesses", [])
        if weaknesses:
            areas.extend([f"Tactical: {w}" for w in weaknesses[:2]])
        
        # Check KPI performance
        if kpis.get("timing_performance", 0) < 70:
            areas.append("Entry timing coordination")
        
        if kpis.get("rotation_performance", 0) < 70:
            areas.append("Rotation speed and map awareness")
        
        if kpis.get("agent_synergy", 0) < 80:
            areas.append("Agent composition and synergy")
        
        if kpis.get("tactical_efficiency", 0) < 75:
            areas.append("Overall tactical efficiency")
        
        return areas[:3]  # Top 3 priorities
    
    def _determine_strategic_focus(self, data: Dict[str, Any], strategies: Dict[str, Any]) -> str:
        """Determine primary strategic focus"""
        context = data.get("analysis_results", {})
        audit = context.get("tactical_audit", {})
        
        # Analyze weaknesses to determine focus
        weaknesses = audit.get("weaknesses", [])
        weakness_text = " ".join(weaknesses).lower()
        
        if "timing" in weakness_text:
            return "Coordination and Entry Timing"
        elif "rotation" in weakness_text:
            return "Map Control and Rotations"
        elif "formation" in weakness_text:
            return "Team Positioning and Setup"
        elif "slow" in weakness_text:
            return "Aggressive Playmaking"
        else:
            return "Fundamental Tactical Improvement"
    
    def _analyze_team_composition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current team composition"""
        agents = data.get("detected_agents", [])
        
        # Define agent roles
        agent_roles = {
            "Duelist": ["JETT", "REYNA", "PHOENIX", "RAZE", "NEON", "YORU"],
            "Controller": ["OMEN", "BRIMSTONE", "VAULT", "HARBOR", "Astra"],
            "Initiator": ["SOVA", "BREACH", "KAY/O", "SKYE", "FADE", "DEADLOCK"],
            "Sentinel": ["SAGE", "KILLJOY", "CYPER", "CHAMBER"]
        }
        
        # Count roles
        role_counts = {role: 0 for role in agent_roles}
        for agent in agents:
            for role, role_agents in agent_roles.items():
                if agent in role_agents:
                    role_counts[role] += 1
        
        # Analyze composition balance
        balance_score = self._calculate_composition_balance(role_counts)
        
        return {
            "current_agents": agents,
            "role_distribution": role_counts,
            "balance_score": balance_score,
            "composition_type": self._classify_composition(role_counts),
            "suggestions": self._get_composition_suggestions(role_counts)
        }
    
    def _calculate_composition_balance(self, role_counts: Dict[str, int]) -> float:
        """Calculate team composition balance score"""
        # Ideal distribution: 2 Duelists, 1 Controller, 1 Initiator, 1 Sentinel
        ideal = {"Duelist": 2, "Controller": 1, "Initiator": 1, "Sentinel": 1}
        
        score = 100
        for role, ideal_count in ideal.items():
            actual_count = role_counts.get(role, 0)
            diff = abs(actual_count - ideal_count)
            score -= diff * 15  # Penalty for deviation
        
        return max(0, score)
    
    def _classify_composition(self, role_counts: Dict[str, int]) -> str:
        """Classify team composition type"""
        duelists = role_counts.get("Duelist", 0)
        controllers = role_counts.get("Controller", 0)
        initiators = role_counts.get("Initiator", 0)
        sentinels = role_counts.get("Sentinel", 0)
        
        if duelists >= 3:
            return "Aggressive Duelist Stack"
        elif sentinels >= 2:
            return "Defensive Sentinel Setup"
        elif controllers >= 2:
            return "Map Control Oriented"
        elif initiators >= 2:
            return "Information/Entry Focused"
        else:
            return "Balanced Standard"
    
    def _get_composition_suggestions(self, role_counts: Dict[str, int]) -> List[str]:
        """Get composition improvement suggestions"""
        suggestions = []
        
        if role_counts.get("Duelist", 0) < 2:
            suggestions.append("Consider adding more duelists for entry fragging")
        
        if role_counts.get("Controller", 0) == 0:
            suggestions.append("Add a controller for smoke and area denial")
        
        if role_counts.get("Initiator", 0) == 0:
            suggestions.append("Include an initiator for information and utility")
        
        if role_counts.get("Sentinel", 0) == 0:
            suggestions.append("Consider a sentinel for site control")
        
        return suggestions
    
    def _generate_meta_context(self, data: Dict[str, Any], strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meta-contextual analysis"""
        recommendations = strategies.get("recommendations", [])
        
        # Analyze strategy patterns
        difficulties = [r.get("difficulty", "Beginner") for r in recommendations]
        success_rates = [r.get("success_rate", 50) for r in recommendations]
        
        return {
            "meta_analysis": {
                "recommended_difficulty": self._get_most_common(difficulties),
                "average_success_rate": np.mean(success_rates) if success_rates else 50,
                "strategy_diversity": len(set(r.get("strategy_name", "") for r in recommendations)),
                "pro_team_adoption": len(set(r.get("pro_teams", []) for r in recommendations if r.get("pro_teams")))
            },
            "current_meta_position": self._assess_meta_position(data),
            "improvement_trajectory": self._predict_improvement_trajectory(data)
        }
    
    def _get_most_common(self, items: List[str]) -> str:
        """Get most common item from list"""
        if not items:
            return "Unknown"
        return max(set(items), key=items.count)
    
    def _assess_meta_position(self, data: Dict[str, Any]) -> str:
        """Assess current meta position"""
        kpis = data.get("analysis_results", {}).get("kpis", {})
        ovr_score = kpis.get("ovr_score", 0)
        
        if ovr_score >= 80:
            return "Meta-Defining"
        elif ovr_score >= 70:
            return "Meta-Strong"
        elif ovr_score >= 60:
            return "Meta-Competitive"
        elif ovr_score >= 50:
            return "Meta-Relevant"
        else:
            return "Meta-Lagging"
    
    def _predict_improvement_trajectory(self, data: Dict[str, Any]) -> str:
        """Predict improvement trajectory"""
        current_performance = self._assess_performance_level(data.get("analysis_results", {}).get("kpis", {}))
        
        trajectories = {
            "Professional": "Maintain Excellence",
            "Advanced": "Refine for Pro Level",
            "Intermediate": "Rapid Improvement Potential",
            "Beginner": "Steep Learning Curve",
            "Developing": "Fundamental Growth Phase"
        }
        
        return trajectories.get(current_performance, "Unknown")
    
    def _create_actionable_recommendations(self, data: Dict[str, Any], strategies: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create actionable recommendations"""
        recommendations = []
        
        # Strategy-based recommendations
        for strategy in strategies.get("recommendations", [])[:2]:
            rec = {
                "type": "strategy",
                "priority": "High" if strategy.get("success_rate", 0) > 75 else "Medium",
                "title": f"Adopt {strategy.get('strategy_name', 'Strategy')}",
                "description": strategy.get("description", ""),
                "steps": strategy.get("key_points", [])[:3],
                "expected_impact": f"+{strategy.get('success_rate', 50)}% success rate",
                "difficulty": strategy.get("difficulty", "Intermediate"),
                "time_to_implement": "1-2 weeks"
            }
            recommendations.append(rec)
        
        # Composition-based recommendations
        composition = self._analyze_team_composition(data)
        if composition.get("balance_score", 0) < 70:
            rec = {
                "type": "composition",
                "priority": "Medium",
                "title": "Optimize Team Composition",
                "description": "Improve agent role balance for better synergy",
                "steps": composition.get("suggestions", [])[:3],
                "expected_impact": "+15% tactical efficiency",
                "difficulty": "Easy",
                "time_to_implement": "Immediate"
            }
            recommendations.append(rec)
        
        # Performance-based recommendations
        kpis = data.get("analysis_results", {}).get("kpis", {})
        if kpis.get("timing_performance", 0) < 70:
            rec = {
                "type": "performance",
                "priority": "High",
                "title": "Improve Entry Timing",
                "description": "Focus on coordination and entry timing",
                "steps": [
                    "Practice entry coordination with utility",
                    "Establish clear entry caller",
                    "Time utility usage with entry"
                ],
                "expected_impact": "+20% timing performance",
                "difficulty": "Medium",
                "time_to_implement": "2-3 weeks"
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _calculate_confidence(self, data: Dict[str, Any], strategies: Dict[str, Any]) -> float:
        """Calculate confidence score for recommendations"""
        base_confidence = 75.0
        
        # Boost confidence based on strategy relevance
        recs = strategies.get("recommendations", [])
        if recs:
            avg_relevance = np.mean([r.get("relevance_score", 0) for r in recs])
            base_confidence += avg_relevance * 10
        
        # Boost based on data quality
        if data.get("validation_status") == "VALID":
            base_confidence += 10
        
        # Boost based on analysis completeness
        if data.get("analysis_results"):
            base_confidence += 5
        
        return min(100, base_confidence)
    
    def _update_strategy_memory(self, data: Dict[str, Any], strategies: Dict[str, Any]):
        """Update strategy memory for learning"""
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "match_id": data.get("match_id"),
            "context": {
                "map": data.get("detected_map"),
                "agents": data.get("detected_agents"),
                "situation": data.get("situation")
            },
            "recommendations": strategies.get("recommendations", []),
            "performance": data.get("analysis_results", {}).get("kpis", {})
        }
        
        self.strategy_history.append(memory_entry)
        
        # Keep only last 100 entries
        if len(self.strategy_history) > 100:
            self.strategy_history = self.strategy_history[-100:]

class OracleBot(AuroraAgent):
    """Prediction and Probability Evaluation Agent"""
    
    def __init__(self):
        super().__init__("OracleBot")
        self.prediction_model = None
        self.historical_data = []
        self._load_historical_data()
        
    def _load_historical_data(self):
        """Load historical match data for predictions"""
        # Create synthetic historical data for demonstration
        np.random.seed(42)
        for i in range(100):
            self.historical_data.append({
                "match_id": f"historical_{i}",
                "ovr_score": np.random.uniform(40, 90),
                "tactical_efficiency": np.random.uniform(50, 95),
                "agent_synergy": np.random.uniform(60, 95),
                "timing_performance": np.random.uniform(40, 90),
                "map_advantage": np.random.uniform(-20, 20),
                "result": np.random.choice(["WIN", "LOSS"], p=[0.6, 0.4])  # 60% win rate
            })
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions and probability evaluations"""
        self.log_activity("Starting prediction analysis", data)
        
        # Extract features for prediction
        features = self._extract_features(data)
        
        # Generate win probability prediction
        win_probability = self._predict_win_probability(features)
        
        # Simulate strategy success rates
        strategy_predictions = self._predict_strategy_success(data, features)
        
        # Generate performance forecast
        performance_forecast = self._generate_performance_forecast(features)
        
        # Calculate risk assessment
        risk_assessment = self._calculate_risk_assessment(features)
        
        oracle_results = {
            "match_id": data.get("match_id", "unknown"),
            "predictions": {
                "win_probability": win_probability,
                "confidence_interval": self._calculate_confidence_interval(win_probability),
                "key_factors": self._identify_key_factors(features)
            },
            "strategy_predictions": strategy_predictions,
            "performance_forecast": performance_forecast,
            "risk_assessment": risk_assessment,
            "oracle_timestamp": datetime.now().isoformat()
        }
        
        self.log_activity("Prediction analysis complete", oracle_results)
        return oracle_results
    
    def _extract_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for prediction model"""
        context = data.get("analysis_results", {})
        kpis = context.get("kpis", {})
        
        features = {
            "ovr_score": kpis.get("ovr_score", 50),
            "tactical_efficiency": kpis.get("tactical_efficiency", 50),
            "agent_synergy": kpis.get("agent_synergy", 75),
            "timing_performance": kpis.get("timing_performance", 50),
            "rotation_performance": kpis.get("rotation_performance", 50),
            "win_probability": kpis.get("win_probability", 50)
        }
        
        # Add map advantage (synthetic for demonstration)
        map_advantages = {
            "ASCENT": 5, "BIND": 0, "HAVEN": 3, "SPLIT": -2, "ICEBOX": 1,
            "BREEZE": 4, "FRACTURE": -1, "PEARL": 2, "LOTUS": 0, "SUNSET": 3
        }
        detected_map = data.get("detected_map", "UNKNOWN")
        features["map_advantage"] = map_advantages.get(detected_map, 0)
        
        return features
    
    def _predict_win_probability(self, features: Dict[str, float]) -> float:
        """Predict win probability using historical patterns"""
        # Simple linear model based on historical data
        weights = {
            "ovr_score": 0.3,
            "tactical_efficiency": 0.25,
            "agent_synergy": 0.2,
            "timing_performance": 0.15,
            "map_advantage": 0.1
        }
        
        weighted_score = sum(features[key] * weight for key, weight in weights.items())
        
        # Normalize to probability
        probability = (weighted_score / 100) * 0.8 + 0.1  # Scale to 0.1-0.9 range
        
        return min(0.95, max(0.05, probability * 100))
    
    def _calculate_confidence_interval(self, probability: float) -> Dict[str, float]:
        """Calculate confidence interval for prediction"""
        # Standard error based on historical data variance
        std_error = 8.0  # Synthetic standard error
        
        lower = max(0, probability - 1.96 * std_error)
        upper = min(100, probability + 1.96 * std_error)
        
        return {
            "lower_bound": lower,
            "upper_bound": upper,
            "confidence_level": 95
        }
    
    def _identify_key_factors(self, features: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify key factors affecting prediction"""
        factor_importance = [
            {"factor": "Overall Rating (OVR)", "value": features["ovr_score"], "impact": "High"},
            {"factor": "Tactical Efficiency", "value": features["tactical_efficiency"], "impact": "High"},
            {"factor": "Agent Synergy", "value": features["agent_synergy"], "impact": "Medium"},
            {"factor": "Timing Performance", "value": features["timing_performance"], "impact": "Medium"},
            {"factor": "Map Advantage", "value": features["map_advantage"], "impact": "Low"}
        ]
        
        return factor_importance
    
    def _predict_strategy_success(self, data: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict success rates for recommended strategies"""
        coach_results = data.get("coach_results", {})
        recommendations = coach_results.get("strategy_recommendations", {}).get("recommendations", [])
        
        strategy_predictions = []
        for rec in recommendations[:3]:  # Top 3 strategies
            base_success = rec.get("success_rate", 50)
            
            # Adjust based on current team performance
            performance_multiplier = features["ovr_score"] / 75  # Normalized to average
            
            # Adjust based on agent compatibility
            agents = data.get("detected_agents", [])
            strategy_agents = rec.get("agents", [])
            compatibility = len(set(agents) & set(strategy_agents)) / len(strategy_agents)
            
            # Calculate predicted success
            predicted_success = base_success * performance_multiplier * (0.7 + 0.3 * compatibility)
            
            strategy_predictions.append({
                "strategy_name": rec.get("strategy_name", "Unknown"),
                "base_success_rate": base_success,
                "predicted_success_rate": min(95, predicted_success),
                "confidence": min(95, 70 + compatibility * 25),
                "key_factors": [
                    f"Team performance: {features['ovr_score']:.1f} OVR",
                    f"Agent compatibility: {compatibility*100:.0f}%"
                ]
            })
        
        return {"strategies": strategy_predictions}
    
    def _generate_performance_forecast(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Generate performance improvement forecast"""
        current_ovr = features["ovr_score"]
        
        # Simulate improvement over time
        forecasts = []
        for week in range(1, 9):  # 8 weeks forecast
            # Diminishing returns improvement
            improvement = (8 - week) * 2.5 * (1 - current_ovr / 100)
            projected_ovr = min(95, current_ovr + improvement)
            
            forecasts.append({
                "week": week,
                "projected_ovr": projected_ovr,
                "improvement": improvement,
                "confidence": max(60, 95 - week * 5)
            })
        
        return {
            "current_ovr": current_ovr,
            "forecasts": forecasts,
            "peak_performance": max(f["projected_ovr"] for f in forecasts),
            "time_to_peak": next((f["week"] for f in forecasts if f["projected_ovr"] >= 90), None)
        }
    
    def _calculate_risk_assessment(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Calculate risk assessment for team performance"""
        risks = []
        
        # Performance risks
        if features["ovr_score"] < 50:
            risks.append({
                "type": "Performance",
                "level": "High",
                "description": "Low overall rating indicates fundamental issues",
                "mitigation": "Focus on basic tactical fundamentals"
            })
        elif features["ovr_score"] < 70:
            risks.append({
                "type": "Performance",
                "level": "Medium",
                "description": "Moderate performance with room for improvement",
                "mitigation": "Refine advanced tactics and coordination"
            })
        
        # Coordination risks
        if features["timing_performance"] < 60:
            risks.append({
                "type": "Coordination",
                "level": "High",
                "description": "Poor timing coordination affecting entry success",
                "mitigation": "Practice entry timing and utility usage"
            })
        
        # Composition risks
        if features["agent_synergy"] < 70:
            risks.append({
                "type": "Composition",
                "level": "Medium",
                "description": "Agent composition lacks optimal synergy",
                "mitigation": "Consider agent role adjustments"
            })
        
        # Overall risk level
        risk_levels = [r["level"] for r in risks]
        if "High" in risk_levels:
            overall_risk = "High"
        elif "Medium" in risk_levels:
            overall_risk = "Medium"
        else:
            overall_risk = "Low"
        
        return {
            "overall_risk_level": overall_risk,
            "identified_risks": risks,
            "risk_score": len([r for r in risks if r["level"] == "High"]) * 3 + len([r for r in risks if r["level"] == "Medium"]) * 1,
            "recommendations": [
                "Address high-priority risks first",
                "Monitor risk factors over time",
                "Adjust strategies based on risk assessment"
            ]
        }

# Initialize advanced agents
coach_bot = CoachBot()
oracle_bot = OracleBot()

def run_advanced_analysis(cleaned_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Run CoachBot and OracleBot analysis"""
    print("🧠 Starting Advanced AI Analysis")
    
    # Prepare data for CoachBot
    coach_input = {
        "match_id": cleaned_data.get("match_id"),
        "detected_map": cleaned_data.get("detected_map"),
        "detected_agents": cleaned_data.get("detected_agents"),
        "tactical_suggestion": cleaned_data.get("tactical_suggestion"),
        "weaknesses": analysis_results.get("tactical_audit", {}).get("weaknesses", []),
        "analysis_results": analysis_results
    }
    
    # Run CoachBot
    coach_results = coach_bot.process(coach_input)
    
    # Prepare data for OracleBot
    oracle_input = {
        "match_id": cleaned_data.get("match_id"),
        "detected_map": cleaned_data.get("detected_map"),
        "detected_agents": cleaned_data.get("detected_agents"),
        "analysis_results": analysis_results,
        "coach_results": coach_results
    }
    
    # Run OracleBot
    oracle_results = oracle_bot.process(oracle_input)
    
    return {
        "status": "SUCCESS",
        "coach_analysis": coach_results,
        "oracle_predictions": oracle_results,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test the advanced agents
    test_data = {
        "match_id": "test_advanced_001",
        "detected_map": "ASCENT",
        "detected_agents": ["JETT", "OMEN", "SOVA", "SAGE", "REYNA"],
        "tactical_suggestion": "Entry detected with coordination issues",
        "weaknesses": ["Slow entry timing - coordination issues detected"],
        "analysis_results": {
            "kpis": {
                "ovr_score": 65,
                "tactical_efficiency": 72,
                "agent_synergy": 78,
                "timing_performance": 55,
                "rotation_performance": 70
            },
            "tactical_audit": {
                "weaknesses": ["Slow entry timing - coordination issues detected"],
                "strengths": ["Good agent composition"]
            }
        }
    }
    
    result = run_advanced_analysis(test_data, test_data["analysis_results"])
    print("✅ Advanced Analysis Complete!")
    print(f"Win Probability: {result['oracle_predictions']['predictions']['win_probability']:.1f}%")
    print(f"Coach Confidence: {result['coach_analysis']['confidence_score']:.1f}%")
    print(f"Overall Risk: {result['oracle_predictions']['risk_assessment']['overall_risk_level']}")
