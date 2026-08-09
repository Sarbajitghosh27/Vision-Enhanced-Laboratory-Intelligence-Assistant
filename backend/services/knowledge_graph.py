"""
backend/services/knowledge_graph.py
Defines the Semester-Wise Electronics Knowledge Graph.
Maps concepts, lab experiments, and prerequisite topics.
"""

ECE_KNOWLEDGE_GRAPH = {
    "nodes": [
        # Concept nodes
        {"id": "c_semiconductors", "label": "Semiconductor Physics", "type": "concept", "semester": 1},
        {"id": "c_pn_diode", "label": "PN Junction Diode", "type": "concept", "semester": 1},
        {"id": "c_zener_diode", "label": "Zener Diode Breakdown", "type": "concept", "semester": 1},
        {"id": "c_rectifiers", "label": "Rectifiers & Filters", "type": "concept", "semester": 3},
        {"id": "c_bjt", "label": "BJT Physics", "type": "concept", "semester": 1},
        {"id": "c_amplifier", "label": "Common Emitter Amplification", "type": "concept", "semester": 1},
        {"id": "c_opamp", "label": "Operational Amplifiers", "type": "concept", "semester": 1},
        {"id": "c_filters", "label": "Passive Filters (LPF/HPF)", "type": "concept", "semester": 3},
        {"id": "c_oscillators", "label": "Sinusoidal Oscillators", "type": "concept", "semester": 3},
        {"id": "c_digital", "label": "Digital Logic & Boolean Algebra", "type": "concept", "semester": 1},
        {"id": "c_am", "label": "Amplitude Modulation", "type": "concept", "semester": 5},
        {"id": "c_fm", "label": "Frequency Modulation", "type": "concept", "semester": 5},

        # Lab nodes
        {"id": "lab_cro", "label": "CRO & Lissajous Measurements", "type": "lab", "semester": 1},
        {"id": "lab_pn_vi", "label": "Diode V-I characteristics", "type": "lab", "semester": 1},
        {"id": "lab_zener_reg", "label": "Zener Regulator Design", "type": "lab", "semester": 1},
        {"id": "lab_bjt_curves", "label": "BJT Characteristics Lab", "type": "lab", "semester": 1},
        {"id": "lab_ce_amp", "label": "BJT Amplifier Design", "type": "lab", "semester": 1},
        {"id": "lab_opamp_gain", "label": "Op-Amp Closed-Loop Gain", "type": "lab", "semester": 1},
        {"id": "lab_logic", "label": "Logic Gate Realization", "type": "lab", "semester": 1},
        {"id": "lab_rectifiers", "label": "Rectifier Construction", "type": "lab", "semester": 3},
        {"id": "lab_filters", "label": "RC Frequency Response", "type": "lab", "semester": 3},
        {"id": "lab_phase_shift", "gi": "RC Phase Shift Oscillator", "label": "RC Phase Shift Oscillator", "type": "lab", "semester": 3},
        {"id": "lab_wien", "label": "Wien Bridge Oscillator", "type": "lab", "semester": 3},
        {"id": "lab_am", "label": "AM Modulation & Demod", "type": "lab", "semester": 5},
        {"id": "lab_fm", "label": "FM Modulation & Demod", "type": "lab", "semester": 5}
    ],
    "edges": [
        # Prerequisite links (from -> to)
        {"from": "c_semiconductors", "to": "c_pn_diode", "label": "Prerequisite"},
        {"from": "c_pn_diode", "to": "c_zener_diode", "label": "Prerequisite"},
        {"from": "c_pn_diode", "to": "c_rectifiers", "label": "Prerequisite"},
        {"from": "c_pn_diode", "to": "c_bjt", "label": "Prerequisite"},
        {"from": "c_bjt", "to": "c_amplifier", "label": "Prerequisite"},
        {"from": "c_amplifier", "to": "c_opamp", "label": "Prerequisite"},
        {"from": "c_opamp", "to": "c_filters", "label": "Prerequisite"},
        {"from": "c_opamp", "to": "c_oscillators", "label": "Prerequisite"},
        {"from": "c_filters", "to": "c_oscillators", "label": "Prerequisite"},
        {"from": "c_amplifier", "to": "c_am", "label": "Prerequisite"},
        {"from": "c_oscillators", "to": "c_fm", "label": "Prerequisite"},

        # Lab belongs to concept links
        {"from": "lab_pn_vi", "to": "c_pn_diode", "label": "Validates"},
        {"from": "lab_zener_reg", "to": "c_zener_diode", "label": "Applies"},
        {"from": "lab_rectifiers", "to": "c_rectifiers", "label": "Validates"},
        {"from": "lab_bjt_curves", "to": "c_bjt", "label": "Validates"},
        {"from": "lab_ce_amp", "to": "c_amplifier", "label": "Applies"},
        {"from": "lab_opamp_gain", "to": "c_opamp", "label": "Validates"},
        {"from": "lab_filters", "to": "c_filters", "label": "Applies"},
        {"from": "lab_phase_shift", "to": "c_oscillators", "label": "Applies"},
        {"from": "lab_wien", "to": "c_oscillators", "label": "Applies"},
        {"from": "lab_logic", "to": "c_digital", "label": "Validates"},
        {"from": "lab_am", "to": "c_am", "label": "Applies"},
        {"from": "lab_fm", "to": "c_fm", "label": "Applies"}
    ]
}


def get_knowledge_graph() -> dict:
    """Returns the full knowledge graph nodes and edges."""
    return ECE_KNOWLEDGE_GRAPH


def get_prerequisite_pathway(concept_name: str) -> list:
    """
    Returns nodes representing the prerequisite path to master a concept.
    E.g. Wien Bridge Oscillator requires LPF/HPF Filters and Op-Amps.
    """
    pathway = []
    concept_lower = concept_name.lower()
    
    # Map input weak concept string to graph IDs
    target_node = None
    for n in ECE_KNOWLEDGE_GRAPH["nodes"]:
        if n["label"].lower() in concept_lower or concept_lower in n["label"].lower():
            target_node = n
            break
            
    if not target_node:
        return [{"label": "Basic Semiconductor Physics", "detail": "Master diode biasing and energy bands first."}]

    # Compute immediate prerequisite nodes from edges
    direct_prereqs = []
    for edge in ECE_KNOWLEDGE_GRAPH["edges"]:
        if edge["to"] == target_node["id"] and edge["label"] == "Prerequisite":
            # Find the from node
            for n in ECE_KNOWLEDGE_GRAPH["nodes"]:
                if n["id"] == edge["from"]:
                    direct_prereqs.append(n)
                    break
                    
    for p in direct_prereqs:
        pathway.append({
            "label": p["label"],
            "type": p["type"],
            "semester": p["semester"],
            "detail": f"Prerequisite foundation for {target_node['label']}. Make sure you understand this concept first."
        })
        
    if not pathway:
        pathway.append({
            "label": "Basic Electronics Principles",
            "type": "concept",
            "semester": 1,
            "detail": "Understand voltage loops, currents, and component ratings."
        })
        
    return pathway
