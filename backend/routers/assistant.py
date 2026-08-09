"""
backend/routers/assistant.py
FastAPI router for the RAG experiment assistant chat.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict
from rag.retriever import get_retriever
from rag.generator import generate_response

router = APIRouter(prefix="/assistant", tags=["assistant"])

class ChatRequest(BaseModel):
    query: str
    experiment_id: Optional[str] = None
    mode: Optional[str] = "general"
    extra: Optional[Dict] = None

class ChatResponse(BaseModel):
    answer: str
    source: str
    experiment_id: Optional[str] = None
    experiment_title: Optional[str] = None
    mode: str

@router.post("/chat", response_model=ChatResponse)
def chat_assistant(req: ChatRequest):
    """
    Handles student chatbot questions.
    Uses FAISS index to find context, then calls generator (local Ollama / Groq / Gemini).
    """
    retriever = get_retriever()
    target_exp = None
    
    # 1. Fetch experiment context if ID is supplied
    if req.experiment_id:
        for e in retriever.experiments:
            if e["id"] == req.experiment_id:
                target_exp = e
                break
                
    # 2. If no experiment ID but we have a query, use retriever to find the most relevant manual
    if not target_exp and req.query:
        target_exp, score = retriever.retrieve_one(req.query)
        # Only use context if the retrieval score is decent (e.g. > 0.15) to avoid false context
        if score < 0.15:
            target_exp = None

    # 3. Call generator
    result = generate_response(
        query=req.query,
        experiment=target_exp,
        mode=req.mode,
        extra=req.extra
    )
    
    return ChatResponse(
        answer=result["answer"],
        source=result["source"],
        experiment_id=result["experiment_id"],
        experiment_title=result["experiment_title"],
        mode=result["mode"]
    )
