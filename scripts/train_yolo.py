"""
scripts/train_yolo.py
Generates a synthetic breadboard dataset including resistors, diodes, LEDs, jumper wires, IC chips, and capacitors.
Trains a YOLOv8n model and exports it to ONNX format for lightweight local backend inference.
"""

import os
import cv2
import numpy as np
import random
import shutil

# Paths configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(BASE_DIR, "static", "synthetic_dataset")
TRAIN_IMG_DIR = os.path.join(DATASET_DIR, "images", "train")
TRAIN_LBL_DIR = os.path.join(DATASET_DIR, "labels", "train")
VAL_IMG_DIR = os.path.join(DATASET_DIR, "images", "val")
VAL_LBL_DIR = os.path.join(DATASET_DIR, "labels", "val")

os.makedirs(TRAIN_IMG_DIR, exist_ok=True)
os.makedirs(TRAIN_LBL_DIR, exist_ok=True)
os.makedirs(VAL_IMG_DIR, exist_ok=True)
os.makedirs(VAL_LBL_DIR, exist_ok=True)

# YOLO class IDs
# 0: resistor, 1: diode, 2: led, 3: jumper_wire, 4: ic_chip, 5: capacitor

def draw_breadboard_background(w=640, h=480) -> np.ndarray:
    """Draws a synthetic breadboard with grid points and power rails."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = (245, 245, 245) # Off-white background
    
    # Draw rails
    cv2.line(img, (20, 20), (w-20, 20), (50, 50, 200), 2)  # Blue rail
    cv2.line(img, (20, 30), (w-20, 30), (50, 200, 50), 2)  # Red rail
    cv2.line(img, (20, h-30), (w-20, h-30), (50, 200, 50), 2)
    cv2.line(img, (20, h-20), (w-20, h-20), (50, 50, 200), 2)
    
    # Draw grid sockets
    for x in range(40, w-40, 20):
        for y in range(60, h-60, 20):
            cv2.circle(img, (x, y), 2, (180, 180, 180), -1)
            
    # Draw divider trench in the middle
    cv2.rectangle(img, (15, h//2 - 10), (w-15, h//2 + 10), (220, 220, 220), -1)
    return img

def generate_dataset_split(img_dir, lbl_dir, num_samples):
    """Generates synthetic samples and labels for a specific data split."""
    for i in range(num_samples):
        img = draw_breadboard_background()
        h_img, w_img, _ = img.shape
        labels_lines = []
        
        # 0. Resistors
        num_resistors = random.randint(1, 3)
        for _ in range(num_resistors):
            rx = random.randint(80, 500)
            ry = random.randint(80, 200)
            rw, rh = 60, 14
            cv2.rectangle(img, (rx, ry), (rx+rw, ry+rh), (180, 210, 230), -1)
            cv2.rectangle(img, (rx+10, ry), (rx+14, ry+rh), (42, 42, 165), -1)   # Brown band
            cv2.rectangle(img, (rx+20, ry), (rx+24, ry+rh), (0, 0, 0), -1)       # Black band
            cv2.rectangle(img, (rx+30, ry), (rx+34, ry+rh), (0, 0, 255), -1)     # Red band
            
            cx = (rx + rw/2) / w_img
            cy = (ry + rh/2) / h_img
            nw = rw / w_img
            nh = rh / h_img
            labels_lines.append(f"0 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")
            
        # 1. Diodes
        num_diodes = random.randint(0, 2)
        for _ in range(num_diodes):
            dx = random.randint(80, 500)
            dy = random.randint(240, 400)
            dw, dh = 50, 16
            fault = random.choice([True, False])
            
            # Dark grey diode body
            cv2.rectangle(img, (dx, dy), (dx+dw, dy+dh), (40, 40, 40), -1)
            if fault:
                cv2.rectangle(img, (dx+5, dy), (dx+11, dy+dh), (200, 200, 200), -1) # Cathode on left
            else:
                cv2.rectangle(img, (dx+dw-11, dy), (dx+dw-5, dy+dh), (200, 200, 200), -1) # Cathode on right
                
            cx = (dx + dw/2) / w_img
            cy = (dy + dh/2) / h_img
            nw = dw / w_img
            nh = dh / h_img
            labels_lines.append(f"1 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

        # 4. IC Chips (Opamps)
        if random.choice([True, False]):
            cx_chip = random.randint(200, 400)
            cy_chip = h_img // 2 - 20
            cw_chip, ch_chip = 80, 40
            # Draw black IC block
            cv2.rectangle(img, (cx_chip, cy_chip), (cx_chip+cw_chip, cy_chip+ch_chip), (30, 30, 30), -1)
            # Notch on left side
            cv2.circle(img, (cx_chip, cy_chip + ch_chip//2), 6, (200, 200, 200), -1)
            # Pins
            for px in range(cx_chip + 10, cx_chip + cw_chip - 10, 15):
                cv2.rectangle(img, (px, cy_chip-8), (px+6, cy_chip), (200, 200, 200), -1)
                cv2.rectangle(img, (px, cy_chip+ch_chip), (px+6, cy_chip+ch_chip+8), (200, 200, 200), -1)
                
            cx = (cx_chip + cw_chip/2) / w_img
            cy = (cy_chip + ch_chip/2) / h_img
            nw = cw_chip / w_img
            nh = ch_chip / h_img
            labels_lines.append(f"4 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

        # 5. Capacitors (Electrolytic or Ceramic disk)
        num_caps = random.randint(0, 2)
        for _ in range(num_caps):
            cap_type = random.choice(["ceramic", "electrolytic"])
            cx_cap = random.randint(80, 500)
            cy_cap = random.randint(100, 380)
            
            if cap_type == "ceramic":
                cw_cap, ch_cap = 24, 24
                # Draw circular orange disc
                cv2.circle(img, (cx_cap + 12, cy_cap + 12), 12, (80, 160, 240), -1) # Light brown/orange BGR: (80,160,240)
                # Drawing leads
                cv2.line(img, (cx_cap+6, cy_cap+24), (cx_cap+6, cy_cap+36), (150, 150, 150), 2)
                cv2.line(img, (cx_cap+18, cy_cap+24), (cx_cap+18, cy_cap+36), (150, 150, 150), 2)
            else:
                cw_cap, ch_cap = 20, 32
                # Draw blue cylindrical capacitor body
                cv2.rectangle(img, (cx_cap, cy_cap), (cx_cap+cw_cap, cy_cap+ch_cap), (200, 50, 50), -1) # Blue BGR: (200, 50, 50)
                # Draw white negative stripe
                cv2.rectangle(img, (cx_cap+12, cy_cap), (cx_cap+18, cy_cap+ch_cap), (240, 240, 240), -1)
                # Leads
                cv2.line(img, (cx_cap+5, cy_cap+ch_cap), (cx_cap+5, cy_cap+ch_cap+12), (150, 150, 150), 2)
                cv2.line(img, (cx_cap+15, cy_cap+ch_cap), (cx_cap+15, cy_cap+ch_cap+12), (150, 150, 150), 2)

            cx = (cx_cap + cw_cap/2) / w_img
            cy = (cy_cap + ch_cap/2) / h_img
            nw = cw_cap / w_img
            nh = ch_cap / h_img
            labels_lines.append(f"5 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

        # 3. Jumper Wires
        num_wires = random.randint(2, 5)
        for _ in range(num_wires):
            wx1 = random.randint(40, 600)
            wy1 = random.randint(40, 440)
            wx2 = wx1 + random.randint(-120, 120)
            wy2 = wy1 + random.randint(-120, 120)
            wx2 = max(min(wx2, w_img-10), 10)
            wy2 = max(min(wy2, h_img-10), 10)
            
            color = random.choice([(0, 255, 255), (255, 0, 0), (0, 165, 255)]) # Yellow, Blue, Orange
            cv2.line(img, (wx1, wy1), (wx2, wy2), color, 3)
            
            min_x, max_x = min(wx1, wx2), max(wx1, wx2)
            min_y, max_y = min(wy1, wy2), max(wy1, wy2)
            ww = max(max_x - min_x, 8)
            wh = max(max_y - min_y, 8)
            
            cx = (min_x + ww/2) / w_img
            cy = (min_y + wh/2) / h_img
            nw = ww / w_img
            nh = wh / h_img
            labels_lines.append(f"3 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

        # Save image and label files
        img_filename = f"sample_{i:04d}.jpg"
        lbl_filename = f"sample_{i:04d}.txt"
        cv2.imwrite(os.path.join(img_dir, img_filename), img)
        with open(os.path.join(lbl_dir, lbl_filename), "w") as f:
            f.writelines(labels_lines)

def train_and_export():
    """Generates synthetic dataset, trains YOLOv8 model, and exports it to ONNX."""
    print("Step 1: Generating enhanced synthetic dataset...")
    generate_dataset_split(TRAIN_IMG_DIR, TRAIN_LBL_DIR, 120)
    generate_dataset_split(VAL_IMG_DIR, VAL_LBL_DIR, 30)
    print("Dataset generation complete!")

    # Write dataset.yaml
    yaml_content = f"""
path: {DATASET_DIR}
train: images/train
val: images/val
names:
  0: resistor
  1: diode
  2: led
  3: jumper_wire
  4: ic_chip
  5: capacitor
"""
    yaml_path = os.path.join(DATASET_DIR, "dataset.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content.strip())
    print(f"Wrote dataset config to {yaml_path}")

    # Import YOLO and train
    print("Step 2: Starting YOLOv8n local training...")
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Ultralytics library is not installed. Please run 'pip install ultralytics' first.")
        return

    # Train a new YOLO model
    model = YOLO("yolov8n.pt")
    
    # Train for 3 epochs. This is fast and will run in about 2-3 minutes on most CPUs
    model.train(
        data=yaml_path,
        epochs=3,
        imgsz=640,
        batch=8,
        workers=0,
        device="cpu", # Use CPU for maximum environment compatibility
        plots=False
    )
    print("YOLOv8 training completed successfully!")

    # Export to ONNX
    print("Step 3: Exporting trained model to ONNX format...")
    onnx_path = model.export(format="onnx", imgsz=640)
    print(f"YOLOv8 ONNX model exported to: {onnx_path}")

    # Move ONNX model to models/ directory
    dest_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, "yolov8_breadboard.onnx")
    
    # Usually YOLO exports to same directory as weights, e.g. runs/detect/train/weights/best.onnx
    # or inside the current folder
    src_onnx = onnx_path
    if os.path.exists(src_onnx):
        shutil.copy(src_onnx, dest_path)
        print(f"Successfully copied YOLOv8 ONNX model to: {dest_path}")
    else:
        # Search for best.onnx inside runs/
        found = False
        for root, dirs, files in os.walk(os.path.join(BASE_DIR, "runs")):
            for file in files:
                if file.endswith(".onnx"):
                    shutil.copy(os.path.join(root, file), dest_path)
                    print(f"Found and copied ONNX model from {os.path.join(root, file)} to {dest_path}")
                    found = True
                    break
            if found:
                break
        if not found:
            print("Warning: Could not automatically locate the exported ONNX model file. Please check your 'runs/' directory.")

if __name__ == "__main__":
    train_and_export()
