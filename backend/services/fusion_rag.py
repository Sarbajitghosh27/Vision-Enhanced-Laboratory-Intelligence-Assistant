"""
backend/services/fusion_rag.py
Fuses retrieval-augmented generation (RAG) manual lookups
with ECE Prerequisite Knowledge Graph mappings.
"""

from typing import Optional
from rag.retriever import get_retriever
from backend.services.knowledge_graph import get_prerequisite_pathway, get_knowledge_graph

def retrieve_fusion_context(query: str) -> dict:
    """
    Finds the most relevant manual and merges its content with prerequisite concepts
    retrieved from the Knowledge Graph.
    """
    retriever = get_retriever()
    exp, score = retriever.retrieve_one(query)
    
    context_chunks = []
    prereq_pathway = []
    experiment_id = None
    experiment_title = None

    if exp and score > 0.15:
        experiment_id = exp["id"]
        experiment_title = exp["title"]
        
        # 1. Base manual details
        context_chunks.append(
            f"EXPERIMENT: {exp['title']}\n"
            f"AIM: {exp.get('aim','')}\n"
            f"THEORY SUMMARY: {exp.get('theory',{}).get('summary','')}\n"
        )
        
        # 2. Query knowledge graph for prerequisite concepts
        prereq_pathway = get_prerequisite_pathway(exp["title"])
        
        # 3. Inject prerequisite summaries into the context
        if prereq_pathway:
            p_str = "\nFOUNDATIONAL PREREQUISITES FOR THIS EXPERIMENT:\n"
            for p in prereq_pathway:
                p_str += f"  • {p['label']} (Semester {p['semester']}): {p['detail']}\n"
            context_chunks.append(p_str)
            
    else:
        # Fallback to general ECE concepts
        context_chunks.append("General ECE context. No matching experiment manual found.")
        prereq_pathway = [{"label": "Basic Semiconductor Physics", "detail": "Biasing and basic energy bands."}]

    fused_context = "\n".join(context_chunks)
    
    return {
        "fused_context": fused_context,
        "experiment_id": experiment_id,
        "experiment_title": experiment_title,
        "prerequisites": prereq_pathway,
        "score": score
    }
