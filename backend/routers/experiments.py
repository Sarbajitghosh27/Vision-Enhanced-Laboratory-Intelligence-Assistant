"""
backend/routers/experiments.py
FastAPI router for retrieving experiment manuals and metadata.
Supports on-the-fly generation of missing ECE syllabus experiments.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import re
import os
import json
import requests
from dotenv import load_dotenv
from rag.retriever import get_retriever
from frontend.ece_syllabus import ECE_SYLLABUS

router = APIRouter(prefix="/experiments", tags=["experiments"])

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path)
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

class ExperimentHeader(BaseModel):
    id: str
    title: str
    semester: int
    lab_code: str

@router.get("", response_model=List[ExperimentHeader])
def list_experiments(semester: Optional[int] = None, lab_code: Optional[str] = None):
    """List all available experiments, optionally filtered by semester or lab code."""
    retriever = get_retriever()
    exps = retriever.experiments
    results = []
    for e in exps:
        # Apply filters if set
        if semester is not None and e.get("semester") != semester:
            continue
        if lab_code is not None and e.get("lab_code") != lab_code:
            continue
            
        results.append(ExperimentHeader(
            id=e["id"],
            title=e["title"],
            semester=e.get("semester", 1),
            lab_code=e.get("lab_code", "ECE")
        ))
    return results


def _generate_experiment_manual(exp_id: str, semester: int, lab_code: str, lab_name: str, exp_number: int, syllabus_exp: dict) -> dict:
    def get_static_fallback():
        return {
            "id": exp_id,
            "semester": semester,
            "lab_code": lab_code,
            "lab_name": lab_name,
            "exp_number": exp_number,
            "title": syllabus_exp["title"],
            "type": "hardware",
            "aim": syllabus_exp.get("aim", ""),
            "theory": {
                "summary": f"Laboratory manual for {syllabus_exp['title']} covering operational principles and circuit design.",
                "key_formulas": [
                    {"name": "Standard Relation", "formula": "V = I * R", "variables": "V=voltage, I=current, R=resistance"}
                ],
                "key_concepts": syllabus_exp.get("components", ["ECE Circuit Analysis"])
            },
            "components": [{"name": c, "spec": "Standard Lab Spec", "quantity": 1} for c in syllabus_exp.get("components", ["Breadboard", "Power Supply", "Connecting Wires"])],
            "procedure": [
                "Step 1: Set up the power supply and configure breadboard connections.",
                "Step 2: Place and verify the circuit components as per schematic.",
                "Step 3: Connect oscilloscope probes and record input/output waveforms.",
                "Step 4: Tabulate observations and calculate experimental metrics."
            ],
            "observations": {
                "table_headers": ["Parameter", "Expected", "Measured"],
                "sample_row": ["Output Value", "Nominal", "Observed"],
                "what_to_plot": "Plot characteristic curve based on recorded readings."
            },
            "expected_results": {
                "description": "Output parameters align with theoretical calculations within ±5% laboratory tolerance.",
                "typical_values": [
                    {"parameter": "Nominal Operating Point", "expected": "Within spec", "unit": "V"}
                ]
            },
            "common_errors": [
                {
                    "symptom": "No signal detected on oscilloscope / multimeter",
                    "causes": ["Loose breadboard wire", "Supply rail not grounded"],
                    "fix": "Check common ground connection and verify supply rails with a multimeter."
                }
            ],
            "circuit_diagnosis_hints": ["Ensure supply voltages and component polarities are correct."],
            "viva_questions": [
                {"q": f"What is the primary objective of {syllabus_exp['title']}?", "a": f"The primary objective is: {syllabus_exp.get('aim', 'To verify circuit behavior under standard conditions.')}"},
                {"q": "What precautions should be taken when powering this circuit?", "a": "Ensure proper ground reference, check polarity of active devices, and do not exceed rated component currents."}
            ]
        }

    prompt = f"""
    You are an expert ECE Professor at BIT Mesra. Write a highly detailed, technically accurate laboratory manual for the following experiment:
    
    Semester: {semester}
    Lab Code: {lab_code}
    Lab Name: {lab_name}
    Experiment Number: {exp_number}
    Title: {syllabus_exp['title']}
    Aim: {syllabus_exp.get('aim', '')}
    Expected Components: {', '.join(syllabus_exp.get('components', []))}
    
    You must return a raw JSON response ONLY (no markdown blocks, no backticks, no other text). The JSON structure must match this schema exactly:
    {{
        "id": "{exp_id}",
        "semester": {semester},
        "lab_code": "{lab_code}",
        "lab_name": "{lab_name}",
        "exp_number": {exp_number},
        "title": "{syllabus_exp['title']}",
        "type": "hardware",
        "aim": "{syllabus_exp.get('aim', '')}",
        "theory": {{
            "summary": "Detailed theoretical summary explaining the circuit/concept, how it works, active physics/logic, and formulas.",
            "key_formulas": [
                {{"name": "Formula Name", "formula": "LaTeX or plain text formula string", "variables": "description of variables"}}
            ],
            "key_concepts": ["concept1", "concept2", "concept3"]
        }},
        "components": [
            {{"name": "Resistor", "spec": "10kΩ, 0.25W", "quantity": 1}}
        ],
        "procedure": [
            "Step 1...", "Step 2...", "Step 3..."
        ],
        "observations": {{
            "table_headers": ["Header1", "Header2"],
            "sample_row": ["value1", "value2"],
            "what_to_plot": "Instructions on what curves/graphs to plot."
        }},
        "expected_results": {{
            "description": "What values to expect.",
            "typical_values": [
                {{"parameter": "Parameter Name", "expected": "Value range", "unit": "Unit"}}
            ]
        }},
        "common_errors": [
            {{
                "symptom": "What went wrong",
                "causes": ["cause 1", "cause 2"],
                "fix": "how to debug on breadboard/software"
            }}
        ],
        "circuit_diagnosis_hints": [
            "Hint 1 for diagnostic scan..."
        ],
        "viva_questions": [
            {{"q": "viva question 1?", "a": "expert technical answer 1"}},
            {{"q": "viva question 2?", "a": "expert technical answer 2"}},
            {{"q": "viva question 3?", "a": "expert technical answer 3"}}
        ]
    }}
    """

    resp_text = None
    
    # 1. Primary: Groq (ultra-fast JSON generation < 1 second)
    if GROQ_KEY:
        try:
            from groq import Groq
            g_client = Groq(api_key=GROQ_KEY)
            completion = g_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional ECE laboratory curriculum engineer. Return only valid JSON adhering strictly to the schema."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2500,
                timeout=10
            )
            if completion.choices and completion.choices[0].message.content:
                resp_text = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq manual generation fallback: {e}")

    # 2. Secondary: Google GenAI SDK / REST fallback
    if not resp_text and GEMINI_KEY:
        try:
            from google import genai as genai_new
            from google.genai import types as genai_types
            client = genai_new.Client(api_key=GEMINI_KEY)
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2500
                )
            )
            if resp.text:
                resp_text = resp.text.strip()
        except Exception as e:
            print(f"google.genai SDK fallback in manual generation: {e}")

    # 3. Direct REST API fallback
    if not resp_text and GEMINI_KEY:
        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2500}
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
            r = requests.post(url, json=payload, timeout=8)
            if r.status_code == 200:
                resp_text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"REST Gemini fallback in manual generation: {e}")

    if not resp_text:
        return get_static_fallback()

    try:
        # Clean possible markdown wrap from the LLM response
        if resp_text.startswith("```json"):
            resp_text = resp_text.replace("```json", "", 1)
        if resp_text.startswith("```"):
            resp_text = resp_text.replace("```", "", 1)
        if resp_text.endswith("```"):
            resp_text = resp_text[:-3]
        resp_text = resp_text.strip()
        
        manual_data = json.loads(resp_text)
        
        # Save to disk
        dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "experiments"))
        dest_path = os.path.join(dest_dir, f"generated_{exp_id}.json")
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(manual_data, f, indent=2, ensure_ascii=False)
            
        # Fast registration in active retriever memory without blocking full rebuild
        retriever = get_retriever()
        if not any(e.get("id") == manual_data.get("id") for e in retriever.experiments):
            retriever.experiments.append(manual_data)
        
        return manual_data
    except Exception as e:
        print(f"Error parsing generated manual JSON: {e}")
        return get_static_fallback()


@router.get("/{exp_id}")
def get_experiment_details(exp_id: str):
    """Retrieve full detail of a specific experiment by ID."""
    retriever = get_retriever()
    for e in retriever.experiments:
        if e["id"] == exp_id:
            return e
            
    # Try dynamic generation if ID matches format
    match = re.match(r"sem(\d+)_([A-Z0-9]+)_exp(\d+)", exp_id)
    if match:
        sem_num = int(match.group(1))
        course_code = match.group(2)
        exp_idx = int(match.group(3))
        
        roman_map = {1: "Semester I", 2: "Semester II", 3: "Semester III", 4: "Semester IV", 5: "Semester V", 6: "Semester VI", 7: "Semester VII", 8: "Semester VIII"}
        sem_key = roman_map.get(sem_num)
        
        if sem_key and sem_key in ECE_SYLLABUS:
            courses = ECE_SYLLABUS[sem_key]
            if course_code in courses:
                course = courses[course_code]
                exps = course.get("experiments", [])
                if 1 <= exp_idx <= len(exps):
                    syllabus_exp = exps[exp_idx - 1]
                    
                    generated_exp = _generate_experiment_manual(
                        exp_id=exp_id,
                        semester=sem_num,
                        lab_code=course_code,
                        lab_name=course["name"],
                        exp_number=exp_idx,
                        syllabus_exp=syllabus_exp
                    )
                    if generated_exp:
                        return generated_exp
                        
    raise HTTPException(status_code=404, detail=f"Experiment '{exp_id}' not found.")
