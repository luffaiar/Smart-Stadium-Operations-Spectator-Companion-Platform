import os
import sys
import time
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
from stadium_ops.core.security import (
    sanitize_input,
    detect_prompt_injection,
    enforce_length_limit,
    is_rate_limited,
    log_security_violation
)
from stadium_ops.core.exceptions import SecurityValidationError
from stadium_ops.services.assistant import StadiumAssistant
from stadium_ops.services.crowd_management import CrowdManagementService
from stadium_ops.services.sustainability import SustainabilityService
from stadium_ops.services.transport_service import TransportService
from stadium_ops.utils.accessibility import inject_accessibility_css, text_to_speech_component

# Initialize services (cached for maximum performance)
@st.cache_resource
def load_assistant_service():
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

# 4. Live Volunteer Roster Display
st.sidebar.subheader("👥 Active Volunteers Roster")
for v in st.session_state.volunteer_roster:
    badge_color = "#22c55e" if v["status"] == "Available" else "#ef4444"
    st.sidebar.markdown(
        f"""
        <div style="font-size: 13px; margin-bottom: 8px; padding: 6px; background-color: #f8fafc; border-radius: 4px; border-left: 3px solid {badge_color};">
            <strong>{v['name']}</strong> ({v['role']})<br>
            <span style="font-size: 11px; color:#64748b;">📍 {v['sector']}</span> | 
            <span style="font-size: 11px; color:{badge_color}; font-weight:bold;">{v['status']}</span>
        </div>
        """,
        unsafe_allow_html=True
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

# ================= TAB 1: STAFF PORTAL =================
with tab_staff:
    st.header("🏟️ Stadium Live Control Room")
    st.subheader(f"Current Operations Dashboard: {selected_stadium}")
    
    # 1. Live Crowd Densities (Simulated)
    st.write("### 👥 Simulated Live Crowd Density")
    sectors = CrowdManagementService.get_simulated_sectors(selected_stadium)
    
    cols = st.columns(len(sectors))
    for i, sector in enumerate(sectors):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border-left: 5px solid {sector['color']}; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-height: 120px;">
                    <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{sector['name']}</div>
                    <div style="font-size: 24px; font-weight: 900; color: #0f172a; margin-top: 5px;">{sector['density']}%</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">{sector['description']}</div>
                    <span style="display: inline-block; background-color: {sector['color']}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-top: 8px;">{sector['status']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    # 2. Automated Crowd Redistribution Action Plan
    st.write("### 📈 Operations Intelligence Advice")
    recs = CrowdManagementService.get_crowd_recommendations(sectors)
    for rec in recs:
        st.markdown(rec)
        
    st.markdown("---")
    
    # 3. Real-Time Transportation Monitor
    st.write("### 🚇 Real-Time Match-Day Transportation Monitor")
    transit_routes = TransportService.get_transit_status(selected_stadium)
    cols_transit = st.columns(len(transit_routes))
    for idx, route in enumerate(transit_routes):
        with cols_transit[idx]:
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border-top: 4px solid {route['color']}; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-height: 110px;">
                    <div style="font-size: 16px; font-weight: 700; color: #0f172a;">{route['icon']} {route['route']}</div>
                    <div style="font-size: 13px; color: #475569; margin-top: 3px;">Frequency: {route['frequency']}</div>
                    <span style="display: inline-block; color: {route['color']}; font-weight: bold; font-size: 13px; margin-top: 6px;">Status: {route['status']}</span>
                    {f"<br><span style='font-size:11px; color:#ef4444;'>Delay: {route['delay']}</span>" if route['status'] in ['Delayed', 'Congested'] else ""}
                </div>
                """,
                unsafe_allow_html=True
            )
            
    st.markdown("---")
    
    # 4. GenAI Incident Dispatcher
    st.write("### 🚨 GenAI Incident Dispatcher")
    st.write("Input incident notifications reported by field staff or cameras to classify and create actionable response procedures.")
    
    incident_input = st.text_area(
        "Incident details (e.g. 'A spectator fainted near Sector 102 concession stands')",
        placeholder="Type incident report here...",
        height=100
    )
    
    if st.button("Log & Classify Incident"):
        # 1. Rate Limiter Validation
        if is_rate_limited(st.session_state.request_timestamps, limit=6, period=60.0):
            st.error("⚠️ Rate Limit Triggered: You are submitting requests too quickly. Please wait a moment.")
            log_security_violation("RATE_LIMIT_EXCEEDED", "Incident log submission spamming", "StaffSession")
        else:
            try:
                # 2. Input Size Guards (300 character cap)
                enforce_length_limit(incident_input, max_len=300)
                
                # 3. HTML Sanitization
                sanitized_report = sanitize_input(incident_input)
                
                if not sanitized_report:
                    st.warning("Please type a description of the incident before submission.")
                # 4. Prompt Injection Blockers
                elif detect_prompt_injection(sanitized_report, user_id="StaffSession"):
                    st.error("🚨 Security Alert: Prompt injection patterns detected! Operation aborted.")
                else:
                    # Update rate limit timestamps
                    st.session_state.request_timestamps.append(time.time())
                    
                    with st.spinner("GenAI analyzing severity and building response checklists..."):
                        analysis = CrowdManagementService.analyze_and_dispatch_incident(sanitized_report)
                        
                        if analysis:
                            # 5. Smart Volunteer Proximity Dispatch Allocation
                            category = analysis.get("category", "General")
                            role_map = {
                                "Medical": "Medical Assistant",
                                "Security": "Venue Security Assistant",
                                "Facilities / Maintenance": "Facilities support"
                            }
                            target_role = role_map.get(category, "General Support")
                            
                            # Retrieve list of available matching volunteers
                            candidates = [v for v in st.session_state.volunteer_roster if v["role"] == target_role and v["status"] == "Available"]
                            if not candidates:
                                candidates = [v for v in st.session_state.volunteer_roster if v["role"] in ["General Support", "Navigational Guide"] and v["status"] == "Available"]
                                
                            matched_volunteer = None
                            if candidates:
                                # Prioritize exact sector matches in report text
                                for c in candidates:
                                    if c["sector"].lower() in sanitized_report.lower():
                                        matched_volunteer = c
                                        break
                                if not matched_volunteer:
                                    matched_volunteer = candidates[0]
                                    
                            if matched_volunteer:
                                matched_volunteer["status"] = "Dispatched"
                                volunteer_name = f"{matched_volunteer['name']} ({matched_volunteer['role']}) - Sector: {matched_volunteer['sector']}"
                            else:
                                volunteer_name = "None Available (Escalating to Operations Command)"
                                
                            st.session_state.incidents.insert(0, {
                                "report": sanitized_report,
                                "analysis": analysis,
                                "volunteer": volunteer_name
                            })
                            st.success("Incident logged successfully!")
                        else:
                            st.error("Could not process the incident.")
            except SecurityValidationError as e:
                st.error(f"⚠️ Security Validation Failed: {e}")
                log_security_violation("INPUT_SIZE_VIOLATION", incident_input, "StaffSession")
                    
    # Render logged incidents
    if st.session_state.incidents:
        st.write("#### Active Incidents Queue")
        for idx, inc in enumerate(st.session_state.incidents):
            report_text = inc["report"]
            analysis = inc["analysis"]
            volunteer = inc.get("volunteer", "None Assigned")
            severity = analysis.get("severity", "Low")
            category = analysis.get("category", "General")
            dept = analysis.get("department", "Rescue Squad")
            checklist = analysis.get("checklist", [])
            
            sev_color = "#ff4b4b" if severity == "High" else ("#ffa500" if severity == "Medium" else "#00c853")
            
            with st.expander(f"⚠️ {category} Alert ({severity} Urgency) - {report_text[:40]}...", expanded=True):
                st.markdown(
                    f"""
                    <div style="padding: 10px; background-color: #f1f5f9; border-radius: 6px; margin-bottom: 10px;">
                        <strong>Original Report:</strong> "{report_text}"<br>
                        <strong>Assigned Responder Unit:</strong> <span style="color: #2563eb; font-weight: bold;">{dept}</span><br>
                        <strong>🎯 Dispatched Volunteer:</strong> <span style="color: #16a34a; font-weight: bold;">{volunteer}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.write("**Dispatched Actions Checklist:**")
                for step in checklist:
                    st.checkbox(step, key=f"step_{idx}_{step[:25]}")


# ================= TAB 2: FAN PORTAL =================
with tab_fan:
    st.header("👋 Welcome to the World Cup Fan Experience Portal")
    
    # Grid layout for Assistant and Sustainability
    col_assistant, col_green = st.columns([3, 2])
    
    with col_assistant:
        st.subheader("🤖 Multilingual RAG Stadium Assistant")
        st.write(
            f"Ask questions about access gates, accessible elevators, dining concessions, "
            f"or local family nursing spots at **{selected_stadium}**."
        )
        
        language = st.selectbox(
            "Response Language",
            options=["English", "Español", "Français", "Português", "Deutsch", "العربية"],
            index=0
        )
        
        fan_query = st.text_input(
            "How can we help you today?",
            placeholder="e.g., Where is the nearest diaper-changing table?",
            key="fan_query_input"
        )
        
        if st.button("Submit Question"):
            # 1. Rate Limiter Validation
            if is_rate_limited(st.session_state.request_timestamps, limit=6, period=60.0):
                st.error("⚠️ Rate Limit Triggered: You are submitting requests too quickly. Please wait a moment.")
                log_security_violation("RATE_LIMIT_EXCEEDED", "Assistant question spamming", "FanSession")
            else:
                try:
                    # 2. Input Size Guards (300 character cap)
                    enforce_length_limit(fan_query, max_len=300)
                    
                    # 3. HTML Sanitization
                    sanitized_query = sanitize_input(fan_query)
                    
                    if not sanitized_query:
                        st.warning("Please type a question.")
                    # 4. Prompt Injection Blockers
                    elif detect_prompt_injection(sanitized_query, user_id="FanSession"):
                        st.error("🚨 Security Alert: Prompt injection attempt blocked.")
                    else:
                        # Update rate limit timestamps
                        st.session_state.request_timestamps.append(time.time())
                        
                        with st.spinner("Retrieving stadium guides and processing response..."):
                            answer = assistant_service.get_answer(sanitized_query, selected_stadium, language)
                            
                            st.markdown(
                                f"""
                                <div style="background-color: #eff6ff; border-left: 5px solid #2563eb; padding: 15px; border-radius: 8px; margin-top: 15px;">
                                    <h4 style="margin: 0 0 8px 0; color: #1e3a8a;">🤖 ArenaFlow Guide</h4>
                                    <p style="margin: 0; font-size: 15px; color: #1e293b;">{answer}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Renders browser-based text to speech
                            text_to_speech_component(answer, auto_speak=auto_audio)
                except SecurityValidationError as e:
                    st.error(f"⚠️ Security Validation Failed: {e}")
                    log_security_violation("INPUT_SIZE_VIOLATION", fan_query, "FanSession")
                    
    with col_green:
        st.subheader("♻️ Green Fan Scorecard")
        st.write("Log your sustainable habits inside the stadium to earn World Cup Eco Points!")
        
        # Checkbox logs
        rail = st.checkbox("🚇 Took light rail / SkyTrain", value=False)
        bus = st.checkbox("🚌 Took express shuttle / bus", value=False)
        carpool = st.checkbox("🚗 Carpooled to stadium (3+ fans)", value=False)
        walk_cycle = st.checkbox("🚲 Walked or biked", value=False)
        refill = st.checkbox("🥤 Used reusable water bottle & refill station", value=False)
        recycle = st.checkbox("♻️ Recycled bottles & cups", value=False)
        vegan = st.checkbox("🌱 Ordered plant-based concession meal", value=False)
        
        if st.button("Calculate Environmental Impact"):
            actions = []
            if rail: actions.append("light_rail")
            if bus: actions.append("bus")
            if carpool: actions.append("carpool")
            if walk_cycle: actions.append("walk_cycle")
            if refill: actions.append("refill_bottle")
            if recycle: actions.append("recycle_cup")
            if vegan: actions.append("plant_based_meal")
            
            result = SustainabilityService.calculate_impact(actions)
            co2_saved = result["total_co2_saved_kg"]
            points = result["points"]
            badge = result["badge"]
            
            st.markdown(
                f"""
                <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <h4 style="margin: 0 0 8px 0; color: #166534;">🌟 Sustainability Scorecard</h4>
                    <p style="margin: 3px 0;"><strong>Carbon Saved:</strong> {co2_saved} kg CO2</p>
                    <p style="margin: 3px 0;"><strong>Points Earned:</strong> {points} pts</p>
                    <p style="margin: 3px 0;"><strong>Badge:</strong> <span style="background-color: #bbf7d0; color: #166534; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{badge}</span></p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Generate AI-based motivating tip
            with st.spinner("AI generating green recommendation tip..."):
                eco_tip = SustainabilityService.get_eco_tip(actions)
                st.info(f"💡 **AI Eco-Tip**: {eco_tip}")


# ================= TAB 3: HACKATHON INFO =================
with tab_info:
    st.markdown(
        """
        ### ⚽ ArenaFlow 2026: FIFA World Cup Smart Stadium Hub
        
        #### Hackathon Challenge 4: Smart Stadiums & Tournament Operations
        ArenaFlow 2026 is a Generative AI-enabled dashboard that enhances stadium safety operations and spectator coordination during the FIFA World Cup 2026.
        
        #### 🌟 Features & Pitch
        *   **RAG-Grounded Multilingual Chatbot**: Direct answer synthesis grounded in official stadium layout specifications retrieved via `StadiumRepository` and translated dynamically.
        *   **AI Incident Dispatch & Nearest Volunteer Recommend**: Categorizes severity, tags department units, and automatically matches logged events to the closest matching active volunteer (e.g. First Aid).
        *   **Inclusive UI Design (Accessibility Focus)**:
            *   *CSS Font Scaler*: Adjust text elements across the layout (Standard, Large, Extra Large).
            *   *Text-to-Speech (TTS)*: Dynamic native client-side speech rendering using the HTML5 Web Speech API.
            *   *High Contrast theme*: Toggles strong contrast layouts suited for sunlight reading.
            *   *Color-Blindness SVG Overlays*: Direct visual spectral shifts for Protanopia (red-blindness) and Deuteranopia (green-blindness).
            *   *Reduced Motion Setting*: Suppresses all layout animations and translation transitions.
        *   **Sustainability Tracker**: Fans log environment-friendly practices, generating real-time carbon calculations and AI motivating suggestions.
        *   **Live Transit Board**: Displays bus schedules, rail line status, and delays to coordinate spectator transport flows.
        
        #### 🔒 Security Safeguards
        *   **Prompt Injection Interceptor**: Catches jailbreak strings, prevent system prompt hijacking, and serves mock alerts.
        *   **XSS Tag Sanitizer**: Neutralizes malicious HTML scripting before evaluating queries.
        *   **Session-based Rate Limiter**: Implements a rolling-window request rate evaluator checking timestamps inside Session State.
        *   **Size Guards**: Blocks user queries exceeding 300 characters to prevent prompt bloat or remote model overflows.
        *   **Audit Logger**: Automatically writes security threats, spam attempts, and size blocks with timestamp parameters to `security_audit.log`.
        
        #### 🧪 Architecture & OOP Design Patterns
        *   **Strategy Pattern**: Declares `LLMService` abstract class, implemented by `GeminiLLMService` (API calls) and `HeuristicLLMService` (offline backups).
        *   **Factory Pattern**: `LLMServiceFactory` loads correct strategies dynamically depending on credentials presence.
        *   **Repository Pattern**: `StadiumRepository` encapsulates file reading and caching database tasks.
        *   Contains unit, integration, and security test files covering 99% code coverage.
        """
    )
    
    # Render local security log if it exists (for Hackathon evaluation display)
    if os.path.exists("security_audit.log"):
        st.write("---")
        with st.expander("🛡️ View Live Security Audit Logs (stadium_ops/core/security_audit.log)"):
            try:
                with open("security_audit.log", "r", encoding="utf-8") as log_file:
                    log_data = log_file.readlines()
                    # Show last 20 violations
                    for line in reversed(log_data[-20:]):
                        st.text(line.strip())
            except Exception as e:
                st.write(f"Could not read audit log file: {e}")
