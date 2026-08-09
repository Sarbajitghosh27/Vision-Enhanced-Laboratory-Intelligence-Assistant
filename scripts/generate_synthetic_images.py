"""
scripts/generate_synthetic_images.py
Automated generator for synthetic breadboard datasets.
Renders circuit layouts using OpenCV and exports YOLOv8 text annotations.
"""

import os
import cv2
import numpy as np
import random

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "synthetic_dataset"))
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
LABELS_DIR = os.path.join(OUTPUT_DIR, "labels")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LABELS_DIR, exist_ok=True)

# YOLO class IDs
# 0: resistor, 1: diode, 2: led, 3: jumper_wire, 4: ic_chip

def draw_breadboard_background(w=640, h=480) -> np.ndarray:
    """Draws a synthetic breadboard with grid points and red/blue power rails."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = (245, 245, 245) # Off-white background
    
    # Draw red/blue rails at the top
    cv2.line(img, (20, 20), (w-20, 20), (50, 50, 200), 2)  # Blue rail
    cv2.line(img, (20, 30), (w-20, 30), (50, 200, 50), 2)  # Red rail
    
    # Draw red/blue rails at the bottom
    cv2.line(img, (20, h-30), (w-20, h-30), (50, 200, 50), 2)
    cv2.line(img, (20, h-20), (w-20, h-20), (50, 50, 200), 2)
    
    # Draw breadboard tie points grid (5x64 points)
    for x in range(40, w-40, 20):
        for y in range(60, h-60, 20):
            # Draw a tiny gray dot representing tie socket hole
            cv2.circle(img, (x, y), 2, (180, 180, 180), -1)
            
    # Draw divider trench in the middle
    cv2.rectangle(img, (15, h//2 - 10), (w-15, h//2 + 10), (220, 220, 220), -1)
    
    return img


def generate_samples(num_samples=30):
    """Generates synthetic images with annotated labels."""
    print(f"Generating {num_samples} synthetic breadboard layouts...")
    
    for i in range(num_samples):
        img = draw_breadboard_background()
        h_img, w_img, _ = img.shape
        labels_file_lines = []
        
        # Inject Resistors (YOLO ID: 0)
        num_resistors = random.randint(1, 3)
        for _ in range(num_resistors):
            rx = random.randint(80, 500)
            ry = random.randint(80, 200)
            rw, rh = 60, 14
            # Draw beige resistor body
            cv2.rectangle(img, (rx, ry), (rx+rw, ry+rh), (180, 210, 230), -1)
            # Draw color bands (brown, black, red)
            cv2.rectangle(img, (rx+10, ry), (rx+14, ry+rh), (42, 42, 165), -1)   # Brown
            cv2.rectangle(img, (rx+20, ry), (rx+24, ry+rh), (0, 0, 0), -1)       # Black
            cv2.rectangle(img, (rx+30, ry), (rx+34, ry+rh), (0, 0, 255), -1)     # Red
            
            # Normalize for YOLO annotation format
            cx = (rx + rw/2) / w_img
            cy = (ry + rh/2) / h_img
            nw = rw / w_img
            nh = rh / h_img
            labels_file_lines.append(f"0 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")
            
        # Inject Diodes (YOLO ID: 1)
        num_diodes = random.randint(1, 2)
        for d_idx in range(num_diodes):
            dx = random.randint(80, 500)
            dy = random.randint(240, 400)
            dw, dh = 50, 16
            
            # Simulate reversed polarity fault randomly
            fault = random.choice([True, False])
            
            # Draw dark grey diode body
            cv2.rectangle(img, (dx, dy), (dx+dw, dy+dh), (40, 40, 40), -1)
            
            if fault:
                # Silver band cathode drawn on the wrong side (left instead of right)
                cv2.rectangle(img, (dx+5, dy), (dx+11, dy+dh), (200, 200, 200), -1)
            else:
                # Normal silver band cathode on the right side
                cv2.rectangle(img, (dx+dw-11, dy), (dx+dw-5, dy+dh), (200, 200, 200), -1)
                
            # Normalize coordinates
            cx = (dx + dw/2) / w_img
            cy = (dy + dh/2) / h_img
            nw = dw / w_img
            nh = dh / h_img
            labels_file_lines.append(f"1 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

        # Inject Jumper Wires (YOLO ID: 3)
        num_wires = random.randint(2, 4)
        for _ in range(num_wires):
            wx1 = random.randint(40, 600)
            wy1 = random.randint(40, 440)
            wx2 = wx1 + random.randint(-150, 150)
            wy2 = wy1 + random.randint(-150, 150)
            wx2 = max(min(wx2, w_img-10), 10)
            wy2 = max(min(wy2, h_img-10), 10)
            
            color = random.choice([(0, 255, 255), (255, 0, 0), (0, 165, 255)]) # Yellow, Blue, Orange
            cv2.line(img, (wx1, wy1), (wx2, wy2), color, 3)
            
            # Wire box bounding box
            min_x, max_x = min(wx1, wx2), max(wx1, wx2)
            min_y, max_y = min(wy1, wy2), max(wy1, wy2)
            ww = max(max_x - min_x, 8)
            wh = max(max_y - min_y, 8)
            
            cx = (min_x + ww/2) / w_img
            cy = (min_y + wh/2) / h_img
            nw = ww / w_img
            nh = wh / h_img
            labels_file_lines.append(f"3 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

        # Save Image & Labels
        img_name = f"breadboard_sample_{i:04d}.jpg"
        txt_name = f"breadboard_sample_{i:04d}.txt"
        
        cv2.imwrite(os.path.join(IMAGES_DIR, img_name), img)
        with open(os.path.join(LABELS_DIR, txt_name), "w") as f:
            f.writelines(labels_file_lines)

    print(f"Synthetic generation complete! Saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_samples()
