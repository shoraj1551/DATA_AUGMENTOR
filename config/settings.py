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

# 1. Try Streamlit Config (Secrets)
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        # Try exact match first, then lowercase
        OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
        if not OPENROUTER_API_KEY:
             OPENROUTER_API_KEY = st.secrets.get("openrouter_api_key")
             
        # Debug log for server console
        if OPENROUTER_API_KEY:
            print("INFO: Successfully loaded OPENROUTER_API_KEY from secrets.")
        else:
            print("INFO: Streamlit secrets found but no OPENROUTER_API_KEY detected.")
except Exception as e:
    print(f"INFO: Could not load secrets: {e}")
    pass

# 2. Try Environment if not found in secrets
if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Warning instead of crash if missing
if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY is not set. AI features will be disabled.")

def get_api_key():
    """
    Dynamically retrieve API Key from secrets or env.
    Preferred over static variable to avoid import-time issues.
    """
    global OPENROUTER_API_KEY
    
    # 1. Try static variable if already set
    if OPENROUTER_API_KEY:
        return OPENROUTER_API_KEY
        
    # 2. Try Secrets (Runtime check)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            key = st.secrets.get("OPENROUTER_API_KEY") or st.secrets.get("openrouter_api_key")
            if key: 
                OPENROUTER_API_KEY = key
                return key
    except:
        pass
        
    # 3. Try Environment
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        OPENROUTER_API_KEY = key
    return key


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
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct",
            "mistralai/mistral-7b-instruct"
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
        ],
    },


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
        ],
    },
    # ===============================
    # 6️⃣ Document Parser & Intelligence
    # ===============================
    "document_parser": {
        "default": "google/gemini-2.0-flash-exp:free",
        "alternatives": [
            "meta-llama/llama-3.1-8b-instruct",
            "qwen/qwen-2.5-7b-instruct"
        ],
        "why": [
            "1M token context window perfect for large PDFs/Docs",
            "Native multimodal support for images/charts",
            "Strong reasoning for Q&A and extraction"
        ]
    },
    
    # ===============================
    # 7️⃣ Analytics & Insights Tools
    # ===============================
    "data_profiling": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct",
            "mistralai/mistral-7b-instruct"
        ]
    },
    "dq_rules": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    "requirement_interpreter": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    "knowledge_base": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    
    # ===============================
    # 8️⃣ Sales Intelligence Tools
    # ===============================
    "company_intelligence": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    "selling_opportunity": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    "strategic_sales": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    "contact_intelligence": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    "insurance_claims": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    
    # ===============================
    # 9️⃣ OCR Intelligence
    # ===============================
    "ocr_intelligence": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct"
        ]
    },
    
    # ===============================
    # 🔟 Company Intelligence
    # ===============================
    "company_intelligence": {
        "default": "meta-llama/llama-3.1-8b-instruct",
        "alternatives": [
            "qwen/qwen-2.5-7b-instruct",
            "mistralai/mistral-7b-instruct"
        ]
    }
}

def get_model_for_feature(feature_name: str) -> str:
    """
    Get the default model ID for a specific feature.
    
    Args:
        feature_name: Feature name (e.g., 'data_augmentor', 'code_review', etc.)
        
    Returns:
        str: Model ID string (e.g. 'meta-llama/llama-3.1-8b-instruct')
    """
    feature_config = FREE_MODELS_BY_USE_CASE.get(feature_name)
    if not feature_config:
        # Fallback to a safe default if feature not found
        return "meta-llama/llama-3.1-8b-instruct"
    
    return feature_config["default"]


def get_model_with_fallback(feature_name: str, attempt: int = 0) -> str:
    """
    Get model for feature with automatic fallback on rate limits.
    
    Args:
        feature_name: Feature name
        attempt: Current attempt number (0 = default, 1+ = alternatives)
        
    Returns:
        str: Model ID to try
    """
    feature_config = FREE_MODELS_BY_USE_CASE.get(feature_name)
    if not feature_config:
        return "meta-llama/llama-3.1-8b-instruct"
    
    # First attempt: use default
    if attempt == 0:
        return feature_config["default"]
    
    # Subsequent attempts: use alternatives
    alternatives = feature_config.get("alternatives", [])
    if attempt - 1 < len(alternatives):
        return alternatives[attempt - 1]
    
    # Exhausted all options, return last alternative
    return alternatives[-1] if alternatives else feature_config["default"]


def get_all_alternative_models(feature_name: str) -> list:
    """
    Get all alternative models for a feature (for retry logic).
    
    Returns:
        list: [default, alt1, alt2, ...]
    """
    feature_config = FREE_MODELS_BY_USE_CASE.get(feature_name)
    if not feature_config:
        return ["meta-llama/llama-3.1-8b-instruct"]
    
    models = [feature_config["default"]]
    models.extend(feature_config.get("alternatives", []))
    return models


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
    if not OPENROUTER_API_KEY:
        return False

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )

        # Lightweight authenticated request
        client.models.list()
        return True

    except Exception as e:
        print(f"API Validation Failed: {e}")
        return False