"""
AURORA Valorant Data Scraper
Comprehensive Valorant data collection and analysis system
"""

import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValorantDataScraper:
    """Main Valorant data scraping engine"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.db_conn = sqlite3.connect('valorant_data.db')
        self.setup_database()
        
    def setup_database(self):
        """Setup database for storing scraped data"""
        cursor = self.db_conn.cursor()
        
        # Player stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                player_tag TEXT,
                rank TEXT,
                tier INTEGER,
                win_rate REAL,
                kd_ratio REAL,
                headshot_pct REAL,
                agents_played TEXT,
                last_updated TIMESTAMP,
                source TEXT
            )
        ''')
        
        # Match data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                map_name TEXT,
                game_mode TEXT,
                score TEXT,
                duration INTEGER,
                player_stats TEXT,
                timestamp TIMESTAMP,
                source TEXT
            )
        ''')
        
        # Agent meta data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_meta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                pick_rate REAL,
                win_rate REAL,
                kd_average REAL,
                role TEXT,
                patch_version TEXT,
                last_updated TIMESTAMP,
                source TEXT
            )
        ''')
        
        # Map statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS map_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                map_name TEXT,
                attack_win_rate REAL,
                defense_win_rate REAL,
                average_duration INTEGER,
                popular_agents TEXT,
                patch_version TEXT,
                last_updated TIMESTAMP,
                source TEXT
            )
        ''')
        
        self.db_conn.commit()
        logger.info("Database setup complete")
    
    def scrape_tracker_gg_player(self, player_name: str, player_tag: str) -> Optional[Dict]:
        """Scrape player data from tracker.gg"""
        try:
            url = f"https://tracker.gg/valorant/profile/riot/{player_name}%23{player_tag}/overview"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {player_name}#{player_tag} from tracker.gg")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract rank information
            rank_element = soup.find('div', class_='rank')
            rank = rank_element.text.strip() if rank_element else "Unknown"
            
            # Extract stats
            stats = {
                'player_name': player_name,
                'player_tag': player_tag,
                'rank': rank,
                'win_rate': self.extract_stat(soup, 'Win Rate'),
                'kd_ratio': self.extract_stat(soup, 'K/D Ratio'),
                'headshot_pct': self.extract_stat(soup, 'Headshot %'),
                'agents_played': self.extract_agents(soup),
                'last_updated': datetime.now(),
                'source': 'tracker.gg'
            }
            
            # Store in database
            self.store_player_stats(stats)
            return stats
            
        except Exception as e:
            logger.error(f"Error scraping {player_name}#{player_tag}: {e}")
            return None
    
    def extract_stat(self, soup, stat_name):
        """Extract specific stat from page"""
        try:
            stat_elements = soup.find_all('span', class_='stat')
            for element in stat_elements:
                if stat_name in element.text:
                    value = element.find_next('span', class_='value')
                    if value:
                        return self.parse_stat_value(value.text)
            return 0.0
        except:
            return 0.0
    
    def parse_stat_value(self, value_str):
        """Parse stat value string to float"""
        try:
            # Remove % and other characters, convert to float
            cleaned = re.sub(r'[^\d.]', '', value_str)
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    def extract_agents(self, soup):
        """Extract agent information"""
        try:
            agents = []
            agent_elements = soup.find_all('div', class_='agent')
            for element in agent_elements:
                agent_name = element.find('span', class_='name')
                if agent_name:
                    agents.append(agent_name.text.strip())
            return ','.join(agents) if agents else ""
        except:
            return ""
    
    def scrape_blitz_gg_meta(self) -> List[Dict]:
        """Scrape agent meta data from blitz.gg"""
        try:
            url = "https://blitz.gg/valorant/stats"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning("Failed to fetch meta data from blitz.gg")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            agents = []
            agent_elements = soup.find_all('div', class_='agent-stat')
            
            for element in agent_elements:
                try:
                    agent_data = {
                        'agent_name': self.extract_text(element, 'agent-name'),
                        'pick_rate': self.extract_stat_value(element, 'pick-rate'),
                        'win_rate': self.extract_stat_value(element, 'win-rate'),
                        'kd_average': self.extract_stat_value(element, 'kd-average'),
                        'role': self.extract_text(element, 'agent-role'),
                        'patch_version': 'current',
                        'last_updated': datetime.now(),
                        'source': 'blitz.gg'
                    }
                    agents.append(agent_data)
                except Exception as e:
                    logger.warning(f"Error parsing agent data: {e}")
                    continue
            
            # Store in database
            for agent in agents:
                self.store_agent_meta(agent)
            
            return agents
            
        except Exception as e:
            logger.error(f"Error scraping blitz.gg meta: {e}")
            return []
    
    def extract_text(self, element, class_name):
        """Extract text from element with specific class"""
        try:
            text_element = element.find('div', class_=class_name)
            return text_element.text.strip() if text_element else ""
        except:
            return ""
    
    def extract_stat_value(self, element, class_name):
        """Extract stat value from element"""
        try:
            stat_element = element.find('div', class_=class_name)
            if stat_element:
                return self.parse_stat_value(stat_element.text)
            return 0.0
        except:
            return 0.0
    
    def scrape_vct_matches(self) -> List[Dict]:
        """Scrape VCT match data"""
        try:
            url = "https://www.vct.gg/matches"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning("Failed to fetch VCT matches")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            matches = []
            match_elements = soup.find_all('div', class_='match-card')
            
            for element in match_elements:
                try:
                    match_data = {
                        'match_id': self.extract_match_id(element),
                        'map_name': self.extract_text(element, 'map-name'),
                        'game_mode': 'Competitive',
                        'score': self.extract_text(element, 'score'),
                        'duration': self.extract_duration(element),
                        'player_stats': self.extract_match_players(element),
                        'timestamp': datetime.now(),
                        'source': 'vct.gg'
                    }
                    matches.append(match_data)
                except Exception as e:
                    logger.warning(f"Error parsing match data: {e}")
                    continue
            
            # Store in database
            for match in matches:
                self.store_match_data(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error scraping VCT matches: {e}")
            return []
    
    def extract_match_id(self, element):
        """Extract match ID"""
        try:
            link = element.find('a', href=True)
            if link:
                return link['href'].split('/')[-1]
            return f"match_{int(time.time())}"
        except:
            return f"match_{int(time.time())}"
    
    def extract_duration(self, element):
        """Extract match duration"""
        try:
            duration_element = element.find('span', class_='duration')
            if duration_element:
                duration_text = duration_element.text.strip()
                # Parse "24:35" format to seconds
                parts = duration_text.split(':')
                return int(parts[0]) * 60 + int(parts[1])
            return 0
        except:
            return 0
    
    def extract_match_players(self, element):
        """Extract player statistics from match"""
        try:
            players = []
            player_elements = element.find_all('div', class_='player-stat')
            
            for player_element in player_elements:
                player_data = {
                    'name': self.extract_text(player_element, 'player-name'),
                    'kills': self.extract_stat_value(player_element, 'kills'),
                    'deaths': self.extract_stat_value(player_element, 'deaths'),
                    'assists': self.extract_stat_value(player_element, 'assists'),
                    'agent': self.extract_text(player_element, 'agent')
                }
                players.append(player_data)
            
            return json.dumps(players)
        except:
            return "[]"
    
    def store_player_stats(self, stats: Dict):
        """Store player statistics in database"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO player_stats 
            (player_name, player_tag, rank, win_rate, kd_ratio, headshot_pct, agents_played, last_updated, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stats['player_name'],
            stats['player_tag'],
            stats['rank'],
            stats['win_rate'],
            stats['kd_ratio'],
            stats['headshot_pct'],
            stats['agents_played'],
            stats['last_updated'],
            stats['source']
        ))
        self.db_conn.commit()
    
    def store_agent_meta(self, agent_data: Dict):
        """Store agent meta data in database"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO agent_meta 
            (agent_name, pick_rate, win_rate, kd_average, role, patch_version, last_updated, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent_data['agent_name'],
            agent_data['pick_rate'],
            agent_data['win_rate'],
            agent_data['kd_average'],
            agent_data['role'],
            agent_data['patch_version'],
            agent_data['last_updated'],
            agent_data['source']
        ))
        self.db_conn.commit()
    
    def store_match_data(self, match_data: Dict):
        """Store match data in database"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO match_data 
            (match_id, map_name, game_mode, score, duration, player_stats, timestamp, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_data['match_id'],
            match_data['map_name'],
            match_data['game_mode'],
            match_data['score'],
            match_data['duration'],
            match_data['player_stats'],
            match_data['timestamp'],
            match_data['source']
        ))
        self.db_conn.commit()
    
    def get_player_stats(self, player_name: str, player_tag: str) -> Optional[Dict]:
        """Get player statistics from database"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT * FROM player_stats 
            WHERE player_name = ? AND player_tag = ?
            ORDER BY last_updated DESC
            LIMIT 1
        ''', (player_name, player_tag))
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_agent_meta(self) -> List[Dict]:
        """Get agent meta data from database"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT * FROM agent_meta 
            ORDER BY pick_rate DESC
        ''')
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_recent_matches(self, limit: int = 10) -> List[Dict]:
        """Get recent match data"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT * FROM match_data 
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def analyze_player_trends(self, player_name: str, player_tag: str) -> Dict:
        """Analyze player performance trends"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT * FROM player_stats 
            WHERE player_name = ? AND player_tag = ?
            ORDER BY last_updated DESC
            LIMIT 10
        ''', (player_name, player_tag))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        history = [dict(zip(columns, row)) for row in rows]
        
        if len(history) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trends
        recent = history[0]
        previous = history[1]
        
        trends = {
            "rank_trend": self.compare_rank(recent['rank'], previous['rank']),
            "win_rate_trend": recent['win_rate'] - previous['win_rate'],
            "kd_trend": recent['kd_ratio'] - previous['kd_ratio'],
            "headshot_trend": recent['headshot_pct'] - previous['headshot_pct'],
            "data_points": len(history),
            "last_updated": recent['last_updated']
        }
        
        return trends
    
    def compare_rank(self, current_rank: str, previous_rank: str) -> str:
        """Compare rank progression"""
        rank_order = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Immortal", "Radiant"]
        
        try:
            current_idx = rank_order.index(current_rank.split()[0])
            previous_idx = rank_order.index(previous_rank.split()[0])
            
            if current_idx > previous_idx:
                return "up"
            elif current_idx < previous_idx:
                return "down"
            else:
                return "same"
        except:
            return "unknown"
    
    def generate_meta_report(self) -> Dict:
        """Generate comprehensive meta analysis report"""
        agent_meta = self.get_agent_meta()
        recent_matches = self.get_recent_matches(50)
        
        # Agent popularity analysis
        top_agents = sorted(agent_meta, key=lambda x: x['pick_rate'], reverse=True)[:5]
        
        # Map analysis
        map_stats = {}
        for match in recent_matches:
            map_name = match['map_name']
            if map_name not in map_stats:
                map_stats[map_name] = {'count': 0, 'total_duration': 0}
            map_stats[map_name]['count'] += 1
            map_stats[map_name]['total_duration'] += match['duration']
        
        report = {
            "generated_at": datetime.now(),
            "top_agents": top_agents,
            "map_statistics": map_stats,
            "total_matches_analyzed": len(recent_matches),
            "agents_tracked": len(agent_meta),
            "data_freshness": self.get_data_freshness()
        }
        
        return report
    
    def get_data_freshness(self) -> Dict:
        """Check data freshness across all sources"""
        cursor = self.db_conn.cursor()
        
        # Get latest update times
        cursor.execute('SELECT MAX(last_updated) FROM player_stats')
        latest_player = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(last_updated) FROM agent_meta')
        latest_meta = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(timestamp) FROM match_data')
        latest_match = cursor.fetchone()[0]
        
        # Handle empty case
        all_dates = [date for date in [latest_player, latest_meta, latest_match] if date is not None]
        overall_fresh = max(all_dates) if all_dates else None
        
        return {
            "player_data": latest_player,
            "meta_data": latest_meta,
            "match_data": latest_match,
            "overall_fresh": overall_fresh
        }
    
    def run_full_scrape(self):
        """Run complete scraping cycle"""
        logger.info("Starting full Valorant data scrape...")
        
        # Scrape meta data
        meta_data = self.scrape_blitz_gg_meta()
        logger.info(f"Scraped {len(meta_data)} agent meta entries")
        
        # Scrape VCT matches
        match_data = self.scrape_vct_matches()
        logger.info(f"Scraped {len(match_data)} VCT matches")
        
        # Generate report
        report = self.generate_meta_report()
        logger.info("Meta analysis report generated")
        
        return report
    
    def close(self):
        """Close database connection"""
        self.db_conn.close()

# Example usage and testing
if __name__ == "__main__":
    scraper = ValorantDataScraper()
    
    # Test player scraping
    print("Testing player data scrape...")
    player_data = scraper.scrape_tracker_gg_player("TenZ", "1234")
    if player_data:
        print(f"Player data: {player_data}")
    
    # Test meta scraping
    print("\nTesting meta data scrape...")
    meta_data = scraper.scrape_blitz_gg_meta()
    print(f"Meta data entries: {len(meta_data)}")
    
    # Test VCT scraping
    print("\nTesting VCT match scrape...")
    match_data = scraper.scrape_vct_matches()
    print(f"Match data entries: {len(match_data)}")
    
    # Generate report
    print("\nGenerating meta report...")
    report = scraper.generate_meta_report()
    print(f"Report: {report}")
    
    scraper.close()
