"""
backend/services/fault_classifier.py
Hybrid multi-stage fault classification engine (Rule + RF + MLP Neural Network + LLM XAI).
Loads trained model joblib files, predicts faults, and builds diagnostic justifications.
"""

import os
import joblib
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path)

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

_MODEL_DATA = None

def _get_model():
    global _MODEL_DATA
    if _MODEL_DATA is None:
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "fault_classifier.joblib"))
        if os.path.exists(model_path):
            try:
                _MODEL_DATA = joblib.load(model_path)
            except Exception as e:
                print(f"Error loading fault classifier model: {e}")
    return _MODEL_DATA


def parse_float(val) -> float:
    try:
        if isinstance(val, (int, float)):
            return float(val)
        cleaned = "".join(c for c in str(val) if c.isdigit() or c == "." or c == "-")
        return float(cleaned) if cleaned else 0.0
    except Exception:
        return 0.0


def _get_exp_type_code(exp_id: str) -> int:
    exp_id = exp_id.lower()
    if "cro_measurements" in exp_id or "lissajous" in exp_id:
        return 0
    elif "pn_junction" in exp_id or "rectifiers" in exp_id:
        return 1
    elif "zener" in exp_id:
        return 2
    elif "transistor_amplifier" in exp_id or "bjt_characteristics" in exp_id:
        return 3
    elif "opamp" in exp_id:
        return 4
    return 1


def _explain_fault_with_llm(fault_label: str, measured: dict, exp_id: str) -> str:
    """Invokes local/cloud LLM to produce explainable AI (XAI) reasoning for the diagnosed fault."""
    prompt = (
        f"You are an ECE Virtual Lab Instructor.\n"
        f"The diagnostic system classified a circuit anomaly as: '{fault_label}'\n"
        f"Student's measured values: {measured}\n"
        f"Experiment ID: {exp_id}\n\n"
        f"Write a concise, 3-4 sentence explanation detailing:\n"
        f"1. What this fault physically means in the circuit.\n"
        f"2. Why the measured readings led to this classification (e.g. diode blocks current if reversed).\n"
        f"3. Practical debugging tips to resolve this issue on a breadboard."
    )
    
    # 1. Try local Ollama
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": f"<system>Provide a concise diagnostic explanation.</system>\n\n<user>{prompt}</user>",
            "stream": False
        }
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=4)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
    except Exception:
        pass

    # 2. Try Groq
    if GROQ_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_KEY)
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.3
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            pass

    # 3. Try Gemini
    if GEMINI_KEY:
        try:
            from google import genai as genai_new
            from google.genai import types as genai_types
            client = genai_new.Client(api_key=GEMINI_KEY)
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai_types.GenerateContentConfig(temperature=0.2, max_output_tokens=500)
            )
            if resp.text:
                return resp.text.strip()
        except Exception:
            pass

        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash")
            resp = model.generate_content(prompt)
            if resp.text:
                return resp.text.strip()
        except Exception:
            pass

        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500}
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
            r = requests.post(url, json=payload, timeout=8)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass

    # Static Fallback
    return (
        f"XAI Explainable Fallback: The combination of measured parameters suggests a '{fault_label}'. "
        f"Verify that components are correctly aligned on the breadboard rows and DC grounds are tied."
    )


def classify_faults(exp_id: str, measured: dict, expected: dict, symptom: str = "") -> dict:
    """
    Evaluates readings through Rules, Random Forest, and MLP Neural Network.
    Generates LLM-based Explainable AI reasoning.
    """
    model_data = _get_model()
    meas_parsed = {k: parse_float(v) for k, v in measured.items()}
    exp_parsed = {k: parse_float(v) for k, v in expected.items()}
    
    # ── Stage 1: Rule Engine ──
    # Check for empty readings
    if not meas_parsed or all(v == 0.0 for v in meas_parsed.values()):
        return {
            "status": "faulty",
            "faults": ["Open Circuit / Dead Breadboard"],
            "recommendations": [
                "Ensure power supply is powered ON.",
                "Check the main power rail connections on the breadboard."
            ],
            "details": "Rule Engine triggered: all values are zero, implying an open circuit path."
        }

    # ── Stage 2: ML Model Inference (RF + MLP NN) ──
    if model_data is None:
        # Fallback to rule checking if model is missing
        return {
            "status": "warning",
            "faults": ["Models Unloaded"],
            "recommendations": ["Rebuild fault classifier models: run `python scripts/train_fault_classifier.py`"],
            "details": "Classifier joblib models missing."
        }

    exp_type = _get_exp_type_code(exp_id)
    meas_1, meas_2, meas_3 = 0.0, 0.0, 0.0
    exp_1, exp_2, exp_3 = 0.0, 0.0, 0.0

    if exp_type == 0:
        meas_1 = meas_parsed.get("Vp", 0.0)
        meas_2 = meas_parsed.get("f", 0.0)
        exp_1 = exp_parsed.get("Vp", 2.0)
        exp_2 = exp_parsed.get("f", 1000.0)
    elif exp_type == 1:
        meas_1 = meas_parsed.get("Vd", 0.0)
        meas_2 = meas_parsed.get("Id", 0.0)
        exp_1 = exp_parsed.get("Vd", 0.7)
        exp_2 = exp_parsed.get("Id", 15.0)
    elif exp_type == 2:
        meas_1 = meas_parsed.get("Vin", 10.0)
        meas_2 = meas_parsed.get("Vout", 0.0)
        exp_1 = exp_parsed.get("Vin", 10.0)
        exp_2 = exp_parsed.get("Vout", 5.1)
    elif exp_type == 3:
        meas_1 = meas_parsed.get("VCE", 0.0)
        meas_2 = meas_parsed.get("Gain", 0.0)
        meas_3 = 1.0 if ("clip" in symptom.lower() or "saturat" in symptom.lower()) else 0.0
        exp_1 = exp_parsed.get("VCE", 6.0)
        exp_2 = exp_parsed.get("Gain", 15.0)
    elif exp_type == 4:
        meas_1 = meas_parsed.get("Gain", 0.0)
        meas_2 = meas_parsed.get("Vout", 0.0)
        meas_3 = 1.0 if ("clip" in symptom.lower() or "saturat" in symptom.lower()) else 0.0
        exp_1 = exp_parsed.get("Gain", 10.0)
        exp_2 = exp_parsed.get("Vout", 5.0)

    df_features = pd.DataFrame([[exp_type, meas_1, meas_2, meas_3, exp_1, exp_2, exp_3]], 
                               columns=["exp_type", "meas_1", "meas_2", "meas_3", "exp_1", "exp_2", "exp_3"])
    
    rf = model_data["random_forest"]
    mlp = model_data["neural_network"]
    classes = model_data["classes"]
    
    pred_rf = rf.predict(df_features)[0]
    pred_mlp = mlp.predict(df_features)[0]
    
    status = "correct" if pred_rf == 0 else "faulty"
    
    faults_list = []
    recommendations = []
    reasoning = ""
    
    if status == "faulty":
        faults_list.append(classes[pred_rf])
        if pred_rf != pred_mlp:
            faults_list.append(classes[pred_mlp])
            
        # Get tailored recommendations
        for f in faults_list:
            recs = _get_recommendations_for_fault(f, exp_id)
            recommendations.extend(recs)
            
        # ── Stage 3: Explainable AI Layer (LLM Explanation) ──
        reasoning = _explain_fault_with_llm(classes[pred_rf], measured, exp_id)
    else:
        # Normal check
        reasoning = "All measurements are normal. The circuit is performing correctly."
        
    return {
        "status": status,
        "faults": faults_list if faults_list else ["None (Parameters normal)"],
        "recommendations": list(set(recommendations)),
        "reasoning": reasoning,
        "details": f"GNN/Classifier: RF predicted {classes[pred_rf]} & DNN predicted {classes[pred_mlp]}."
    }


def _get_recommendations_for_fault(fault: str, exp_id: str) -> list[str]:
    recs = []
    f_lower = fault.lower()
    
    if "open" in f_lower or "loose" in f_lower:
        recs.extend([
            "Check component continuity using multimeter diode-check mode.",
            "Verify jumper wires are inserted firmly into active breadboard rows.",
            "Ensure the DC power supply rails are active and connected."
        ])
    elif "reversed" in f_lower or "polarity" in f_lower:
        recs.append("Check component alignment: silver cathode band on diodes and negative stripe on capacitors must face ground.")
        if "zener" in exp_id.lower():
            recs.append("Ensure Zener diode is reverse biased for voltage regulation (cathode connects to Vin).")
        else:
            recs.append("Ensure regular rectifying diodes are forward biased (anode to positive supply).")
    elif "cutoff" in f_lower:
        recs.extend([
            "Check transistor base voltage VBE. It must be at least 0.65V to turn on.",
            "Ensure R1 and R2 divider resistors are not swapped.",
            "Check if the collector voltage VCE equals supply VCC (indicating no collector current)."
        ])
    elif "saturation" in f_lower:
        recs.extend([
            "Verify collector load resistor RC is of correct value. A value too high forces saturation.",
            "Reduce base current by checking if R1 is open-circuited.",
            "Verify VCE is around 0.2V."
        ])
    elif "droop" in f_lower:
        recs.extend([
            "Increase load resistance (RL) to reduce load current demands.",
            "Ensure Rs is not too large (which limits Zener breakdown current)."
        ])
    elif "bypass" in f_lower or "gain" in f_lower:
        recs.extend([
            "Verify the 100μF emitter bypass capacitor (CE) is connected across RE.",
            "Check op-amp feedback loop: verify Rf connects pin 6 to pin 2.",
            "Verify non-inverting input is grounded in inverting configuration."
        ])
    elif "clipping" in f_lower or "overdrive" in f_lower:
        recs.extend([
            "Reduce the amplitude of the input AC generator (try 10mV to 50mV peak).",
            "Verify dual power supplies are set to correct voltage and fully connected to pins 7 and 4."
        ])
        
    return recs
