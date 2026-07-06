import streamlit as st
import streamlit.components.v1 as components

def inject_accessibility_css(font_size: str, high_contrast: bool):
    """
    Injects custom CSS overrides into the Streamlit app to adjust font scale and colors.
    """
    css_lines = []
    
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
        
    if high_contrast:
        css_lines.append("""
        <style>
            .stApp {
                background-color: #0f172a !important; /* Dark blue slate */
                color: #ffffff !important;
            }
            /* High contrast text elements */
            p, span, li, h1, h2, h3, label {
                color: #f8fafc !important;
            }
            /* Clear thick borders on input components */
            input, select, textarea {
                border: 2px solid #38bdf8 !important;
                background-color: #1e293b !important;
                color: #ffffff !important;
            }
        </style>
        """)
        
    if css_lines:
        full_css = "\n".join(css_lines)
        st.markdown(full_css, unsafe_allow_html=True)


def text_to_speech_component(text: str, auto_speak: bool = False):
    """
    Renders an HTML/JS widget that exposes a button triggering the browser's speechSynthesis.
    It reads out the text on demand, working client-side without any server-side delay.
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
