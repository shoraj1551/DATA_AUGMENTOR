import os
from pathlib import Path

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    print(f"[DEBUG] Looking for .env file at: {env_path}")
    print(f"[DEBUG] .env file exists: {env_path.exists()}")
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"[DEBUG] Loaded .env file successfully")
    else:
        print(f"[DEBUG] .env file not found, skipping")
except ImportError:
    # python-dotenv not installed, skip
    print("[DEBUG] python-dotenv not installed, skipping .env loading")
    pass

# OpenRouter API Configuration
# Priority: 1. Streamlit secrets, 2. .env file, 3. Environment variable
try:
    import streamlit as st
    # Try Streamlit secrets first, then fall back to environment
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    print(f"[DEBUG] API Key from st.secrets or os.getenv: {OPENROUTER_API_KEY[:20] if OPENROUTER_API_KEY else 'None'}...")
except:
    # Not running in Streamlit, use environment variable
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    print(f"[DEBUG] API Key from os.getenv (no Streamlit): {OPENROUTER_API_KEY[:20] if OPENROUTER_API_KEY else 'None'}...")

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set. Please configure it in .env, .streamlit/secrets.toml or environment variables.")
else:
    print(f"[DEBUG] Final API Key loaded: {OPENROUTER_API_KEY[:20]}... (length: {len(OPENROUTER_API_KEY)})")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-4o-mini"
DEFAULT_ROWS = 50
MAX_ROWS = 1000

# Cache settings
CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_MAX_SIZE = 100  # Maximum number of cached responses
