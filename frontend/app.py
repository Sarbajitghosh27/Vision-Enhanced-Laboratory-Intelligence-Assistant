"""
frontend/app.py — ECE Intelligent Laboratory Assistant
Premium AI Product User Interface communicating with FastAPI Backend
"""

import streamlit as st
import requests
import json
import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Ensure the project root is in the python path for importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.ece_syllabus import ECE_SYLLABUS

def find_matching_db_exp(syllabus_exp, db_exps):
    for db_exp in db_exps:
        if db_exp["title"].lower() == syllabus_exp["title"].lower():
            return db_exp
        if "id_match" in syllabus_exp and syllabus_exp["id_match"] in db_exp["id"]:
            return db_exp
    return None

# ── Backend Configuration ───────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://vision-enhanced-laboratory-intelligence.onrender.com/api")

# ── Load Logo Assets ─────────────────────────────────────────────────────────
import base64
from PIL import Image
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
logo_square_path = os.path.join(os.path.dirname(__file__), "logo_square.png")
logo_img = None
logo_html_src = ""
logo_square_html_src = ""

if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode("utf-8")
            logo_html_src = f"data:image/png;base64,{logo_base64}"
    except Exception:
        pass

if os.path.exists(logo_square_path):
    try:
        logo_img = Image.open(logo_square_path)
        with open(logo_square_path, "rb") as f:
            logo_square_base64 = base64.b64encode(f.read()).decode("utf-8")
            logo_square_html_src = f"data:image/png;base64,{logo_square_base64}"
    except Exception:
        pass

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VELIA — Vision-Enhanced Laboratory Intelligence Assistant",
    page_icon=logo_img if logo_img else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom Premium Styling (Dark Theme, Glassmorphism, Custom Fonts) ─────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
  
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    color: #f8fafc;
  }
  
  /* Main background gradient matching enterprise AI platforms */
  .stApp {
    background-color: #05070f;
    background-image: 
        radial-gradient(at 5% 10%, rgba(59, 130, 246, 0.12) 0px, transparent 45%),
        radial-gradient(at 95% 85%, rgba(139, 92, 246, 0.12) 0px, transparent 45%),
        radial-gradient(at 50% 50%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
    background-attachment: fixed;
  }
  
  /* Sidebar dark styling */
  [data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
  }
  
  /* Premium Glassmorphism Cards */
  .glass-card {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7) !important;
    margin-bottom: 20px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  }
  
  .glass-card:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(59, 130, 246, 0.25) !important;
    box-shadow: 0 15px 35px -5px rgba(59, 130, 246, 0.1) !important;
  }
  
  /* Capability Card Deck */
  .feat-card {
    background: rgba(17, 24, 39, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 10px;
    padding: 18px;
    height: 100%;
    transition: all 0.25s ease;
  }
  
  .feat-card:hover {
    border-color: rgba(139, 92, 246, 0.2);
    background: rgba(17, 24, 39, 0.6);
    box-shadow: 0 5px 20px rgba(139, 92, 246, 0.05);
  }
  
  .glow-text {
    background: linear-gradient(135deg, #60a5fa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  .formula-block {
    background: #090d16;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: monospace;
    font-size: 14px;
    margin: 8px 0;
    border-left: 4px solid #a78bfa;
    color: #cbd5e1;
    border-right: 1px solid rgba(255, 255, 255, 0.03);
  }

  .source-badge {
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 20px;
    background: rgba(30, 58, 138, 0.3);
    color: #93c5fd;
    font-family: monospace;
    border: 1px solid rgba(59, 130, 246, 0.2);
  }
  
  /* Custom styled Badges */
  .badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 5px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-right: 6px;
  }
  
  .badge-easy {
    background: rgba(16, 185, 129, 0.12);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.2);
  }
  
  .badge-medium {
    background: rgba(245, 158, 11, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.2);
  }
  
  .badge-hard {
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.2);
  }
  
  /* Streamlit Tabs Custom Design */
  button[data-baseweb="tab"] {
      background-color: transparent !important;
      border: 1px solid rgba(255, 255, 255, 0.05) !important;
      border-radius: 8px !important;
      padding: 8px 16px !important;
      margin-right: 6px !important;
      color: #94a3b8 !important;
      transition: all 0.3s ease !important;
  }
  button[data-baseweb="tab"]:hover {
      border-color: rgba(59, 130, 246, 0.4) !important;
      color: #f1f5f9 !important;
  }
  button[data-baseweb="tab"][aria-selected="true"] {
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(124, 58, 237, 0.15)) !important;
      border-color: #3b82f6 !important;
      color: #60a5fa !important;
      box-shadow: 0 0 12px rgba(59, 130, 246, 0.15) !important;
  }
  
  /* Conversational Chat Bubbles */
  .chat-bubble {
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0;
    max-width: 85%;
    font-size: 14px;
    line-height: 1.5;
  }
  
  .chat-ai {
    background: rgba(30, 41, 59, 0.6);
    border-left: 4px solid #3b82f6;
    border-top: 1px solid rgba(255, 255, 255, 0.03);
    color: #cbd5e1;
    align-self: flex-start;
  }
  
  .chat-student {
    background: rgba(124, 58, 237, 0.12);
    border-left: 4px solid #8b5cf6;
    border-top: 1px solid rgba(255, 255, 255, 0.03);
    color: #e2e8f0;
    margin-left: auto;
  }

  /* File Uploader custom border styling */
  [data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.4) !important;
    border: 2px dashed rgba(59, 130, 246, 0.2) !important;
    border-radius: 10px !important;
  }
  
  /* Interactive Premium Buttons styling */
  .stButton>button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    padding: 8px 20px !important;
  }
  .stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 15px rgba(37, 99, 235, 0.4) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
  }
  .stButton>button:active {
    transform: translateY(0) !important;
  }
  
  /* Secondary/Exit button style overrides */
  .stButton>button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.5) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
  }
  .stButton>button[kind="secondary"]:hover {
    background: rgba(30, 41, 59, 0.8) !important;
    box-shadow: 0 0 10px rgba(148, 163, 184, 0.1) !important;
  }

  /* Developer Credit Sidebar Card */
  .dev-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.5)) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-left: 4px solid #3b82f6 !important;
    border-radius: 10px !important;
    padding: 16px !important;
    margin-top: 20px !important;
    text-align: center !important;
  }

  /* Status Pulsing Animations */
  @keyframes pulse {
    0% {
      transform: scale(0.9);
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
      transform: scale(1);
      box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
    }
    100% {
      transform: scale(0.9);
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
  }
  @keyframes pulse-offline {
    0% {
      transform: scale(0.9);
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
    }
    70% {
      transform: scale(1);
      box-shadow: 0 0 0 6px rgba(239, 68, 68, 0);
    }
    100% {
      transform: scale(0.9);
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    }
  }
  
  .status-indicator-online {
    height: 8px;
    width: 8px;
    background-color: #10b981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #10b981;
    animation: pulse 2s infinite;
  }
  
  .status-indicator-offline {
    height: 8px;
    width: 8px;
    background-color: #ef4444;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #ef4444;
    animation: pulse-offline 2s infinite;
  }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions for API Communication ───────────────────────────────────
def get_backend_root_url():
    return API_BASE_URL.replace("/api", "").rstrip("/")

def check_backend_status():
    """
    Pings backend root and returns status dict:
    'status': 'online' | 'waking_up' | 'offline'
    """
    root_url = get_backend_root_url()
    try:
        r = requests.get(root_url, timeout=4)
        if r.status_code == 200:
            return {"status": "online", "data": r.json()}
    except requests.exceptions.Timeout:
        return {"status": "waking_up", "message": "Render free-tier instance is spinning up (~30-50s)..."}
    except requests.exceptions.ConnectionError:
        pass
    except Exception as e:
        print(f"Backend ping error: {e}")
    return {"status": "offline", "message": "Backend server is offline or unreachable."}


def get_all_experiments(semester=None):
    try:
        params = {}
        if semester:
            params["semester"] = semester
        r = requests.get(f"{API_BASE_URL}/experiments", params=params, timeout=15)
        if r.status_code == 200:
            return r.json()
        st.warning(f"Experiment catalog returned status {r.status_code}.")
        return []
    except requests.exceptions.Timeout:
        st.info("⏳ Backend is waking up. Loading experiments may take a few moments on cold start...")
        return []
    except Exception as e:
        print(f"Failed to fetch experiments: {e}")
        return []


def get_experiment_detail(exp_id):
    try:
        r = requests.get(f"{API_BASE_URL}/experiments/{exp_id}", timeout=50)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"Failed to fetch details for {exp_id}: Server returned status code {r.status_code}")
            return None
    except requests.exceptions.Timeout:
        st.error(f"⏳ Request for experiment '{exp_id}' timed out. If the backend is still spinning up, please retry.")
        return None
    except Exception as e:
        st.error(f"Failed to fetch details for {exp_id}: {e}")
        return None


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


# ── Helper Functions for Plotly Interactive Visualizations ──────────────────
def plot_plotly_bode(bode_data):
    freqs = [p["frequency_hz"] for p in bode_data]
    gains = [p["gain_db"] for p in bode_data]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freqs, y=gains,
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=6, color='#60a5fa'),
        name='Voltage Gain (dB)'
    ))
    
    fig.update_layout(
        title="<b>Frequency Response (Bode Plot)</b>",
        title_font=dict(size=14, color='#f8fafc', family='Outfit'),
        paper_bgcolor='rgba(15, 23, 42, 0.4)',
        plot_bgcolor='rgba(9, 13, 22, 0.8)',
        xaxis=dict(
            type='log',
            title=dict(text='Frequency (Hz)', font=dict(color='#cbd5e1', size=11)),
            tickfont=dict(color='#94a3b8', size=10),
            gridcolor='#1e293b',
            zerolinecolor='#1e293b'
        ),
        yaxis=dict(
            title=dict(text='Gain (dB)', font=dict(color='#cbd5e1', size=11)),
            tickfont=dict(color='#94a3b8', size=10),
            gridcolor='#1e293b',
            zerolinecolor='#1e293b'
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        height=320,
        showlegend=False
    )
    return fig


def plot_plotly_load_line(load_line, q_point):
    vces = [p["Vce_V"] for p in load_line]
    ics = [p["Ic_mA"] for p in load_line]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=vces, y=ics,
        mode='lines',
        line=dict(color='#a78bfa', width=3),
        name='DC Load Line'
    ))
    
    q_vce = q_point["Vce_V"]
    q_ic = q_point["Ic_mA"]
    fig.add_trace(go.Scatter(
        x=[q_vce], y=[q_ic],
        mode='markers+text',
        marker=dict(color='#f43f5e', size=13, line=dict(color='#ffffff', width=2)),
        text=[f"Q ({q_vce:.2f}V, {q_ic:.2f}mA)"],
        textposition="top right",
        textfont=dict(color='#f8fafc', size=10),
        name='Q-Point'
    ))
    
    fig.update_layout(
        title="<b>BJT DC Load Line & Q-Point</b>",
        title_font=dict(size=14, color='#f8fafc', family='Outfit'),
        paper_bgcolor='rgba(15, 23, 42, 0.4)',
        plot_bgcolor='rgba(9, 13, 22, 0.8)',
        xaxis=dict(
            title=dict(text='V_CE (Voltage, V)', font=dict(color='#cbd5e1', size=11)),
            tickfont=dict(color='#94a3b8', size=10),
            gridcolor='#1e293b',
            zerolinecolor='#1e293b'
        ),
        yaxis=dict(
            title=dict(text='I_C (Current, mA)', font=dict(color='#cbd5e1', size=11)),
            tickfont=dict(color='#94a3b8', size=10),
            gridcolor='#1e293b',
            zerolinecolor='#1e293b'
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        height=320,
        showlegend=False
    )
    return fig


def plot_plotly_failures(failed_exps):
    df = pd.DataFrame(failed_exps)
    fig = px.bar(
        df,
        x='pct',
        y='experiment',
        orientation='h',
        labels={'pct': 'Failure Rate (%)', 'experiment': 'Laboratory'},
        title='<b>Most Frequently Failed Experiments</b>'
    )
    fig.update_traces(marker_color='#ef4444', marker_line_color='rgba(255,255,255,0.1)', opacity=0.8)
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 0.4)',
        plot_bgcolor='rgba(9, 13, 22, 0.8)',
        title_font=dict(size=14, color='#f8fafc', family='Outfit'),
        font=dict(color='#cbd5e1', size=10),
        xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8')),
        yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8')),
        margin=dict(l=140, r=20, t=40, b=40),
        height=300
    )
    return fig


def plot_plotly_weaknesses(weaknesses):
    df = pd.DataFrame(weaknesses)
    fig = px.pie(
        df,
        values='weakness_pct',
        names='concept',
        title='<b>Cohort Concept-wise Weaknesses</b>',
        color_discrete_sequence=px.colors.sequential.Purples_r
    )
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 0.4)',
        plot_bgcolor='rgba(9, 13, 22, 0.8)',
        title_font=dict(size=14, color='#f8fafc', family='Outfit'),
        font=dict(color='#cbd5e1', size=11),
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        showlegend=True,
        legend=dict(font=dict(size=9))
    )
    return fig


# ── Vis.js HTML Injection for Knowledge Graph ────────────────────────────────
def draw_visjs_graph(nodes, edges):
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
            #mynetwork {{
                width: 100%;
                height: 460px;
                background-color: #090d16;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }}
        </style>
    </head>
    <body>
        <div id="mynetwork"></div>
        <script type="text/javascript">
            var rawNodes = {nodes_json};
            var rawEdges = {edges_json};
            
            var nodesArray = rawNodes.map(function(node) {{
                var color = '#2563eb'; // Concept default
                if (node.type === 'lab') {{
                    color = '#059669'; // Lab Experiment
                }}
                return {{
                    id: node.id,
                    label: node.label,
                    shape: 'box',
                    margin: 12,
                    color: {{
                        background: color,
                        border: 'rgba(255,255,255,0.1)',
                        highlight: {{
                            background: '#7c3aed',
                            border: '#a78bfa'
                        }}
                    }},
                    font: {{
                        color: '#f8fafc',
                        face: 'Outfit, sans-serif',
                        size: 13
                    }},
                    borderWidth: 1,
                    shadow: true
                }};
            }});
            
            var edgesArray = rawEdges.map(function(edge) {{
                return {{
                    from: edge.from,
                    to: edge.to,
                    label: edge.label || '',
                    font: {{
                        color: '#64748b',
                        size: 10,
                        background: '#090d16'
                    }},
                    arrows: 'to',
                    color: {{
                        color: '#334155',
                        highlight: '#7c3aed'
                    }},
                    width: 1.5
                }};
            }});
            
            var container = document.getElementById('mynetwork');
            var data = {{
                nodes: new vis.DataSet(nodesArray),
                edges: new vis.DataSet(edgesArray)
            }};
            var options = {{
                physics: {{
                    barnesHut: {{
                        gravitationalConstant: -1800,
                        centralGravity: 0.25,
                        springLength: 95,
                        springConstant: 0.04
                    }}
                }},
                interaction: {{
                    hover: true,
                    dragNodes: true,
                    zoomView: true
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    return html_code


# ── Render Page Top / Status ─────────────────────────────────────────────────
backend_ok = check_backend_status()

# ── Sidebar Branding ─────────────────────────────────────────────────────────
with st.sidebar:
    # 1. Custom CSS-based Brand Emblem & Title (Using the Logo asset if loaded)
    if logo_square_html_src:
        emblem_html = (
            f'<div style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; '
            f'overflow: hidden; border-radius: 8px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);">'
            f'<img src="{logo_square_html_src}" style="max-width: 100%; max-height: 100%; object-fit: contain; '
            f'image-rendering: -webkit-optimize-contrast; image-rendering: crisp-edges;" />'
            f'</div>'
        )
    else:
        emblem_html = (
            f'<div style="background: linear-gradient(135deg, #2563eb, #7c3aed); width: 44px; height: 44px; '
            f'border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; '
            f'font-size: 20px; color: white; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35);">V</div>'
        )

    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 14px; margin-top: 15px; margin-bottom: 25px; '
        f'background: rgba(15, 23, 42, 0.4); padding: 12px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.04);">'
        f'{emblem_html}'
        f'<div>'
        f'<span style="font-size: 18px; font-weight: 800; color: #f8fafc; letter-spacing: 0.5px; line-height: 1.1; '
        f'display: block; font-family: \'Outfit\', sans-serif;">VELIA</span>'
        f'<span style="font-size: 8.5px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.2px; '
        f'font-weight: 600; display: block; margin-top: 2px;">Intelligence Assistant</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # 2. Pulsing Status Indicator Card
    backend_status = backend_ok.get("status") if isinstance(backend_ok, dict) else ("online" if backend_ok else "offline")
    
    if backend_status == "online":
        ai_info = backend_ok.get("data", {}).get("ai_status", {})
        groq_on = ai_info.get("groq_configured", True)
        gemini_on = ai_info.get("gemini_configured", True)
        ai_badge = " (AI Ready)" if (groq_on or gemini_on) else " (Offline Fallback)"
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 10px 14px; display: flex; align-items: center; gap: 10px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.05);">
          <span class="status-indicator-online"></span>
          <div>
            <span style="color: #34d399; font-size: 12.5px; font-weight: 600; letter-spacing: 0.3px; display:block;">API Core Online{ai_badge}</span>
            <span style="color: #6ee7b7; font-size: 9px; opacity: 0.8;">{get_backend_root_url()}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    elif backend_status == "waking_up":
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 10px 14px; margin-bottom: 15px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#f59e0b; box-shadow:0 0 8px #f59e0b;"></span>
            <span style="color: #fbbf24; font-size: 12.5px; font-weight: 600;">Server Waking Up (~45s)</span>
          </div>
          <p style="color: #fde68a; font-size: 10px; margin-top: 6px; margin-bottom: 0;">Free-tier instance is spinning up. First request takes ~50s.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Check Server Status", use_container_width=True):
            st.rerun()
    else:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-bottom: 15px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span class="status-indicator-offline"></span>
            <span style="color: #f87171; font-size: 12.5px; font-weight: 600; letter-spacing: 0.3px;">API Core Offline</span>
          </div>
          <span style="color: #fca5a5; font-size: 9.5px; display:block; margin-top:4px;">Target: {get_backend_root_url()}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Reconnect / Wake Server", use_container_width=True):
            st.rerun()
        
    # Track selection in Session State
    if "active_exp_id" not in st.session_state:
        st.session_state.active_exp_id = None
        st.session_state.active_exp_title = None

    # Workspace status
    if st.session_state.active_exp_id:
        st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.04); border: 1px solid rgba(59, 130, 246, 0.1); border-radius: 8px; padding: 12px; margin-bottom: 20px;">
            <span style="color: #94a3b8; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; display:block;">ACTIVE LAB WORKSPACE</span>
            <div style="color: #f1f5f9; font-weight: 600; font-size: 13px; margin-top: 4px; margin-bottom: 10px; line-height: 1.4;">{st.session_state.active_exp_title}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Exit Lab Workspace", use_container_width=True, type="secondary"):
            st.session_state.active_exp_id = None
            st.session_state.active_exp_title = None
            st.rerun()
    else:
        st.markdown("""
        <div style="color: #94a3b8; font-size: 12px; line-height: 1.5; padding: 4px 6px; margin-bottom: 25px;">
            Explore the ECE syllabus experiments on the homepage, then click <b>Launch Workspace</b> on any lab to begin simulations, diagnosis scans, and viva exams.
        </div>
        """, unsafe_allow_html=True)
        
    # Spacer instead of harsh divider line
    st.markdown('<div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent); margin: 20px 0;"></div>', unsafe_allow_html=True)
    
    # 3. Developer Credit Card & System Environment Info (Merged and Redesigned)
    dev_card_html = (
        f'<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.45)) !important; '
        f'border: 1px solid rgba(255, 255, 255, 0.06) !important; border-top: 2px solid #8b5cf6 !important; '
        f'border-radius: 12px !important; padding: 16px !important; margin-top: 20px !important; '
        f'box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.8) !important; backdrop-filter: blur(10px) !important;">'
        f'<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; text-align: left;">'
        f'<div style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); width: 36px; height: 36px; '
        f'border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; '
        f'font-size: 13px; color: #ffffff; box-shadow: 0 0 10px rgba(139, 92, 246, 0.4); '
        f'border: 1px solid rgba(255, 255, 255, 0.1);">SG</div>'
        f'<div>'
        f'<span style="color: #94a3b8; font-size: 8px; font-weight: 700; text-transform: uppercase; '
        f'letter-spacing: 1px; display: block;">SYSTEM DEVELOPER</span>'
        f'<span style="font-size: 14px; font-weight: 800; color: #f8fafc; display: block; '
        f'font-family: \'Outfit\', sans-serif;">Sarbajit Ghosh</span>'
        f'<span style="font-size: 10px; color: #a78bfa; font-weight: 500; display: block; margin-top: 1px;">Dept. of ECE, BIT Mesra</span>'
        f'</div>'
        f'</div>'
        f'<div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent); margin: 10px 0;"></div>'
        f'<div style="text-align: left;">'
        f'<span style="color: #64748b; font-size: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; display: block; margin-bottom: 3px;">SYSTEM ENVIRONMENT</span>'
        f'<span style="color: #cbd5e1; font-size: 10.5px; line-height: 1.4; display: block; font-weight: 400;">'
        f'Offline-capable local inference stack running through FastAPI orchestration layer.'
        f'</span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(dev_card_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ── LANDING PAGE: PRODUCT SHOWCASE & CATALOG ─────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.active_exp_id:
    # ── 1. Hero Showcase Banner ──
    logo_header_html = ""
    if logo_html_src:
        logo_header_html = (
            f'<div style="margin: 0 auto 20px auto; width: 268px; display: flex; align-items: center; '
            f'justify-content: center; filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.25));">'
            f'<img src="{logo_html_src}" style="width: 100%; height: auto; object-fit: contain; '
            f'image-rendering: -webkit-optimize-contrast; image-rendering: crisp-edges;" />'
            f'</div>'
        )
        
    st.markdown(
        f'<div style="position: relative; padding: 45px 24px; text-align: center; background: radial-gradient(circle, rgba(15,23,42,0.75) 0%, rgba(5,7,15,1) 100%); border-radius: 16px; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 35px; overflow: hidden;">'
        f'<div style="position: absolute; top: -50px; left: -50px; width: 220px; height: 220px; background: rgba(59,130,246,0.15); filter: blur(80px); border-radius: 50%;"></div>'
        f'<div style="position: absolute; bottom: -50px; right: -50px; width: 250px; height: 250px; background: rgba(139,92,246,0.12); filter: blur(95px); border-radius: 50%;"></div>'
        f'{logo_header_html}'
        f'<h1 style="font-size: 40px; margin: 12px 0; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2;"><span class="glow-text">VELIA — Vision-Enhanced Laboratory Intelligence Assistant</span></h1>'
        f'<p style="font-size: 16px; color: #94a3b8; max-width: 820px; margin: 0 auto 30px auto; font-family: \'Inter\', sans-serif; font-weight: 300; line-height: 1.6;">An offline-capable AI virtual laboratory environment for Electronics & Communication Engineering. Integrates deep learning computer vision, graph neural networks, SPICE digital twins, and LLM-explainable diagnostics.<br><br><span style="color:#60a5fa; font-weight: 500; font-size:14px; letter-spacing:0.5px;">Developed by Sarbajit Ghosh (Department of ECE, BIT Mesra)</span></p>'
        f'<div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">'
        f'<span style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); padding: 5px 12px; border-radius: 20px; font-size: 11px; color: #cbd5e1; font-weight: 500;">YOLOv8 Assembly Scan</span>'
        f'<span style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); padding: 5px 12px; border-radius: 20px; font-size: 11px; color: #cbd5e1; font-weight: 500;">Graph Neural Networks</span>'
        f'<span style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); padding: 5px 12px; border-radius: 20px; font-size: 11px; color: #cbd5e1; font-weight: 500;">Digital Twin Solver</span>'
        f'<span style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); padding: 5px 12px; border-radius: 20px; font-size: 11px; color: #cbd5e1; font-weight: 500;">Adaptive LLM Examiner</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── 2. Real-Time Platform Statistics (Clickable Dashboard) ──
    st.markdown("### Platform Metrics & Benchmarks")
    st.caption("Click on any button below to explore the detailed integration specifications.")
    
    if "selected_metric" not in st.session_state:
        st.session_state.selected_metric = None
        
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        is_selected = st.session_state.selected_metric == "curriculum"
        border_color = "rgba(59, 130, 246, 0.5)" if is_selected else "rgba(255, 255, 255, 0.05)"
        shadow_style = "box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);" if is_selected else ""
        st.markdown(f"""
        <div style="background:rgba(17,24,39,0.5); border:1px solid {border_color}; border-radius:10px; padding:20px; text-align:center; transition:all 0.3s; {shadow_style}">
            <span style="color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Curriculum Experiments</span><br>
            <span style="font-size:32px; font-weight:800; color:#3b82f6;">80+</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Curriculum", key="btn_curriculum", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.selected_metric = None if is_selected else "curriculum"
            st.rerun()
            
    with col_stat2:
        is_selected = st.session_state.selected_metric == "models"
        border_color = "rgba(16, 185, 129, 0.5)" if is_selected else "rgba(255, 255, 255, 0.05)"
        shadow_style = "box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);" if is_selected else ""
        st.markdown(f"""
        <div style="background:rgba(17,24,39,0.5); border:1px solid {border_color}; border-radius:10px; padding:20px; text-align:center; transition:all 0.3s; {shadow_style}">
            <span style="color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">AI Models Stack</span><br>
            <span style="font-size:32px; font-weight:800; color:#10b981;">4</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore AI Models", key="btn_models", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.selected_metric = None if is_selected else "models"
            st.rerun()
            
    with col_stat3:
        is_selected = st.session_state.selected_metric == "faults"
        border_color = "rgba(245, 158, 11, 0.5)" if is_selected else "rgba(255, 255, 255, 0.05)"
        shadow_style = "box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);" if is_selected else ""
        st.markdown(f"""
        <div style="background:rgba(17,24,39,0.5); border:1px solid {border_color}; border-radius:10px; padding:20px; text-align:center; transition:all 0.3s; {shadow_style}">
            <span style="color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Fault Biasing Isolated</span><br>
            <span style="font-size:32px; font-weight:800; color:#f59e0b;">8</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Fault Classes", key="btn_faults", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.selected_metric = None if is_selected else "faults"
            st.rerun()
            
    with col_stat4:
        is_selected = st.session_state.selected_metric == "knowledge"
        border_color = "rgba(167, 139, 250, 0.5)" if is_selected else "rgba(255, 255, 255, 0.05)"
        shadow_style = "box-shadow: 0 0 15px rgba(167, 139, 250, 0.2);" if is_selected else ""
        st.markdown(f"""
        <div style="background:rgba(17,24,39,0.5); border:1px solid {border_color}; border-radius:10px; padding:20px; text-align:center; transition:all 0.3s; {shadow_style}">
            <span style="color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Knowledge Concepts</span><br>
            <span style="font-size:32px; font-weight:800; color:#a78bfa;">25 Nodes</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Concept Maps", key="btn_knowledge", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.selected_metric = None if is_selected else "knowledge"
            st.rerun()
            
    # Render Details block based on selection
    if st.session_state.selected_metric == "curriculum":
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid #3b82f6 !important; background: rgba(30, 41, 59, 0.4) !important; margin-top:20px;">
            <h4 style="color:#60a5fa; margin-top:0;">Curriculum Experiments Coverage</h4>
            <p style="font-size:13.5px; color:#cbd5e1; line-height:1.6; margin-bottom: 20px;">
                VELIA covers a wide array of laboratory experiments across semesters. These virtual labs provide SPICE simulation digital twins, automated verification, and hardware diagnostics.
            </p>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;">
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#60a5fa; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Semester I & III</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Basic Electronics & Networks</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Diodes, Zeners, Rectifiers, and basic CRO measurements are covered.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#60a5fa; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Semester IV & V</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Analog Circuits & ICs</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">BJT Amplifiers, Op-Amp configurations, filters, and oscillators.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#60a5fa; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Semester VI</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Digital Communications</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">AM/FM Modulator, Phase Shift Keying, and signal sampling rates.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#60a5fa; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Semester VII</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Microprocessors & IoT</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">I2C Communication, Embedded EEPROM read/writes, ADC/DAC modules.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Close Details", key="close_curriculum", use_container_width=True):
            st.session_state.selected_metric = None
            st.rerun()
            
    elif st.session_state.selected_metric == "models":
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid #10b981 !important; background: rgba(30, 41, 59, 0.4) !important; margin-top:20px;">
            <h4 style="color:#34d399; margin-top:0;">VELIA Artificial Intelligence Stack</h4>
            <p style="font-size:13.5px; color:#cbd5e1; line-height:1.6; margin-bottom: 20px;">
                Our hybrid intelligence pipeline integrates four modern machine learning models and computer vision pipelines to analyze, verify, and explain circuits.
            </p>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;">
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#10b981; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">1. Bounding-Box Detection</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">YOLOv8 CV Engine</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Identifies resistor values, diode orientation, IC pins, and breadboard row contacts.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#10b981; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">2. Topology Analysis</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">PyTorch Graph Neural Network</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Processes adjacency matrices to isolate circuit mismatches and wiring anomalies.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#10b981; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">3. Waveform Parser</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">OpenCV HSV Trace Masking</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Processes screen coordinates and traces signals to measure Vp-p, frequency, and clipping.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#10b981; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">4. Explanation & Tutoring</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">RAG & Fine-Tuned Local LLM</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Retrieves lab documentation to provide structured debugging fixes and conduct viva exams.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Close Details", key="close_models", use_container_width=True):
            st.session_state.selected_metric = None
            st.rerun()
            
    elif st.session_state.selected_metric == "faults":
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid #f59e0b !important; background: rgba(30, 41, 59, 0.4) !important; margin-top:20px;">
            <h4 style="color:#fbbf24; margin-top:0;">Isolated Circuit Fault Categories</h4>
            <p style="font-size:13.5px; color:#cbd5e1; line-height:1.6; margin-bottom: 20px;">
                Our diagnostic estimators isolate deviations in biasing, wiring, digital logic, and communication signals across eight comprehensive ECE fault classes to support all 80+ curriculum experiments.
            </p>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 15px;">
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#fbbf24; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">1. Device Biasing & Parameters</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Active Biasing States</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Cutoff/saturation in active devices (BJTs, FETs) and out-of-tolerance passive parameters.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#fbbf24; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">2. Signal Quality & Distortion</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Waveform & RF Integrity</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Identifies signal clipping, saturation distortion, phase errors, and high-frequency bandwidth rolloff.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#fbbf24; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">3. Assembly & Continuity</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Breadboard Connections</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Flags open circuit paths, shorted net loops, missing components, and row contact misalignments.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#fbbf24; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">4. Polarities & Structural Mismatch</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Orientation Mismatches</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Flags reversed diodes, reversed electrolytic capacitors, incorrect IC directions, or swapped terminal pins.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#fbbf24; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">5. Feedback Loops</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Op-Amp Loop Failures</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Detects open feedback paths (saturation), positive feedback latching, and impedance loading.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#fbbf24; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">6. Digital Logic & States</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Gate & Delay Violations</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Isolates stuck-at-0/stuck-at-1 pins, floating logic inputs, race conditions, and clock skew.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#fbbf24; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">7. Modulation & Channels</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Modulated Signal Integrity</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Identifies AM overmodulation, FM frequency scale offsets, carrier leakage, and inter-symbol interference.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255, 255, 255, 0.03);">
                    <span style="color:#fbbf24; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">8. Embedded Protocols & Buses</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Protocol & Bus Contention</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Diagnoses I2C/SPI swapped lines, missing pull-ups, slave address mismatches, and baud rate scale issues.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Close Details", key="close_faults", use_container_width=True):
            st.session_state.selected_metric = None
            st.rerun()
            
    elif st.session_state.selected_metric == "knowledge":
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid #a78bfa !important; background: rgba(30, 41, 59, 0.4) !important; margin-top:20px;">
            <h4 style="color:#c084fc; margin-top:0;">Conceptual Knowledge Graph Mappings</h4>
            <p style="font-size:13.5px; color:#cbd5e1; line-height:1.6; margin-bottom: 20px;">
                Our interactive Knowledge Graph maps prerequisite pathways and conceptual nodes to form a syllabus blueprint.
            </p>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;">
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#a78bfa; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Prerequisite Tracking</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Dependency Maps</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Enforces step-by-step progress, ensuring students review prerequisite diode physics before launching Zener labs.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#a78bfa; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Dynamic Skill Profiles</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Student Mastery Log</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Updates concept scores (CRO, diode, BJT, op-amp) based on adaptive viva answers.</span>
                </div>
                <div style="background:rgba(9, 13, 22, 0.6); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#a78bfa; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Adaptive Pathway Finder</span>
                    <div style="color:#f1f5f9; font-weight:600; font-size:14px; margin-top:4px; margin-bottom:6px;">Personal learning pathways</div>
                    <span style="color:#94a3b8; font-size:11.5px; line-height:1.4; display:block;">Suggests revision items and study paths for weak nodes mapped directly from the knowledge network.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Close Details", key="close_knowledge", use_container_width=True):
            st.session_state.selected_metric = None
            st.rerun()

    st.divider()

    # ── 3. Platform Capabilities Deck ──
    st.markdown("### Core AI Platform Capabilities")
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        st.markdown("""
        <div class="feat-card">
            <h5 style="color:#60a5fa; margin-bottom:8px;">Fault Diagnosis</h5>
            <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
                Hybrid logic checking against Random Forest and Deep MLP fault estimators to diagnose cutoff, saturation, and droop.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown("""
        <div class="feat-card">
            <h5 style="color:#10b981; margin-bottom:8px;">Computer Vision</h5>
            <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
                Scans breadboard wiring rows and matches component connectivity matrices using YOLOv8 bounding boxes.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_c3:
        st.markdown("""
        <div class="feat-card">
            <h5 style="color:#f59e0b; margin-bottom:8px;">Waveform Analyzer</h5>
            <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
                Applies OpenCV HSV filter masking to trace CRO screenshot signals and isolate clipping distortion.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_c4:
        st.markdown("""
        <div class="feat-card">
            <h5 style="color:#a78bfa; margin-bottom:8px;">Digital Twin</h5>
            <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
                Simulates real-time electrical output voltages, Bode plots, and load lines matching SPICE formulations.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col_c5, col_c6, col_c7, col_c8 = st.columns(4)
    with col_c5:
        st.markdown("""
        <div class="feat-card">
            <h5 style="color:#f43f5e; margin-bottom:8px;">Adaptive Viva</h5>
            <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
                Tutors students using a conversational grading interface, adapting difficulty and updating skill charts.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_c6:
        st.markdown("""
        <div class="feat-card">
            <h5 style="color:#06b6d4; margin-bottom:8px;">Knowledge Graph</h5>
            <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
                Maps prerequisite conceptual paths visually across semesters using interactive Vis.js node structures.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_c7:
        st.markdown("""
        <div class="feat-card">
            <h5 style="color:#ec4899; margin-bottom:8px;">LLM XAI Reasoning</h5>
            <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
                Synthesizes qualitative engineering justifications for diagnosed circuit faults from physical principles.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_c8:
        st.markdown("""
        <div class="feat-card">
            <h5 style="color:#34d399; margin-bottom:8px;">CAD Exporter</h5>
            <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
                Synthesizes LTspice schematic (.asc), KiCad netlists, and Circuitikz LaTeX schematics for physical verification.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── 4. Semester-Wise Lab Curriculum Selection Cards ──
    st.markdown("### Semester-Wise Laboratory Curriculum")
    
    sem_keys = ["Semester I", "Semester III", "Semester IV", "Semester V", "Semester VI", "Semester VII"]
    tabs = st.tabs(sem_keys)
    
    db_exps = get_all_experiments()
    
    for tab, sem_key in zip(tabs, sem_keys):
        with tab:
            courses = ECE_SYLLABUS.get(sem_key, {})
            if not courses:
                st.info("No courses cataloged for this semester.")
            else:
                for course_code, course_data in courses.items():
                    st.markdown(f"#### {course_code} — {course_data['name']}")
                    
                    for exp_idx, exp in enumerate(course_data["experiments"], 1):
                        # Find matching active experiment in database
                        matched_db = find_matching_db_exp(exp, db_exps)
                        
                        is_active = True
                        status_badge = '<span class="badge badge-easy" style="background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.25);">AI Lab Active</span>'
                        diff_color = "badge-easy" if exp["difficulty"] == "Easy" else ("badge-medium" if exp["difficulty"] == "Medium" else "badge-hard")
                        diff_badge = f'<span class="badge {diff_color}">{exp["difficulty"]}</span>'
                        
                        st.markdown(f"""
                        <div class="glass-card" style="margin-bottom: 12px; padding: 18px !important;">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;">
                                <div>
                                    {diff_badge}
                                    {status_badge}
                                    <h5 style="color:#f1f5f9; margin:8px 0; font-size:16px;">{exp['title']}</h5>
                                    <p style="color:#cbd5e1; font-size:12px; margin:0 0 6px 0; line-height:1.4;"><b>Aim:</b> {exp.get('aim', '')}</p>
                                    <p style="color:#94a3b8; font-size:11px; margin:0;">Components: {", ".join(exp.get("components", ["Standard Bench Equipment"]))}</p>
                                </div>
                                <div style="text-align:right; font-size:11px; color:#cbd5e1; font-family:monospace; margin-top:4px;">
                                    Duration: {exp['time']}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"Launch AI Intelligent Workspace ({exp['title'][:30]}...)", key=f"launch_{exp['title']}", use_container_width=True, type="primary"):
                            if matched_db:
                                st.session_state.active_exp_id = matched_db['id']
                                st.session_state.active_exp_title = matched_db['title']
                            else:
                                sem_num = sem_key.split()[-1]
                                roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
                                sem_digit = roman_map.get(sem_num, 1)
                                st.session_state.active_exp_id = f"sem{sem_digit}_{course_code}_exp{exp_idx}"
                                st.session_state.active_exp_title = exp['title']
                            st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)

    st.divider()

    # ── 5. Technical Pipeline & Architecture Section ──
    st.markdown("### System Architecture & AI Pipeline Showcase")
    st.caption("Click on any node in the architecture diagram to examine the model specifications, mathematical representation, and RAG data pipelines.")
    
    showcase_html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      background-color: transparent;
      color: #cbd5e1;
      font-family: 'Inter', sans-serif;
      overflow: hidden;
      padding: 5px;
    }
    .architecture-showcase {
      display: grid;
      grid-template-columns: 1.35fr 1fr;
      gap: 20px;
      width: 100%;
      height: 380px;
    }
    @media (max-width: 768px) {
      .architecture-showcase {
        grid-template-columns: 1fr;
        height: auto;
        overflow-y: auto;
      }
    }
    .grid-container {
      display: grid;
      grid-template-columns: 1fr 30px 1fr 30px 1fr;
      grid-template-rows: 75px 30px 75px 30px 75px;
      gap: 5px;
      align-items: center;
      background: rgba(15, 23, 42, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 15px;
    }
    .pipeline-node {
      background: rgba(15, 23, 42, 0.65);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 10px 8px;
      text-align: center;
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      user-select: none;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .pipeline-node:hover {
      transform: translateY(-2px);
      border-color: rgba(139, 92, 246, 0.3);
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.1);
    }
    
    #node-photo { grid-row: 1; grid-column: 1; }
    #arrow-1 { grid-row: 1; grid-column: 2; }
    #node-yolo { grid-row: 1; grid-column: 3; }
    #arrow-2 { grid-row: 1; grid-column: 4; }
    #node-pins { grid-row: 1; grid-column: 5; }

    #arrow-3 { grid-row: 2; grid-column: 5; }

    #node-matrix { grid-row: 3; grid-column: 5; }
    #arrow-4 { grid-row: 3; grid-column: 4; }
    #node-networkx { grid-row: 3; grid-column: 3; }
    #arrow-5 { grid-row: 3; grid-column: 2; }
    #node-gnn { grid-row: 3; grid-column: 1; }

    #arrow-6 { grid-row: 4; grid-column: 1; }

    #node-fault { grid-row: 5; grid-column: 1; }
    #arrow-7 { grid-row: 5; grid-column: 2; }
    #node-faiss { grid-row: 5; grid-column: 3; }
    #arrow-8 { grid-row: 5; grid-column: 4; }
    #node-llm { grid-row: 5; grid-column: 5; }

    .pipeline-arrow {
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      color: #475569;
      font-weight: bold;
    }
    .vertical-arrow {
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      color: #475569;
      font-weight: bold;
      height: 100%;
    }
    
    .node-number {
      font-family: 'Outfit', sans-serif;
      font-size: 9px;
      font-weight: 800;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 2px;
    }
    .node-title {
      font-family: 'Outfit', sans-serif;
      font-size: 11px;
      font-weight: 700;
      color: #f1f5f9;
      line-height: 1.2;
    }
    .node-type {
      font-size: 8px;
      color: #94a3b8;
      margin-top: 3px;
    }
    
    /* Phase specific active colors */
    #node-photo.active, #node-yolo.active, #node-pins.active {
      border-color: #3b82f6 !important;
      background: rgba(37, 99, 235, 0.1) !important;
      box-shadow: 0 0 15px rgba(59, 130, 246, 0.2) !important;
    }
    #node-matrix.active, #node-networkx.active, #node-gnn.active {
      border-color: #8b5cf6 !important;
      background: rgba(124, 58, 237, 0.1) !important;
      box-shadow: 0 0 15px rgba(139, 92, 246, 0.2) !important;
    }
    #node-fault.active, #node-faiss.active, #node-llm.active {
      border-color: #fbbf24 !important;
      background: rgba(245, 158, 11, 0.1) !important;
      box-shadow: 0 0 15px rgba(251, 191, 36, 0.2) !important;
    }

    .detail-panel {
      background: rgba(15, 23, 42, 0.65);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(12px);
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      transition: all 0.3s ease;
    }
    .detail-phase {
      font-size: 9px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: #a78bfa;
      margin-bottom: 6px;
    }
    .detail-title {
      font-family: 'Outfit', sans-serif;
      font-size: 18px;
      font-weight: 800;
      color: #f8fafc;
      margin: 0 0 8px 0;
    }
    .detail-tech {
      display: inline-block;
      align-self: flex-start;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(59, 130, 246, 0.08);
      border: 1px solid rgba(59, 130, 246, 0.15);
      font-family: monospace;
      font-size: 9.5px;
      color: #60a5fa;
      margin-bottom: 12px;
    }
    .detail-desc {
      font-size: 12px;
      color: #cbd5e1;
      line-height: 1.6;
      margin: 0;
    }
  </style>
</head>
<body>

<div class="architecture-showcase">
  <div class="grid-container">
    <div class="pipeline-node" onclick="selectNode('photo')" id="node-photo">
      <div class="node-number">01</div>
      <div class="node-title">Breadboard Photo</div>
      <div class="node-type">Input Image</div>
    </div>
    <div class="pipeline-arrow" id="arrow-1">→</div>
    <div class="pipeline-node" onclick="selectNode('yolo')" id="node-yolo">
      <div class="node-number">02</div>
      <div class="node-title">YOLOv8 Detector</div>
      <div class="node-type">CV Model</div>
    </div>
    <div class="pipeline-arrow" id="arrow-2">→</div>
    <div class="pipeline-node" onclick="selectNode('pins')" id="node-pins">
      <div class="node-number">03</div>
      <div class="node-title">Pin Coordinates</div>
      <div class="node-type">Geometric Extract</div>
    </div>

    <div class="vertical-arrow" id="arrow-3">↓</div>

    <div class="pipeline-node" onclick="selectNode('gnn')" id="node-gnn">
      <div class="node-number">06</div>
      <div class="node-title">GNN Verify</div>
      <div class="node-type">PyTorch GNN</div>
    </div>
    <div class="pipeline-arrow" id="arrow-5">←</div>
    <div class="pipeline-node" onclick="selectNode('networkx')" id="node-networkx">
      <div class="node-number">05</div>
      <div class="node-title">NetworkX Graph</div>
      <div class="node-type">Graph Model</div>
    </div>
    <div class="pipeline-arrow" id="arrow-4">←</div>
    <div class="pipeline-node" onclick="selectNode('matrix')" id="node-matrix">
      <div class="node-number">04</div>
      <div class="node-title">Adjacency Matrix</div>
      <div class="node-type">Representation</div>
    </div>

    <div class="vertical-arrow" id="arrow-6">↓</div>

    <div class="pipeline-node" onclick="selectNode('fault')" id="node-fault">
      <div class="node-number">07</div>
      <div class="node-title">Fault Prediction</div>
      <div class="node-type">MLP/RF Classifier</div>
    </div>
    <div class="pipeline-arrow" id="arrow-7">→</div>
    <div class="pipeline-node" onclick="selectNode('faiss')" id="node-faiss">
      <div class="node-number">08</div>
      <div class="node-title">FAISS Vector DB</div>
      <div class="node-type">Offline RAG</div>
    </div>
    <div class="pipeline-arrow" id="arrow-8">→</div>
    <div class="pipeline-node" onclick="selectNode('llm')" id="node-llm">
      <div class="node-number">09</div>
      <div class="node-title">Explainable AI LLM</div>
      <div class="node-type">Local Inference</div>
    </div>
  </div>

  <div class="detail-panel">
    <div class="detail-phase" id="detail-phase">Phase 1: Input Perception</div>
    <h4 class="detail-title" id="detail-title">Breadboard Photograph</h4>
    <div class="detail-tech" id="detail-tech">JPEG/PNG Input · OpenCV Preprocessing</div>
    <p class="detail-desc" id="detail-desc">
      Captures the high-resolution physical breadboard assembly details under varying lab lighting. OpenCV corrects perspective skew and runs bilateral filter smoothing to prepare for neural feature extraction.
    </p>
  </div>
</div>

<script>
const details = {
  photo: {
    title: "Breadboard Photograph",
    phase: "Phase 1: Input Perception",
    tech: "JPEG/PNG Input · OpenCV Preprocessing",
    desc: "Captures high-resolution physical breadboard assembly details under varying lab lighting conditions. OpenCV corrects perspective skew and applies bilateral filter smoothing to optimize component edge definition."
  },
  yolo: {
    title: "YOLOv8 Component Detection",
    phase: "Phase 1: Computer Vision Scan",
    tech: "PyTorch · Ultralytics YOLOv8 · Custom Weights",
    desc: "Performs bounding-box inference to identify physical resistors, diodes, transistors, IC packages, and jumper endpoints. Yields component labels and bounding centroid coordinates."
  },
  pins: {
    title: "Pin Coordinates Extraction",
    phase: "Phase 1: Geometric Grid Mapping",
    tech: "Coordinate Transforms · Geometric Intersections",
    desc: "Translates bounding-box centroid coordinates into physical breadboard grid coordinates, identifying which breadboard row and column contacts hold the component leads."
  },
  matrix: {
    title: "Adjacency Matrix",
    phase: "Phase 2: Mathematical Representation",
    tech: "NumPy Matrix Arrays",
    desc: "Constructs an N x N connectivity representation where rows and columns denote individual component terminals. Non-zero values define shared nodes and electrical continuity paths."
  },
  networkx: {
    title: "NetworkX Graph Reconstruction",
    phase: "Phase 2: Topological Reconstruction",
    tech: "NetworkX Structure Modeling",
    desc: "Builds a mathematical graph twin of the physical circuit, standardizing components as edges and breadboard rail rows as vertices, enabling structural node analysis."
  },
  gnn: {
    title: "GNN Topology Verify",
    phase: "Phase 2: Graph Convolutional Network",
    tech: "PyTorch Geometric · GCN Classifier",
    desc: "An offline Graph Convolutional Network verifies if the physical topology matches the reference schematic. Detects missing components, polarity reversals, and open loop faults."
  },
  fault: {
    title: "Fault Prediction",
    phase: "Phase 3: Diagnostic Estimators",
    tech: "Scikit-Learn Random Forest · PyTorch MLP",
    desc: "Classifies operational circuit faults (cutoff biasing, saturation distortion, parameter out-of-tolerance) by evaluating numerical voltages and gain readings."
  },
  faiss: {
    title: "FAISS Vector DB",
    phase: "Phase 3: Offline RAG Retrieval",
    tech: "FAISS Index · SentenceTransformers",
    desc: "Pipes user queries to an offline vector index containing laboratory manuals, curriculum guidelines, and theory summaries to retrieve relevant context with low latency."
  },
  llm: {
    title: "Explainable AI (XAI) LLM",
    phase: "Phase 3: Natural Language Reasoning",
    tech: "Local LLaMA/Mistral · HuggingFace Transformers",
    desc: "Synthesizes mathematical diagnostics and retrieved RAG context to output natural, human-readable troubleshooting fixes and viva explanations. Runs fully offline."
  }
};

function selectNode(id) {
  document.querySelectorAll('.pipeline-node').forEach(node => {
    node.classList.remove('active');
  });
  
  const activeNode = document.getElementById('node-' + id);
  if (activeNode) activeNode.classList.add('active');
  
  const data = details[id];
  if (data) {
    document.getElementById('detail-title').innerText = data.title;
    document.getElementById('detail-phase').innerText = data.phase;
    document.getElementById('detail-tech').innerText = data.tech;
    document.getElementById('detail-desc').innerText = data.desc;
  }
}

// Initial selection
selectNode('photo');
</script>

</body>
</html>
"""
    st.components.v1.html(showcase_html, height=400)

# ─────────────────────────────────────────────────────────────────────────────
# ── WORKSPACE WINDOW: EXPERIMENT ACTIVE ──────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
else:
    selected_exp_id = st.session_state.active_exp_id
    exp_detail = get_experiment_detail(selected_exp_id)
    
    if not exp_detail:
        st.error("Failed to retrieve experiment details. Please try returning to the catalog.")
    else:
        st.markdown(f'<h2>Active Lab: <span class="glow-text">{exp_detail["title"]}</span></h2>', unsafe_allow_html=True)
        st.caption(f"Code: {exp_detail.get('lab_code')} · {exp_detail.get('lab_name')} · Semester {exp_detail.get('semester')}")
        
        # ── Setup Workspace Navigation tabs ──
        tab_t, tab_proc, tab_cv, tab_viva, tab_kg, tab_analytics, tab_rag = st.tabs([
            "Pre-Lab & Twin", 
            "Step-by-Step Procedure", 
            "Fault & CV Scan", 
            "Adaptive Viva Prep", 
            "Knowledge Graph", 
            "Faculty Analytics", 
            "Ask Assistant (RAG)"
        ])
        
        # ── TAB: Pre-Lab & Twin Simulator ──
        with tab_t:
            col_aim, col_info = st.columns([3, 2])
            with col_aim:
                st.subheader("Aim")
                st.info(exp_detail.get("aim", ""))
                
                st.subheader("Theoretical Summary")
                st.write(exp_detail.get("theory", {}).get("summary", ""))
                
                st.subheader("Core Concepts")
                for c in exp_detail.get("theory", {}).get("key_concepts", []):
                    st.markdown(f"- **{c}**")
                    
            with col_info:
                st.subheader("Formulas")
                for f in exp_detail.get("theory", {}).get("key_formulas", []):
                    st.markdown(
                        f'<div class="formula-block">'
                        f'<strong>{f["name"]}</strong><br>'
                        f'<code style="color:#f472b6;">{f["formula"]}</code><br>'
                        f'<span style="color:#94a3b8;font-size:12px">{f.get("variables", "")}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                st.subheader("Component Requirements")
                for c in exp_detail.get("components", []):
                    st.markdown(f"• **{c['name']}** — {c.get('spec', '')} ×{c.get('quantity', 1)}")
            
            st.divider()
            
            # Digital Twin Simulator
            st.subheader("Spice Digital Twin Simulator")
            st.write("Tune component parameters to predict circuit performance outcomes dynamically.")
            
            col_params, col_predict = st.columns([2, 3])
            
            with col_params:
                st.markdown("#### Input Parameters")
                params = {}
                
                if "cro_measurements" in selected_exp_id:
                    params["divisions"] = st.slider("Vertical divisions (Vp)", 1.0, 8.0, 4.0, 0.1)
                    params["volts_div"] = st.selectbox("VOLTS/DIV setting (V)", [0.1, 0.2, 0.5, 1.0, 2.0, 5.0], index=3)
                    params["time_divisions"] = st.slider("Horizontal divisions per cycle (T)", 1.0, 10.0, 5.0, 0.1)
                    params["time_div_ms"] = st.selectbox("TIME/DIV setting (ms)", [0.1, 0.2, 0.5, 1.0, 2.0, 5.0], index=3)
                elif "pn_junction" in selected_exp_id:
                    params["Vd"] = st.slider("Diode Forward Voltage Vd (V)", 0.0, 1.2, 0.7, 0.01)
                    params["ideality_factor"] = st.slider("Ideality factor n", 1.0, 2.0, 1.0, 0.1)
                elif "zener" in selected_exp_id:
                    params["Vin"] = st.slider("Input Voltage Vin (V)", 0.0, 15.0, 10.0, 0.5)
                    params["Vz"] = st.selectbox("Zener Clamping Voltage Vz (V)", [3.3, 5.1, 6.2, 9.1], index=1)
                    params["Rs_ohms"] = st.number_input("Series Resistance Rs (Ω)", 100, 2000, 470)
                    params["RL_ohms"] = st.number_input("Load Resistance RL (Ω)", 100, 10000, 1000)
                elif "transistor_amplifier" in selected_exp_id:
                    params["Vcc"] = st.selectbox("Supply Voltage Vcc (V)", [5.0, 9.0, 12.0, 15.0], index=2)
                    params["R1_k"] = st.number_input("Bias R1 (kΩ)", 1.0, 100.0, 33.0)
                    params["R2_k"] = st.number_input("Bias R2 (kΩ)", 1.0, 100.0, 10.0)
                    params["Rc_k"] = st.number_input("Collector Rc (kΩ)", 0.1, 20.0, 3.3)
                    params["Re_k"] = st.number_input("Emitter Re (kΩ)", 0.1, 10.0, 1.0)
                    params["beta"] = st.slider("Transistor Beta (hFE)", 50, 400, 150)
                elif "opamp" in selected_exp_id:
                    params["R1_k"] = st.number_input("Input R1 (kΩ)", 1.0, 100.0, 10.0)
                    params["Rf_k"] = st.number_input("Feedback Rf (kΩ)", 1.0, 500.0, 100.0)
                    params["Vin"] = st.slider("Input Amplitude Vin (V)", -5.0, 5.0, 0.5, 0.1)
                elif "rc_filters" in selected_exp_id:
                    params["R_k"] = st.number_input("Resistance R (kΩ)", 1.0, 200.0, 10.0)
                    params["C_uF"] = st.number_input("Capacitance C (μF)", 0.001, 10.0, 0.01, format="%.3f")
                elif "oscillator" in selected_exp_id or "phase_shift" in selected_exp_id or "wien_bridge" in selected_exp_id:
                    params["R_k"] = st.number_input("Oscillation R (kΩ)", 1.0, 100.0, 10.0)
                    params["C_uF"] = st.number_input("Oscillation C (μF)", 0.001, 1.0, 0.01, format="%.3f")
                elif "am_modulation" in selected_exp_id:
                    params["Am"] = st.slider("Message Amplitude Am (V)", 0.1, 5.0, 1.0, 0.1)
                    params["Ac"] = st.slider("Carrier Amplitude Ac (V)", 1.0, 10.0, 2.0, 0.1)
                    params["fm_Hz"] = st.number_input("Message Frequency fm (Hz)", 100, 5000, 1000)
                elif "fm_modulation" in selected_exp_id:
                    params["Am"] = st.slider("Message Amplitude Am (V)", 0.1, 3.0, 1.0, 0.1)
                    params["kv_Hz_V"] = st.number_input("VCO Sensitivity (Hz/V)", 1000, 20000, 8000)
                    params["fm_Hz"] = st.number_input("Message Frequency fm (Hz)", 100, 5000, 1000)
                else:
                    st.caption("No custom parameters required.")
                    
            with col_predict:
                st.markdown("#### Predicted Waveforms & Outcomes")
                if st.button("Calculate & Predict Output", use_container_width=True):
                    with st.spinner("Executing mathematical spice solver..."):
                        try:
                            resp = requests.post(f"{API_BASE_URL}/diagnosis/predict-twin", json={
                                "experiment_id": selected_exp_id,
                                "parameters": params
                            }, timeout=25)
                            if resp.status_code == 200:
                                res = resp.json()
                                if "error" in res.get("predictions", {}):
                                    st.error(res["predictions"]["error"])
                                else:
                                    preds = res["predictions"]
                                    st.success("Analysis Complete!")
                                    
                                    # Render Plotly Bode plot and DC Load line side by side
                                    if "bode_plot" in preds or "dc_load_line" in preds:
                                        col_plots_1, col_plots_2 = st.columns(2)
                                        with col_plots_1:
                                            if "bode_plot" in preds:
                                                fig_bode = plot_plotly_bode(preds["bode_plot"])
                                                st.plotly_chart(fig_bode, use_container_width=True)
                                            else:
                                                st.info("No frequency response data available for this circuit.")
                                        
                                        with col_plots_2:
                                            if "dc_load_line" in preds and "q_point" in preds:
                                                fig_load = plot_plotly_load_line(preds["dc_load_line"], preds["q_point"])
                                                st.plotly_chart(fig_load, use_container_width=True)
                                            else:
                                                st.info("No DC load line data available for this circuit.")
                                    else:
                                        st.json(preds)
                                    
                                    # Show individual metrics
                                    col_met1, col_met2 = st.columns(2)
                                    with col_met1:
                                        if "Vout" in preds:
                                            st.metric("Predicted Output Voltage", f"{preds['Vout']:.3f} V")
                                        if "Gain_with_CE" in preds:
                                            st.metric("AC Voltage Gain (Av)", f"{preds['Gain_with_CE']:.1f} V/V")
                                    with col_met2:
                                        if "cutoff_frequency_Hz" in preds:
                                            st.metric("Calculated Cutoff Frequency", f"{preds['cutoff_frequency_Hz']:.1f} Hz")
                                        if "fo_Hz" in preds:
                                            st.metric("Oscillation Frequency (fo)", f"{preds['fo_Hz']:.1f} Hz")
                            else:
                                st.error(f"Solver failed: Backend returned status {resp.status_code}")
                        except requests.exceptions.Timeout:
                            st.error("⏳ Prediction solver timed out. The server might be waking up. Please retry.")
                        except Exception as e:
                            st.error(f"Failed to connect to digital twin solver: {e}")
                                
        # ── TAB: Step-by-Step Procedure ──
        with tab_proc:
            st.info(f"**AIM:** {exp_detail.get('aim')}")
            col_proc, col_exp = st.columns([3, 2])
            
            with col_proc:
                st.subheader("Procedure Instructions")
                for i, step in enumerate(exp_detail.get("procedure", []), 1):
                    st.markdown(f"**Step {i}:** {step}")
                    
                st.subheader("Observation Table Headers")
                obs = exp_detail.get("observations", {})
                if obs.get("table_headers"):
                    st.table([obs["table_headers"]])
                    st.caption(f"**Sample Row Data:** {', '.join(obs.get('sample_row', []))}")
                if obs.get("what_to_plot"):
                    st.info(f"Graph requirements: {obs['what_to_plot']}")
                    
            with col_exp:
                st.subheader("Expected Results")
                er = exp_detail.get("expected_results", {})
                st.write(er.get("description", ""))
                
                for tv in er.get("typical_values", []):
                    st.metric(tv["parameter"], f"{tv['expected']} {tv.get('unit', '')}")
                    
                st.subheader("Common Troubleshooting Indicators")
                for err in exp_detail.get("common_errors", []):
                    with st.expander(f"Symptom: {err['symptom']}"):
                        st.write(f"**Potential Causes:** {', '.join(err.get('causes', []))}")
                        st.success(f"**Fix:** {err.get('fix')}")
                        
        # ── TAB: Fault & CV scan ──
        with tab_cv:
            st.subheader("Intelligent Circuit Diagnosis Center")
            st.write("Compare experimental measurements, analyze CRO screenshots, or run visual breadboard scanning.")
            
            sub_mode = st.radio("Select Diagnostic Tool:", [
                "Measured Readings Diagnostic", 
                "CRO Waveform Scanner", 
                "Breadboard Visual Scan",
                "CAD Schematic Exporter"
            ], horizontal=True)
            
            st.divider()
            
            if sub_mode == "Measured Readings Diagnostic":
                st.write("Verify if your experimental values fall within tolerance limits.")
                col_in1, col_in2 = st.columns(2)
                
                with col_in1:
                    st.markdown("##### Expected values (from formulas)")
                    exp_vals = {}
                    if "cro_measurements" in selected_exp_id:
                        exp_vals["Vp"] = st.text_input("Expected Vp (V)", "1.41")
                        exp_vals["f"] = st.text_input("Expected Frequency (Hz)", "1000")
                    elif "pn_junction" in selected_exp_id:
                        exp_vals["Vd"] = st.text_input("Expected Diode Vd (V)", "0.7")
                        exp_vals["Id"] = st.text_input("Expected Diode Current Id (mA)", "15")
                    elif "zener" in selected_exp_id:
                        exp_vals["Vout"] = st.text_input("Expected Regulated Vout (V)", "5.1")
                    elif "transistor_amplifier" in selected_exp_id:
                        exp_vals["VCE"] = st.text_input("Expected VCE (V)", "6.0")
                        exp_vals["Gain"] = st.text_input("Expected Gain (V/V)", "15.0")
                    elif "opamp" in selected_exp_id:
                        exp_vals["Gain"] = st.text_input("Expected Op-Amp Gain", "10.0")
                    else:
                        exp_vals["value1"] = st.text_input("Expected parameter value", "5.0")
                        
                    symptom = st.text_area(
                        "Describe visual symptoms (optional)",
                        placeholder="e.g. Waveform is clipping, output VCE is stuck, ammeter reads zero..."
                    )
                    
                with col_in2:
                    st.markdown("##### Observed values (CRO / Multimeter)")
                    meas_vals = {}
                    if "cro_measurements" in selected_exp_id:
                        meas_vals["Vp"] = st.text_input("Observed Vp (V)", "1.4")
                        meas_vals["f"] = st.text_input("Observed Frequency (Hz)", "100") # 10x error
                    elif "pn_junction" in selected_exp_id:
                        meas_vals["Vd"] = st.text_input("Observed Diode Vd (V)", "0.7")
                        meas_vals["Id"] = st.text_input("Observed Diode Current Id (mA)", "0.0") # reversed
                    elif "zener" in selected_exp_id:
                        meas_vals["Vout"] = st.text_input("Observed Vout (V)", "10.0") # no clamp
                    elif "transistor_amplifier" in selected_exp_id:
                        meas_vals["VCE"] = st.text_input("Observed VCE (V)", "11.8") # cutoff
                        meas_vals["Gain"] = st.text_input("Observed Gain (V/V)", "1.2") # bypass missing
                    elif "opamp" in selected_exp_id:
                        meas_vals["Gain"] = st.text_input("Observed Op-Amp Gain", "0.0") # open loop
                    else:
                        meas_vals["value1"] = st.text_input("Observed parameter value", "0.0")
                        
                if st.button("Diagnose Observations", use_container_width=True, type="primary"):
                    with st.spinner("Classifying values against ECE fault models..."):
                        try:
                            resp = requests.post(f"{API_BASE_URL}/diagnosis/verify", json={
                                "experiment_id": selected_exp_id,
                                "measured_values": meas_vals,
                                "expected_values": exp_vals,
                                "symptom": symptom
                            }, timeout=30)
                            if resp.status_code == 200:
                                res = resp.json()
                                st.divider()
                                st.subheader("Diagnosis Report")
                                if res.get("status") == "correct":
                                    st.success("Measurements normal. Deviation is within tolerance.")
                                elif res.get("status") == "warning":
                                    st.warning("Warning: Minor discrepancies detected.")
                                else:
                                    st.error("Faults Detected!")
                                    
                                st.markdown("#### Predicted Fault Mode:")
                                for f in res.get("faults", []):
                                    st.markdown(f"- **{f}**")
                                    
                                st.markdown("#### Corrective Action Recommendations:")
                                for rec in res.get("recommendations", []):
                                    st.markdown(f"• {rec}")
                                    
                                if res.get("reasoning"):
                                    st.markdown("#### LLM Explainable AI (XAI) Diagnosis:")
                                    st.info(res["reasoning"])
                                    
                                st.caption(res.get("details", ""))
                            else:
                                st.error(f"Diagnosis failed: Backend returned status code {resp.status_code}")
                        except requests.exceptions.Timeout:
                            st.error("⏳ Diagnosis request timed out. The backend might still be waking up. Please retry.")
                        except Exception as e:
                            st.error(f"Error connecting to diagnosis engine: {e}")
                    
            elif sub_mode == "CRO Waveform Scanner":
                st.write("Upload an image of your CRO screen trace. The system will extract signal dimensions and diagnose wave distortion.")
                col_w_upload, col_w_settings = st.columns([1, 1])
                with col_w_settings:
                    volts_div = st.number_input("VOLTS/DIV setting (V)", min_value=0.01, max_value=100.0, value=1.0, step=0.1)
                    time_div_ms = st.number_input("TIME/DIV setting (ms)", min_value=0.001, max_value=1000.0, value=1.0, step=0.1)
                
                with col_w_upload:
                    uploaded_waveform = st.file_uploader("Upload CRO Screenshot...", type=["png", "jpg", "jpeg"], key="wave_uploader")
                    
                if uploaded_waveform:
                    st.image(uploaded_waveform, caption="Uploaded CRO Display", width=400)
                    if st.button("Run Waveform Analysis", use_container_width=True, type="primary"):
                        with st.spinner("Processing waveform trace in OpenCV..."):
                            try:
                                files = {"file": (uploaded_waveform.name, uploaded_waveform.getvalue(), uploaded_waveform.type)}
                                data = {"volts_div": volts_div, "time_div_ms": time_div_ms}
                                resp = requests.post(f"{API_BASE_URL}/diagnosis/upload-waveform", data=data, files=files, timeout=35)
                                if resp.status_code == 200:
                                    res = resp.json()
                                    st.success("Waveform trace parsed successfully!")
                                    col_det1, col_det2 = st.columns([1, 1])
                                    
                                    with col_det1:
                                        if res.get("waveform_image_url"):
                                            backend_root = get_backend_root_url()
                                            st.markdown("#### Trace Extraction Overlay:")
                                            st.image(f"{backend_root}{res['waveform_image_url']}", caption="Annotated Trace Graph with Peak Lines", use_container_width=True)
                                            
                                    with col_det2:
                                        st.markdown("#### Extracted Signal Parameters:")
                                        st.metric("Peak-to-Peak Voltage (Vp-p)", f"{res.get('peak_to_peak_voltage', 0.0):.2f} V")
                                        st.metric("Peak Voltage (Vp)", f"{res.get('peak_voltage', 0.0):.2f} V")
                                        st.metric("Frequency (f)", f"{res.get('frequency_hz', 0.0):.1f} Hz")
                                        
                                        st.divider()
                                        st.markdown("#### Waveform Quality Report:")
                                        if res.get("clipping_fault"):
                                            st.error(f"CLIPPING DETECTED: {res.get('distortion_report', '')}")
                                        else:
                                            st.success(f"Waveform normal. {res.get('distortion_report', '')}")
                                else:
                                    st.error(f"Waveform scan failed: Backend returned {resp.status_code}. Detail: {resp.text}")
                            except requests.exceptions.Timeout:
                                st.error("⏳ Waveform analysis timed out. Please retry.")
                            except Exception as e:
                                st.error(f"Error connecting to backend: {e}")
                                
            elif sub_mode == "Breadboard Visual Scan":
                st.write("Upload an image of your breadboard. The YOLOv8 model will scan for correct component placement and alignment.")
                uploaded_file = st.file_uploader("Choose a circuit image...", type=["jpg", "jpeg", "png"])
                
                if uploaded_file:
                    st.image(uploaded_file, caption="Uploaded Assembly", width=400)
                    if st.button("Run CV Wire Detection", use_container_width=True, type="primary"):
                        with st.spinner("Running YOLOv8 component classifier..."):
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            data = {"experiment_id": selected_exp_id}
                            try:
                                resp = requests.post(f"{API_BASE_URL}/diagnosis/upload-image", data=data, files=files, timeout=60)
                                if resp.status_code == 200:
                                    res = resp.json()
                                    st.success("Visual scan complete!")
                                    
                                    if res.get("error_map_url"):
                                        st.markdown("#### Vision-Annotated Assembly Map:")
                                        backend_base = get_backend_root_url()
                                        st.image(backend_base + res["error_map_url"], caption="OpenCV component layout & error map", use_container_width=True)
                                    
                                    st.divider()
                                    st.markdown("#### Component Graph Matches:")
                                    st.json(res["components"])
                                    
                                    st.markdown("#### Wiring Faults Identified:")
                                    for f in res["faults"]:
                                        st.error(f"**{f['type']}** ({f['component']}): {f['description']}")
                                        st.info(f"**Recommended Fix:** {f['fix']}")
                                        
                                    st.markdown("#### Graph Reconstruction Suggestions:")
                                    for s in res["correction_suggestions"]:
                                        st.markdown(f"- {s}")
                                        
                                    if "gnn_topology_check" in res:
                                        st.divider()
                                        st.markdown("### PyTorch GNN Topology Verification")
                                        gnn = res["gnn_topology_check"]
                                        conf = gnn["confidence"] * 100
                                        if gnn["class_index"] == 0:
                                            st.success(f"**{gnn['predicted_class']}** (Confidence: {conf:.1f}%)")
                                        else:
                                            st.error(f"**Topology Anomaly Warning: {gnn['predicted_class']}** (Confidence: {conf:.1f}%)")
                                        st.info(gnn["details"])
                                else:
                                    st.error(f"Failed to scan image: Backend returned status code {resp.status_code}. Detail: {resp.text}")
                            except requests.exceptions.Timeout:
                                st.error("⏳ Vision analysis timed out (~60s). If the server was waking up, please retry now.")
                            except Exception as e:
                                st.error(f"Error connecting to backend server: {e}")
                            
            elif sub_mode == "CAD Schematic Exporter":
                st.write("Generate and download corrected circuit schematics, LTspice files, and Circuitikz LaTeX codes.")
                if st.button("Generate CAD Codes", use_container_width=True):
                    with st.spinner("Synthesizing schematics..."):
                        try:
                            resp = requests.get(f"{API_BASE_URL}/diagnosis/schematics/{selected_exp_id}", timeout=25)
                            if resp.status_code == 200:
                                res = resp.json()
                                backend_root = get_backend_root_url()
                                col_lt, col_tikz, col_ki = st.columns(3)
                                with col_lt:
                                    st.markdown("#### 1. LTspice Schematic (.asc)")
                                    st.code(res["ltspice_code"], language="text")
                                    st.markdown(f"[Download LTspice File]({backend_root}{res['ltspice_url']})")
                                Carriage = ""
                                with col_tikz:
                                    st.markdown("#### 2. LaTeX Circuitikz Code")
                                    st.code(res["circuitikz_latex"], language="latex")
                                    st.markdown(f"[Download LaTeX File]({backend_root}{res['circuitikz_url']})")
                                with col_ki:
                                    st.markdown("#### 3. KiCad Netlist Schema")
                                    st.json(res["kicad_schema"])
                                    st.markdown(f"[Download KiCad Schema]({backend_root}{res['kicad_url']})")
                            else:
                                st.error(f"Failed to generate CAD: Backend returned status code {resp.status_code}. Detail: {resp.text}")
                        except requests.exceptions.Timeout:
                            st.error("⏳ Schematic generation timed out. Please retry.")
                        except Exception as e:
                            st.error(f"Error connecting to backend server: {e}")
                        
        # ── TAB: Adaptive Viva Prep ──
        with tab_viva:
            st.subheader("Conversational AI Viva Prep")
            
            if "viva_session_id" not in st.session_state:
                st.session_state.viva_session_id = None
                st.session_state.viva_question = None
                st.session_state.viva_q_num = 1
                st.session_state.viva_total = 0
                st.session_state.viva_difficulty = "medium"
                st.session_state.viva_history = []
                st.session_state.student_name = ""
                
            if not st.session_state.viva_session_id:
                # Persistent skill dashboard
                st.markdown("### Student Skill Profile & Mastery Dashboard")
                if "skill_profile" not in st.session_state:
                    st.session_state.skill_profile = {
                        "cro": 65.0,
                        "diode": 60.0,
                        "amplifier": 55.0,
                        "opamp": 50.0
                    }
                
                col_sk1, col_sk2, col_sk3, col_sk4 = st.columns(4)
                topics_meta = {
                    "cro": ("CRO & Signals", "#60a5fa"),
                    "diode": ("Diodes & Zener", "#10b981"),
                    "amplifier": ("BJT & Amplifiers", "#a78bfa"),
                    "opamp": ("Op-Amp Circuits", "#f59e0b")
                }
                for key, (label, color) in topics_meta.items():
                    val = st.session_state.skill_profile[key]
                    col = col_sk1 if key == "cro" else (col_sk2 if key == "diode" else (col_sk3 if key == "amplifier" else col_sk4))
                    with col:
                        st.markdown(
                            f'<div style="background:#111827; border-radius:10px; padding:18px; border:1px solid rgba(255,255,255,0.05); border-left:5px solid {color}; text-align:center;">'
                            f'<span style="color:#94a3b8; font-size:12px; font-weight:600;">{label}</span><br>'
                            f'<span style="font-size:22px; font-weight:700; color:#f1f5f9;">{val:.1f}%</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                
                st.divider()
                st.write("Start a new session to begin your evaluation.")
                st.session_state.student_name = st.text_input("Enter your name:", "Student")
                
                if st.button("Start Viva Session", use_container_width=True, type="primary"):
                    with st.spinner("Initializing session..."):
                        try:
                            resp = requests.post(f"{API_BASE_URL}/viva/start", json={
                                "experiment_id": selected_exp_id,
                                "student_name": st.session_state.student_name
                            }, timeout=25)
                            if resp.status_code == 200:
                                res = resp.json()
                                st.session_state.viva_session_id = res["session_id"]
                                st.session_state.viva_question = res["question"]
                                st.session_state.viva_q_num = res["question_number"]
                                st.session_state.viva_total = res["total_questions"]
                                st.session_state.viva_difficulty = res["difficulty"]
                                st.session_state.viva_history = []
                                st.rerun()
                            else:
                                st.error(f"Failed to start Viva: Backend returned status code {resp.status_code}. Detail: {resp.text}")
                        except requests.exceptions.Timeout:
                            st.error("⏳ Viva start request timed out. Please retry.")
                        except Exception as e:
                            st.error(f"Error connecting to backend server: {e}")
            else:
                st.success(f"Session Active: {st.session_state.student_name} · Difficulty: **{st.session_state.viva_difficulty.upper()}**")
                st.progress(st.session_state.viva_q_num / st.session_state.viva_total)
                
                # Render Conversational Chat bubble history
                st.markdown("#### Conversational Interview Thread:")
                for item in st.session_state.viva_history:
                    st.markdown(f'<div class="chat-bubble chat-ai"><b>AI Examiner:</b> {item["q"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="chat-bubble chat-student"><b>{st.session_state.student_name}:</b> {item["student"]}</div>', unsafe_allow_html=True)
                    st.caption(f"Score: {item['score']}/10 | Feedback: {item['feedback']}")
                
                st.divider()
                st.markdown(f'<div class="chat-bubble chat-ai"><b>AI Examiner:</b> {st.session_state.viva_question}</div>', unsafe_allow_html=True)
                ans = st.text_area("Your response:", placeholder="Type your answer clearly here...")
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Submit Answer", use_container_width=True, type="primary"):
                        if not ans:
                            st.warning("Please type an answer first.")
                        else:
                            with st.spinner("Grading..."):
                                try:
                                    resp = requests.post(f"{API_BASE_URL}/viva/answer", json={
                                        "session_id": st.session_state.viva_session_id,
                                        "student_answer": ans
                                    }, timeout=25)
                                    if resp.status_code == 200:
                                        res = resp.json()
                                        if res.get("completed"):
                                            st.session_state.viva_history.append({
                                                "q": st.session_state.viva_question,
                                                "student": ans,
                                                "score": res.get("score_last", 0),
                                                "feedback": res.get("feedback_last", "")
                                            })
                                            st.session_state.viva_session_id = "done"
                                            st.session_state.viva_summary = res
                                            st.rerun()
                                        else:
                                            st.session_state.viva_history.append({
                                                "q": st.session_state.viva_question,
                                                "student": ans,
                                                "score": res["score_last"],
                                                "feedback": res["feedback_last"]
                                            })
                                            st.session_state.viva_question = res["question"]
                                            st.session_state.viva_q_num = res["question_number"]
                                            st.session_state.viva_difficulty = res["difficulty"]
                                            st.rerun()
                                    else:
                                        st.error(f"Failed to grade answer: Backend returned status code {resp.status_code}. Detail: {resp.text}")
                                except Exception as e:
                                    st.error(f"Error connecting to backend: {e}")
                                
                with col_b2:
                    if st.button("Quit Session", use_container_width=True):
                        st.session_state.viva_session_id = None
                        st.rerun()
                        
            if st.session_state.viva_session_id == "done":
                st.divider()
                sumry = st.session_state.viva_summary
                st.balloons()
                st.markdown("### Viva Completed!")
                
                col_score1, col_score2 = st.columns([1, 2])
                with col_score1:
                    st.metric("Final Score", f"{sumry['score']:.1f}/10", f"{sumry['percentage']:.1f}%")
                with col_score2:
                    st.info(sumry["feedback"])
                
                # --- Visual Skill Profile ---
                st.markdown("### Updated ECE Topic Mastery Profile")
                topic = _get_topic_key(selected_exp_id)
                score_pct = sumry.get("percentage", 0.0)
                
                if "skill_profile" not in st.session_state:
                    st.session_state.skill_profile = {
                        "cro": 65.0,
                        "diode": 60.0,
                        "amplifier": 55.0,
                        "opamp": 50.0
                    }
                st.session_state.skill_profile[topic] = score_pct
                
                col_sk1, col_sk2, col_sk3, col_sk4 = st.columns(4)
                topics_meta = {
                    "cro": ("CRO & Signals", "#60a5fa"),
                    "diode": ("Diodes & Zener", "#10b981"),
                    "amplifier": ("BJT & Amplifiers", "#a78bfa"),
                    "opamp": ("Op-Amp Circuits", "#f59e0b")
                }
                
                for key, (label, color) in topics_meta.items():
                    val = st.session_state.skill_profile[key]
                    col = col_sk1 if key == "cro" else (col_sk2 if key == "diode" else (col_sk3 if key == "amplifier" else col_sk4))
                    with col:
                        st.markdown(
                            f'<div style="background:#111827; border-radius:10px; padding:18px; border:1px solid rgba(255,255,255,0.05); border-left:5px solid {color}; text-align:center;">'
                            f'<span style="color:#94a3b8; font-size:12px; font-weight:600;">{label}</span><br>'
                            f'<span style="font-size:22px; font-weight:700; color:#f1f5f9;">{val:.1f}%</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                
                st.divider()
                
                # --- Personal Roadmap Cards ---
                st.markdown("### Personal Learning Roadmap")
                col_road1, col_road2 = st.columns(2)
                with col_road1:
                    st.markdown("#### Identified Conceptual Weaknesses:")
                    if sumry["weak_concepts"]:
                        for c in sumry["weak_concepts"]:
                            st.error(f"- **{c}**")
                    else:
                        st.success("No weak concepts found! Excellent job.")
                
                with col_road2:
                    st.markdown("#### Recommended Revision Pathway:")
                    for p in sumry["revision_pathway"]:
                        st.warning(f"**Focus Area: {p['concept']}**")
                        st.write(p["suggestion"])
                    
                if st.button("Restart Viva Session", use_container_width=True):
                    st.session_state.viva_session_id = None
                    st.rerun()
                    
        # ── TAB: Knowledge Graph ──
        with tab_kg:
            st.subheader("Semester-Wise Electronics Knowledge Graph")
            st.write("Drag, zoom, and explore concepts and prerequisite connections in the vis.js network below.")
            
            with st.spinner("Retrieving graph mappings..."):
                try:
                    resp = requests.get(f"{API_BASE_URL}/knowledge-graph", timeout=20)
                    if resp.status_code == 200:
                        res = resp.json()
                        graph_html = draw_visjs_graph(res.get("nodes", []), res.get("edges", []))
                        st.components.v1.html(graph_html, height=480)
                    else:
                        st.warning(f"Could not load Knowledge Graph (status {resp.status_code}).")
                except Exception as e:
                    st.warning(f"Failed to retrieve Knowledge Graph: {e}")
            
            st.divider()
            st.markdown("### Trace My Prerequisite Path")
            concept_query = st.text_input("Enter a concept or lab name you find weak:", "Wien Bridge Oscillator")
            
            if st.button("Trace Pathway", use_container_width=True):
                with st.spinner("Mapping dependency edges..."):
                    try:
                        resp = requests.get(f"{API_BASE_URL}/knowledge-graph/prereq", params={"concept": concept_query}, timeout=20)
                        if resp.status_code == 200:
                            prereqs = resp.json()
                            st.success("Recommended study path:")
                            for p in prereqs:
                                st.warning(f"**Study: {p['label']}**")
                                st.write(p["detail"])
                        else:
                            st.error(f"Failed to trace prerequisites: Status {resp.status_code}")
                    except Exception as e:
                        st.error(f"Error tracing prerequisites: {e}")
                    
        # ── TAB: Faculty Analytics ──
        with tab_analytics:
            st.subheader("Faculty Performance Analytics Dashboard")
            st.write("Review student completion rates, common assembly faults, and concept mastery curves.")
            
            with st.spinner("Fetching database statistics..."):
                try:
                    resp = requests.get(f"{API_BASE_URL}/analytics/dashboard", timeout=20)
                    if resp.status_code == 200:
                        res = resp.json()
                        col_e1, col_e2, col_e3 = st.columns(3)
                        with col_e1:
                            st.metric("Total Active Students", res["engagement"]["total_students_active"])
                        with col_e2:
                            st.metric("Total Sessions Conducted", res["engagement"]["sessions_run"])
                        with col_e3:
                            st.metric("Avg Completion Rate", f"{res['engagement']['completion_rate_pct']}%")
                            
                        col_ch1, col_ch2 = st.columns(2)
                        with col_ch1:
                            fig_fail = plot_plotly_failures(res["most_failed_experiments"])
                            st.plotly_chart(fig_fail, use_container_width=True)
                            
                        with col_ch2:
                            fig_weak = plot_plotly_weaknesses(res["concept_weaknesses"])
                            st.plotly_chart(fig_weak, use_container_width=True)
                            
                        st.divider()
                        st.markdown("#### Common Connection Errors & Completion Times")
                        col_tbl1, col_tbl2 = st.columns(2)
                        with col_tbl1:
                            st.markdown("##### Common Assembly Errors")
                            st.table(res["common_student_mistakes"])
                        with col_tbl2:
                            st.markdown("##### Avg Completion Times")
                            st.table(res["average_completion_times_mins"])
                    else:
                        st.error(f"Failed to load analytics: Status {resp.status_code}")
                except Exception as e:
                    st.error(f"Error connecting to analytics engine: {e}")
                
        # ── TAB: Ask Assistant (RAG) ──
        with tab_rag:
            st.subheader("RAG Assistant Chat")
            st.caption(f"Interfacing with experiment context: **{exp_detail['title']}**")
            
            query = st.text_area(
                "Ask the AI any laboratory question:",
                placeholder="e.g. Why does the BJT collector current saturate? How do I set the trigger point for a sine wave?"
            )
            
            if st.button("Send to Assistant", use_container_width=True, type="primary"):
                if query:
                    with st.spinner("Querying vector database & invoking LLM..."):
                        try:
                            resp = requests.post(f"{API_BASE_URL}/assistant/chat", json={
                                "query": query,
                                "experiment_id": selected_exp_id,
                                "mode": "general"
                            }, timeout=45)
                            if resp.status_code == 200:
                                res = resp.json()
                                st.divider()
                                st.markdown(res.get("answer", "No answer returned."))
                                st.markdown(
                                    f'<br><span class="source-badge">Orchestration Source: {res.get("source", "unknown")}</span>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.error(f"Assistant returned status {resp.status_code}: {resp.text}")
                        except requests.exceptions.Timeout:
                            st.error("⏳ Assistant request timed out (~45s). If the free-tier backend was sleeping, it has now woken up. Please click 'Send to Assistant' again!")
                        except Exception as e:
                            st.error(f"Failed to communicate with RAG Assistant: {e}")
