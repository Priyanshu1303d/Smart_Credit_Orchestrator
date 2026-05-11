"""
Smart Credit Orchestrator – Streamlit UI
Run from the project root:
  streamlit run streamlit/ui/app.py
"""

import sys, os, importlib.util

# Add project root to path so src.* imports work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

import streamlit as st

st.set_page_config(
    page_title="Smart Credit Orchestrator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS – Full Dark Theme ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Main app background ── */
.stApp, .main, [data-testid="stAppViewContainer"] {
    background: #0f172a !important;
}
[data-testid="stHeader"] { background: #0f172a !important; }
[data-testid="stToolbar"] { background: #0f172a !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0f172a 100%) !important;
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] hr { border-color: #334155 !important; }

/* ── Cards ── */
.card {
    background: #1e293b;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    border-left: 4px solid #6366f1;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.card h4  { margin: 0 0 .3rem 0; font-size: 1rem; color: #94a3b8; }
.card .val { font-size: 2rem; font-weight: 700; color: #818cf8; }

/* ── Stat boxes ── */
.stat {
    text-align: center;
    background: #1e293b;
    border-radius: 12px;
    padding: 1.1rem 1rem;
    border: 1px solid #334155;
}
.stat .n { font-size: 2.2rem; font-weight: 700; }
.stat .l { font-size: .8rem; color: #64748b; margin-top: .3rem; }

/* ── Badges ── */
.badge { display: inline-block; border-radius: 20px; padding: 3px 11px; font-size: .75rem; font-weight: 600; }
.badge-1 { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-2 { background: #1c1917; color: #fbbf24; border: 1px solid #92400e; }
.badge-3 { background: #1c1207; color: #fb923c; border: 1px solid #9a3412; }
.badge-4 { background: #1f0707; color: #f87171; border: 1px solid #991b1b; }
.badge-e { background: #1a0b2e; color: #c084fc; border: 1px solid #7e22ce; }

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white; border-radius: 14px;
    padding: 1.6rem 2rem; margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.3);
}
.page-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
.page-header p  { margin: .3rem 0 0; opacity: .8; font-size: .9rem; }

/* ── Inputs & widgets ── */
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}
div[data-testid="stExpander"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}
div[data-testid="stExpander"] summary {
    color: #e2e8f0 !important;
}

/* ── Dividers ── */
hr { border-color: #1e293b !important; }

/* ── Metric widget ── */
[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: .8rem 1rem;
}
[data-testid="stMetricValue"] { color: #818cf8 !important; }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
</style>
""", unsafe_allow_html=True)



def _load_page(filename: str):
    """Load a page module from the same directory using importlib (avoids streamlit name clash)."""
    here = os.path.dirname(__file__)
    path = os.path.join(here, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💼 Smart Credit\n### Orchestrator")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "📋 Invoice Queue", "⚡ Run Agent", "📜 Audit Log", "ℹ️ About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("AI-powered invoice follow-up\nengine · LangGraph + Groq")

# ── Route to the right page ───────────────────────────────────────────────────
page_map = {
    "🏠 Dashboard":    "page_dashboard.py",
    "📋 Invoice Queue":"page_invoices.py",
    "⚡ Run Agent":     "page_agent.py",
    "📜 Audit Log":    "page_audit.py",
    "ℹ️ About":        "page_about.py",
}

_load_page(page_map[page]).render()
