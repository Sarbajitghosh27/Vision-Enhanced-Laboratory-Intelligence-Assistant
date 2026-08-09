"""
backend/routers/viva.py
FastAPI router for the Adaptive AI Viva Examiner.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.viva_evaluator import start_viva_session, evaluate_student_answer
from rag.retriever import get_retriever

router = APIRouter(prefix="/viva", tags=["viva"])

class StartVivaRequest(BaseModel):
    experiment_id: str
    student_name: str

class AnswerVivaRequest(BaseModel):
    session_id: str
    student_answer: str

@router.post("/start")
def start_viva(req: StartVivaRequest):
    """Starts an adaptive ECE viva session."""
    retriever = get_retriever()
    exp_data = None
    
    # Load manual details
    for e in retriever.experiments:
        if e["id"] == req.experiment_id:
            exp_data = e
            break
            
    if not exp_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Experiment '{req.experiment_id}' not found in database."
        )
        
    result = start_viva_session(
        exp_id=req.experiment_id,
        student_name=req.student_name,
        exp_data=exp_data
    )
    return result

@router.post("/answer")
def submit_answer(req: AnswerVivaRequest):
    """
    Submits a student's answer, scores it semantically,
    adapts difficulty, and serves the next question.
    """
    result = evaluate_student_answer(
        session_id=req.session_id,
        student_answer=req.student_answer
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
