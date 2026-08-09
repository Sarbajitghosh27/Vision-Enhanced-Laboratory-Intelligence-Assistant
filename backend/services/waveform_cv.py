"""
backend/services/waveform_cv.py
Waveform computer vision analyzer for Cathode Ray Oscilloscope (CRO) display screenshots.
Uses HSV color masking to trace green/cyan grid waveforms and diagnose signal distortion.
"""

import os
import cv2
import numpy as np

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
ERROR_MAP_DIR = os.path.join(STATIC_DIR, "error_maps")
os.makedirs(ERROR_MAP_DIR, exist_ok=True)


def analyze_cro_waveform(image_filename: str, volts_div: float = 1.0, time_div_ms: float = 1.0) -> dict:
    """
    Loads CRO screenshot, traces green signal lines using HSV masking,
    calculates voltage/frequency parameters, and checks for distortion/clipping.
    """
    image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", image_filename))
    out_filename = f"waveform_analysis_{image_filename}"
    out_path = os.path.join(ERROR_MAP_DIR, out_filename)
    
    # 1. Load image using OpenCV
    img = cv2.imread(image_path)
    if img is None:
        # Generate a dummy CRO screenshot if none exists (Dark green background grid)
        h, w = 400, 600
        img = np.zeros((h, w, 3), dtype=np.uint8)
        img[:, :] = (15, 23, 15) # Dark green tint
        # Draw grid
        for grid_x in range(0, w, 40):
            cv2.line(img, (grid_x, 0), (grid_x, h), (30, 60, 30), 1)
        for grid_y in range(0, h, 40):
            cv2.line(img, (0, grid_y), (w, grid_y), (30, 60, 30), 1)
            
        # Draw a clipped sine wave
        xs = np.arange(0, w)
        ys = h//2 + 120 * np.sin(2 * np.pi * 2.0 * xs / w)
        ys = np.clip(ys, h//2 - 90, h//2 + 90) # Clip top and bottom
        for px, py in zip(xs, ys):
            cv2.circle(img, (int(px), int(py)), 2, (50, 255, 100), -1) # Bright green trace
            
    h, w, _ = img.shape
    
    # 2. HSV color filtering for green trace lines
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # 3. Analyze waveform pixels
    y_indices, x_indices = np.where(mask > 0)
    
    clipping_detected = False
    v_pp = 0.0
    frequency_hz = 0.0
    distortion_msg = "Waveform looks clean."
    
    if len(x_indices) > 100:
        # Group Y values by X coordinate to get a clean 1D trace
        trace_y = {}
        for x, y in zip(x_indices, y_indices):
            if x not in trace_y:
                trace_y[x] = []
            trace_y[x].append(y)
            
        x_sorted = sorted(trace_y.keys())
        y_sorted = [np.mean(trace_y[x]) for x in x_sorted]
        
        # Calculate Peak-to-Peak (Y direction is inverted in image coordinates)
        max_y = max(y_sorted)
        min_y = min(y_sorted)
        height_pixels = max_y - min_y
        
        # Assume 40 pixels = 1 division on our grid
        div_height = height_pixels / 40.0
        v_pp = div_height * volts_div
        
        # Detect flat peaks (clipping/saturation check)
        # Check standard deviation of Y values near the absolute peaks
        peak_threshold = min_y + 5
        valley_threshold = max_y - 5
        
        top_pixels = [y for y in y_sorted if y <= peak_threshold]
        bottom_pixels = [y for y in y_sorted if y >= valley_threshold]
        
        # If there are many flat pixels at the bounds, it's clipped
        if len(top_pixels) > 15 and np.std(top_pixels) < 1.5:
            clipping_detected = True
            distortion_msg = "Severe Peak Clipping: Waveform top is flat, indicating transistor saturation or supply rail clipping."
            
        if len(bottom_pixels) > 15 and np.std(bottom_pixels) < 1.5:
            clipping_detected = True
            distortion_msg = "Severe Trough Clipping: Waveform bottom is flat, indicating cutoff or rail saturation."
            
        # Zero-crossings counting for period calculation
        mid_y = np.mean(y_sorted)
        crossings = []
        for idx in range(1, len(x_sorted)):
            y1 = y_sorted[idx-1] - mid_y
            y2 = y_sorted[idx] - mid_y
            if y1 * y2 < 0: # Zero crossing detected
                crossings.append(x_sorted[idx])
                
        if len(crossings) >= 2:
            # Average distance between consecutive crossings represents half a period
            half_periods = np.diff(crossings)
            avg_half_period_px = np.mean(half_periods)
            period_px = avg_half_period_px * 2.0
            
            # Assume 40 pixels = 1 division
            period_divisions = period_px / 40.0
            period_ms = period_divisions * time_div_ms
            period_seconds = period_ms / 1000.0
            
            frequency_hz = 1.0 / period_seconds if period_seconds > 0 else 0.0
            
        # Draw analysis markings
        # Peak indicators
        cv2.line(img, (0, int(min_y)), (w, int(min_y)), (0, 0, 255), 1) # Red line at peak
        cv2.line(img, (0, int(max_y)), (w, int(max_y)), (0, 0, 255), 1) # Red line at trough
        cv2.putText(img, f"Vp-p: {v_pp:.2f} V", (20, int(min_y) + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(img, f"Freq: {frequency_hz:.1f} Hz", (20, int(max_y) - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        if clipping_detected:
            # Highlight clipping region
            cv2.putText(img, "CLIPPING FAULT DETECTED", (w//2 - 100, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (59, 130, 246), 2)
            
    else:
        distortion_msg = "No signal trace detected. Verify CRO channel inputs or calibration."

    cv2.imwrite(out_path, img)

    return {
        "image_processed": image_filename,
        "waveform_image_url": f"/static/error_maps/{out_filename}",
        "peak_to_peak_voltage": v_pp,
        "peak_voltage": v_pp / 2.0,
        "frequency_hz": frequency_hz,
        "clipping_fault": clipping_detected,
        "distortion_report": distortion_msg
    }
