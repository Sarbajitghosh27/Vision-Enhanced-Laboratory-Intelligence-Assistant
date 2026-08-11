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
from urllib.parse import quote, unquote

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

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VELIA — Vision-Enhanced Laboratory Intelligence Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom Premium Styling (Notion-style, Zinc Black, Poppins) ──────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
  
  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #a1a1aa;
    font-size: 15px;
    line-height: 1.65;
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    color: #fafafa;
    letter-spacing: -0.3px;
  }
  
  h1 { font-size: 2.25rem; font-weight: 700; }
  h2 { font-size: 1.6rem; font-weight: 600; }
  h3 { font-size: 1.25rem; font-weight: 600; color: #e4e4e7; }
  
  p, li, span, div {
    font-family: 'DM Sans', sans-serif;
  }
  
  /* Zinc 950 black background — Notion-style */
  .stApp {
    background-color: #09090b;
    background-image: none;
  }
  
  /* Completely hide sidebar and collapse button */
  [data-testid="stSidebar"],
  section[data-testid="stSidebar"],
  [data-testid="collapsedControl"],
  button[data-testid="baseButton-headerNoPadding"],
  button[aria-label="Close sidebar"],
  button[aria-label="Open sidebar"] {
    display: none !important;
  }
  
  /* Minimal zinc cards */
  .glass-card {
    background: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 10px !important;
    padding: 24px !important;
    margin-bottom: 16px !important;
    transition: border-color 0.2s ease !important;
  }
  
  .glass-card:hover {
    border-color: #3b82f6 !important;
  }
  
  /* Capability Card Deck */
  .feat-card {
    background: #18181b;
    border: 1px solid #27272a;
    border-radius: 10px;
    padding: 20px;
    height: 100%;
    transition: border-color 0.2s ease;
  }
  
  .feat-card:hover {
    border-color: #3b82f6;
  }
  
  .glow-text {
    background: linear-gradient(135deg, #e4e4e7, #a1a1aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  .formula-block {
    background: #141415;
    border-radius: 6px;
    padding: 14px 18px;
    font-family: 'DM Mono', 'Fira Code', monospace;
    font-size: 13.5px;
    margin: 8px 0;
    border-left: 3px solid #3b82f6;
    color: #a1a1aa;
    border: 1px solid #27272a;
  }

  .source-badge {
    font-size: 11px;
    padding: 3px 9px;
    border-radius: 4px;
    background: #1e1e22;
    color: #71717a;
    font-family: 'DM Sans', sans-serif;
    border: 1px solid #27272a;
    letter-spacing: 0.3px;
  }
  
  /* Custom styled Badges */
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-right: 6px;
    font-family: 'DM Sans', sans-serif;
  }
  
  .badge-easy {
    background: #14241e;
    color: #4ade80;
    border: 1px solid #166534;
  }
  
  .badge-medium {
    background: #241e10;
    color: #fbbf24;
    border: 1px solid #78350f;
  }
  
  .badge-hard {
    background: #241414;
    color: #f87171;
    border: 1px solid #7f1d1d;
  }
  
  /* Streamlit Tabs — Notion-style */
  button[data-baseweb="tab"] {
      background-color: transparent !important;
      border: 1px solid #27272a !important;
      border-radius: 6px !important;
      padding: 7px 16px !important;
      margin-right: 6px !important;
      color: #71717a !important;
      font-family: 'DM Sans', sans-serif !important;
      font-size: 13.5px !important;
      font-weight: 500 !important;
      transition: all 0.15s ease !important;
  }
  button[data-baseweb="tab"]:hover {
      border-color: #3b82f6 !important;
      color: #e4e4e7 !important;
  }
  button[data-baseweb="tab"][aria-selected="true"] {
      background: #1a1a1e !important;
      border-color: #3b82f6 !important;
      color: #fafafa !important;
  }
  
  /* Chat Bubbles */
  .chat-bubble {
    border-radius: 8px;
    padding: 14px 18px;
    margin: 10px 0;
    max-width: 85%;
    font-size: 14.5px;
    line-height: 1.6;
    font-family: 'DM Sans', sans-serif;
  }
  .chat-ai {
    background: #18181b;
    border-left: 3px solid #3b82f6;
    border: 1px solid #27272a;
    color: #a1a1aa;
    align-self: flex-start;
  }
  .chat-student {
    background: #1a1a1e;
    border: 1px solid #27272a;
    border-left: 3px solid #52525b;
    color: #e4e4e7;
    margin-left: auto;
  }

  /* File Uploader */
  [data-testid="stFileUploader"] {
    background: #141415 !important;
    border: 2px dashed #27272a !important;
    border-radius: 8px !important;
  }
  
  /* Buttons — minimal zinc style */
  .stButton>button {
    background: #3b82f6 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    letter-spacing: 0.1px !important;
    transition: background 0.15s ease !important;
    padding: 7px 18px !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    white-space: nowrap !important;
  }
  .stButton>button:hover {
    background: #2563eb !important;
  }
  .stButton>button[kind="secondary"] {
    background: #18181b !important;
    color: #a1a1aa !important;
    border: 1px solid #27272a !important;
  }
  .stButton>button[kind="secondary"]:hover {
    border-color: #3b82f6 !important;
    color: #fafafa !important;
  }


  /* Developer Credit Sidebar Card */
  .dev-card {
    background: #18181b !important;
    border: 1px solid #27272a !important;
    border-left: 3px solid #3b82f6 !important;
    border-radius: 8px !important;
    padding: 14px !important;
    margin-top: 20px !important;
  }

  /* Status Pulse Animations */
  @keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.6); }
    70%  { box-shadow: 0 0 0 5px rgba(74, 222, 128, 0); }
    100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
  }
  @keyframes pulse-offline {
    0%   { box-shadow: 0 0 0 0 rgba(248, 113, 113, 0.6); }
    70%  { box-shadow: 0 0 0 5px rgba(248, 113, 113, 0); }
    100% { box-shadow: 0 0 0 0 rgba(248, 113, 113, 0); }
  }
  .status-indicator-online {
    height: 7px; width: 7px;
    background-color: #4ade80;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
  }
  .status-indicator-offline {
    height: 7px; width: 7px;
    background-color: #f87171;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-offline 2s infinite;
  }

  /* Full width container overrides */
  #MainMenu {visibility: hidden;}
  header {visibility: hidden;}
  footer {visibility: hidden;}
  .block-container {
    padding-top: 0rem !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
    width: 100% !important;
  }
  .main .block-container {
    max-width: 100% !important;
  }

  /* ── Mobile Responsive Overrides ── */
  @media (max-width: 768px) {
    /* Navbar mobile stacking */
    .nav-mobile-wrap {
      flex-direction: column !important;
      align-items: flex-start !important;
      gap: 10px !important;
      padding: 12px 18px !important;
    }
    .nav-right-section {
      flex-direction: column !important;
      align-items: flex-start !important;
      gap: 8px !important;
      width: 100% !important;
    }
    .nav-links-row {
      flex-wrap: wrap !important;
      gap: 6px !important;
    }
    .nav-attribution {
      display: none !important;
    }

    /* Hero section mobile */
    .hero-section {
      height: auto !important;
      min-height: unset !important;
      padding: 60px 18px 48px 18px !important;
    }
    .hero-title {
      font-size: 28px !important;
      letter-spacing: -0.5px !important;
      padding: 0 !important;
    }
    .hero-desc {
      font-size: 14.5px !important;
      padding: 0 !important;
    }
    .hero-badges {
      justify-content: flex-start !important;
    }
    .hero-badges span {
      font-size: 11px !important;
      padding: 5px 10px !important;
    }

    /* Tabs mobile scroll */
    [data-baseweb="tab-list"] {
      overflow-x: auto !important;
      flex-wrap: nowrap !important;
      -webkit-overflow-scrolling: touch !important;
      scrollbar-width: none !important;
    }
    [data-baseweb="tab-list"]::-webkit-scrollbar {
      display: none !important;
    }
    button[data-baseweb="tab"] {
      flex-shrink: 0 !important;
      font-size: 12px !important;
      padding: 6px 12px !important;
      white-space: nowrap !important;
    }

    /* Experiments page header padding */
    .experiments-header {
      padding: 24px 18px 18px 18px !important;
    }
    .experiments-content {
      padding: 0 18px 36px 18px !important;
    }
    .experiments-header h1 {
      font-size: 26px !important;
    }

    /* Cards on mobile: single column, full width */
    .stHorizontalBlock {
      flex-direction: column !important;
    }
    [data-testid="column"] {
      width: 100% !important;
      flex: none !important;
      min-width: 100% !important;
    }

    /* Glass card mobile padding */
    .glass-card {
      padding: 16px !important;
      margin-bottom: 10px !important;
    }

    /* Feature cards: adjust height auto */
    .feat-card {
      height: auto !important;
      padding: 16px !important;
    }

    /* Metric grid wrap */
    .metrics-grid {
      flex-direction: column !important;
    }

    /* Buttons full width on mobile */
    .stButton > button {
      width: 100% !important;
      padding: 10px 16px !important;
      font-size: 13px !important;
    }

    /* Reduce heading sizes on mobile */
    h1 { font-size: 1.7rem !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.1rem !important; }

    /* Chat bubbles full width */
    .chat-bubble {
      max-width: 100% !important;
    }

    /* Formula blocks */
    .formula-block {
      font-size: 12px !important;
      padding: 10px 12px !important;
    }

    /* CTA banner mobile */
    .cta-banner {
      padding: 24px 18px !important;
    }

    /* Active lab bar */
    .active-lab-bar {
      flex-direction: column !important;
      gap: 8px !important;
    }
  }

  @media (max-width: 480px) {
    html, body, [class*="css"] {
      font-size: 14px !important;
    }
    .hero-title {
      font-size: 24px !important;
      line-height: 1.25 !important;
    }
    .hero-overline {
      font-size: 10px !important;
      letter-spacing: 0.8px !important;
      padding: 4px 10px !important;
    }
    .stButton > button {
      font-size: 12.5px !important;
    }
    button[data-baseweb="tab"] {
      font-size: 11.5px !important;
      padding: 5px 10px !important;
    }
    .nav-brand {
      font-size: 16px !important;
    }
    .nav-badge {
      display: none !important;
    }
  }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions for API Communication ───────────────────────────────────
def get_backend_root_url():
    return API_BASE_URL.replace("/api", "").rstrip("/")

@st.cache_data(ttl=180, show_spinner=False)
def check_backend_status():
    """
    Pings backend root and returns status dict (cached for 3 minutes):
    'status': 'online' | 'waking_up' | 'offline'
    """
    root_url = get_backend_root_url()
    try:
        r = requests.get(root_url, timeout=1.5)
        if r.status_code == 200:
            return {"status": "online", "data": r.json()}
    except requests.exceptions.Timeout:
        return {"status": "waking_up", "message": "Render instance is spinning up..."}
    except Exception:
        pass
    return {"status": "offline", "message": "Backend server is offline or unreachable."}


@st.cache_data(ttl=600, show_spinner=False)
def get_all_experiments(semester=None):
    try:
        params = {}
        if semester:
            params["semester"] = semester
        r = requests.get(f"{API_BASE_URL}/experiments", params=params, timeout=5)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception:
        return []


@st.cache_data(ttl=600, show_spinner=False)
def get_experiment_detail(exp_id):
    try:
        r = requests.get(f"{API_BASE_URL}/experiments/{exp_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
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


# ── Session State & Page Routing ─────────────────────────────────────────────
if "active_exp_id" not in st.session_state:
    st.session_state.active_exp_id = None
    st.session_state.active_exp_title = None

# Handle ?_launch=EXP_ID&_title=EXP_TITLE links from card buttons
_launch_id = st.query_params.get("_launch", None)
_launch_title = st.query_params.get("_title", None)
if _launch_id and _launch_title:
    st.session_state.active_exp_id = unquote(_launch_id)
    st.session_state.active_exp_title = unquote(_launch_title)
    # Clear launch params and stay on experiments page
    st.query_params.clear()
    st.rerun()

# Handle ?_exit=true link to exit active workspace
if st.query_params.get("_exit", None) == "true":
    st.session_state.active_exp_id = None
    st.session_state.active_exp_title = None
    st.query_params.clear()
    st.query_params["page"] = "experiments"
    st.rerun()

# Track current page via query parameters / session state
query_page = st.query_params.get("page", "home")
st.session_state.current_page = query_page

# ── Render Page Top / Status ─────────────────────────────────────────────────
backend_ok = check_backend_status()
backend_status = backend_ok.get("status") if isinstance(backend_ok, dict) else ("online" if backend_ok else "offline")

if backend_status == "online":
    status_badge = '<span class="status-indicator-online" style="margin-right:6px;"></span><span style="color:#4ade80;font-size:12px;font-weight:500;">Online</span>'
elif backend_status == "waking_up":
    status_badge = '<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#fbbf24;margin-right:6px;"></span><span style="color:#fbbf24;font-size:12px;font-weight:500;">Waking Up</span>'
else:
    status_badge = '<span class="status-indicator-offline" style="margin-right:6px;"></span><span style="color:#f87171;font-size:12px;font-weight:500;">Offline</span>'

# ── Top Navbar (Full Width Sticky Header) ────────────────────────────────────
nav_active_html = ""
if st.session_state.active_exp_id:
    nav_active_html = (
        f'<div style="display:flex;align-items:center;gap:10px;background:#18181b;border:1px solid #27272a;padding:5px 12px;border-radius:6px;">'
        f'<span style="color:#71717a;font-size:11px;text-transform:uppercase;font-weight:600;letter-spacing:0.5px;">Active Lab:</span>'
        f'<span style="color:#fafafa;font-size:13px;font-weight:600;">{st.session_state.active_exp_title}</span>'
        f'</div>'
    )

is_home = st.session_state.current_page == "home"
is_exp = st.session_state.current_page == "experiments"

home_style = "color:#fafafa;background:#27272a;border-color:#3f3f46;" if is_home else "color:#a1a1aa;background:#18181b;border-color:#27272a;"
exp_style = "color:#ffffff;background:#2563eb;border-color:#3b82f6;font-weight:600;" if is_exp else "color:#a1a1aa;background:#18181b;border-color:#27272a;"

navbar_html = f"""<div class="nav-mobile-wrap" style="position:sticky;top:0;z-index:999;width:100%;box-sizing:border-box;display:flex;align-items:center;justify-content:space-between;padding:14px 36px;background:#09090b;border-bottom:1px solid #27272a;margin-bottom:0;">
<div style="display:flex;align-items:center;gap:10px;">
<a href="?page=home" target="_self" class="nav-brand" style="text-decoration:none;font-family:'Poppins',sans-serif;font-weight:700;font-size:18px;color:#fafafa;letter-spacing:-0.4px;">VELIA</a>
<span class="nav-badge" style="font-family:'DM Sans',sans-serif;font-size:11px;color:#71717a;letter-spacing:0.5px;padding:2px 8px;background:#18181b;border:1px solid #27272a;border-radius:4px;font-weight:500;">ECE Lab Intelligence</span>
<div style="display:flex;align-items:center;padding:2px 8px;background:#141415;border:1px solid #27272a;border-radius:20px;">{status_badge}</div>
</div>
<div class="nav-right-section" style="display:flex;align-items:center;gap:12px;">
{nav_active_html}
<div class="nav-links-row" style="display:flex;align-items:center;gap:8px;">
<a href="?page=home" target="_self" style="font-family:'DM Sans',sans-serif;font-size:13px;font-weight:500;padding:5px 12px;border:1px solid;border-radius:6px;text-decoration:none;{home_style}">Home</a>
<a href="?page=experiments" target="_self" style="font-family:'DM Sans',sans-serif;font-size:13px;padding:5px 14px;border:1px solid;border-radius:6px;text-decoration:none;{exp_style}">Experiments</a>
<span class="nav-attribution" style="font-family:'DM Sans',sans-serif;font-size:12px;color:#71717a;padding-left:8px;border-left:1px solid #27272a;">Dept. of ECE · BIT Mesra</span>
</div>
</div>
</div>"""

st.markdown(navbar_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ── LANDING / EXPERIMENTS ROUTING ────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.active_exp_id:
    # ── ROUTE 1: HOME PAGE ───────────────────────────────────────────────────
    if st.session_state.current_page == "home":
        # ── 1. Hero Section — Full Viewport Height & Refined Typography ──
        hero_html = """<div class="hero-section" style="height:calc(100vh - 68px);min-height:calc(100vh - 68px);width:100%;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:30px 24px;background:#09090b;border-bottom:1px solid #27272a;margin-bottom:40px;">
<div style="margin-bottom:20px;">
<span class="hero-overline" style="font-family:'DM Sans',sans-serif;font-size:12.5px;font-weight:600;color:#60a5fa;text-transform:uppercase;letter-spacing:1.5px;padding:5px 14px;background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:20px;">Developed by Sarbajit Ghosh · Dept. of ECE, BIT Mesra</span>
</div>
<h1 class="hero-title" style="font-family:'Poppins',sans-serif;font-size:clamp(28px, 4.4vw, 58px);font-weight:700;color:#fafafa;letter-spacing:-1.2px;line-height:1.2;margin:0 auto 18px auto;max-width:880px;padding:0 12px;">VELIA — Vision-Enhanced<br>Laboratory Intelligence Assistant</h1>
<p class="hero-desc" style="font-family:'DM Sans',sans-serif;font-size:clamp(14px, 1.4vw, 18.5px);color:#a1a1aa;max-width:680px;margin:0 auto 32px auto;font-weight:400;line-height:1.65;padding:0 12px;">An offline-capable AI virtual laboratory environment for Electronics &amp; Communication Engineering. Breadboard CV scanning, GNN topology verification, digital twin simulation &amp; adaptive viva.</p>
<div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-bottom:32px;">
<a href="?page=experiments" target="_self" style="font-family:'DM Sans',sans-serif;background:#2563eb;color:#ffffff;padding:10px 24px;border-radius:6px;font-size:14px;font-weight:600;text-decoration:none;display:inline-block;transition:background 0.15s;">Explore Experiments →</a>
<a href="#metrics" style="font-family:'DM Sans',sans-serif;background:#18181b;color:#a1a1aa;border:1px solid #27272a;padding:10px 20px;border-radius:6px;font-size:14px;font-weight:500;text-decoration:none;display:inline-block;">Platform Overview ↓</a>
</div>
<div class="hero-badges" style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;">
<span style="font-family:'DM Sans',sans-serif;background:#18181b;border:1px solid #27272a;padding:6px 14px;border-radius:6px;font-size:12.5px;color:#71717a;font-weight:500;">YOLOv8 Vision Scan</span>
<span style="font-family:'DM Sans',sans-serif;background:#18181b;border:1px solid #27272a;padding:6px 14px;border-radius:6px;font-size:12.5px;color:#71717a;font-weight:500;">PyTorch GNN</span>
<span style="font-family:'DM Sans',sans-serif;background:#18181b;border:1px solid #27272a;padding:6px 14px;border-radius:6px;font-size:12.5px;color:#71717a;font-weight:500;">Digital Twin</span>
<span style="font-family:'DM Sans',sans-serif;background:#18181b;border:1px solid #27272a;padding:6px 14px;border-radius:6px;font-size:12.5px;color:#71717a;font-weight:500;">LLM Viva Examiner</span>
<span style="font-family:'DM Sans',sans-serif;background:#18181b;border:1px solid #27272a;padding:6px 14px;border-radius:6px;font-size:12.5px;color:#71717a;font-weight:500;">RAG Assistant</span>
</div>
</div>"""
        st.markdown(hero_html, unsafe_allow_html=True)

        # ── 2. Real-Time Platform Statistics (Interactive Spotlight Carousel) ──
        st.markdown("""
        <style>
        .home-section-wrap {
            padding: 0 52px 64px 52px;
            box-sizing: border-box;
        }
        @media (max-width: 768px) {
            .home-section-wrap {
                padding: 0 18px 48px 18px !important;
            }
        }
        /* Spotlight Card */
        .spotlight-card {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 14px;
            padding: 32px 36px;
            display: grid;
            grid-template-columns: 180px 1fr;
            gap: 32px;
            align-items: center;
            transition: border-color 0.25s ease;
            box-shadow: 0 4px 24px rgba(0,0,0,0.25);
            margin-bottom: 20px;
        }
        @media (max-width: 768px) {
            .spotlight-card {
                grid-template-columns: 1fr;
                gap: 16px;
                padding: 24px 20px;
            }
        }
        .spotlight-stat-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px;
            background: #111113;
            border: 1px solid #27272a;
            border-radius: 10px;
        }
        .spotlight-stat-num {
            font-family: 'Poppins', sans-serif;
            font-size: clamp(38px, 4vw, 52px);
            font-weight: 800;
            color: #fafafa;
            line-height: 1;
            margin-bottom: 6px;
        }
        .spotlight-stat-label {
            font-family: 'DM Sans', sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #71717a;
        }
        .spotlight-info {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .spotlight-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
        }
        .spotlight-pill {
            font-family: 'DM Sans', sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #60a5fa;
            background: rgba(59,130,246,0.08);
            border: 1px solid rgba(59,130,246,0.25);
            padding: 3px 10px;
            border-radius: 20px;
        }
        .spotlight-index {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: #52525b;
            font-weight: 600;
        }
        .spotlight-title {
            font-family: 'Poppins', sans-serif;
            font-size: clamp(17px, 2vw, 22px);
            font-weight: 700;
            color: #fafafa;
            margin: 0;
            line-height: 1.3;
        }
        .spotlight-desc {
            font-family: 'DM Sans', sans-serif;
            font-size: 13.5px;
            color: #a1a1aa;
            line-height: 1.6;
            margin: 0;
        }
        .spotlight-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 2px;
        }
        .spotlight-tag-item {
            font-family: 'DM Sans', sans-serif;
            font-size: 11.5px;
            color: #71717a;
            background: #111113;
            border: 1px solid #27272a;
            padding: 4px 10px;
            border-radius: 6px;
        }
        /* Thumbnail Cards Row */
        .carousel-selector-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }
        @media (max-width: 768px) {
            .carousel-selector-row {
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }
        }
        .carousel-thumb-card {
            background: #141416;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            transition: all 0.15s ease;
            cursor: pointer;
        }
        .carousel-thumb-card:hover {
            border-color: #3b82f6;
            background: #18181b;
        }
        .carousel-thumb-card.active {
            background: #1e1e24;
            border-color: #3b82f6;
            box-shadow: 0 0 0 1px rgba(59,130,246,0.3);
        }
        </style>
        <div class="home-section-wrap" id="metrics">
            <div style="margin-bottom: 24px;">
                <h2 style="font-family:'Poppins',sans-serif; font-size:clamp(20px, 2.5vw, 24px); font-weight:700; color:#fafafa; margin:0 0 6px 0; letter-spacing:-0.5px;">Platform Metrics &amp; Benchmarks</h2>
                <p style="font-family:'DM Sans',sans-serif; font-size:13.5px; color:#71717a; margin:0;">Explore verified curriculum nodes, machine learning stacks, diagnostic estimators, and knowledge maps.</p>
            </div>
        """, unsafe_allow_html=True)

        METRIC_SLIDES = [
            {
                "stat": "80+",
                "stat_label": "Experiments",
                "tag": "Curriculum Coverage",
                "title": "Comprehensive ECE Laboratory Syllabus",
                "desc": "Full digital curriculum coverage across Semesters I through VIII at BIT Mesra, including Basic Electronics, Analog Circuits, Digital ICs, VLSI, DSP, and Microcontrollers.",
                "badges": ["8 Semesters Cataloged", "10+ Laboratory Courses", "Hardware Component Inventories"],
                "cta_text": "Explore Experiments Catalog →",
                "cta_link": "?page=experiments"
            },
            {
                "stat": "4",
                "stat_label": "AI Models",
                "tag": "Neural Network Stack",
                "title": "Multi-Modal Machine Learning & Vision Architecture",
                "desc": "YOLOv8 nano for breadboard pin-level component bounding boxes, PyTorch GNN for schematic graph validation, Random Forest/MLP for circuit fault prediction, and FAISS vector RAG.",
                "badges": ["YOLOv8 Object Detection", "PyTorch Geometric GNN", "FAISS RAG Vector Store"],
                "cta_text": "View Experiments →",
                "cta_link": "?page=experiments"
            },
            {
                "stat": "8",
                "stat_label": "Fault Classes",
                "tag": "Automated Diagnostics",
                "title": "Real-Time Circuit Fault Detection & Root-Cause Biasing",
                "desc": "Automated diagnostic logic checking against Random Forest and Deep MLP estimators to detect cutoff biasing, saturation, thermal runaway, open collector, and power rail droop.",
                "badges": ["Cutoff / Saturation Detection", "BJT Q-Point Drift", "Thermal & Rail Droop Diagnostics"],
                "cta_text": "Launch Laboratory →",
                "cta_link": "?page=experiments"
            },
            {
                "stat": "25",
                "stat_label": "Concept Nodes",
                "tag": "Knowledge Graph",
                "title": "Interactive Topological Knowledge & Concept Pre-Requisites",
                "desc": "A linked topological knowledge graph connecting circuit components, semiconductor physics, formulas, and troubleshooting steps to deliver contextual adaptive viva grading.",
                "badges": ["Formula Linking", "Interactive Vis.js Graph", "Automated Viva Grading Engine"],
                "cta_text": "Launch Interactive Lab →",
                "cta_link": "?page=experiments"
            }
        ]

        if "metric_slide_idx" not in st.session_state:
            st.session_state.metric_slide_idx = 0

        curr_idx = st.session_state.metric_slide_idx
        slide = METRIC_SLIDES[curr_idx]

        # ── 1. Big Center Spotlight Card ──
        badges_html = "".join([f'<span class="spotlight-tag-item">{b}</span>' for b in slide["badges"]])

        st.markdown(f"""
        <div class="spotlight-card">
            <div class="spotlight-stat-box">
                <div class="spotlight-stat-num">{slide["stat"]}</div>
                <div class="spotlight-stat-label">{slide["stat_label"]}</div>
            </div>
            <div class="spotlight-info">
                <div class="spotlight-header">
                    <span class="spotlight-pill">{slide["tag"]}</span>
                    <span class="spotlight-index">0{curr_idx + 1} / 04</span>
                </div>
                <h3 class="spotlight-title">{slide["title"]}</h3>
                <p class="spotlight-desc">{slide["desc"]}</p>
                <div class="spotlight-tags">{badges_html}</div>
                <div style="margin-top:6px;">
                    <a href="{slide['cta_link']}" target="_self" style="font-family:'DM Sans',sans-serif;font-size:12.5px;font-weight:600;color:#ffffff;background:#2563eb;padding:7px 18px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;transition:background 0.15s ease;">
                        {slide['cta_text']}
                    </a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 2. Carousel Thumbnails Row / Selector ──
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        thumb_cols = [col_t1, col_t2, col_t3, col_t4]
        thumb_titles = ["Curriculum (80+)", "AI Models (4)", "Fault Classes (8)", "Knowledge (25 Nodes)"]

        def _select_metric_slide(i):
            st.session_state.metric_slide_idx = i

        for idx, (t_col, t_title) in enumerate(zip(thumb_cols, thumb_titles)):
            with t_col:
                is_active = (idx == curr_idx)
                btn_type = "primary" if is_active else "secondary"
                st.button(
                    t_title, 
                    key=f"btn_slide_{idx}", 
                    use_container_width=True, 
                    type=btn_type,
                    on_click=_select_metric_slide,
                    args=(idx,)
                )

        # ── Divider with Proper Spacing ──
        st.markdown('<div style="height:1px; background:#27272a; margin:52px 0 36px 0;"></div>', unsafe_allow_html=True)

        # ── 3. Platform Capabilities Deck ──
        st.markdown("""
        <div style="margin-bottom: 22px;">
            <h2 style="font-family:'Poppins',sans-serif; font-size:clamp(20px, 2.5vw, 24px); font-weight:700; color:#fafafa; margin:0 0 6px 0; letter-spacing:-0.5px;">Core AI Platform Capabilities</h2>
            <p style="font-family:'DM Sans',sans-serif; font-size:13.5px; color:#71717a; margin:0;">Multi-modal AI pipelines powering automated grading, circuit validation, and real-time laboratory assistance.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.markdown("""
            <div class="feat-card">
                <h5 style="color:#fafafa; margin-bottom:8px; font-family:'Poppins',sans-serif; font-size:15px; font-weight:600;">Fault Diagnosis</h5>
                <p style="font-size:12.5px; color:#71717a; line-height:1.55; margin:0;">
                    Hybrid logic checking against Random Forest and Deep MLP fault estimators to diagnose cutoff, saturation, and droop.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_c2:
            st.markdown("""
            <div class="feat-card">
                <h5 style="color:#fafafa; margin-bottom:8px; font-family:'Poppins',sans-serif; font-size:15px; font-weight:600;">Computer Vision</h5>
                <p style="font-size:12.5px; color:#71717a; line-height:1.55; margin:0;">
                    Scans breadboard wiring rows and matches component connectivity matrices using YOLOv8 bounding boxes.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_c3:
            st.markdown("""
            <div class="feat-card">
                <h5 style="color:#fafafa; margin-bottom:8px; font-family:'Poppins',sans-serif; font-size:15px; font-weight:600;">Waveform Analyzer</h5>
                <p style="font-size:12.5px; color:#71717a; line-height:1.55; margin:0;">
                    Applies OpenCV HSV filter masking to trace CRO screenshot signals and isolate clipping distortion.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_c4:
            st.markdown("""
            <div class="feat-card">
                <h5 style="color:#fafafa; margin-bottom:8px; font-family:'Poppins',sans-serif; font-size:15px; font-weight:600;">Digital Twin</h5>
                <p style="font-size:12.5px; color:#71717a; line-height:1.55; margin:0;">
                    Simulates real-time electrical output voltages, Bode plots, and load lines matching SPICE formulations.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROUTE 2: DEDICATED EXPERIMENTS PAGE ──────────────────────────────────
    elif st.session_state.current_page == "experiments":

        # ── Global Page CSS Overrides for Experiments ─────────────────────────
        st.markdown("""
        <style>
        /* ── Experiments Header Banner ── */
        .exp-header-banner {
            padding: 28px 52px 20px 52px;
            background: #09090b;
            border-bottom: 1px solid #27272a;
            margin-bottom: 0px;
        }

        /* ── Notion-Style Pill Tabs (Both Semester & Lab Courses) ── */
        [data-baseweb="tab-list"] {
            padding-left: 52px !important;
            padding-right: 52px !important;
            padding-top: 14px !important;
            padding-bottom: 8px !important;
            gap: 8px !important;
            background: #09090b !important;
            border-bottom: none !important;
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
        }
        [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }

        /* Tab Pill Buttons */
        button[data-baseweb="tab"] {
            background-color: #141416 !important;
            border: 1px solid #27272a !important;
            border-radius: 8px !important;
            padding: 7px 16px !important;
            color: #71717a !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
            margin: 0 !important;
        }
        button[data-baseweb="tab"]:hover {
            border-color: #3b82f6 !important;
            color: #e4e4e7 !important;
            background-color: #18181b !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #1e1e24 !important;
            border-color: #3b82f6 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 0 0 1px rgba(59,130,246,0.3) !important;
        }

        /* Suppress default Streamlit tab borders & lines */
        [data-baseweb="tab-border"],
        [data-baseweb="tab-highlight"] {
            display: none !important;
            height: 0 !important;
        }

        /* Zero out tab panel margins/paddings */
        [data-baseweb="tab-panel"] {
            padding: 0 !important;
            margin: 0 !important;
        }
        [data-baseweb="tab-panel"] > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /* ── Experiment Count & Info Bar ── */
        .exp-count-bar {
            padding: 10px 52px 14px 52px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: 'DM Sans', sans-serif;
            font-size: 13px;
            color: #71717a;
        }
        .exp-count-badge {
            background: #18181b;
            border: 1px solid #27272a;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            color: #a1a1aa;
            font-weight: 500;
        }

        /* ── Experiment Cards Grid ── */
        .exp-cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            padding: 0 52px 48px 52px;
            box-sizing: border-box;
        }

        /* ── Card Styling ── */
        .exp-card-item {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 10px;
            padding: 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 12px;
            min-height: 220px;
            box-sizing: border-box;
            transition: border-color 0.2s ease, transform 0.15s ease;
        }
        .exp-card-item:hover {
            border-color: #3b82f6;
        }

        /* ── Launch Button (Pure White text, Blue bg) ── */
        .exp-launch-btn {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 12.5px !important;
            font-weight: 600 !important;
            color: #ffffff !important;
            background: #2563eb !important;
            padding: 7px 16px !important;
            border-radius: 6px !important;
            text-decoration: none !important;
            white-space: nowrap !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 4px !important;
            transition: background 0.15s ease !important;
        }
        .exp-launch-btn:hover {
            background: #1d4ed8 !important;
            color: #ffffff !important;
            text-decoration: none !important;
        }

        /* ── Mobile Responsive (< 768px) ── */
        @media (max-width: 768px) {
            .exp-header-banner {
                padding: 20px 18px 16px 18px !important;
            }
            [data-baseweb="tab-list"] {
                padding-left: 18px !important;
                padding-right: 18px !important;
                gap: 6px !important;
            }
            button[data-baseweb="tab"] {
                padding: 6px 12px !important;
                font-size: 12px !important;
            }
            .exp-count-bar {
                padding: 8px 18px 12px 18px !important;
            }
            .exp-cards-grid {
                grid-template-columns: 1fr !important;
                padding: 0 18px 36px 18px !important;
                gap: 12px !important;
            }
            .exp-card-item {
                padding: 16px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        # ── Experiments Header Banner ─────────────────────────────────────────
        st.markdown("""
        <div class="exp-header-banner">
            <a href="?page=home" target="_self" style="font-family:'DM Sans',sans-serif;color:#3b82f6;text-decoration:none;font-size:13px;font-weight:500;display:inline-flex;align-items:center;gap:4px;margin-bottom:8px;">
                ← Back to Home
            </a>
            <h1 style="font-family:'Poppins',sans-serif;font-size:clamp(22px,3.5vw,34px);font-weight:700;color:#fafafa;margin:4px 0 4px 0;letter-spacing:-0.8px;">Experiments</h1>
            <p style="font-family:'DM Sans',sans-serif;color:#a1a1aa;font-size:clamp(13px,1.2vw,14.5px);margin:0;">Semester-Wise Laboratory Curriculum &amp; AI-Powered Interactive Workspaces</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Semester Tabs (Notion-Style Pills) ────────────────────────────────
        sem_keys = ["Semester I", "Semester III", "Semester IV", "Semester V", "Semester VI", "Semester VII"]
        sem_tabs = st.tabs(sem_keys)

        db_exps = get_all_experiments()

        for sem_tab, sem_key in zip(sem_tabs, sem_keys):
            with sem_tab:
                courses = ECE_SYLLABUS.get(sem_key, {})
                if not courses:
                    st.markdown(f'<div style="padding:32px 52px;color:#71717a;font-family:\'DM Sans\',sans-serif;font-size:13.5px;">No laboratory courses cataloged for {sem_key}.</div>', unsafe_allow_html=True)
                else:
                    course_codes = list(courses.keys())
                    course_names = [f"{code} — {courses[code]['name']}" for code in course_codes]

                    # ── Lab Course Tabs (Exact Same Notion-Style Pills as Semester) ──
                    course_tabs = st.tabs(course_names)

                    for course_tab, course_code in zip(course_tabs, course_codes):
                        with course_tab:
                            course_data = courses[course_code]
                            experiments_list = course_data.get("experiments", [])
                            total = len(experiments_list)

                            # ── Count Line with Proper Left Padding ──
                            st.markdown(
                                f'<div class="exp-count-bar">'
                                f'<span class="exp-count-badge">{total} experiment{"s" if total != 1 else ""}</span>'
                                f'<span>in this laboratory</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                            # ── Experiment Cards in Responsive 2-Col Grid ──
                            cards_inner_html = ""
                            for exp_idx, exp in enumerate(experiments_list, 1):
                                matched_db = find_matching_db_exp(exp, db_exps)
                                diff = exp.get("difficulty", "Medium")
                                if diff == "Easy":
                                    diff_badge = '<span class="badge badge-easy">Easy</span>'
                                elif diff == "Medium":
                                    diff_badge = '<span class="badge badge-medium">Medium</span>'
                                else:
                                    diff_badge = '<span class="badge badge-hard">Hard</span>'

                                status_badge = '<span class="badge badge-easy" style="background:#14241e;color:#4ade80;border:1px solid #166534;">AI Lab Active</span>'

                                if matched_db:
                                    l_id = quote(matched_db['id'])
                                    l_title = quote(matched_db['title'])
                                else:
                                    sem_num = sem_key.split()[-1]
                                    roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
                                    sem_digit = roman_map.get(sem_num, 1)
                                    l_id = quote(f"sem{sem_digit}_{course_code}_exp{exp_idx}")
                                    l_title = quote(exp['title'])

                                components_str = ", ".join(exp.get("components", ["Standard Bench Equipment"]))
                                aim_str = exp.get("aim", "")

                                cards_inner_html += f"""
<div class="exp-card-item">
  <div>
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:12px;">{diff_badge} {status_badge}</div>
    <h4 style="font-family:'Poppins',sans-serif;font-size:15.5px;font-weight:600;color:#fafafa;margin:0 0 8px 0;line-height:1.35;">{exp['title']}</h4>
    <p style="font-family:'DM Sans',sans-serif;color:#a1a1aa;font-size:12.5px;margin:0 0 8px 0;line-height:1.45;"><b>Aim:</b> {aim_str}</p>
    <p style="font-family:'DM Sans',sans-serif;color:#71717a;font-size:11.5px;margin:0;"><b>Components:</b> {components_str}</p>
  </div>
  <div style="border-top:1px solid #27272a;padding-top:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
    <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:#71717a;">&#x23f1;&#xfe0f; Duration: <b style="color:#e4e4e7;">{exp['time']}</b></span>
    <a href="?page=experiments&_launch={l_id}&_title={l_title}" target="_self" class="exp-launch-btn">Launch AI Workspace &#8594;</a>
  </div>
</div>"""

                            st.markdown(f'<div class="exp-cards-grid">{cards_inner_html}</div>', unsafe_allow_html=True)





# ─────────────────────────────────────────────────────────────────────────────
# ── WORKSPACE WINDOW: EXPERIMENT ACTIVE ──────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
else:
    selected_exp_id = st.session_state.active_exp_id
    exp_detail = get_experiment_detail(selected_exp_id)
    
    if not exp_detail:
        st.error("Failed to retrieve experiment details. Please try returning to the catalog.")
    else:
        # ── Workspace Global CSS Overrides for Minimalist Report Aesthetic ──
        st.markdown("""
        <style>
        .active-workspace-wrap {
            padding: 24px 52px 64px 52px;
            box-sizing: border-box;
        }
        @media (max-width: 768px) {
            .active-workspace-wrap {
                padding: 16px 18px 36px 18px !important;
            }
        }
        .report-card {
            background: #141416;
            border: 1px solid #27272a;
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 24px;
            box-sizing: border-box;
        }
        .report-section-overline {
            font-family: 'DM Sans', sans-serif;
            font-size: 11px;
            font-weight: 700;
            color: #60a5fa;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .report-card-title {
            font-family: 'Poppins', sans-serif;
            font-size: 17px;
            font-weight: 600;
            color: #fafafa;
            margin: 0 0 14px 0;
            line-height: 1.35;
        }
        .step-callout {
            background: #18181b;
            border: 1px solid #27272a;
            border-left: 3px solid #3b82f6;
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 10px;
            font-family: 'DM Sans', sans-serif;
            font-size: 13px;
            color: #a1a1aa;
            line-height: 1.55;
        }
        .step-num-tag {
            font-family: 'DM Mono', monospace;
            font-weight: 700;
            font-size: 11px;
            color: #60a5fa;
            margin-right: 6px;
        }

        /* ── Workspace tab navbar: 52px L/R padding ── */
        [data-baseweb="tab-list"] {
            padding-left: 52px !important;
            padding-right: 52px !important;
        }
        @media (max-width: 768px) {
            [data-baseweb="tab-list"] {
                padding-left: 18px !important;
                padding-right: 18px !important;
            }
        }

        /* ── Workspace tab panels: 52px L/R padding (injected only in workspace, not experiments page) ── */
        [data-baseweb="tab-panel"] {
            padding-left: 52px !important;
            padding-right: 52px !important;
            padding-top: 12px !important;
            padding-bottom: 48px !important;
        }
        @media (max-width: 768px) {
            [data-baseweb="tab-panel"] {
                padding-left: 18px !important;
                padding-right: 18px !important;
                padding-top: 8px !important;
                padding-bottom: 32px !important;
            }
        }
        </style>
        <div class="active-workspace-wrap">
        """, unsafe_allow_html=True)

        # ── Minimalist Academic Lab Report Header ──
        lab_code = exp_detail.get('lab_code', 'ECE-LAB')
        semester = exp_detail.get('semester', 1)
        lab_name = exp_detail.get('lab_name', 'Electronics & Communication Laboratory')
        exp_title = exp_detail.get('title', 'Experiment Workspace')

        st.markdown(f"""
        <div style="background:#111113; border:1px solid #27272a; border-radius:12px; padding:24px 28px; margin-bottom:24px;">
            <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; margin-bottom:10px;">
                <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                    <span style="font-family:'DM Sans',sans-serif; font-size:11px; font-weight:700; color:#60a5fa; background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.25); padding:3px 10px; border-radius:4px; text-transform:uppercase; letter-spacing:0.8px;">LABORATORY REPORT</span>
                    <span style="font-family:'DM Sans',sans-serif; font-size:12.5px; color:#a1a1aa;">Code: <b style="color:#fafafa;">{lab_code}</b> &nbsp;·&nbsp; Semester <b style="color:#fafafa;">{semester}</b></span>
                </div>
                <a href="?page=experiments&_exit=true" target="_self" style="font-family:'DM Sans',sans-serif; font-size:12px; font-weight:600; color:#f87171; background:rgba(248,113,113,0.1); border:1px solid rgba(248,113,113,0.3); padding:4px 12px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:4px; transition:all 0.15s ease;">✕ Exit Workspace</a>
            </div>
            <h2 style="font-family:'Poppins',sans-serif; font-size:clamp(20px, 3vw, 28px); font-weight:700; color:#fafafa; margin:0 0 6px 0; letter-spacing:-0.5px;">{exp_title}</h2>
            <p style="font-family:'DM Sans',sans-serif; font-size:13.5px; color:#71717a; margin:0;">{lab_name} — Department of ECE, BIT Mesra</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                st.markdown("""
                <div class="report-card">
                    <div class="report-section-overline">SECTION 01 · OBJECTIVE &amp; THEORETICAL SUMMARY</div>
                    <h3 class="report-card-title">Aim &amp; Theoretical Background</h3>
                """, unsafe_allow_html=True)
                st.info(exp_detail.get("aim", ""))
                st.markdown(f'<p style="font-family:\'DM Sans\',sans-serif;font-size:13.5px;color:#a1a1aa;line-height:1.65;margin:12px 0;">{exp_detail.get("theory", {}).get("summary", "")}</p>', unsafe_allow_html=True)
                
                st.markdown('<h4 style="font-family:\'Poppins\',sans-serif;font-size:14px;font-weight:600;color:#fafafa;margin:16px 0 8px 0;">Core Concepts</h4>', unsafe_allow_html=True)
                for c in exp_detail.get("theory", {}).get("key_concepts", []):
                    st.markdown(f"- **{c}**")
                st.markdown('</div>', unsafe_allow_html=True)
                    
            with col_info:
                st.markdown("""
                <div class="report-card">
                    <div class="report-section-overline">SECTION 02 · MATHEMATICAL FORMULAS &amp; INVENTORY</div>
                    <h3 class="report-card-title">Formulas &amp; Component Specs</h3>
                """, unsafe_allow_html=True)
                for f in exp_detail.get("theory", {}).get("key_formulas", []):
                    st.markdown(
                        f'<div class="formula-block">'
                        f'<strong>{f["name"]}</strong><br>'
                        f'<code style="color:#60a5fa;">{f["formula"]}</code><br>'
                        f'<span style="color:#71717a;font-size:12px">{f.get("variables", "")}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                st.markdown('<h4 style="font-family:\'Poppins\',sans-serif;font-size:14px;font-weight:600;color:#fafafa;margin:16px 0 8px 0;">Required Components</h4>', unsafe_allow_html=True)
                for c in exp_detail.get("components", []):
                    st.markdown(f"• **{c['name']}** — {c.get('spec', '')} ×{c.get('quantity', 1)}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Digital Twin Simulator
            st.markdown("""
            <div class="report-card">
                <div class="report-section-overline">SECTION 03 · SPICE DIGITAL TWIN SIMULATOR</div>
                <h3 class="report-card-title">Circuit Parameter Solver &amp; Waveform Predictor</h3>
                <p style="font-family:'DM Sans',sans-serif;font-size:13px;color:#71717a;margin:0 0 16px 0;">Tune component parameters to predict output voltages, Bode plots, and DC load lines dynamically.</p>
            """, unsafe_allow_html=True)

            
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
                st.markdown('</div>', unsafe_allow_html=True)
                                
        # ── TAB: Step-by-Step Procedure ──
        with tab_proc:
            st.markdown("""
            <div class="report-card">
                <div class="report-section-overline">SECTION 04 · EXPERIMENTAL PROCEDURE &amp; OBSERVATION</div>
                <h3 class="report-card-title">Laboratory Execution &amp; Data Logging</h3>
            """, unsafe_allow_html=True)
            st.info(f"**AIM:** {exp_detail.get('aim')}")
            col_proc, col_exp = st.columns([3, 2])
            
            with col_proc:
                st.markdown('<h4 style="font-family:\'Poppins\',sans-serif;font-size:14px;font-weight:600;color:#fafafa;margin:14px 0 10px 0;">Procedure Steps</h4>', unsafe_allow_html=True)
                for i, step in enumerate(exp_detail.get("procedure", []), 1):
                    st.markdown(
                        f'<div class="step-callout">'
                        f'<span class="step-num-tag">STEP {i:02d}</span> {step}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    
                st.markdown('<h4 style="font-family:\'Poppins\',sans-serif;font-size:14px;font-weight:600;color:#fafafa;margin:18px 0 10px 0;">Observation Table Format</h4>', unsafe_allow_html=True)
                obs = exp_detail.get("observations", {})
                if obs.get("table_headers"):
                    st.table([obs["table_headers"]])
                    st.caption(f"**Sample Row Data:** {', '.join(obs.get('sample_row', []))}")
                if obs.get("what_to_plot"):
                    st.info(f"Graph requirements: {obs['what_to_plot']}")
                    
            with col_exp:
                st.markdown('<h4 style="font-family:\'Poppins\',sans-serif;font-size:14px;font-weight:600;color:#fafafa;margin:14px 0 10px 0;">Expected Results</h4>', unsafe_allow_html=True)
                er = exp_detail.get("expected_results", {})
                st.write(er.get("description", ""))
                
                for tv in er.get("typical_values", []):
                    st.metric(tv["parameter"], f"{tv['expected']} {tv.get('unit', '')}")
                    
                st.markdown('<h4 style="font-family:\'Poppins\',sans-serif;font-size:14px;font-weight:600;color:#fafafa;margin:18px 0 10px 0;">Common Troubleshooting Indicators</h4>', unsafe_allow_html=True)
                for err in exp_detail.get("common_errors", []):
                    with st.expander(f"Symptom: {err['symptom']}"):
                        st.write(f"**Potential Causes:** {', '.join(err.get('causes', []))}")
                        st.success(f"**Fix:** {err.get('fix')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
                        
        # ── TAB: Fault & CV scan ──
        with tab_cv:
            st.markdown("""
            <div class="report-card">
                <div class="report-section-overline">SECTION 05 · INTELLIGENT CIRCUIT DIAGNOSTICS &amp; SCANNER</div>
                <h3 class="report-card-title">Fault Biasing &amp; Vision Inspection Center</h3>
            """, unsafe_allow_html=True)
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
            st.markdown("""
            <div class="report-card">
                <div class="report-section-overline">SECTION 06 · ADAPTIVE VIVA EXAMINER &amp; EVALUATION</div>
                <h3 class="report-card-title">Conversational AI Viva Prep</h3>
            """, unsafe_allow_html=True)
            
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
                st.markdown('<h4 style="font-family:\'Poppins\',sans-serif;font-size:14px;font-weight:600;color:#fafafa;margin:0 0 12px 0;">Student Skill Profile &amp; Mastery Dashboard</h4>', unsafe_allow_html=True)
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
                            f'<div style="background:#111113; border-radius:8px; padding:16px; border:1px solid #27272a; border-left:4px solid {color}; text-align:center;">'
                            f'<span style="color:#71717a; font-size:11.5px; font-weight:600;">{label}</span><br>'
                            f'<span style="font-size:22px; font-weight:700; color:#fafafa;">{val:.1f}%</span>'
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
            st.markdown('</div>', unsafe_allow_html=True)
                    
        # ── TAB: Knowledge Graph ──
        with tab_kg:
            st.markdown("""
            <div class="report-card">
                <div class="report-section-overline">SECTION 07 · ONTOLOGICAL KNOWLEDGE GRAPH</div>
                <h3 class="report-card-title">Semester-Wise Electronics Knowledge Graph</h3>
            """, unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)
                    
        # ── TAB: Faculty Analytics ──
        with tab_analytics:
            st.markdown("""
            <div class="report-card">
                <div class="report-section-overline">SECTION 08 · FACULTY PERFORMANCE ANALYTICS</div>
                <h3 class="report-card-title">Faculty Performance Analytics Dashboard</h3>
            """, unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)
                
        # ── TAB: Ask Assistant (RAG) ──
        with tab_rag:
            st.markdown("""
            <div class="report-card">
                <div class="report-section-overline">SECTION 09 · DOCUMENTATION &amp; RAG ASSISTANT</div>
                <h3 class="report-card-title">RAG Assistant Chat</h3>
            """, unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)

        # Close .active-workspace-wrap
        st.markdown('</div>', unsafe_allow_html=True)
