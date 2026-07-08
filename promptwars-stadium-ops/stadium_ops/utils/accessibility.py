"""Accessibility styles, theme controllers, and browser audio reader utilities.

This module provides tools to dynamically inject CSS styles into the Streamlit app
to handle font sizing, high-contrast Slate themes, color blindness correction matrices,
vestibular reduced-motion profiles, and browser speech rendering.
"""

import streamlit as st
import streamlit.components.v1 as components

def inject_accessibility_css(
    font_size: str,
    high_contrast: bool,
    color_blind_mode: str = "Standard",
    reduced_motion: bool = False
) -> None:
    """Injects custom CSS styles and SVG filters into Streamlit to adapt the UI.

    Args:
        font_size: Standard, Large, or Extra Large text sizing.
        high_contrast: If True, activates dark slate high-contrast backgrounds.
        color_blind_mode: Color filters (Standard, Protanopia, Deuteranopia).
        reduced_motion: If True, disables transitions and scroll-behavior.
    """
    css_lines = []
    
    # 1. Text Sizing CSS Injections
    if font_size == "Large":
        css_lines.append("""
        <style>
            html, body, p, span, li, button, input, select, textarea, label {
                font-size: 18px !important;
            }
            h1 { font-size: 32px !important; }
            h2 { font-size: 26px !important; }
            h3 { font-size: 21px !important; }
        </style>
        """)
    elif font_size == "Extra Large":
        css_lines.append("""
        <style>
            html, body, p, span, li, button, input, select, textarea, label {
                font-size: 22px !important;
            }
            h1 { font-size: 38px !important; }
            h2 { font-size: 32px !important; }
            h3 { font-size: 26px !important; }
        </style>
        """)
        
    # 2. High Contrast Theme Injections
    if high_contrast:
        css_lines.append("""
        <style>
            .stApp {
                background-color: #0f172a !important;
                color: #ffffff !important;
            }
            p, span, li, h1, h2, h3, label {
                color: #f8fafc !important;
            }
            input, select, textarea {
                border: 2px solid #38bdf8 !important;
                background-color: #1e293b !important;
                color: #ffffff !important;
            }
        </style>
        """)
        
    # 3. Reduced Motion CSS
    if reduced_motion:
        css_lines.append("""
        <style>
            *, *::before, *::after {
                animation-delay: -1ms !important;
                animation-duration: 1ms !important;
                animation-iteration-count: 1 !important;
                background-attachment: initial !important;
                scroll-behavior: auto !important;
                transition-duration: 0s !important;
                transition-delay: 0s !important;
            }
        </style>
        """)
        
    # Inject core styling sheets
    if css_lines:
        full_css = "\n".join(css_lines)
        st.markdown(full_css, unsafe_allow_html=True)
        
    # 4. Color-Blindness SVG Matrix Injections
    if color_blind_mode == "Protanopia":
        # Red-blind correction matrix
        st.markdown(
            """
            <svg style="display:none">
              <filter id="protanopia-filter">
                <feColorMatrix type="matrix" values="0.567, 0.433, 0, 0, 0, 0.558, 0.442, 0, 0, 0, 0, 0.242, 0.758, 0, 0, 0, 0, 0, 1, 0"/>
              </filter>
            </svg>
            <style>
              html, body, .stApp {
                filter: url(#protanopia-filter) !important;
              }
            </style>
            """,
            unsafe_allow_html=True
        )
    elif color_blind_mode == "Deuteranopia":
        # Green-blind correction matrix
        st.markdown(
            """
            <svg style="display:none">
              <filter id="deuteranopia-filter">
                <feColorMatrix type="matrix" values="0.625, 0.375, 0, 0, 0, 0.7, 0.3, 0, 0, 0, 0, 0.3, 0.7, 0, 0, 0, 0, 0, 1, 0"/>
              </filter>
            </svg>
            <style>
              html, body, .stApp {
                filter: url(#deuteranopia-filter) !important;
              }
            </style>
            """,
            unsafe_allow_html=True
        )


def text_to_speech_component(text: str, auto_speak: bool = False) -> None:
    """Renders a client-side audio button triggers browser speechSynthesis.

    Args:
        text: The text string to read aloud.
        auto_speak: If True, reads out the text on page load delay.
    """
    if not text:
        return
        
    # Escape quotes and formatting for Javascript strings safely
    escaped_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    
    html_code = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; display: flex; align-items: center; gap: 8px;">
        <button id="speak-btn" style="
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            transition: background-color 0.2s;
        " onmouseover="this.style.backgroundColor='#1d4ed8'" onmouseout="this.style.backgroundColor='#2563eb'">
            🔊 Listen to Response (Audio)
        </button>
    </div>
    <script>
        const btn = document.getElementById('speak-btn');
        function speak() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance('{escaped_text}');
                utterance.rate = 1.0;
                window.speechSynthesis.speak(utterance);
            }} else {{
                alert("Speech synthesis not supported in this browser.");
            }}
        }}
        btn.addEventListener('click', speak);
        if ({'true' if auto_speak else 'false'}) {{
            setTimeout(speak, 500);
        }}
    </script>
    """
    components.html(html_code, height=45)
