"""
backend/routers/kg.py
FastAPI router for ECE Knowledge Graph prerequisite mapping.
"""

from fastapi import APIRouter
from backend.services.knowledge_graph import get_knowledge_graph, get_prerequisite_pathway

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])

@router.get("")
def get_graph():
    """Retrieve all nodes and edges in the ECE knowledge graph."""
    return get_knowledge_graph()

@router.get("/prereq")
def get_prerequisites(concept: str):
    """Retrieve prerequisite pathway for a specific weak concept."""
    return get_prerequisite_pathway(concept)
