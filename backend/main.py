"""
backend/main.py
Main entry point for the Vision-Language ECE Lab Assistant FastAPI backend.
"""

import sys
import os
# Ensure root directory is on the path for robust imports of rag/backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import experiments, assistant, diagnosis, viva, analytics, kg

app = FastAPI(
    title="VELIA — Vision-Enhanced Laboratory Intelligence Assistant Backend",
    description="Offline-capable FastAPI orchestration layer for ECE Lab guide, fault diagnosis, CV, and analytics.",
    version="1.0.0"
)

# Mount Static Files directory
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
os.makedirs(os.path.join(static_dir, "error_maps"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "downloads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Enable CORS for Streamlit communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(experiments.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(diagnosis.router, prefix="/api")
app.include_router(viva.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(kg.router, prefix="/api")

@app.get("/")
def get_root():
    has_groq = bool(os.getenv("GROQ_API_KEY", ""))
    has_gemini = bool(os.getenv("GEMINI_API_KEY", ""))
    return {
        "status": "online",
        "service": "VELIA API Orchestration Layer",
        "version": "1.0.0",
        "description": "Offline-capable backend API for AI labs. Access /docs for Swagger UI API docs.",
        "ai_status": {
            "groq_configured": has_groq,
            "gemini_configured": has_gemini
        }
    }

@app.get("/health")
def get_health():
    return {"status": "ok", "message": "VELIA backend active and responsive"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting VELIA FastAPI server on http://{host}:{port}...")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
