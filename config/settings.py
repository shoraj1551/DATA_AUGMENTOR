import os
from pathlib import Path

# -------------------------------------------------------
# Load .env for local development (safe to ignore in prod)
# -------------------------------------------------------
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv not installed
    pass


# -------------------------------------------------------
# Load OpenRouter API Key
# Priority:
# 1. Streamlit secrets
# 2. Environment variable
# -------------------------------------------------------
OPENROUTER_API_KEY = None

try:
    import streamlit as st
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
except Exception:
    # Not running in Streamlit
    pass

if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing. "
        "Set it in .streamlit/secrets.toml or as an environment variable."
    )


# -------------------------------------------------------
# OpenRouter / Model Configuration
# -------------------------------------------------------
# -------------------------------------------------------
# OpenRouter / Model Configuration
# -------------------------------------------------------
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Free models configuration by use case
FREE_MODELS_BY_USE_CASE = {
    # ================================
    # 1️⃣ DataAugmentor (Core)
    # ================================
    "data_augmentor": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct",
            "mistralai/mistral-7b-instruct"
        ],
        "why": [
            "Strong structured JSON output",
            "Good schema following",
            "Handles tabular data reasoning well",
            "Stable for synthetic data, PII masking, edge cases"
        ]
    },

    # ================================
    # 2️⃣ File Comparison (Analytics)
    # ================================
    # Using data_augmentor models for now as requirements are similar
    "file_comparison": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": ["qwen/qwen-2.5-7b-instruct"]
    },

    # ================================
    # 3️⃣ Code Review
    # ================================
    "code_review": {
        "default": "mistralai/mistral-7b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ],
        "why": [
            "Trained heavily on code",
            "Strong static analysis capabilities",
            "Good at identifying edge cases and risks",
            "Low verbosity, precise feedback"
        ]
    },

    # ================================
    # 4️⃣ Delivery Intelligence
    # ================================
    "delivery_intelligence": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ],
        "why": [
            "Excellent planning and reasoning",
            "Handles epics → stories → tasks well",
            "Good at effort estimation & breakdowns",
            "Stable long-context performance"
        ]


    # ================================
    # 5️⃣ Web Data Scraper
    # ================================
    "web_scraper": {
        "default": "google/gemini-2.0-flash-exp:free",
        "alternatives": [
            "google/gemini-2.0-flash-thinking-exp:free"
        ],
        "why": [
            "Massive context window (1M tokens) for HTML parsing",
            "Excellent at converting unstructured text to JSON",
            "Fast inference speed for real-time scraping",
            "Free tier availability"
        ]
    }
}

def get_model_for_feature(feature_name: str) -> str:
    """
    Get the default model ID for a specific feature.
    
    Args:
        feature_name: One of 'data_augmentor', 'code_review', 'delivery_intelligence', 'file_comparison'
        
    Returns:
        str: Model ID string (e.g. 'meta-llama/llama-3.1-8b-instruct')
    """
    feature_config = FREE_MODELS_BY_USE_CASE.get(feature_name)
    if not feature_config:
        # Fallback to a safe default if feature not found
        return "meta-llama/llama-3.1-8b-instruct"
    
    return feature_config["default"]

DEFAULT_ROWS = 50
MAX_ROWS = 1000


# -------------------------------------------------------
# Cache Configuration
# -------------------------------------------------------
CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_MAX_SIZE = 100


# -------------------------------------------------------
# Runtime API Key Validation (NO LENGTH CHECKS)
# -------------------------------------------------------
def validate_openrouter_api_key():
    """
    Validate OpenRouter API key by making a lightweight authenticated call.
    This is the ONLY reliable validation method.
    """
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )

        # Lightweight authenticated request
        client.models.list()

    except Exception as e:
        raise RuntimeError(
            "OPENROUTER_API_KEY is present but invalid, expired, or unauthorized."
        ) from e


# Validate once at startup
validate_openrouter_api_key()