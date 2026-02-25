"""
AURORA Enhanced Valorant Data Collection System
Integrates existing dataset with live scraping and advanced analytics
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from valorant_scraper import ValorantDataScraper
from valorant_scraper_integration import ValorantScraperIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedValorantDataCollector:
    """Enhanced data collection system for Valorant tactical analysis"""
    
    def __init__(self, dataset_path: str = "valorant_dataset"):
        self.dataset_path = dataset_path
        self.scraper = ValorantDataScraper()
        self.integration = ValorantScraperIntegration()
        self.setup_enhanced_database()
        self.load_existing_dataset()
        
    def setup_enhanced_database(self):
        """Setup enhanced database with additional tables for advanced analytics"""
        cursor = self.scraper.db_conn.cursor()
        
        # Enhanced player analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_player_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                player_tag TEXT,
                map_name TEXT,
                tactical_situation TEXT,
                formation TEXT,
                position_type TEXT,
                entry_rating INTEGER,
                timing_gap REAL,
                formation_score REAL,
                planting_score REAL,
                rotation_score REAL,
                win_rate REAL,
                agents_detected TEXT,
                frame_path TEXT,
                timestamp TIMESTAMP,
                data_source TEXT,
                confidence_score REAL
            )
        ''')
        
        # Match context table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                tournament_name TEXT,
                team_a TEXT,
                team_b TEXT,
                map_name TEXT,
                round_number INTEGER,
                score_a INTEGER,
                score_b INTEGER,
                economy_type TEXT,
                player_positions TEXT,
                tactical_outcome TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        # Agent performance analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_performance_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                map_name TEXT,
                tactical_situation TEXT,
                position_type TEXT,
                success_rate REAL,
                average_kills REAL,
                average_deaths REAL,
                average_assists REAL,
                utility_usage REAL,
                clutch_success_rate REAL,
                entry_success_rate REAL,
                sample_size INTEGER,
                last_updated TIMESTAMP
            )
        ''')
        
        # Meta trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patch_version TEXT,
                map_name TEXT,
                agent_name TEXT,
                pick_rate REAL,
                ban_rate REAL,
                win_rate REAL,
                average_score REAL,
                popularity_trend REAL,
                effectiveness_rating REAL,
                timestamp TIMESTAMP
            )
        ''')
        
        # VOD analysis integration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vod_analysis_integration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vod_url TEXT,
                frame_number INTEGER,
                frame_path TEXT,
                detected_agents TEXT,
                tactical_situation TEXT,
                formation_analysis TEXT,
                performance_metrics TEXT,
                confidence_score REAL,
                processed_timestamp TIMESTAMP,
                ai_analysis TEXT
            )
        ''')
        
        self.scraper.db_conn.commit()
        logger.info("Enhanced database setup complete")
    
    def load_existing_dataset(self):
        """Load and integrate existing dataset"""
        try:
            # Load dataset info
            dataset_info_path = os.path.join(self.dataset_path, "dataset_info.json")
            if os.path.exists(dataset_info_path):
                with open(dataset_info_path, 'r') as f:
                    self.dataset_info = json.load(f)
                logger.info(f"Loaded dataset info: {self.dataset_info['name']}")
            
            # Load existing annotations
            annotations_path = os.path.join(self.dataset_path, "annotations", "auto_annotations.json")
            if os.path.exists(annotations_path):
                with open(annotations_path, 'r') as f:
                    self.existing_annotations = json.load(f)
                logger.info(f"Loaded {len(self.existing_annotations)} existing annotations")
                self.integrate_existing_annotations()
            
            # Load VOD metadata
            vod_metadata_path = os.path.join(self.dataset_path, "vod_metadata.json")
            if os.path.exists(vod_metadata_path):
                with open(vod_metadata_path, 'r') as f:
                    self.vod_metadata = json.load(f)
                logger.info(f"Loaded {len(self.vod_metadata)} VOD metadata entries")
                
        except Exception as e:
            logger.error(f"Error loading existing dataset: {e}")
            self.dataset_info = {}
            self.existing_annotations = {}
            self.vod_metadata = {}
    
    def integrate_existing_annotations(self):
        """Integrate existing annotations into enhanced database"""
        cursor = self.scraper.db_conn.cursor()
        integrated_count = 0
        
        for sample_id, annotation in self.existing_annotations.items():
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO enhanced_player_analytics 
                    (player_name, player_tag, map_name, tactical_situation, formation, 
                     position_type, entry_rating, timing_gap, formation_score, 
                     planting_score, rotation_score, win_rate, agents_detected, 
                     frame_path, timestamp, data_source, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    "dataset_player",  # Placeholder name
                    "dataset",         # Placeholder tag
                    annotation.get('map', 'Unknown'),
                    annotation.get('tactical_situation', 'Unknown'),
                    annotation.get('formation', 'Unknown'),
                    annotation.get('position_type', 'Unknown'),
                    annotation.get('performance_metrics', {}).get('entry_rating', 0),
                    annotation.get('performance_metrics', {}).get('timing_gap', 0.0),
                    annotation.get('performance_metrics', {}).get('formation_score', 0.0),
                    annotation.get('performance_metrics', {}).get('planting_score', 0.0),
                    annotation.get('performance_metrics', {}).get('rotation_score', 0.0),
                    annotation.get('performance_metrics', {}).get('win_rate', 0.0),
                    json.dumps(annotation.get('agents_detected', [])),
                    annotation.get('image_path', ''),
                    datetime.now(),
                    'existing_dataset',
                    0.85  # High confidence for existing curated data
                ))
                integrated_count += 1
                
            except Exception as e:
                logger.warning(f"Error integrating annotation {sample_id}: {e}")
                continue
        
        self.scraper.db_conn.commit()
        logger.info(f"Integrated {integrated_count} existing annotations into enhanced database")
    
    async def collect_live_match_data(self, match_id: str, tournament_name: str = "Unknown") -> Dict:
        """Collect live match data and integrate with dataset"""
        try:
            # Scrape match data
            match_data = await self.integration.scrape_match_data()
            
            if match_data and 'match_data' in match_data:
                cursor = self.scraper.db_conn.cursor()
                
                for match in match_data['match_data']:
                    cursor.execute('''
                        INSERT OR REPLACE INTO match_context 
                        (match_id, tournament_name, map_name, round_number, 
                         score_a, score_b, tactical_outcome, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        match.get('match_id', match_id),
                        tournament_name,
                        match.get('map_name', 'Unknown'),
                        0,  # Round number placeholder
                        0,  # Score placeholders
                        0,
                        'scraped',
                        datetime.now()
                    ))
                
                self.scraper.db_conn.commit()
                logger.info(f"Collected live match data for {match_id}")
                
                return {
                    "status": "success",
                    "matches_collected": len(match_data['match_data']),
                    "match_id": match_id
                }
            
            return {"status": "no_data", "message": "No match data available"}
            
        except Exception as e:
            logger.error(f"Error collecting live match data: {e}")
            return {"status": "error", "message": str(e)}
    
    async def enhance_vod_analysis(self, vod_url: str, analysis_results: Dict) -> Dict:
        """Enhance VOD analysis with scraped data integration"""
        try:
            cursor = self.scraper.db_conn.cursor()
            
            # Extract frame-level analysis
            frame_analysis = analysis_results.get('frame_analysis', [])
            
            for frame_data in frame_analysis:
                cursor.execute('''
                    INSERT OR REPLACE INTO vod_analysis_integration 
                    (vod_url, frame_number, frame_path, detected_agents, 
                     tactical_situation, formation_analysis, performance_metrics, 
                     confidence_score, processed_timestamp, ai_analysis)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    vod_url,
                    frame_data.get('frame_number', 0),
                    frame_data.get('frame_path', ''),
                    json.dumps(frame_data.get('detected_agents', [])),
                    frame_data.get('tactical_situation', 'Unknown'),
                    json.dumps(frame_data.get('formation_analysis', {})),
                    json.dumps(frame_data.get('performance_metrics', {})),
                    frame_data.get('confidence_score', 0.0),
                    datetime.now(),
                    json.dumps(frame_data.get('ai_analysis', {}))
                ))
            
            self.scraper.db_conn.commit()
            logger.info(f"Enhanced VOD analysis for {vod_url}")
            
            return {
                "status": "success",
                "vod_url": vod_url,
                "frames_processed": len(frame_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error enhancing VOD analysis: {e}")
            return {"status": "error", "message": str(e)}
    
    async def generate_meta_trends_analysis(self) -> Dict:
        """Generate comprehensive meta trends analysis"""
        try:
            # Get current meta data
            meta_data = await self.integration.scrape_meta_data()
            
            if not meta_data or 'agent_meta' not in meta_data:
                return {"status": "no_data", "message": "No meta data available"}
            
            cursor = self.scraper.db_conn.cursor()
            current_patch = "8.0"  # Current patch version
            
            for agent in meta_data['agent_meta']:
                cursor.execute('''
                    INSERT OR REPLACE INTO meta_trends 
                    (patch_version, agent_name, pick_rate, ban_rate, 
                     win_rate, average_score, popularity_trend, effectiveness_rating, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    current_patch,
                    agent.get('agent_name', 'Unknown'),
                    agent.get('pick_rate', 0.0),
                    agent.get('ban_rate', 0.0),  # May not be available
                    agent.get('win_rate', 0.0),
                    agent.get('average_score', 0.0),
                    agent.get('popularity_trend', 0.0),
                    agent.get('effectiveness_rating', 0.0),
                    datetime.now()
                ))
            
            self.scraper.db_conn.commit()
            
            # Generate analysis report
            cursor.execute('''
                SELECT agent_name, AVG(pick_rate) as avg_pick_rate, 
                       AVG(win_rate) as avg_win_rate, COUNT(*) as data_points
                FROM meta_trends 
                WHERE patch_version = ?
                GROUP BY agent_name
                ORDER BY avg_pick_rate DESC
            ''', (current_patch,))
            
            trends = cursor.fetchall()
            
            return {
                "status": "success",
                "patch_version": current_patch,
                "trends": [
                    {
                        "agent": row[0],
                        "avg_pick_rate": row[1],
                        "avg_win_rate": row[2],
                        "data_points": row[3]
                    }
                    for row in trends
                ],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating meta trends: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_comprehensive_analytics(self) -> Dict:
        """Get comprehensive analytics from all data sources"""
        cursor = self.scraper.db_conn.cursor()
        
        # Dataset statistics
        cursor.execute('SELECT COUNT(*) FROM enhanced_player_analytics')
        total_analytics = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM match_context')
        total_matches = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM agent_performance_analytics')
        total_agent_performance = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM meta_trends')
        total_meta_trends = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vod_analysis_integration')
        total_vod_frames = cursor.fetchone()[0]
        
        # Map distribution
        cursor.execute('''
            SELECT map_name, COUNT(*) as count 
            FROM enhanced_player_analytics 
            GROUP BY map_name 
            ORDER BY count DESC
        ''')
        map_distribution = cursor.fetchall()
        
        # Tactical situation distribution
        cursor.execute('''
            SELECT tactical_situation, COUNT(*) as count 
            FROM enhanced_player_analytics 
            GROUP BY tactical_situation 
            ORDER BY count DESC
        ''')
        tactical_distribution = cursor.fetchall()
        
        # Performance averages
        cursor.execute('''
            SELECT AVG(entry_rating), AVG(timing_gap), AVG(formation_score), 
                   AVG(planting_score), AVG(rotation_score), AVG(win_rate)
            FROM enhanced_player_analytics
        ''')
        performance_averages = cursor.fetchone()
        
        return {
            "dataset_statistics": {
                "total_analytics": total_analytics,
                "total_matches": total_matches,
                "total_agent_performance": total_agent_performance,
                "total_meta_trends": total_meta_trends,
                "total_vod_frames": total_vod_frames,
                "existing_annotations": len(self.existing_annotations),
                "vod_metadata": len(self.vod_metadata)
            },
            "map_distribution": [
                {"map": row[0], "count": row[1]} for row in map_distribution
            ],
            "tactical_distribution": [
                {"situation": row[0], "count": row[1]} for row in tactical_distribution
            ],
            "performance_averages": {
                "entry_rating": performance_averages[0],
                "timing_gap": performance_averages[1],
                "formation_score": performance_averages[2],
                "planting_score": performance_averages[3],
                "rotation_score": performance_averages[4],
                "win_rate": performance_averages[5]
            },
            "generated_at": datetime.now().isoformat()
        }
    
    async def run_comprehensive_collection_cycle(self) -> Dict:
        """Run comprehensive data collection cycle"""
        logger.info("Starting comprehensive data collection cycle...")
        
        results = {
            "cycle_start": datetime.now().isoformat(),
            "collection_results": {}
        }
        
        try:
            # 1. Collect meta trends
            logger.info("Collecting meta trends...")
            meta_results = await self.generate_meta_trends_analysis()
            results["collection_results"]["meta_trends"] = meta_results
            
            # 2. Collect match data
            logger.info("Collecting match data...")
            match_results = await self.collect_live_match_data("cycle_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
            results["collection_results"]["match_data"] = match_results
            
            # 3. Generate comprehensive analytics
            logger.info("Generating comprehensive analytics...")
            analytics = self.get_comprehensive_analytics()
            results["analytics"] = analytics
            
            results["cycle_end"] = datetime.now().isoformat()
            results["status"] = "success"
            
            logger.info("Comprehensive collection cycle completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in collection cycle: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            results["cycle_end"] = datetime.now().isoformat()
            return results
    
    def export_enhanced_dataset(self, output_path: str = "enhanced_valorant_dataset.json") -> Dict:
        """Export enhanced dataset for training and analysis"""
        try:
            cursor = self.scraper.db_conn.cursor()
            
            # Get all enhanced analytics
            cursor.execute('''
                SELECT * FROM enhanced_player_analytics 
                ORDER BY timestamp DESC
            ''')
            
            analytics_data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            enhanced_dataset = {
                "dataset_info": {
                    "name": "Enhanced Valorant Tactical Dataset",
                    "version": "2.0",
                    "created": datetime.now().isoformat(),
                    "description": "Enhanced dataset with live scraping integration",
                    "total_samples": len(analytics_data),
                    "data_sources": ["existing_dataset", "live_scraping", "vod_analysis"]
                },
                "enhanced_annotations": {}
            }
            
            # Convert to original format with enhancements
            for i, row in enumerate(analytics_data):
                sample_id = f"enhanced_sample_{i}"
                sample_data = dict(zip(columns, row))
                
                enhanced_dataset["enhanced_annotations"][sample_id] = {
                    "map": sample_data.get('map_name', 'Unknown'),
                    "tactical_situation": sample_data.get('tactical_situation', 'Unknown'),
                    "formation": sample_data.get('formation', 'Unknown'),
                    "position_type": sample_data.get('position_type', 'Unknown'),
                    "performance_metrics": {
                        "entry_rating": sample_data.get('entry_rating', 0),
                        "timing_gap": sample_data.get('timing_gap', 0.0),
                        "formation_score": sample_data.get('formation_score', 0.0),
                        "planting_score": sample_data.get('planting_score', 0.0),
                        "rotation_score": sample_data.get('rotation_score', 0.0),
                        "win_rate": sample_data.get('win_rate', 0.0)
                    },
                    "image_path": sample_data.get('frame_path', ''),
                    "frame_number": sample_data.get('id', 0),
                    "enhancements": {
                        "data_source": sample_data.get('data_source', 'unknown'),
                        "confidence_score": sample_data.get('confidence_score', 0.0),
                        "agents_detected": json.loads(sample_data.get('agents_detected', '[]')),
                        "timestamp": sample_data.get('timestamp')
                    }
                }
            
            # Save enhanced dataset
            with open(output_path, 'w') as f:
                json.dump(enhanced_dataset, f, indent=2, default=str)
            
            logger.info(f"Enhanced dataset exported to {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "total_samples": len(analytics_data),
                "file_size": os.path.getsize(output_path)
            }
            
        except Exception as e:
            logger.error(f"Error exporting enhanced dataset: {e}")
            return {"status": "error", "message": str(e)}
    
    def close(self):
        """Close database connections"""
        self.scraper.close()

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_enhanced_collector():
        collector = EnhancedValorantDataCollector()
        
        print("🔍 Testing Enhanced Valorant Data Collector...")
        
        # Test comprehensive analytics
        analytics = collector.get_comprehensive_analytics()
        print(f"📊 Analytics: {analytics}")
        
        # Test collection cycle
        collection_results = await collector.run_comprehensive_collection_cycle()
        print(f"🔄 Collection Results: {collection_results}")
        
        # Test dataset export
        export_results = collector.export_enhanced_dataset()
        print(f"📤 Export Results: {export_results}")
        
        collector.close()
        print("🎉 Enhanced collector test completed!")
    
    asyncio.run(test_enhanced_collector())
