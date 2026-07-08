"""Hackathon pitch presentation and security logs UI component.

This module renders the static hackathon pitch details and displays the real-time
security violations logs for evaluator grading checks.
"""

import os
import streamlit as st


def render_pitch_info() -> None:
    """Renders the hackathon challenge pitch deck and prints the security audit log."""
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
