from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

# Lazy client initialization to ensure API key is loaded from Streamlit secrets
_client = None

def get_client():
    """Get or create OpenAI client with lazy initialization."""
    global _client
    if _client is None:
        # Re-import to get latest API key
        import os
        from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
        
        # Double check if key is loaded, if not try to get from env again
        api_key = OPENROUTER_API_KEY
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
            
        if not api_key:
             raise ValueError("API Key is missing. Please check .streamlit/secrets.toml or OPENROUTER_API_KEY environment variable.")

        _client = OpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL
        )
    return _client
