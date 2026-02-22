"""
AURORA RAG System - Professional Strategy Memory
Implements FAISS-based retrieval for professional Valorant strategies
"""
import numpy as np
import json
import pickle
from typing import List, Dict, Any, Tuple
from datetime import datetime
import os

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("FAISS not available - using fallback memory system")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except (ImportError, OSError):
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Sentence Transformers not available - using fallback embeddings")

class AuroraRAGSystem:
    """Retrieval-Augmented Generation system for professional Valorant strategies"""
    
    def __init__(self):
        self.index_path = "aurora_strategy_index.faiss"
        self.metadata_path = "aurora_strategy_metadata.pkl"
        self.strategies_db_path = "aurora_strategies.json"
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = 384
        else:
            self.embedding_model = None
            self.embedding_dim = 100  # Fallback dimension
        
        # Initialize FAISS index
        self.index = None
        self.strategy_metadata = []
        
        # Load existing data or create new
        self._load_or_create_index()
        
        # Build professional strategy database
        self._build_strategy_database()
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one"""
        if FAISS_AVAILABLE and os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    self.strategy_metadata = pickle.load(f)
                print(f"[RAG] Loaded existing index with {len(self.strategy_metadata)} strategies")
            except Exception as e:
                print(f"[RAG] Error loading index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create new FAISS index"""
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner Product for similarity
            print(f"[RAG] Created new FAISS index with dimension {self.embedding_dim}")
        else:
            print("[RAG] Using fallback memory system (FAISS not available)")
    
    def _build_strategy_database(self):
        """Build professional strategy database"""
        if not os.path.exists(self.strategies_db_path):
            strategies = self._create_professional_strategies()
            with open(self.strategies_db_path, 'w') as f:
                json.dump(strategies, f, indent=2)
            print(f"[RAG] Created strategy database with {len(strategies)} strategies")
        else:
            with open(self.strategies_db_path, 'r') as f:
                strategies = json.load(f)
            print(f"[RAG] Loaded existing strategy database with {len(strategies)} strategies")
        
        # Add strategies to index
        self._add_strategies_to_index(strategies)
    
    def _create_professional_strategies(self) -> List[Dict[str, Any]]:
        """Create professional Valorant strategies database"""
        strategies = [
            {
                "id": "ascent_a_split",
                "map": "ASCENT",
                "situation": "entry",
                "strategy": "A-Site Split Entry with Flash and Smoke Coordination",
                "description": "Coordinate Jett flash with Omen smoke for mid control, then split A site",
                "agents": ["JETT", "OMEN", "SOVA", "SAGE", "REYNA"],
                "success_rate": 78,
                "pro_teams": ["Sentinels", "Fnatic", "LOUD"],
                "key_points": [
                    "Jett uses Updraft to gain height advantage",
                    "Omen smokes mid heaven and main",
                    "Sage wall blocks rotate",
                    "SOVA recon arrow confirms site clear",
                    "Reyna cleans up with dismiss"
                ],
                "timing_requirements": "< 2.0s entry",
                "difficulty": "Advanced"
            },
            {
                "id": "bind_post_plant",
                "map": "BIND",
                "situation": "post_plant",
                "strategy": "B-Site Post-Plant with Crossfire Setup",
                "description": "Establish crossfire positions after spike plant on B site",
                "agents": ["KILLJOY", "CYPER", "SOVA", "PHOENIX", "OMEN"],
                "success_rate": 82,
                "pro_teams": ["100 Thieves", "OpTic", "Evil Geniuses"],
                "key_points": [
                    "Killjoy turret watches default",
                    "Cyper tripwire blocks rotate",
                    "SOVA dart checks hookah",
                    "Phoenix flash for post-plant",
                    "Omen teleport for flank watch"
                ],
                "timing_requirements": "Immediate setup",
                "difficulty": "Intermediate"
            },
            {
                "id": "haven_mid_control",
                "map": "HAVEN",
                "situation": "mid_control",
                "strategy": "Mid-Dominance with Sentinel Setup",
                "description": "Control middle area with sentinel agents for map control",
                "agents": ["SAGE", "KILLJOY", "CYPER", "SOVA", "BREACH"],
                "success_rate": 75,
                "pro_teams": ["Team Liquid", "G2 Esports", "NRG"],
                "key_points": [
                    "Sage wall cuts rotations",
                    "Killjoy nest in mid garage",
                    "Cyper tripwire on C long",
                    "SOVA shock dart for info",
                    "Breach fault line for setup"
                ],
                "timing_requirements": "3-4s setup",
                "difficulty": "Intermediate"
            },
            {
                "id": "split_retake",
                "map": "SPLIT",
                "situation": "retake",
                "strategy": "A-Site Retake with Utility Coordination",
                "description": "Coordinated retake on A site with flash and stun utility",
                "agents": ["BREACH", "SKYE", "PHOENIX", "OMEN", "JETT"],
                "success_rate": 71,
                "pro_teams": ["Cloud9", "TSM", "Version1"],
                "key_points": [
                    "Breach fault line clears heaven",
                    "Skye flash initiates retake",
                    "Phoenix curve flash for entry",
                    "Omen smoke blocks defender vision",
                    "Jett dash for trade frag"
                ],
                "timing_requirements": "< 1.5s coordination",
                "difficulty": "Advanced"
            },
            {
                "id": "icebox_default",
                "map": "ICEBOX",
                "situation": "default",
                "strategy": "Default Setup with Site Control",
                "description": "Standard default setup with controlled site aggression",
                "agents": ["RAZE", "SOVA", "SAGE", "OMEN", "REYNA"],
                "success_rate": 68,
                "pro_teams": ["VCT Teams"],
                "key_points": [
                    "Raze satchel for site control",
                    "SOVA recon for information",
                    "Sage slow for entry denial",
                    "Omen smoke for map control",
                    "Reyna for aggressive picks"
                ],
                "timing_requirements": "Flexible",
                "difficulty": "Beginner"
            },
            {
                "id": "breeze_fast_break",
                "map": "BREEZE",
                "situation": "entry",
                "strategy": "Fast A-Break with Operator Support",
                "description": "Quick A site break with Chamber operator support",
                "agents": ["CHAMBER", "JETT", "KAY/O", "SOVA", "SAGE"],
                "success_rate": 73,
                "pro_teams": ["DRX", "Paper Rex", "FURIA"],
                "key_points": [
                    "Chamber operator watches heaven",
                    "Jett dash for site entry",
                    "KAY/O suppress for utility denial",
                    "SOVA dart for site check",
                    "Sage wall for post-plant"
                ],
                "timing_requirements": "< 2.5s",
                "difficulty": "Advanced"
            },
            {
                "id": "fracture_orchard",
                "map": "FRACTURE",
                "situation": "mid_control",
                "strategy": "Orchard Control with Sentinel Setup",
                "description": "Control orchard area with sentinel agents for B site preparation",
                "agents": ["KILLJOY", "DEADLOCK", "SOVA", "OMEN", "PHOENIX"],
                "success_rate": 77,
                "pro_teams": ["Leviatán", "KRÜ Esports", "LOUD"],
                "key_points": [
                    "Killjoy nest in orchard",
                    "Deadlock wall cuts rotate",
                    "SOVA shock dart for info",
                    "Omen smoke for B site",
                    "Phoenix flash for orchard"
                ],
                "timing_requirements": "2-3s setup",
                "difficulty": "Intermediate"
            },
            {
                "id": "pearl_aggressive_mid",
                "map": "PEARL",
                "situation": "entry",
                "strategy": "Aggressive Mid Control with Duelists",
                "description": "Aggressive mid control with duelists for site split",
                "agents": ["NEON", "REYNA", "JETT", "SOVA", "OMEN"],
                "success_rate": 70,
                "pro_teams": ["Fnatic", "NRG", "100 Thieves"],
                "key_points": [
                    "Neon slide for mid control",
                    "Reyna aggressive picks",
                    "Jett dash for trades",
                    "SOVA recon for information",
                    "Omen smoke for site prep"
                ],
                "timing_requirements": "< 2.0s",
                "difficulty": "Advanced"
            }
        ]
        
        return strategies
    
    def _add_strategies_to_index(self, strategies: List[Dict[str, Any]]):
        """Add strategies to FAISS index"""
        if not FAISS_AVAILABLE or not self.embedding_model:
            print("[RAG] Using fallback memory - strategies stored in metadata")
            self.strategy_metadata = strategies
            return
        
        # Create embeddings for strategies
        strategy_texts = []
        for strategy in strategies:
            # Combine strategy text for embedding
            text = f"{strategy['strategy']} {strategy['description']} {' '.join(strategy['key_points'])}"
            strategy_texts.append(text)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(strategy_texts)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Add to index
        self.index.add(embeddings.astype(np.float32))
        
        # Store metadata
        self.strategy_metadata = strategies
        
        # Save index and metadata
        if FAISS_AVAILABLE:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.strategy_metadata, f)
        
        print(f"[RAG] Added {len(strategies)} strategies to index")
    
    def query_strategies(self, query: str, map_name: str = None, situation: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Query strategies based on input context"""
        print(f"[RAG] Querying strategies for: {query}")
        
        # Filter strategies by map and situation if specified
        candidate_strategies = self.strategy_metadata
        if map_name:
            candidate_strategies = [s for s in candidate_strategies if s["map"] == map_name.upper()]
        if situation:
            candidate_strategies = [s for s in candidate_strategies if s["situation"] == situation.lower()]
        
        if not FAISS_AVAILABLE or not self.embedding_model:
            # Fallback: simple keyword matching
            return self._fallback_query(query, candidate_strategies, top_k)
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Search in index
        if len(candidate_strategies) == 0:
            # Search all strategies
            distances, indices = self.index.search(query_embedding.astype(np.float32), min(top_k, len(self.strategy_metadata)))
            candidate_indices = indices[0]
        else:
            # Search only in filtered strategies
            filtered_indices = [i for i, s in enumerate(self.strategy_metadata) if s in candidate_strategies]
            if not filtered_indices:
                return []
            
            # Create filtered index
            filtered_embeddings = []
            for idx in filtered_indices:
                # Get embedding from index (this is a simplified approach)
                filtered_embeddings.append(self.strategy_metadata[idx])
            
            # For simplicity, return filtered strategies sorted by success rate
            candidate_strategies.sort(key=lambda x: x["success_rate"], reverse=True)
            return candidate_strategies[:top_k]
        
        # Get results
        results = []
        for i, idx in enumerate(candidate_indices[:top_k]):
            if idx < len(self.strategy_metadata):
                strategy = self.strategy_metadata[idx].copy()
                strategy["similarity_score"] = float(distances[0][i])
                results.append(strategy)
        
        print(f"[RAG] Found {len(results)} relevant strategies")
        return results
    
    def _fallback_query(self, query: str, strategies: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Fallback query using keyword matching"""
        query_lower = query.lower()
        scored_strategies = []
        
        for strategy in strategies:
            score = 0
            # Check keyword matches
            if any(word in strategy["strategy"].lower() for word in query_lower.split()):
                score += 2
            if any(word in strategy["description"].lower() for word in query_lower.split()):
                score += 1
            for point in strategy["key_points"]:
                if any(word in point.lower() for word in query_lower.split()):
                    score += 1
            
            # Add success rate bonus
            score += strategy["success_rate"] / 20
            
            scored_strategies.append((strategy, score))
        
        # Sort by score and return top_k
        scored_strategies.sort(key=lambda x: x[1], reverse=True)
        results = []
        for strategy, score in scored_strategies[:top_k]:
            strategy_copy = strategy.copy()
            strategy_copy["similarity_score"] = score
            results.append(strategy_copy)
        
        return results
    
    def get_strategy_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy recommendations based on analysis context"""
        map_name = context.get("detected_map")
        situation = self._infer_situation(context)
        weaknesses = context.get("weaknesses", [])
        
        # Build query
        query = f"{map_name} {situation} strategy"
        if weaknesses:
            query += f" fix {weaknesses[0].lower()}"
        
        # Get strategies
        strategies = self.query_strategies(query, map_name, situation, top_k=3)
        
        # Generate recommendations
        recommendations = []
        for strategy in strategies:
            recommendation = {
                "strategy_name": strategy["strategy"],
                "description": strategy["description"],
                "key_points": strategy["key_points"],
                "success_rate": strategy["success_rate"],
                "difficulty": strategy["difficulty"],
                "agents": strategy["agents"],
                "relevance_score": strategy.get("similarity_score", 0),
                "why_recommended": self._explain_recommendation(strategy, context)
            }
            recommendations.append(recommendation)
        
        return {
            "context": {
                "map": map_name,
                "situation": situation,
                "weaknesses": weaknesses
            },
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def _infer_situation(self, context: Dict[str, Any]) -> str:
        """Infer tactical situation from analysis context"""
        tactical_suggestion = context.get("tactical_suggestion", "").lower()
        
        if "entry" in tactical_suggestion:
            return "entry"
        elif "post_plant" in tactical_suggestion or "planting" in tactical_suggestion:
            return "post_plant"
        elif "retake" in tactical_suggestion:
            return "retake"
        elif "mid" in tactical_suggestion:
            return "mid_control"
        else:
            return "default"
    
    def _explain_recommendation(self, strategy: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Explain why this strategy is recommended"""
        reasons = []
        
        # Map match
        if strategy["map"] == context.get("detected_map"):
            reasons.append(f"Perfect for {strategy['map']}")
        
        # Situation match
        situation = self._infer_situation(context)
        if strategy["situation"] == situation:
            reasons.append(f"Ideal for {situation} situations")
        
        # Agent compatibility
        current_agents = context.get("detected_agents", [])
        strategy_agents = strategy["agents"]
        if any(agent in current_agents for agent in strategy_agents):
            matching_agents = [agent for agent in strategy_agents if agent in current_agents]
            reasons.append(f"Uses your current agents: {', '.join(matching_agents)}")
        
        # Addresses weaknesses
        weaknesses = context.get("weaknesses", [])
        if "slow" in " ".join(weaknesses).lower() and strategy["difficulty"] == "Advanced":
            reasons.append("Advanced coordination for timing issues")
        
        if not reasons:
            reasons.append(f"High success rate ({strategy['success_rate']}%)")
        
        return "; ".join(reasons)

# Global RAG instance
rag_system = AuroraRAGSystem()

def get_professional_strategies(analysis_context: Dict[str, Any]) -> Dict[str, Any]:
    """Get professional strategy recommendations"""
    return rag_system.get_strategy_recommendations(analysis_context)

if __name__ == "__main__":
    # Test the RAG system
    test_context = {
        "detected_map": "ASCENT",
        "detected_agents": ["JETT", "OMEN", "SOVA", "SAGE", "REYNA"],
        "tactical_suggestion": "Entry detected with 3/5 tactical execution",
        "weaknesses": ["Slow entry timing - coordination issues detected"]
    }
    
    recommendations = get_professional_strategies(test_context)
    print("🧠 Professional Strategy Recommendations:")
    print(f"Map: {recommendations['context']['map']}")
    print(f"Situation: {recommendations['context']['situation']}")
    print(f"Found {len(recommendations['recommendations'])} strategies")
    
    for i, rec in enumerate(recommendations['recommendations'], 1):
        print(f"\n{i}. {rec['strategy_name']}")
        print(f"   Success Rate: {rec['success_rate']}%")
        print(f"   Difficulty: {rec['difficulty']}")
        print(f"   Why: {rec['why_recommended']}")
        print(f"   Key Points: {', '.join(rec['key_points'][:2])}")
