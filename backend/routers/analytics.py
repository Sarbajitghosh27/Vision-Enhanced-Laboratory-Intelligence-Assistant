"""
backend/routers/analytics.py
FastAPI router for faculty analytics dashboard.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
def get_faculty_analytics():
    """
    Returns analytics and statistical insights for the faculty dashboard.
    Covers common errors, completion times, and student weaknesses.
    """
    return {
        "engagement": {
            "total_students_active": 142,
            "sessions_run": 843,
            "completion_rate_pct": 89.4
        },
        "most_failed_experiments": [
            {"experiment": "Transistor Amplifier (CE)", "fails_count": 34, "pct": 24.2},
            {"experiment": "Wien Bridge Oscillator", "fails_count": 27, "pct": 19.1},
            {"experiment": "Zener Voltage Regulator", "fails_count": 21, "pct": 14.8},
            {"experiment": "PN Junction Diode characteristics", "fails_count": 18, "pct": 12.7}
        ],
        "common_student_mistakes": [
            {"symptom": "Floating TTL inputs", "count": 67, "category": "Digital Electronics"},
            {"symptom": "Missing emitter bypass capacitor", "count": 48, "category": "Analog Circuits"},
            {"symptom": "Reversed electrolytic capacitor", "count": 39, "category": "General Assembly"},
            {"symptom": "Wrong BJT pin alignment (BC547)", "count": 32, "category": "Semiconductors"},
            {"symptom": "Diagonal clipping in AM envelope detector", "count": 29, "category": "Communication Systems"}
        ],
        "average_completion_times_mins": [
            {"lab": "Basic Electronics Lab (Sem 1)", "avg_time_mins": 38.5},
            {"lab": "Analog Circuits Lab (Sem 3)", "avg_time_mins": 52.0},
            {"lab": "Communication Systems Lab (Sem 5)", "avg_time_mins": 46.2}
        ],
        "viva_performance": {
            "average_viva_score": 7.2,
            "total_viva_conducted": 312,
            "highest_viva_score": 10.0,
            "lowest_viva_score": 2.5
        },
        "concept_weaknesses": [
            {"concept": "Feedback Loop Stability (Barkhausen)", "weakness_pct": 42.1},
            {"concept": "Transistor Q-point Biasing", "weakness_pct": 34.8},
            {"concept": "CRO Trigger Level locking", "weakness_pct": 28.5},
            {"concept": "FM VCO Sensitivity kv mapping", "weakness_pct": 21.0}
        ]
    }
