import cv2
import numpy as np

def create_tactical_mock(map_name, color, filename):
    # Create a dark background
    img = np.zeros((600, 800, 3), dtype=np.uint8) + 15
    
    # Add a title
    cv2.putText(img, f"TACTICAL_DATA: {map_name}", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 1, color, 2)
    
    # Add some random "clusters" (Heatmap mock)
    for _ in range(15):
        x, y = np.random.randint(50, 750), np.random.randint(100, 550)
        cv2.circle(img, (x, y), np.random.randint(10, 40), (0, 0, 255), -1) # Red heat
        
    # Add some random "trajectories" (Movement mock)
    for _ in range(5):
        pts = np.array([[np.random.randint(50, 750), np.random.randint(100, 550)] for _ in range(4)])
        cv2.polylines(img, [pts], False, (255, 245, 0), 2) # Cyan/Yellow paths
        
    # Add grid lines
    for i in range(0, 800, 100):
        cv2.line(img, (i, 0), (i, 600), (40, 40, 40), 1)
    for i in range(0, 600, 100):
        cv2.line(img, (0, i), (800, i), (40, 40, 40), 1)
        
    cv2.imwrite(filename, img)
    print(f"[SUCCESS] Generated {filename}")

if __name__ == "__main__":
    create_tactical_mock("BIND", (0, 245, 212), "bind_tactical_data_mock.png")
    create_tactical_mock("HAVEN", (255, 70, 85), "haven_tactical_data_mock.png")
