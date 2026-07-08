"""ArenaFlow 2026: FIFA World Cup Smart Stadium Operations Dashboard.

This is the main entry point of the Streamlit application. It coordinates page layouts,
injects accessibility profiles, sets up state management parameters, and routes
visual layouts to component renderers.
"""

import os
import sys
import streamlit as st

# Ensure the parent directory of this script is in sys.path so 'stadium_ops' imports resolve correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure Streamlit page layout and theme metadata
st.set_page_config(
    page_title="ArenaFlow 2026 - Smart Stadium Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

from stadium_ops.core.config import SUPPORTED_STADIUMS
from stadium_ops.services.assistant import StadiumAssistant
from stadium_ops.utils.accessibility import inject_accessibility_css
from stadium_ops.components import render_staff_hub, render_fan_portal, render_pitch_info

# Initialize services (cached for maximum performance)
@st.cache_resource
def load_assistant_service() -> StadiumAssistant:
    """Instantiates and caches the core StadiumAssistant service.

    Returns:
        A cached instance of StadiumAssistant.
    """
    return StadiumAssistant()

assistant_service = load_assistant_service()

# ----------------- SESSION STATE SETUP -----------------
if "incidents" not in st.session_state:
    st.session_state.incidents = []

if "green_actions" not in st.session_state:
    st.session_state.green_actions = []

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

if "request_timestamps" not in st.session_state:
    st.session_state.request_timestamps = []

# Persistent Volunteer Roster for Operations tracking
if "volunteer_roster" not in st.session_state:
    st.session_state.volunteer_roster = [
        {"name": "Marta Silva", "sector": "Zone 100 Seats", "role": "Medical Assistant", "status": "Available"},
        {"name": "Ahmed Khan", "sector": "Gate A Entrance", "role": "Navigational Guide", "status": "Available"},
        {"name": "Pierre Dupont", "sector": "Food court East", "role": "Facilities support", "status": "Available"},
        {"name": "John Smith", "sector": "VIP Lounge", "role": "Venue Security Assistant", "status": "Available"},
        {"name": "Sarah Connor", "sector": "Zone 200 Seats", "role": "General Support", "status": "Available"},
        {"name": "Luis Gomez", "sector": "Gate B Concourse", "role": "Medical Assistant", "status": "Available"}
    ]

# ----------------- SIDEBAR CONFIG -----------------
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="color: #2563eb; font-size: 28px; margin-bottom: 5px;">⚽ ArenaFlow 2026</h1>
        <p style="font-size: 13px; color: #64748b;">FIFA World Cup 2026 Operations & Experience</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# 1. API Configuration
st.sidebar.subheader("🔑 API Key Setup")
api_key_input = st.sidebar.text_input(
    "Google Gemini API Key",
    value=st.session_state.gemini_api_key,
    type="password",
    help="Provide your Google Gemini API Key to enable live LLM generation. Leave empty to use local fallback engines."
)
if api_key_input != st.session_state.gemini_api_key:
    st.session_state.gemini_api_key = api_key_input
    os.environ["GEMINI_API_KEY"] = api_key_input

# 2. General Settings
st.sidebar.subheader("🏟️ Stadium Selection")
selected_stadium = st.sidebar.selectbox(
    "Select Target Venue",
    options=SUPPORTED_STADIUMS,
    index=0
)

# 3. Accessibility Controls
st.sidebar.subheader("⚙️ Accessibility & UI settings")
font_size = st.sidebar.selectbox(
    "Text Size",
    options=["Standard", "Large", "Extra Large"],
    index=0
)
high_contrast = st.sidebar.checkbox("High Contrast Mode", value=False)

color_blind_mode = st.sidebar.selectbox(
    "Color Blindness Adaptation",
    options=["Standard", "Protanopia", "Deuteranopia"],
    index=0,
    help="Shift screen color scales using SVG matrices to assist color-blind spectators."
)

reduced_motion = st.sidebar.checkbox(
    "Reduced Motion",
    value=False,
    help="Disable CSS layouts transition times and keyframe animations."
)

auto_audio = st.sidebar.checkbox("Auto-play Audio Feedback", value=False)

# Inject custom accessibility styles dynamically based on sidebar controls
inject_accessibility_css(font_size, high_contrast, color_blind_mode, reduced_motion)

st.sidebar.markdown("---")

# 4. Live Volunteer Roster Display (Neutralizes unsafe HTML tags completely)
st.sidebar.subheader("👥 Active Volunteers Roster")
for v in st.session_state.volunteer_roster:
    badge = "🟢" if v["status"] == "Available" else "🔴"
    st.sidebar.markdown(
        f"{badge} **{v['name']}** ({v['role']})  \n"
        f"📍 Sector: {v['sector']} | status: **{v['status']}**"
    )

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Hackathon Evaluator Tip**:\n"
    "This app will work offline even without an API key by falling back to local heuristic engines."
)

# ----------------- MAIN INTERFACE -----------------
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; color: white;">
        <h1 style="margin: 0; font-size: 34px; font-weight: 800; letter-spacing: -0.5px;">ArenaFlow 2026 Hub</h1>
        <p style="margin: 5px 0 0 0; font-size: 16px; opacity: 0.9;">Smart Stadium Operations & Spectator Companion Platform</p>
    </div>
    """,
    unsafe_allow_html=True
)

tab_staff, tab_fan, tab_info = st.tabs([
    "🛡️ Staff Operations Hub", 
    "⚽ Fan Portal & RAG Portal", 
    "ℹ️ Hackathon Project Pitch"
])

# Route each tab rendering to its decoupled UI component function
with tab_staff:
    render_staff_hub(selected_stadium)

with tab_fan:
    render_fan_portal(selected_stadium, assistant_service, auto_audio)

with tab_info:
    render_pitch_info()
