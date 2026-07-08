"""Fan experience portal UI component.

This module renders the multilingual RAG stadium assistant, text-to-speech feedback,
and the green carbon scorecard for spectators.
"""

import time
import streamlit as st
from stadium_ops.core.security import (
    sanitize_input,
    detect_prompt_injection,
    enforce_length_limit,
    is_rate_limited,
    log_security_violation
)
from stadium_ops.core.exceptions import SecurityValidationError
from stadium_ops.services.assistant import StadiumAssistant
from stadium_ops.services.sustainability import SustainabilityService
from stadium_ops.utils.accessibility import text_to_speech_component


def render_fan_portal(
    selected_stadium: str, 
    assistant_service: StadiumAssistant, 
    auto_audio: bool
) -> None:
    """Renders the spectator companion portal and eco-scorecard interfaces.

    Args:
        selected_stadium: The name of the currently selected venue.
        assistant_service: The RAG assistant service instance.
        auto_audio: Boolean value dictating auto-audio TTS readback settings.
    """
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
                            
                            # Render output securely using standard Streamlit info box (eliminates XSS vectors)
                            st.info(f"🤖 **ArenaFlow Guide ({language}):**  \n\n{answer}")
                            
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
            
            # Render output securely using standard Streamlit success block (eliminates unsafe HTML)
            st.success(
                f"🌿 **Sustainability Scorecard**  \n\n"
                f"📉 **Carbon Saved:** {co2_saved} kg CO2  \n"
                f"🏆 **Eco Points Earned:** {points} pts  \n"
                f"🏅 **Badge awarded:** **{badge}**"
            )
            
            # Generate AI-based motivating tip
            with st.spinner("AI generating green recommendation tip..."):
                eco_tip = SustainabilityService.get_eco_tip(actions)
                st.info(f"💡 **AI Eco-Tip**: {eco_tip}")
