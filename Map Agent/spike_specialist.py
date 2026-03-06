import cv2
import numpy as np
from PIL import Image
import io

class SpikeSpecialist:
    def __init__(self):
        # Spike Red (blinking/planted)
        self.lower_red1 = np.array([0, 160, 160])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([170, 160, 160])
        self.upper_red2 = np.array([180, 255, 255])
        
        # Spike Yellow (held/dropped)
        self.lower_yellow = np.array([20, 150, 150])
        self.upper_yellow = np.array([35, 255, 255])

    def detect_spike(self, full_img_pil: Image.Image, minimap_pil: Image.Image) -> dict:
        """
        Analyzes the top HUD and Minimap for Spike status and location.
        """
        try:
            w, h = full_img_pil.size
            
            # 1. Crop Top HUD (Center timer/spike area)
            # Standard 1080p: Center is 960. Range 880-1040.
            hx = int(w * 0.46)
            hy = int(h * 0.01)
            hw = int(w * 0.08)
            hh = int(h * 0.06)
            hud_crop = full_img_pil.crop((hx, hy, hx+hw, hy+hh))
            
            # Convert to CV2
            hud_cv = cv2.cvtColor(np.array(hud_crop), cv2.COLOR_RGB2BGR)
            hud_hsv = cv2.cvtColor(hud_cv, cv2.COLOR_BGR2HSV)
            
            # Check for Red in HUD (Planted/Blinking)
            mask_r1 = cv2.inRange(hud_hsv, self.lower_red1, self.upper_red1)
            mask_r2 = cv2.inRange(hud_hsv, self.lower_red2, self.upper_red2)
            hud_red_mask = cv2.add(mask_r1, mask_r2)
            
            red_pixels = cv2.countNonZero(hud_red_mask)
            is_planted = red_pixels > 50 # Threshold for the red icon
            
            # 2. Check Minimap for Spike Icon (Red if planted, Yellow if dropped)
            mini_cv = cv2.cvtColor(np.array(minimap_pil), cv2.COLOR_RGB2BGR)
            mini_hsv = cv2.cvtColor(mini_cv, cv2.COLOR_BGR2HSV)
            
            # Red on minimap
            m_mask_r1 = cv2.inRange(mini_hsv, self.lower_red1, self.upper_red1)
            m_mask_r2 = cv2.inRange(mini_hsv, self.lower_red2, self.upper_red2)
            mini_red_mask = cv2.add(m_mask_r1, m_mask_r2)
            
            # Yellow on minimap (Dropped)
            mini_yellow_mask = cv2.inRange(mini_hsv, self.lower_yellow, self.upper_yellow)
            
            red_mini_pixels = cv2.countNonZero(mini_red_mask)
            yellow_mini_pixels = cv2.countNonZero(mini_yellow_mask)
            
            status = "🕒 PRE-PLANT"
            location = "UNKNOWN"
            
            if is_planted or red_mini_pixels > 20:
                status = "⚠️ SPIKE PLANTED"
                is_planted = True
                # Location estimation would usually come from the spatial oracle/coordinates
            elif yellow_mini_pixels > 20:
                status = "📍 SPIKE DROPPED"
            
            return {
                "is_planted": is_planted,
                "status_msg": status,
                "red_hud_signal": int(red_pixels),
                "mini_signal": int(max(red_mini_pixels, yellow_mini_pixels))
            }

        except Exception as e:
            print(f"⚠️ Spike Specialist failed: {e}")
            return {
                "is_planted": False,
                "status_msg": "📡 SENSOR ERROR",
                "red_hud_signal": 0,
                "mini_signal": 0
            }

if __name__ == "__main__":
    pass
