from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

# Lazy client initialization to ensure API key is loaded from Streamlit secrets
_client = None

def get_client():
    """Get or create OpenAI client with lazy initialization."""
    global _client
    if _client is None:
        # Re-import to get latest API key (in case Streamlit secrets loaded after initial import)
        from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL
        _client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
    return _client
