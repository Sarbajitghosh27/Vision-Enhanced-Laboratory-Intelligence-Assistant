"""
backend/services/viva_evaluator.py
Manages adaptive viva preparation sessions.
Grades answers using local LLMs (Ollama/Groq/Gemini) or semantic fallback, and adjusts difficulty.
"""

import uuid
import json
import requests
import os
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path)

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

VIVA_SESSIONS = {}

# Extra conceptual questions by topic to adapt difficulty
VIVA_DYN_POOL = {
    "cro": {
        "easy": [
            {"q": "What is the unit of frequency?", "a": "The unit of frequency is Hertz (Hz)."},
            {"q": "What does a CRO stand for?", "a": "CRO stands for Cathode Ray Oscilloscope."}
        ],
        "hard": [
            {"q": "How does the delay line in a CRO function?", "a": "It delays the vertical signal so that it aligns with the horizontal sweep trigger, allowing the leading edge of fast pulses to be visible."},
            {"q": "Why does a high input impedance matter in CRO probes?", "a": "To avoid loading effect, which would otherwise draw current from the circuit and distort the voltage reading."}
        ]
    },
    "diode": {
        "easy": [
            {"q": "What is the cut-in voltage of silicon?", "a": "Silicon diodes typically have a cut-in voltage of 0.6 to 0.7 volts."},
            {"q": "Which terminal of a diode is positive in forward bias?", "a": "The anode is positive relative to the cathode in forward bias."}
        ],
        "hard": [
            {"q": "Explain the physical mechanism of Avalanche breakdown.", "a": "Avalanche breakdown occurs when high electric field accelerates minority carriers to sufficient velocities that they collide with atoms and knock out valence electrons, creating secondary pairs via impact ionization in a chain reaction."},
            {"q": "How does the barrier potential of a PN junction change with temperature?", "a": "It decreases linearly by approximately 2 mV per degree Celsius rise in temperature."}
        ]
    },
    "amplifier": {
        "easy": [
            {"q": "What is the phase shift of a CE amplifier?", "a": "A common emitter amplifier has a phase shift of 180 degrees (phase inversion)."},
            {"q": "What is the purpose of VCC?", "a": "VCC provides the DC supply voltage to bias the transistor into its active operating region."}
        ],
        "hard": [
            {"q": "Explain why the gain of a CE amplifier falls at very high frequencies.", "a": "The gain falls due to the internal junction capacitances of the transistor (such as Cbc and Cbe) and wiring parasitics, which act as short circuits for high-frequency AC signals."},
            {"q": "What is Miller's effect and how does it affect BJT amplifiers?", "a": "Miller effect is the multiplication of the feedback capacitance (Cbc) by the voltage gain of the stage, significantly increasing the input capacitance and lowering the high-frequency bandwidth."}
        ]
    },
    "opamp": {
        "easy": [
            {"q": "What is the gain of a voltage follower?", "a": "A voltage follower (unity gain buffer) has a voltage gain of exactly 1 (unity)."},
            {"q": "What are the two input terminals of an op-amp?", "a": "Inverting terminal (-) and non-inverting terminal (+)."}
        ],
        "hard": [
            {"q": "What is the difference between Slew Rate and Bandwidth in an op-amp?", "a": "Slew rate is the maximum rate of change of output voltage (V/μs) under large signal conditions, while bandwidth is the frequency limit under small signal linear conditions."},
            {"q": "Why is the common-mode rejection ratio (CMRR) ideally infinite?", "a": "To ensure that common noise present on both input terminals is completely rejected and only the differential signal is amplified."}
        ]
    }
}


def _get_topic_key(exp_id: str) -> str:
    exp_id = exp_id.lower()
    if "cro" in exp_id or "lissajous" in exp_id:
        return "cro"
    elif "diode" in exp_id or "zener" in exp_id or "rectifiers" in exp_id:
        return "diode"
    elif "amplifier" in exp_id or "bjt" in exp_id:
        return "amplifier"
    elif "opamp" in exp_id:
        return "opamp"
    return "diode"


def _call_llm_grader(question: str, expected: str, student: str) -> dict:
    """Invokes local Ollama, Groq, or Gemini to grade student responses."""
    system_prompt = (
        "You are an ECE professor grading a student's lab viva response.\n"
        "Analyze the correctness and completeness of the student answer compared to the expected answer.\n"
        "Grade the student on a scale of 0 to 10 (integer).\n"
        "Provide constructive feedback explaining any missing details.\n"
        "Format your output ONLY as a JSON block matching this structure:\n"
        '{"score": <int_score_0_to_10>, "feedback": "<constructive_feedback_text>"}'
    )
    user_prompt = (
        f"Question: {question}\n"
        f"Expected Answer: {expected}\n"
        f"Student Answer: {student}"
    )

    # 1. Try local Ollama
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": f"<system>{system_prompt}</system>\n\n<user>{user_prompt}</user>",
            "stream": False,
            "format": "json"
        }
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=5)
        if r.status_code == 200:
            res_json = r.json()
            return json.loads(res_json.get("response", "{}"))
    except Exception:
        pass

    # 2. Try Groq
    if GROQ_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_KEY)
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            return json.loads(resp.choices[0].message.content)
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
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                    max_output_tokens=500
                )
            )
            if resp.text:
                return json.loads(resp.text)
        except Exception:
            pass

        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash")
            resp = model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(resp.text)
        except Exception:
            pass

        try:
            payload = {
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
                "generationConfig": {"response_mime_type": "application/json", "temperature": 0.1, "maxOutputTokens": 500}
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
            r = requests.post(url, json=payload, timeout=8)
            if r.status_code == 200:
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                return json.loads(raw)
        except Exception:
            pass

    # Fallback to local similarity heuristic
    words1 = set(student.lower().replace(".", "").replace(",", "").split())
    words2 = set(expected.lower().replace(".", "").replace(",", "").split())
    intersection = words1.intersection(words2)
    sim = len(intersection) / max(len(words2), 1)
    
    score = int(sim * 10)
    score = min(max(score, 0), 10)
    
    feedback = (
        f"Keyword Match Fallback. Your answer matched {int(sim*100)}% of keywords. "
        f"Correct expected details: {expected}"
    )
    
    return {"score": score, "feedback": feedback}


def start_viva_session(exp_id: str, student_name: str, exp_data: dict) -> dict:
    session_id = str(uuid.uuid4())
    questions = []
    
    if exp_data and "viva_questions" in exp_data:
        for idx, item in enumerate(exp_data["viva_questions"]):
            questions.append({
                "q": item["q"],
                "a": item["a"],
                "source": "manual",
                "difficulty": "medium",
                "index": idx
            })
            
    if not questions:
        topic = _get_topic_key(exp_id)
        for idx, item in enumerate(VIVA_DYN_POOL[topic]["easy"] + VIVA_DYN_POOL[topic]["hard"]):
            questions.append({
                "q": item["q"],
                "a": item["a"],
                "source": "fallback",
                "difficulty": "medium",
                "index": idx
            })

    session_state = {
        "session_id": session_id,
        "student_name": student_name,
        "experiment_id": exp_id,
        "experiment_title": exp_data.get("title", "ECE Lab") if exp_data else "ECE Lab",
        "questions": questions,
        "current_question_index": 0,
        "scores": [],
        "answers_log": [],
        "feedback_log": [],
        "difficulty_state": "medium",
        "weak_areas": []
    }
    
    VIVA_SESSIONS[session_id] = session_state
    
    return {
        "session_id": session_id,
        "question_number": 1,
        "total_questions": len(questions),
        "question": questions[0]["q"],
        "difficulty": "medium",
        "completed": False
    }


def evaluate_student_answer(session_id: str, student_answer: str) -> dict:
    if session_id not in VIVA_SESSIONS:
        return {"error": "Invalid Session ID. Please restart the viva."}
        
    state = VIVA_SESSIONS[session_id]
    curr_idx = state["current_question_index"]
    questions = state["questions"]
    
    if curr_idx >= len(questions):
        return {"completed": True, "message": "Viva session already finished."}
        
    current_q = questions[curr_idx]
    correct_ans = current_q["a"]
    
    # Run LLM grader
    graded = _call_llm_grader(current_q["q"], correct_ans, student_answer)
    score = int(graded.get("score", 0))
    feedback = graded.get("feedback", "Completed.")
    
    if score < 6:
        state["weak_areas"].append(current_q["q"])
        
    state["scores"].append(score)
    state["answers_log"].append(student_answer)
    state["feedback_log"].append(feedback)
    
    topic = _get_topic_key(state["experiment_id"])
    next_idx = curr_idx + 1
    state["current_question_index"] = next_idx
    
    # Adjust difficulty state
    if score >= 8 and state["difficulty_state"] == "easy":
        state["difficulty_state"] = "medium"
    elif score >= 8 and state["difficulty_state"] == "medium":
        state["difficulty_state"] = "hard"
        if next_idx < len(questions) and VIVA_DYN_POOL.get(topic):
            import random
            hard_q = random.choice(VIVA_DYN_POOL[topic]["hard"])
            questions[next_idx] = {
                "q": hard_q["q"],
                "a": hard_q["a"],
                "source": "dynamic_hard",
                "difficulty": "hard",
                "index": next_idx
            }
    elif score < 5 and state["difficulty_state"] == "hard":
        state["difficulty_state"] = "medium"
    elif score < 5 and state["difficulty_state"] == "medium":
        state["difficulty_state"] = "easy"
        if next_idx < len(questions) and VIVA_DYN_POOL.get(topic):
            import random
            easy_q = random.choice(VIVA_DYN_POOL[topic]["easy"])
            questions[next_idx] = {
                "q": easy_q["q"],
                "a": easy_q["a"],
                "source": "dynamic_easy",
                "difficulty": "easy",
                "index": next_idx
            }
            
    if next_idx >= len(questions):
        avg_score = sum(state["scores"]) / len(state["scores"])
        pct = (avg_score / 10.0) * 100.0
        
        weak_concepts = []
        for q_text in state["weak_areas"]:
            q_text_l = q_text.lower()
            if "phase" in q_text_l or "shift" in q_text_l:
                weak_concepts.append("RC Feedback Networks")
            elif "barkhausen" in q_text_l:
                weak_concepts.append("Barkhausen Criteria")
            elif "probe" in q_text_l or "attenuation" in q_text_l:
                weak_concepts.append("CRO Probes & Loading Effects")
            elif "diode" in q_text_l:
                weak_concepts.append("Diode Forward/Reverse Biasing")
            elif "slew" in q_text_l or "gain" in q_text_l:
                weak_concepts.append("Op-Amp closed-loop dynamics")
            elif "ripple" in q_text_l:
                weak_concepts.append("Rectification & Filtering")
            else:
                weak_concepts.append("Basic circuit physics")
        
        weak_concepts = list(set(weak_concepts))
        if not weak_concepts and pct < 85:
            weak_concepts.append("General ECE lab prerequisites")

        revision_pathway = []
        for c in weak_concepts:
            revision_pathway.append({
                "concept": c,
                "suggestion": f"Review theory for Experiment: {c}. Re-read key formulas and perform digital twin tuning."
            })

        return {
            "completed": True,
            "score": avg_score,
            "percentage": pct,
            "feedback": f"Viva complete! You scored {avg_score:.1f}/10 ({pct:.1f}%).",
            "scores_log": state["scores"],
            "feedback_log": state["feedback_log"],
            "weak_concepts": weak_concepts,
            "revision_pathway": revision_pathway
        }
        
    next_q = questions[next_idx]
    return {
        "completed": False,
        "score_last": score,
        "feedback_last": feedback,
        "question_number": next_idx + 1,
        "total_questions": len(questions),
        "question": next_q["q"],
        "difficulty": state["difficulty_state"]
    }
