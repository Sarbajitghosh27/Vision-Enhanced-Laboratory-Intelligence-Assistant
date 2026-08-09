"""
rag/generator.py
Generates AI responses from retrieved experiment context.

Priority order:
  1. Local Ollama (Phi-3 / Mistral) — completely free, offline
  2. Groq API (llama-3.1-8b-instant) — free tier, 14,400 req/day
  3. Gemini Flash — fallback, 1500 req/day free
  4. Static explanation DB — zero cost, instant, for known fault patterns
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

GROQ_KEY   = os.getenv("GROQ_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

# ── Static explanation DB import ──────────────────────────────────────────────
STATIC_DB_AVAILABLE = False
try:
    import importlib
    import importlib.util
    import sys
    # Suppress static analyzer warnings by dynamically checking and importing the module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    backend_spec = importlib.util.find_spec("backend.explanations")
    if backend_spec is not None:
        backend_explanations = importlib.import_module("backend.explanations")
        get_explanation = backend_explanations.get_explanation
        has_explanation = backend_explanations.has_explanation
        STATIC_DB_AVAILABLE = True
    else:
        raise ImportError
except ImportError:
    STATIC_DB_AVAILABLE = False
    def has_explanation(c, f): return False
    def get_explanation(c, f): return ""


# ── Context builder ───────────────────────────────────────────────────────────
def build_context(experiment: Optional[dict], mode: str, extra: dict = None) -> str:
    """
    Build a focused context string from experiment JSON.
    mode: "theory" | "procedure" | "diagnosis" | "viva" | "general"
    extra: optional dict with student's measured values, fault, etc.
    """
    if not experiment:
        return "No specific experiment context is available.\n"
    
    e = experiment
    th = e.get("theory", {})

    base = (
        f"EXPERIMENT: {e.get('title')}\n"
        f"AIM: {e.get('aim')}\n"
        f"SEMESTER: {e.get('semester')} | LAB: {e.get('lab_code')} — {e.get('lab_name')}\n\n"
    )

    if mode == "theory":
        formulas = "\n".join(
            f"  • {f['name']}: {f['formula']}  [{f.get('variables','')}]"
            for f in th.get("key_formulas", [])
        )
        return (
            base
            + f"THEORY SUMMARY:\n{th.get('summary','')}\n\n"
            + f"KEY FORMULAS:\n{formulas}\n\n"
            + f"KEY CONCEPTS: {', '.join(th.get('key_concepts',[]))}\n"
        )

    elif mode == "procedure":
        steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(e.get("procedure", [])))
        comps = "\n".join(
            f"  • {c['name']} ({c.get('spec', '')}) ×{c.get('quantity',1)}"
            for c in e.get("components", [])
        )
        expected = "\n".join(
            f"  • {t['parameter']}: {t['expected']} {t.get('unit','')}"
            for t in e.get("expected_results", {}).get("typical_values", [])
        )
        return (
            base
            + f"COMPONENTS NEEDED:\n{comps}\n\n"
            + f"PROCEDURE:\n{steps}\n\n"
            + f"EXPECTED RESULTS:\n{expected}\n"
        )

    elif mode == "diagnosis":
        errors = ""
        for err in e.get("common_errors", []):
            errors += (
                f"\n  Symptom: {err.get('symptom')}\n"
                f"  Causes: {', '.join(err.get('causes', []))}\n"
                f"  Fix: {err.get('fix')}\n"
            )
        hints = "\n".join(f"  • {h}" for h in e.get("circuit_diagnosis_hints", []))
        extra_str = ""
        if extra:
            extra_str = (
                f"\nSTUDENT'S SITUATION:\n"
                f"  Measured value: {extra.get('measured', 'not provided')}\n"
                f"  Expected value: {extra.get('expected', 'not provided')}\n"
                f"  Symptom described: {extra.get('symptom', 'not provided')}\n"
            )
        return (
            base
            + f"KNOWN FAULT PATTERNS:{errors}\n"
            + f"DIAGNOSIS HINTS:\n{hints}\n"
            + extra_str
        )

    elif mode == "viva":
        qas = "\n".join(
            f"  Q: {qa['q']}\n  A: {qa['a']}"
            for qa in e.get("viva_questions", [])
        )
        return base + f"VIVA QUESTIONS & ANSWERS:\n{qas}\n"

    else:  # general
        return (
            base
            + f"THEORY: {th.get('summary','')}\n\n"
            + f"AIM: {e.get('aim','')}\n"
        )


def build_system_prompt(mode: str) -> str:
    base = (
        "You are an expert ECE lab assistant at BIT Mesra. "
        "You help students understand experiments, debug circuits, and prepare for vivas. "
        "Always be specific, practical, and encouraging. "
        "Use the provided experiment context to answer accurately. "
        "Keep responses concise — students are at a lab bench, not reading a textbook. "
    )
    additions = {
        "theory":    "Explain concepts clearly using simple analogies. Highlight formulas.",
        "procedure": "Give step-by-step guidance. Warn about common mistakes proactively.",
        "diagnosis": "Identify the most likely fault first. Give exact fix steps for a breadboard.",
        "viva":      "Help the student understand the answer deeply, not just memorize it.",
        "general":   "Answer helpfully based on the experiment context.",
    }
    return base + additions.get(mode, "")


# ── LLM Backends ──────────────────────────────────────────────────────────────

def _call_groq(system: str, user: str) -> str:
    from groq import Groq
    # Configure 5-second timeout so connection hangs don't block the backend
    client = Groq(api_key=GROQ_KEY, timeout=5.0)
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ],
        max_tokens=600,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


def _call_gemini(system: str, user: str) -> str:
    # 1. Try official google.genai SDK
    try:
        from google import genai as genai_new
        from google.genai import types as genai_types
        client = genai_new.Client(api_key=GEMINI_KEY)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user,
            config=genai_types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.3,
                max_output_tokens=800
            )
        )
        if resp.text:
            return resp.text.strip()
    except Exception as e:
        print(f"google.genai SDK call failed: {e}. Trying fallback...")

    # 2. Try legacy google.generativeai SDK
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system,
        )
        resp = model.generate_content(user, request_options={"timeout": 10.0})
        if resp.text:
            return resp.text.strip()
    except Exception as e:
        print(f"google.generativeai call failed: {e}. Trying REST fallback...")

    # 3. Direct REST API fallback
    import requests
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def _call_ollama(system: str, user: str) -> str:
    import requests
    payload = {
        "model":  OLLAMA_MODEL,
        "prompt": f"<system>{system}</system>\n\n<user>{user}</user>\n<assistant>",
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 600},
    }
    resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def _ollama_available() -> bool:
    try:
        import requests
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


# ── Main generate function ────────────────────────────────────────────────────

def generate_response(
    query:      str,
    experiment: Optional[dict],
    mode:       str  = "general",
    extra:      dict = None,
) -> dict:
    """
    Generate a response for the student query.
    Returns dict with keys: answer, source, experiment_title, mode
    """
    context       = build_context(experiment, mode, extra)
    system_prompt = build_system_prompt(mode)
    full_user     = f"CONTEXT:\n{context}\n\nSTUDENT QUESTION: {query}"

    answer = None
    source = None

    # ── Try static DB first for diagnosis mode (zero cost) ────────────────
    if mode == "diagnosis" and STATIC_DB_AVAILABLE and extra and experiment:
        circuit = experiment.get("id", "").split("_exp")[0].replace("sem1_EC24102_", "")
        fault   = extra.get("fault", "")
        if fault and has_explanation(circuit, fault):
            answer = get_explanation(circuit, fault)
            source = "static_db"

    # ── Try local Ollama (fine-tuned Phi-3 or Mistral) ────────────────────
    if answer is None and _ollama_available():
        try:
            answer = _call_ollama(system_prompt, full_user)
            source = f"ollama:{OLLAMA_MODEL}"
        except Exception as e:
            print(f"  Ollama failed: {e}")

    # ── Try Groq free tier ────────────────────────────────────────────────
    if answer is None and GROQ_KEY:
        try:
            answer = _call_groq(system_prompt, full_user)
            source = "groq:llama-3.1-8b-instant"
        except Exception as e:
            print(f"  Groq failed: {e}")

    # ── Try Gemini Flash fallback ─────────────────────────────────────────
    if answer is None and GEMINI_KEY:
        try:
            answer = _call_gemini(system_prompt, full_user)
            source = "gemini:flash"
        except Exception as e:
            print(f"  Gemini failed: {e}")

    # ── Last resort: static context only ─────────────────────────────────
    if answer is None:
        answer = (
            "⚠ No AI backend available. "
            "Here is the raw context from the experiment database:\n\n"
            + context
        )
        source = "static_context_only"

    return {
        "answer":           answer,
        "source":           source,
        "experiment_id":    experiment.get("id") if experiment else None,
        "experiment_title": experiment.get("title") if experiment else None,
        "mode":             mode,
    }
