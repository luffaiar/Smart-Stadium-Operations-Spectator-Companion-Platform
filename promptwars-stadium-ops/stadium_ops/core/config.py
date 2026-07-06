import os
import streamlit as st

# Secure retrieval of the Gemini API Key
def get_gemini_api_key() -> str:
    # 1. Try environment variable
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        return api_key
    
    # 2. Try Streamlit secrets (only if the secrets.toml file actually exists to prevent warning blocks)
    try:
        local_secrets = os.path.join(".streamlit", "secrets.toml")
        home_secrets = os.path.expanduser(os.path.join("~", ".streamlit", "secrets.toml"))
        if os.path.exists(local_secrets) or os.path.exists(home_secrets):
            if "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    
    return ""

DEFAULT_STADIUM = "MetLife Stadium"
SUPPORTED_STADIUMS = ["MetLife Stadium", "Estadio Azteca", "BC Place"]
