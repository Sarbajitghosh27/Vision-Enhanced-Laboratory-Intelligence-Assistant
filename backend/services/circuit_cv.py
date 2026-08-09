"""
backend/services/circuit_cv.py
Upgraded breadboard fault detection using Gemini Vision (primary),
Groq Vision (fallback), and OpenCV contour analysis (offline fallback).

Detection capabilities:
  - Inappropriate/non-breadboard image detection
  - Missing component detection (auto-derived from experiment JSON)
  - Wrong component used (e.g. NPN transistor instead of diode)
  - Reversed polarity (diodes, electrolytic capacitors)
  - Series - Parallel topology swap
  - Short circuit risk detection
  - Power rail (VCC/GND) missing connections
  - Overall circuit mismatch (completely wrong circuit)
"""

import os
import re
import cv2
import json
import base64
import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from rag.retriever import get_retriever

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")

STATIC_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
ERROR_MAP_DIR = os.path.join(STATIC_DIR, "error_maps")
os.makedirs(ERROR_MAP_DIR, exist_ok=True)

# -- Optional imports ----------------------------------------------------------
try:
    import onnxruntime as ort  # type: ignore
    ONNX_AVAILABLE = True
except Exception:
    ONNX_AVAILABLE = False

try:
    from google import genai as genai_new  # type: ignore
    from google.genai import types as genai_types  # type: ignore
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

# -- Severity colours (BGR) ---------------------------------------------------
COLOR_OK       = (34,  197,  94)   # Green   - detected correctly
COLOR_WARN     = (0,   200, 255)   # Amber   - warning
COLOR_FAULT    = (30,   30, 220)   # Red     - fault
COLOR_MISMATCH = (255,  60,  60)   # Bright  - experiment mismatch


# ---------------------------------------------------------------------------
# 1.  Experiment data helpers
# ---------------------------------------------------------------------------

def _get_experiment_by_id(exp_id: str) -> Optional[dict]:
    """Return the full experiment dict from the RAG retriever cache."""
    try:
        retriever = get_retriever()
        for e in retriever.experiments:
            if e["id"] == exp_id:
                return e
    except Exception:
        pass
    return None


def _extract_required_components(exp_data: Optional[dict]) -> str:
    """Build a human-readable string of required components from the experiment JSON."""
    if not exp_data:
        return "No experiment data available."

    lines = []
    for c in exp_data.get("components", []):
        name = c.get("name", "Unknown component")
        spec = c.get("spec", "")
        qty  = c.get("quantity", 1)
        line = f"  - {name}"
        if spec:
            line += f" ({spec})"
        if qty and qty > 1:
            line += f" x{qty}"
        lines.append(line)

    hints = exp_data.get("circuit_diagnosis_hints", [])
    hint_block = ""
    if hints:
        hint_block = "\n\nCircuit wiring hints (from lab manual):\n" + "\n".join(f"  - {h}" for h in hints)

    return "\n".join(lines) + hint_block


def _build_gemini_prompt(exp_data: Optional[dict], exp_id: str) -> str:
    """Construct the structured prompt sent to Gemini Vision."""
    if exp_data:
        exp_title       = exp_data.get("title", exp_id)
        exp_aim         = exp_data.get("aim", "")
        components_text = _extract_required_components(exp_data)
    else:
        exp_title       = exp_id
        exp_aim         = ""
        components_text = "No component list available."

    return f"""You are an expert ECE laboratory instructor AI. A student has uploaded a photo of their assembled breadboard circuit.

ACTIVE EXPERIMENT: "{exp_title}"
AIM: {exp_aim}

REQUIRED COMPONENTS FOR THIS EXPERIMENT:
{components_text}

YOUR TASK: Carefully analyse the uploaded breadboard photo and produce a JSON fault report.

FAULT CATEGORIES TO CHECK:
1. inappropriate_image - Is this even a breadboard circuit photo? Reject random/unrelated photos.
2. missing_component - Is any required component absent from the breadboard?
3. wrong_component - Is a different component used instead of the required one?
4. reversed_polarity - Is a diode/LED/electrolytic capacitor inserted backwards?
5. series_parallel_error - Are components that should be in series wired in parallel or vice versa?
6. short_circuit_risk - Are any breadboard rows bridged that should not be?
7. wrong_ic_number - Is a different IC used than required?
8. missing_power_rail - Are VCC or GND connections missing or incomplete?
9. open_circuit - Is any section of the circuit visually disconnected?
10. circuit_mismatch - Is the overall circuit completely different from the required experiment?

RESPONSE FORMAT (return ONLY valid JSON, no markdown, no extra text):
{{
  "is_breadboard_image": true,
  "inappropriate_reason": null,
  "detected_components": [
    {{"type": "resistor", "count": 1, "location": "top-left quadrant", "notes": "appears correct"}},
    {{"type": "diode", "count": 1, "location": "center", "notes": "band facing left - may be reversed"}}
  ],
  "wiring_observations": [
    "Jumper wire connects column 10 row A to power rail"
  ],
  "faults": [
    {{
      "type": "Reversed Polarity",
      "component": "Diode D1",
      "severity": "CRITICAL",
      "location": "center of breadboard",
      "description": "The cathode silver band is facing the positive supply rail. Diode is in reverse bias, no current will flow.",
      "fix": "Remove the diode and rotate it 180 degrees. The silver band (cathode) must face the GND side."
    }}
  ],
  "series_parallel_errors": [],
  "short_circuit_risks": [],
  "overall_match_score": 0.75,
  "summary": "Circuit mostly correct but diode polarity is reversed."
}}

RULES:
- If the image does NOT show a breadboard or electronic circuit, set is_breadboard_image to false and fill inappropriate_reason.
- If the image shows a breadboard for a COMPLETELY different experiment, add a circuit_mismatch fault with severity CRITICAL.
- overall_match_score must be 0.0 to 1.0 (1.0 = perfect, 0.0 = completely wrong).
- Be specific about location (e.g. top-left of breadboard, row 15 column E).
- If no faults are found, return an empty faults array.
- Return ONLY the JSON object, nothing else."""


# ---------------------------------------------------------------------------
# 2.  Gemini Vision analysis (primary)
# ---------------------------------------------------------------------------

def _encode_image_base64(image_path: str) -> Optional[str]:
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def run_gemini_vision_analysis(image_path: str, exp_id: str, exp_data: Optional[dict]) -> Optional[dict]:
    """Calls Gemini Vision and returns a structured fault dict. Returns None on failure."""
    if not GEMINI_API_KEY:
        print("Gemini API key not set.")
        return None

    prompt = _build_gemini_prompt(exp_data, exp_id)

    # SDK path (google.genai)
    if GENAI_AVAILABLE:
        try:
            client = genai_new.Client(api_key=GEMINI_API_KEY)
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
            ext       = os.path.splitext(image_path)[1].lower()
            mime_map  = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
            mime_type = mime_map.get(ext, "image/jpeg")
            image_part = genai_types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
            response   = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image_part],
                config=genai_types.GenerateContentConfig(temperature=0.1, max_output_tokens=2048)
            )
            return _parse_gemini_json(response.text.strip())
        except Exception as e:
            print(f"Gemini SDK path failed: {e}")

    # REST fallback
    try:
        import requests
        b64_image = _encode_image_base64(image_path)
        if not b64_image:
            return None
        ext      = os.path.splitext(image_path)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")
        payload = {
            "contents": [{"parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": b64_image}}
            ]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048}
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        r   = requests.post(url, json=payload, timeout=45)
        r.raise_for_status()
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return _parse_gemini_json(raw)
    except Exception as e:
        print(f"Gemini REST API path failed: {e}")
        return None


def _parse_gemini_json(raw_text: str) -> Optional[dict]:
    """Safely parse JSON from Gemini response, stripping any markdown fences."""
    text  = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        print(f"No JSON in Gemini response:\n{raw_text[:300]}")
        return None
    try:
        result = json.loads(text[start:end])
        result.setdefault("is_breadboard_image", True)
        result.setdefault("inappropriate_reason", None)
        result.setdefault("detected_components", [])
        result.setdefault("wiring_observations", [])
        result.setdefault("faults", [])
        result.setdefault("series_parallel_errors", [])
        result.setdefault("short_circuit_risks", [])
        result.setdefault("overall_match_score", 0.5)
        result.setdefault("summary", "Analysis complete.")
        return result
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return None


# ---------------------------------------------------------------------------
# 3.  Groq Vision fallback (secondary)
# ---------------------------------------------------------------------------

def run_groq_vision_analysis(image_path: str, exp_id: str, exp_data: Optional[dict]) -> Optional[dict]:
    """Fallback to Groq vision model. Returns None on failure."""
    if not GROQ_API_KEY:
        return None
    try:
        import requests
        b64_image = _encode_image_base64(image_path)
        if not b64_image:
            return None
        ext      = os.path.splitext(image_path)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")
        prompt    = _build_gemini_prompt(exp_data, exp_id)
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_image}"}}
            ]}],
            "max_tokens": 2048,
            "temperature": 0.1
        }
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          json=payload, headers=headers, timeout=45)
        r.raise_for_status()
        raw    = r.json()["choices"][0]["message"]["content"].strip()
        result = _parse_gemini_json(raw)
        if result:
            result["_source"] = "groq_vision"
        return result
    except Exception as e:
        print(f"Groq Vision fallback failed: {e}")
        return None


# ---------------------------------------------------------------------------
# 4.  OpenCV offline fallback (tertiary - low confidence)
# ---------------------------------------------------------------------------

def run_opencv_fallback_analysis(img: np.ndarray, exp_id: str) -> dict:
    """Emergency offline fallback. Returns low-confidence contour count only."""
    gray     = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred  = cv2.GaussianBlur(gray, (5, 5), 0)
    edged    = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = []
    count = 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 25 and h > 25 and w < img.shape[1] * 0.8:
            count += 1
            detected.append({"type": "unknown_component", "count": 1,
                              "location": f"~row {y}, col {x}", "notes": f"offline contour {count}"})
            if count >= 8:
                break

    return {
        "is_breadboard_image": True,
        "inappropriate_reason": None,
        "detected_components": detected,
        "wiring_observations": [f"OpenCV detected {count} contours (offline mode)."],
        "faults": [{
            "type": "Offline Analysis Only", "component": "All", "severity": "WARNING",
            "location": "N/A",
            "description": (f"Gemini Vision is unavailable (no internet or API key). "
                            f"Low-confidence offline analysis only. Detected ~{count} objects."),
            "fix": "Connect to internet and retry for accurate AI-powered fault detection."
        }],
        "series_parallel_errors": [],
        "short_circuit_risks": [],
        "overall_match_score": 0.0,
        "summary": f"Offline mode: {count} objects detected. Enable internet for accurate results.",
        "_source": "opencv_offline"
    }


# ---------------------------------------------------------------------------
# 5.  Image annotation
# ---------------------------------------------------------------------------

def _annotate_image(img: np.ndarray, analysis: dict) -> np.ndarray:
    """Draw colour-coded overlays on the breadboard image."""
    h, w = img.shape[:2]
    overlay = img.copy()

    # Dark top banner
    cv2.rectangle(overlay, (0, 0), (w, 70), (15, 15, 30), -1)
    cv2.addWeighted(overlay, 0.75, img, 0.25, 0, img)

    # Match score progress bar
    score   = float(analysis.get("overall_match_score", 0.5))
    bar_w   = int((w - 40) * score)
    bar_clr = COLOR_OK if score > 0.75 else (COLOR_WARN if score > 0.40 else COLOR_FAULT)
    cv2.rectangle(img, (20, 10), (w - 20, 30), (50, 50, 50), -1)
    if bar_w > 0:
        cv2.rectangle(img, (20, 10), (20 + bar_w, 30), bar_clr, -1)
    cv2.putText(img, f"Match Score: {score:.0%}", (25, 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

    # Summary line
    cv2.putText(img, str(analysis.get("summary", ""))[:90], (15, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 220, 255), 1)

    faults = analysis.get("faults", [])

    if not analysis.get("is_breadboard_image", True):
        cv2.rectangle(img, (4, 4), (w - 4, h - 4), COLOR_FAULT, 6)
        cv2.putText(img, "INVALID IMAGE - Not a breadboard circuit",
                    (15, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_FAULT, 2)

    elif faults:
        has_critical = any(f.get("severity") == "CRITICAL" for f in faults)
        badge_clr    = COLOR_FAULT if has_critical else COLOR_WARN
        badge_text   = f"{len(faults)} FAULT{'S' if len(faults) > 1 else ''} FOUND"
        cv2.rectangle(img, (w - 220, 80), (w - 10, 120), badge_clr, -1)
        cv2.putText(img, badge_text, (w - 215, 108),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        y_off = 140
        for i, fault in enumerate(faults[:6]):
            sev   = fault.get("severity", "WARNING")
            fclr  = COLOR_FAULT if sev == "CRITICAL" else COLOR_WARN
            text  = f"{i+1}. [{sev}] {fault.get('type','')}: {fault.get('component','')}"
            cv2.putText(img, text[:72], (15, y_off), cv2.FONT_HERSHEY_SIMPLEX, 0.4, fclr, 1)
            y_off += 22
            if y_off > h - 40:
                break

        border_clr = COLOR_FAULT if has_critical else COLOR_WARN
        cv2.rectangle(img, (4, 4), (w - 4, h - 4), border_clr, 4)

    else:
        cv2.rectangle(img, (4, 4), (w - 4, h - 4), COLOR_OK, 4)
        cv2.putText(img, "NO FAULTS DETECTED", (15, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_OK, 2)

    # Source watermark
    src_map = {"gemini_vision": "AI: Gemini Vision",
               "groq_vision":   "AI: Groq Vision (fallback)",
               "opencv_offline": "Offline OpenCV (low confidence)"}
    src_label = src_map.get(analysis.get("_source", ""), "AI Analysis")
    cv2.putText(img, src_label, (15, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (150, 150, 150), 1)

    return img


# ---------------------------------------------------------------------------
# 6.  Legacy YOLO ONNX (reference only - not used as primary)
# ---------------------------------------------------------------------------

def run_yolo_onnx_inference(image_path: str, model_path: str,
                            conf_threshold: float = 0.20,
                            iou_threshold: float  = 0.45) -> List[dict]:
    """Legacy YOLOv8 ONNX - kept for reference. Produces <0.08 scores on real images."""
    if not ONNX_AVAILABLE or not os.path.exists(model_path):
        return []
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []
        h_orig, w_orig = img.shape[:2]
        inp   = cv2.resize(img, (640, 640))
        inp   = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        inp   = np.expand_dims(inp.transpose(2, 0, 1), 0)
        sess  = ort.InferenceSession(model_path)
        preds = sess.run([sess.get_outputs()[0].name], {sess.get_inputs()[0].name: inp})[0][0]
        names = {0: "resistor", 1: "diode", 2: "led", 3: "jumper_wire", 4: "ic_chip", 5: "capacitor"}
        boxes, scores, class_ids = [], [], []
        for i in range(preds.shape[1]):
            col  = preds[:, i]
            cls  = int(np.argmax(col[4:]))
            scr  = float(col[4 + cls])
            if scr > conf_threshold:
                xc, yc, wb, hb = col[:4]
                boxes.append([int((xc - wb/2)*w_orig/640), int((yc - hb/2)*h_orig/640),
                               int(wb*w_orig/640), int(hb*h_orig/640)])
                scores.append(scr); class_ids.append(cls)
        indices  = cv2.dnn.NMSBoxes(boxes, scores, conf_threshold, iou_threshold)
        detected = []
        if len(indices) > 0:
            for idx in indices.flatten():
                x, y, bw, bh = boxes[idx]
                detected.append({"label": names.get(class_ids[idx], "unknown"),
                                  "confidence": scores[idx],
                                  "box": [max(0,x), max(0,y), min(w_orig,x+bw), min(h_orig,y+bh)]})
        return detected
    except Exception as e:
        print(f"YOLO ONNX failed: {e}")
        return []


# ---------------------------------------------------------------------------
# 7.  Legacy NetworkX graph (kept for GNN router in diagnosis.py)
# ---------------------------------------------------------------------------

def _build_ideal_graph(exp_id: str) -> nx.Graph:
    G = nx.Graph()
    if "pn_junction" in exp_id:
        G.add_nodes_from(["V1","R1","D1","GND"])
        G.add_edges_from([("V1","R1"),("R1","D1"),("D1","GND"),("V1","GND")])
    elif "zener" in exp_id:
        G.add_nodes_from(["V1","Rs","Dz","RL","GND"])
        G.add_edges_from([("V1","Rs"),("Rs","Dz"),("Rs","RL"),("Dz","GND"),("RL","GND"),("V1","GND")])
    elif "opamp" in exp_id:
        G.add_nodes_from(["U1","R1","Rf","V1","GND"])
        G.add_edges_from([("V1","R1"),("R1","U1"),("U1","Rf"),("U1","GND")])
    elif "rc_filters" in exp_id:
        G.add_nodes_from(["Vin","C1","R1","GND"])
        G.add_edges_from([("Vin","C1"),("C1","R1"),("R1","GND")])
    elif "transistor_amplifier" in exp_id or "bjt_characteristics" in exp_id:
        G.add_nodes_from(["V1","R1","R2","RC","RE","Q1","GND"])
        G.add_edges_from([("V1","R1"),("R1","Q1"),("R2","Q1"),("Q1","RC"),("Q1","RE"),("RE","GND"),("V1","GND")])
    elif "rectifiers" in exp_id:
        G.add_nodes_from(["Vin","D1","D2","D3","D4","RL","C1","GND"])
        G.add_edges_from([("Vin","D1"),("D1","RL"),("RL","GND"),("C1","RL"),("C1","GND")])
    elif "logic_gates" in exp_id or "adder" in exp_id:
        G.add_nodes_from(["VCC","U1","GND","LED1"])
        G.add_edges_from([("VCC","U1"),("U1","LED1"),("LED1","GND")])
    else:
        G.add_nodes_from(["V1","R1","GND"])
        G.add_edges_from([("V1","R1"),("R1","GND")])
    return G


# ---------------------------------------------------------------------------
# 8.  Main entry point
# ---------------------------------------------------------------------------

def analyze_breadboard_photo(exp_id: str, image_filename: str) -> dict:
    """
    Primary breadboard analysis pipeline.
    Waterfall:
      1. Gemini Vision  (cloud AI, structured JSON)
      2. Groq Vision    (secondary if Gemini unavailable)
      3. OpenCV offline (emergency fallback, low confidence)
    """
    image_path     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", image_filename))
    safe_name      = re.sub(r"[^\w\-.]", "_", image_filename)
    error_filename = f"error_map_{safe_name}"
    if not error_filename.lower().endswith((".jpg", ".jpeg", ".png")):
        error_filename += ".jpg"
    error_image_path = os.path.join(ERROR_MAP_DIR, error_filename)

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:] = (30, 41, 59)
        cv2.putText(img, "Image not found", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)

    exp_data = _get_experiment_by_id(exp_id)

    # Tier 1: Gemini Vision
    analysis = None
    if os.path.exists(image_path):
        print(f"[circuit_cv] Running Gemini Vision for {exp_id}...")
        analysis = run_gemini_vision_analysis(image_path, exp_id, exp_data)
        if analysis:
            analysis["_source"] = "gemini_vision"
            print(f"[circuit_cv] Gemini: {len(analysis.get('faults', []))} fault(s).")

    # Tier 2: Groq Vision
    if analysis is None and os.path.exists(image_path):
        print("[circuit_cv] Gemini unavailable, trying Groq Vision...")
        analysis = run_groq_vision_analysis(image_path, exp_id, exp_data)
        if analysis:
            print(f"[circuit_cv] Groq: {len(analysis.get('faults', []))} fault(s).")

    # Tier 3: OpenCV offline
    if analysis is None:
        print("[circuit_cv] All AI unavailable. Using OpenCV offline fallback.")
        analysis = run_opencv_fallback_analysis(img, exp_id)

    # Inappropriate image guard
    if not analysis.get("is_breadboard_image", True):
        reason = analysis.get("inappropriate_reason") or "The uploaded image does not appear to be a breadboard circuit."
        analysis["faults"] = [{
            "type": "Invalid Image", "component": "N/A", "severity": "CRITICAL",
            "location": "N/A",
            "description": f"REJECTED: {reason}",
            "fix": "Upload a clear, well-lit photo of your assembled breadboard circuit."
        }]
        analysis["overall_match_score"] = 0.0
        analysis["summary"] = "Image rejected - not a valid breadboard circuit photo."

    # Annotate and save
    annotated = _annotate_image(img.copy(), analysis)
    cv2.imwrite(error_image_path, annotated)

    # Build legacy NetworkX data for GNN router
    ideal_G     = _build_ideal_graph(exp_id)
    ideal_nodes = [{"id": str(n), "label": str(n)} for n in ideal_G.nodes()]
    ideal_edges = [{"from": str(e[0]), "to": str(e[1]), "label": "Connection"} for e in ideal_G.edges()]

    # Normalise fault format
    legacy_faults = []
    for f in analysis.get("faults", []):
        legacy_faults.append({
            "type":        f.get("type", "Unknown Fault"),
            "component":   f.get("component", "Unknown"),
            "severity":    f.get("severity", "WARNING"),
            "description": f.get("description", ""),
            "fix":         f.get("fix", ""),
            "location":    f.get("location", "")
        })

    suggestions = [f["fix"] for f in legacy_faults if f.get("fix")]
    suggestions += [f"Series/Parallel error: {e}" for e in analysis.get("series_parallel_errors", [])]
    suggestions += [f"Short circuit risk: {r}" for r in analysis.get("short_circuit_risks", [])]

    if not legacy_faults:
        legacy_faults = [{"type": "None", "component": "Circuit", "severity": "OK",
                          "description": "No wiring faults detected.", "fix": "N/A", "location": "N/A"}]
    if not suggestions:
        suggestions = ["No corrections needed. Well done!"]

    return {
        "experiment_id":          exp_id,
        "image_processed":        image_filename,
        "error_map_url":          f"/static/error_maps/{error_filename}",
        "analysis_source":        analysis.get("_source", "unknown"),
        "components_count":       len(analysis.get("detected_components", [])),
        "components":             analysis.get("detected_components", []),
        "wiring_observations":    analysis.get("wiring_observations", []),
        "faults":                 legacy_faults,
        "correction_suggestions": suggestions,
        "series_parallel_errors": analysis.get("series_parallel_errors", []),
        "short_circuit_risks":    analysis.get("short_circuit_risks", []),
        "overall_match_score":    analysis.get("overall_match_score", 0.0),
        "summary":                analysis.get("summary", ""),
        "graph_comparison": {
            "ideal":      {"nodes": ideal_nodes, "edges": ideal_edges},
            "detected":   {"nodes": [], "edges": []},
            "match_rate": analysis.get("overall_match_score", 0.0)
        }
    }
