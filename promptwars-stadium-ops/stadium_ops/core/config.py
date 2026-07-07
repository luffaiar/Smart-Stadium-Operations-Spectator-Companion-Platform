"""Configuration loaders and constant variables.

This module provides tools to load API credentials securely from host environments
or Streamlit secrets vaults with local file-existence fallback guards.
"""

import os
from typing import List
import streamlit as st

DEFAULT_STADIUM: str = "MetLife Stadium"
SUPPORTED_STADIUMS: List[str] = ["MetLife Stadium", "Estadio Azteca", "BC Place"]

def get_gemini_api_key() -> str:
    """Retrieves the Google Gemini API Key from active environment channels.

    First checks environmental variables, then falls back to Streamlit
    secrets only if the file physically exists on the disk, bypassing warnings.

    Returns:
        The API key string or empty string if not configured.
    """
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
    except (AttributeError, KeyError, FileNotFoundError):
        pass
    
    return ""
