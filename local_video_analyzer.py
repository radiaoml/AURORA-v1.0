import cv2
import numpy as np
import os
from typing import List, Dict, Tuple
from valorant_tactical_engine import ValorantTacticalEngine, TacticalPosition, MovementPath, MapCoordinate, TacticalPattern
import time

class LocalVideoAnalyzer:
    def __init__(self):
        self.tactical_engine = ValorantTacticalEngine()
        self.minimap_region = (0, 0, 200, 200)  # Top-left corner for minimap
        self.ui_colors = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'yellow': (0, 255, 255),
            'white': (255, 255, 255),
            'purple': (128, 0, 128)
        }
        
    def analyze_frames(self, frame_paths: List[str]) -> Dict:
        """Analyze extracted frames for tactical patterns"""
        print(f"[LOCAL_ANALYSIS] Processing {len(frame_paths)} frames...")
        
        all_positions = []
        all_paths = []
        detected_map = "ASCENT"  # Default, will be detected
        detected_agents = []
        
        for i, frame_path in enumerate(frame_paths):
            if not os.path.exists(frame_path):
                continue
                
            frame = cv2.imread(frame_path)
            if frame is None:
                continue
            
            # Detect map from visual features
            if i == 0:  # Only detect map from first frame
                detected_map = self._detect_map(frame)
            
            # Detect agents and positions
            positions, agents = self._detect_agents_and_positions(frame, i)
            all_positions.extend(positions)
            detected_agents.extend(agents)
            
            # Detect movement patterns
            if i > 0:
                paths = self._detect_movement_patterns(all_positions, i)
                all_paths.extend(paths)
        
        # Generate comprehensive tactical analysis
        tactical_analysis = self.tactical_engine.generate_tactical_analysis(
            all_positions, all_paths, detected_map
        )
        
        # Add detected agents to analysis
        tactical_analysis["detected_agents"] = list(set(detected_agents))
        
        print(f"[LOCAL_ANALYSIS] Analysis complete for {detected_map}")
        return tactical_analysis
    
    def _detect_map(self, frame: np.ndarray) -> str:
        """Detect Valorant map from visual features"""
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for map detection
        color_ranges = {
            'ASCENT': {
                'orange': [(10, 100, 100), (25, 255, 255)],  # Orange buildings
                'green': [(40, 50, 50), (80, 255, 255)]     # Green vegetation
            },
            'BIND': {
                'orange': [(10, 100, 100), (25, 255, 255)],  # Moroccan architecture
                'blue': [(100, 100, 100), (130, 255, 255)]   # Blue teleporters
            },
            'HAVEN': {
                'red': [(0, 100, 100), (10, 255, 255)],     # Red temples
                'green': [(40, 50, 50), (80, 255, 255)]     # Green courtyards
            }
        }
        
        # Count color pixels for each map
        map_scores = {}
        for map_name, colors in color_ranges.items():
            score = 0
            for color_name, (lower, upper) in colors.items():
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                score += cv2.countNonZero(mask)
            map_scores[map_name] = score
        
        # Return map with highest score
        detected = max(map_scores, key=map_scores.get)
        print(f"[MAP_DETECTION] Detected: {detected}")
        return detected
    
    def _detect_agents_and_positions(self, frame: np.ndarray, frame_index: int) -> Tuple[List[TacticalPosition], List[str]]:
        """Detect agents and their positions from frame"""
        positions = []
        detected_agents = []
        
        # Extract minimap region
        minimap = frame[self.minimap_region[1]:self.minimap_region[1]+self.minimap_region[3],
                           self.minimap_region[0]:self.minimap_region[0]+self.minimap_region[2]]
        
        # Convert minimap to grayscale
        minimap_gray = cv2.cvtColor(minimap, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to find dots (agent positions)
        _, thresh = cv2.threshold(minimap_gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours (agent positions)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze each contour
        for contour in contours:
            area = cv2.contourArea(contour)
            if 5 < area < 50:  # Filter by size (agent dots on minimap)
                # Get center of contour
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Convert minimap coordinates to world coordinates (0-1000 scale)
                    world_x = (cx / self.minimap_region[2]) * 1000
                    world_y = (cy / self.minimap_region[3]) * 1000
                    
                    # Determine agent based on position and color
                    agent = self._identify_agent_by_position(frame, world_x, world_y)
                    
                    position = TacticalPosition(
                        agent=agent,
                        position=MapCoordinate(world_x, world_y, f"Frame_{frame_index}"),
                        timestamp=f"Frame_{frame_index}",
                        action="position_update"
                    )
                    positions.append(position)
                    detected_agents.append(agent)
        
        return positions, detected_agents
    
    def _identify_agent_by_position(self, frame: np.ndarray, x: float, y: float) -> str:
        """Identify agent based on position and visual cues"""
        # Simplified agent identification based on common positions
        # In production, would use agent-specific visual detection
        
        # Extract region around position for agent detection
        frame_x = int((x / 1000) * frame.shape[1])
        frame_y = int((y / 1000) * frame.shape[0])
        
        # Ensure coordinates are within frame bounds
        frame_x = max(0, min(frame_x, frame.shape[1] - 50))
        frame_y = max(0, min(frame_y, frame.shape[0] - 50))
        
        agent_region = frame[frame_y:frame_y+50, frame_x:frame_x+50]
        
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(agent_region, cv2.COLOR_BGR2HSV)
        
        # Agent color detection (simplified)
        agent_colors = {
            'JETT': [(20, 100, 100), (30, 255, 255)],      # Blue-ish
            'REYNA': [(0, 150, 150), (10, 255, 255)],      # Red-ish
            'SOVA': [(100, 100, 100), (130, 255, 255)],    # Blue-green
            'OMEN': [(150, 50, 50), (170, 255, 255)],      # Purple-ish
            'SAGE': [(0, 0, 200), (10, 50, 255)],          # Green-ish
            'KILLJOY': [(20, 150, 150), (30, 255, 255)],   # Yellow-ish
        }
        
        # Detect dominant color in agent region
        agent_scores = {}
        for agent_name, (lower, upper) in agent_colors.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            score = cv2.countNonZero(mask)
            agent_scores[agent_name] = score
        
        # Return agent with highest score, or random if no clear match
        if agent_scores:
            detected = max(agent_scores, key=agent_scores.get)
            return detected
        else:
            # Random assignment for demonstration
            agents = ['JETT', 'REYNA', 'SOVA', 'OMEN', 'SAGE', 'KILLJOY']
            return agents[frame_index % len(agents)]
    
    def _detect_movement_patterns(self, all_positions: List[TacticalPosition], frame_index: int) -> List[MovementPath]:
        """Detect movement patterns from position history"""
        paths = []
        
        # Get recent positions for movement analysis
        recent_positions = [p for p in all_positions if p.timestamp.startswith(f"Frame_{max(0, frame_index-2)}")]
        current_positions = [p for p in all_positions if p.timestamp == f"Frame_{frame_index}"]
        
        if len(recent_positions) >= 2 and len(current_positions) >= 1:
            for current_pos in current_positions:
                for recent_pos in recent_positions:
                    # Calculate distance between positions
                    distance = ((current_pos.position.x - recent_pos.position.x)**2 + 
                              (current_pos.position.y - recent_pos.position.y)**2)**0.5
                    
                    if distance > 50:  # Significant movement threshold
                        # Determine movement type based on distance and direction
                        path_type = self._classify_movement_type(
                            recent_pos.position, current_pos.position, distance
                        )
                        
                        # Estimate duration based on distance (simplified)
                        duration = distance / 200  # Assume 200 units per second
                        
                        path = MovementPath(
                            start=recent_pos.position,
                            end=current_pos.position,
                            path_type=path_type,
                            duration=duration
                        )
                        paths.append(path)
        
        return paths
    
    def _classify_movement_type(self, start: MapCoordinate, end: MapCoordinate, distance: float) -> TacticalPattern:
        """Classify movement type based on start/end positions"""
        # Calculate movement direction
        dx = end.x - start.x
        dy = end.y - start.y
        
        # Large distance movement = rotation
        if distance > 300:
            return TacticalPattern.ROTATION
        
        # Movement towards center = entry
        if abs(dx) < 100 and abs(dy) < 100:
            return TacticalPattern.ENTRY
        
        # Movement away from center = retreat
        if (start.x > 500 and end.x < 500) or (start.x < 500 and end.x > 500):
            return TacticalPattern.RETREAT
        
        # Default to flank
        return TacticalPattern.FLANK
    
    def generate_spatial_data(self, analysis: Dict) -> Dict:
        """Generate spatial data for visualization"""
        positions = analysis.get("map_control", {}).get("dominant_areas", {})
        
        # Generate mock spatial data based on analysis
        kill_locations = []
        player_positions = []
        movement_paths = []
        
        # Generate kill locations based on map control
        if "Aggressive Entry Position" in positions:
            kill_locations.extend([
                {"x": 650, "y": 350, "area": "A Main"},
                {"x": 700, "y": 300, "area": "A Site"}
            ])
        
        if "Defensive Anchor Position" in positions:
            kill_locations.extend([
                {"x": 350, "y": 700, "area": "B Site"},
                {"x": 300, "y": 650, "area": "B Heaven"}
            ])
        
        # Generate player positions
        detected_agents = analysis.get("detected_agents", [])
        for i, agent in enumerate(detected_agents[:5]):  # Max 5 agents
            x = 200 + (i * 150)
            y = 200 + (i * 100)
            player_positions.append({
                "agent": agent,
                "x": x,
                "y": y,
                "timestamp": "Live"
            })
        
        # Generate movement paths
        movement_patterns = analysis.get("movement_patterns", {}).get("common_patterns", [])
        for i, pattern in enumerate(movement_patterns[:3]):  # Max 3 paths
            if pattern == "entry":
                start_x, start_y = 800, 100
                end_x, end_y = 600, 400
            elif pattern == "rotation":
                start_x, start_y = 500, 500
                end_x, end_y = 300, 300
            else:  # flank
                start_x, start_y = 100, 800
                end_x, end_y = 400, 400
            
            movement_paths.append({
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "type": pattern
            })
        
        return {
            "kill_locations": kill_locations,
            "player_positions": player_positions,
            "movement_paths": movement_paths,
            "detected_agents": detected_agents
        }

if __name__ == "__main__":
    # Test the local analyzer
    analyzer = LocalVideoAnalyzer()
    
    # Test with mock frame paths
    test_frames = ["frame_0.jpg", "frame_1.jpg", "frame_2.jpg"]
    analysis = analyzer.analyze_frames(test_frames)
    
    print("Local Analysis Results:")
    print(f"Detected Map: {analysis.get('detected_map')}")
    print(f"Detected Agents: {analysis.get('detected_agents')}")
    print(f"Entry Rating: {analysis.get('performance_metrics', {}).get('entry_rating')}")
    print(f"Win Rate Prediction: {analysis.get('performance_metrics', {}).get('win_rate_prediction')}")
