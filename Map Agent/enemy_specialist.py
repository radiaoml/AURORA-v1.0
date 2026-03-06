import cv2
import numpy as np
from PIL import Image
import io

class EnemySpecialist:
    def __init__(self):
        # Valorant Enemy Red is usually bright and saturated.
        # Primary red dots: HSV ~ (0, 200, 200) to (10, 255, 255)
        # And also wrapping around: (170, 200, 200) to (180, 255, 255)
        self.lower_red1 = np.array([0, 150, 150])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([160, 150, 150])
        self.upper_red2 = np.array([180, 255, 255])

    def detect_enemies(self, minimap_pil: Image.Image) -> dict:
        """
        Analyzes a cropped minimap for red enemy icons/cones.
        Returns: { 'enemy_detected': bool, 'enemy_count': int, 'threat_level': str }
        """
        try:
            # Convert PIL to OpenCV (BGR)
            img_cv = cv2.cvtColor(np.array(minimap_pil), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

            # Mask for red
            mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
            mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
            mask = cv2.add(mask1, mask2)

            # Noise reduction
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # Find contours (blobs)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter by area (ignore tiny specks, focus on dots)
            enemy_blobs = [c for c in contours if cv2.contourArea(c) > 5]
            count = len(enemy_blobs)

            threat = "NONE"
            if count == 1: threat = "LOW (STRAY)"
            elif count == 2: threat = "MEDIUM (DUO)"
            elif count >= 3: threat = "HIGH (EXECUTE)"

            return {
                "enemy_detected": count > 0,
                "enemy_count": count,
                "threat_level": threat,
                "status_msg": "‼️ HOSTILE DETECTED" if count > 0 else "🟢 SECTOR CLEAR"
            }
        except Exception as e:
            print(f"⚠️ Enemy Detection failed: {e}")
            return {
                "enemy_detected": False,
                "enemy_count": 0,
                "threat_level": "UNKNOWN",
                "status_msg": "📡 SENSOR OFFLINE"
            }

if __name__ == "__main__":
    # Test stub
    pass
