"""
backend/services/diagram_generator.py
Generates and writes downloadable circuit files to the static web folder:
1. LTspice-compatible schematics (.asc)
2. LaTeX Circuitikz blocks
3. KiCad schema mock metadata
"""

import os
import json

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
DOWNLOADS_DIR = os.path.join(STATIC_DIR, "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

LTSPICE_TEMPLATES = {
    "pn_junction": """Version 4
SHEET 1 880 680
WIRE 160 80 80 80
WIRE 320 80 240 80
WIRE 320 160 320 80
WIRE 320 272 320 240
WIRE 80 272 80 80
WIRE 320 272 80 272
FLAG 80 272 0
SYMBOL voltage 80 80 R0
WINDOW 123 0 0 Left 2
WINDOW 39 0 0 Left 2
SYMATTR InstName V1
SYMATTR Value SINE(0 2 50)
SYMBOL resistor 240 64 R90
WINDOW 0 0 56 VLeft 2
WINDOW 3 32 56 VLeft 2
SYMATTR InstName R1
SYMATTR Value 1k
SYMBOL diode 320 160 R0
WINDOW 0 0 56 VLeft 2
WINDOW 3 32 56 VLeft 2
SYMATTR InstName D1
SYMATTR Value 1N4007
""",
    "zener": """Version 4
SHEET 1 880 680
WIRE 160 80 80 80
WIRE 320 80 240 80
WIRE 320 160 320 80
WIRE 320 272 320 240
WIRE 480 80 320 80
WIRE 480 160 480 80
WIRE 480 272 480 240
WIRE 80 272 80 80
WIRE 320 272 80 272
WIRE 480 272 320 272
FLAG 80 272 0
SYMBOL voltage 80 80 R0
SYMATTR InstName V1
SYMATTR Value 10
SYMBOL resistor 240 64 R90
SYMATTR InstName Rs
SYMATTR Value 470
SYMBOL zener 320 160 R0
SYMATTR InstName D1
SYMATTR Value BZX84C5V1
SYMBOL resistor 480 160 R0
SYMATTR InstName RL
SYMATTR Value 1k
""",
    "transistor_amplifier": """Version 4
SHEET 1 880 680
WIRE 80 80 80 160
WIRE 80 160 160 160
WIRE 240 160 200 160
WIRE 200 80 200 160
WIRE 200 240 200 320
WIRE 200 320 80 320
WIRE 320 160 280 160
WIRE 320 80 320 160
WIRE 320 240 320 320
WIRE 320 320 200 320
FLAG 80 320 0
SYMBOL voltage 80 80 R0
SYMATTR InstName VCC
SYMATTR Value 12
SYMBOL npn 240 160 R0
SYMATTR InstName Q1
SYMATTR Value BC547
SYMBOL resistor 200 80 R0
SYMATTR InstName RC
SYMATTR Value 3.3k
SYMBOL resistor 200 240 R0
SYMATTR InstName RE
SYMATTR Value 1k
SYMBOL resistor 320 80 R0
SYMATTR InstName R1
SYMATTR Value 33k
SYMBOL resistor 320 240 R0
SYMATTR InstName R2
SYMATTR Value 10k
""",
    "opamp": """Version 4
SHEET 1 880 680
WIRE 160 80 80 80
WIRE 240 80 160 80
WIRE 320 80 320 160
WIRE 320 160 280 160
WIRE 80 270 80 80
WIRE 320 270 80 270
FLAG 80 270 0
SYMBOL voltage 80 80 R0
SYMATTR InstName Vi
SYMATTR Value SINE(0 0.5 1k)
SYMBOL opamp 240 160 R0
SYMATTR InstName U1
SYMATTR Value LM741
SYMBOL resistor 160 64 R90
SYMATTR InstName R1
SYMATTR Value 10k
SYMBOL resistor 280 64 R90
SYMATTR InstName Rf
SYMATTR Value 100k
""",
    "rc_filters": """Version 4
SHEET 1 880 680
WIRE 160 80 80 80
WIRE 320 80 240 80
WIRE 320 160 320 80
WIRE 320 272 320 240
WIRE 80 272 80 80
WIRE 320 272 80 272
FLAG 80 272 0
SYMBOL voltage 80 80 R0
SYMATTR InstName Vi
SYMATTR Value SINE(0 2 1k)
SYMBOL resistor 240 64 R90
SYMATTR InstName R1
SYMATTR Value 10k
SYMBOL capacitor 320 160 R0
SYMATTR InstName C1
SYMATTR Value 0.01u
"""
}

CIRCUITIKZ_TEMPLATES = {
    "pn_junction": """\\begin{circuitikz}[american]
    \\draw (0,0) to[V, l=$V_{in}$] (0,3)
          to[R, l=$R_1(1k\\Omega)$] (3,3)
          to[D, l=$D_1(1N4007)$] (3,0)
          to[short] (0,0);
    \\draw (3,3) to[short, *-o] (4,3) node[right] {$V_{out}$};
    \\draw (3,0) to[short, *-o] (4,0) node[right] {GND};
\\end{circuitikz}""",
    "zener": """\\begin{circuitikz}[american]
    \\draw (0,0) to[V, l=$V_{in}$] (0,3)
          to[R, l=$R_s(470\\Omega)$] (3,3)
          to[zzdiode, l=$D_Z(5.1V)$] (3,0)
          to[short] (0,0);
    \\draw (3,3) to[short, *-] (5,3)
          to[R, l=$R_L(1k\\Omega)$] (5,0)
          to[short, -*] (3,0);
\\end{circuitikz}""",
    "transistor_amplifier": """\\begin{circuitikz}[american]
    \\draw (0,0) node[ground] {} 
          to[V, l=$V_{in}$] (0,2)
          to[C, l=$C_1(10\\mu F)$] (2,2)
          to[short] (3,2);
    \\draw (3,0) to[R, l=$R_2(10k\\Omega)$] (3,2)
          to[R, l=$R_1(33k\\Omega)$] (3,5) -- (5,5);
    \\draw (5,0) to[R, l=$R_E(1k\\Omega)$] (5,1.5)
          to[empty npn, n=npn] (5,3.5)
          to[R, l=$R_C(3.3k\\Omega)$] (5,5) node[above] {$V_{CC}(+12V)$};
    \\draw (3,2) -- (npn.base);
    \\draw (5,1.5) to[short, *-] (6.5,1.5)
          to[C, l=$C_E(100\\mu F)$] (6.5,0) node[ground] {};
    \\draw (npn.collector) to[short, *-] (6.5,3.5)
          to[C, l=$C_2(10\\mu F)$] (8,3.5) node[right] {$V_{out}$};
\\end{circuitikz}""",
    "opamp": """\\begin{circuitikz}[american]
    \\draw (0,0) node[ground] {}
          to[V, l=$V_i$] (0,2.5)
          to[R, l=$R_1(10k\\Omega)$] (2,2.5) node[above] {$v_-$};
    \\draw (3,2) node[op amp] (opamp) {};
    \\draw (2,2.5) -- (opamp.-);
    \\draw (opamp.+) -- (2,1.5) node[ground] {};
    \\draw (2,2.5) to[short, *-] (2,4)
          to[R, l=$R_f(100k\\Omega)$] (4.2,4)
          to[short, -*] (opamp.out);
    \\draw (opamp.out) -- (5,2) node[right] {$V_{out}$};
\\end{circuitikz}""",
    "rc_filters": """\\begin{circuitikz}[american]
    \\draw (0,0) to[V, l=$V_{in}$] (0,3)
          to[R, l=$R(10k\\Omega)$] (3,3)
          to[C, l=$C(0.01\\mu F)$] (3,0)
          to[short] (0,0);
    \\draw (3,3) to[short, *-o] (4,3) node[right] {$V_{out}$};
    \\draw (3,0) to[short, *-o] (4,0) node[right] {GND};
\\end{circuitikz}"""
}


def _get_key(exp_id: str) -> str:
    for key in LTSPICE_TEMPLATES:
        if key in exp_id.lower():
            return key
    return "rc_filters"


def generate_and_save_cad_files(exp_id: str) -> dict:
    """
    Generates LTspice .asc, KiCad schema, and LaTeX codes,
    writes them to the local static downloads directory, and returns direct URLs.
    """
    key = _get_key(exp_id)
    
    # 1. Generate text strings
    ltspice_code = LTSPICE_TEMPLATES[key]
    circuitikz_latex = CIRCUITIKZ_TEMPLATES[key]
    
    kicad_data = {
        "format": "KiCad Schematic Schema V6",
        "file_extension": ".kicad_sch",
        "metadata": {
            "title": f"Corrected Schematic for {exp_id}",
            "author": "Vision-Language ECE Lab Assistant",
            "kicad_version": "6.0.0",
            "sheet_count": 1
        },
        "symbols": [
            {"id": "V1", "lib": "power:Voltage_Source", "value": "SINE/DC", "pos": [50, 100]},
            {"id": "R1", "lib": "Device:R", "value": "10k" if key=="rc_filters" or key=="opamp" else "1k", "pos": [100, 100]},
            {"id": "D1", "lib": "Device:D", "value": "1N4007" if key=="pn_junction" else "Zener", "pos": [150, 100]}
        ],
        "nets": [
            {"name": "Net-_V1-Pad1_", "connections": ["V1:1", "R1:1"]},
            {"name": "Net-_R1-Pad2_", "connections": ["R1:2", "D1:1"]},
            {"name": "GND", "connections": ["V1:2", "D1:2"]}
        ]
    }
    
    # 2. Write files to disk
    asc_filename = f"corrected_{exp_id}.asc"
    kicad_filename = f"corrected_{exp_id}.kicad_sch"
    latex_filename = f"corrected_{exp_id}.tex"
    
    asc_path = os.path.join(DOWNLOADS_DIR, asc_filename)
    kicad_path = os.path.join(DOWNLOADS_DIR, kicad_filename)
    latex_path = os.path.join(DOWNLOADS_DIR, latex_filename)
    
    with open(asc_path, "w", encoding="utf-8") as f:
        f.write(ltspice_code)
        
    with open(kicad_path, "w", encoding="utf-8") as f:
        json.dump(kicad_data, f, indent=2)
        
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(circuitikz_latex)
        
    # 3. Return codes and download URLs
    return {
        "experiment_id": exp_id,
        "ltspice_code": ltspice_code,
        "ltspice_url": f"/static/downloads/{asc_filename}",
        "circuitikz_latex": circuitikz_latex,
        "circuitikz_url": f"/static/downloads/{latex_filename}",
        "kicad_schema": kicad_data,
        "kicad_url": f"/static/downloads/{kicad_filename}"
    }
