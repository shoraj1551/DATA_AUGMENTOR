import os

# OpenRouter API Configuration
# Try to load from Streamlit secrets first (for Streamlit app)
# Fall back to environment variable (for Flask app)
try:
    import streamlit as st
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
except:
    # Not running in Streamlit, use environment variable
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set. Please configure it in .streamlit/secrets.toml or environment variables.")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-4o-mini"
DEFAULT_ROWS = 50
MAX_ROWS = 1000

# Cache settings
CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_MAX_SIZE = 100  # Maximum number of cached responses
