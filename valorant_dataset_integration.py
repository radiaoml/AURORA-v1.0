"""
AURORA Valorant Dataset Integration API
Integrates enhanced data collection with AURORA backend
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from enhanced_valorant_collector import EnhancedValorantDataCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetCollectionRequest(BaseModel):
    """Request model for dataset collection operations"""
    collection_type: str = "comprehensive"  # comprehensive, meta, matches, analytics
    match_id: Optional[str] = None
    tournament_name: Optional[str] = None
    vod_url: Optional[str] = None

class VODEnhancementRequest(BaseModel):
    """Request model for VOD analysis enhancement"""
    vod_url: str
    analysis_results: Dict

class DatasetExportRequest(BaseModel):
    """Request model for dataset export"""
    output_path: Optional[str] = "enhanced_valorant_dataset.json"
    format: str = "json"  # json, csv, training_format

class ValorantDatasetIntegration:
    """Integration layer for enhanced Valorant dataset"""
    
    def __init__(self):
        self.collector = EnhancedValorantDataCollector()
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
    
    async def collect_dataset_data(self, request: DatasetCollectionRequest) -> Dict:
        """Collect enhanced dataset data"""
        try:
            cache_key = f"dataset_{request.collection_type}_{request.match_id or 'general'}"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            if request.collection_type == "comprehensive":
                result = await self.collector.run_comprehensive_collection_cycle()
            elif request.collection_type == "meta":
                result = await self.collector.generate_meta_trends_analysis()
            elif request.collection_type == "matches" and request.match_id:
                result = await self.collector.collect_live_match_data(
                    request.match_id, 
                    request.tournament_name or "Unknown"
                )
            elif request.collection_type == "analytics":
                result = self.collector.get_comprehensive_analytics()
            else:
                raise HTTPException(status_code=400, detail="Invalid collection type")
            
            self.cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error in dataset collection: {e}")
            return {"error": str(e)}
    
    async def enhance_vod_analysis(self, request: VODEnhancementRequest) -> Dict:
        """Enhance VOD analysis with dataset integration"""
        try:
            cache_key = f"vod_enhancement_{hash(request.vod_url)}"
            cached = self.get_cached_data(cache_key)
            if cached:
                return cached
            
            result = await self.collector.enhance_vod_analysis(
                request.vod_url, 
                request.analysis_results
            )
            
            self.cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing VOD analysis: {e}")
            return {"error": str(e)}
    
    def export_dataset(self, request: DatasetExportRequest) -> Dict:
        """Export enhanced dataset"""
        try:
            result = self.collector.export_enhanced_dataset(request.output_path)
            return result
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}")
            return {"error": str(e)}
    
    def get_dataset_statistics(self) -> Dict:
        """Get comprehensive dataset statistics"""
        try:
            analytics = self.collector.get_comprehensive_analytics()
            
            # Add additional statistics
            stats = {
                "dataset_overview": analytics,
                "collection_status": {
                    "last_collection": datetime.now().isoformat(),
                    "total_collections": len(self.cache),
                    "cache_size": sum(len(str(data)) for data, _ in self.cache.values())
                },
                "data_sources": {
                    "existing_dataset": len(self.collector.existing_annotations),
                    "vod_metadata": len(self.collector.vod_metadata),
                    "live_scraping": "active",
                    "ai_analysis": "integrated"
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dataset statistics: {e}")
            return {"error": str(e)}
    
    def get_training_data(self, format_type: str = "json") -> Dict:
        """Get data formatted for training"""
        try:
            cursor = self.collector.scraper.db_conn.cursor()
            
            # Get training-ready data
            cursor.execute('''
                SELECT map_name, tactical_situation, formation, position_type,
                       entry_rating, timing_gap, formation_score, planting_score,
                       rotation_score, win_rate, agents_detected, confidence_score
                FROM enhanced_player_analytics 
                WHERE confidence_score > 0.5
                ORDER BY timestamp DESC
                LIMIT 1000
            ''')
            
            training_data = cursor.fetchall()
            
            if format_type == "training_format":
                # Format for ML training
                formatted_data = []
                for row in training_data:
                    formatted_data.append({
                        "features": {
                            "map": row[0],
                            "tactical_situation": row[1],
                            "formation": row[2],
                            "position_type": row[3],
                            "timing_gap": row[5],
                            "formation_score": row[6],
                            "planting_score": row[7],
                            "rotation_score": row[8]
                        },
                        "labels": {
                            "entry_rating": row[4],
                            "win_rate": row[9]
                        },
                        "metadata": {
                            "agents_detected": json.loads(row[10] or "[]"),
                            "confidence": row[11]
                        }
                    })
                
                return {
                    "training_data": formatted_data,
                    "total_samples": len(formatted_data),
                    "format": "training_format",
                    "generated_at": datetime.now().isoformat()
                }
            
            else:
                # Return raw data
                columns = ["map", "tactical_situation", "formation", "position_type",
                           "entry_rating", "timing_gap", "formation_score", "planting_score",
                           "rotation_score", "win_rate", "agents_detected", "confidence_score"]
                
                return {
                    "data": [dict(zip(columns, row)) for row in training_data],
                    "total_samples": len(training_data),
                    "format": format_type,
                    "generated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting training data: {e}")
            return {"error": str(e)}

# Global instance
dataset_integration = ValorantDatasetIntegration()

def setup_valorant_dataset_routes(app: FastAPI):
    """Setup Valorant dataset API routes"""
    
    @app.post("/valorant/dataset/collect", tags=["Valorant Dataset"])
    async def collect_dataset_data(request: DatasetCollectionRequest):
        """Collect enhanced dataset data"""
        try:
            result = await dataset_integration.collect_dataset_data(request)
            return result
        except Exception as e:
            logger.error(f"Error in dataset collection endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/valorant/dataset/enhance-vod", tags=["Valorant Dataset"])
    async def enhance_vod_analysis(request: VODEnhancementRequest):
        """Enhance VOD analysis with dataset integration"""
        try:
            result = await dataset_integration.enhance_vod_analysis(request)
            return result
        except Exception as e:
            logger.error(f"Error in VOD enhancement endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/valorant/dataset/export", tags=["Valorant Dataset"])
    async def export_dataset(request: DatasetExportRequest):
        """Export enhanced dataset"""
        try:
            result = dataset_integration.export_dataset(request)
            return result
        except Exception as e:
            logger.error(f"Error in dataset export endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/valorant/dataset/statistics", tags=["Valorant Dataset"])
    async def get_dataset_statistics():
        """Get comprehensive dataset statistics"""
        try:
            result = dataset_integration.get_dataset_statistics()
            return result
        except Exception as e:
            logger.error(f"Error in dataset statistics endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/valorant/dataset/training-data", tags=["Valorant Dataset"])
    async def get_training_data(format: str = "json"):
        """Get data formatted for training"""
        try:
            result = dataset_integration.get_training_data(format)
            return result
        except Exception as e:
            logger.error(f"Error in training data endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/valorant/dataset/status", tags=["Valorant Dataset"])
    async def get_dataset_status():
        """Get dataset system status"""
        return {
            "status": "active",
            "dataset_path": "valorant_dataset",
            "existing_annotations": len(dataset_integration.collector.existing_annotations),
            "vod_metadata": len(dataset_integration.collector.vod_metadata),
            "enhanced_database": "SQLite",
            "collection_capabilities": [
                "comprehensive_collection",
                "meta_trends_analysis",
                "live_match_data",
                "vod_enhancement",
                "training_data_export"
            ],
            "integration_points": [
                "existing_dataset_integration",
                "live_scraping_integration",
                "vod_analysis_integration",
                "ml_training_integration"
            ],
            "last_updated": datetime.now().isoformat()
        }
