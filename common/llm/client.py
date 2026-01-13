from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, get_all_alternative_models
import time

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


def call_with_fallback(feature_name: str, messages: list, **kwargs):
    """
    Call LLM with automatic fallback to alternative models on rate limits.
    
    Args:
        feature_name: Feature name to get models from config
        messages: Chat messages
        **kwargs: Additional arguments for chat.completions.create
        
    Returns:
        Response from successful model call
        
    Raises:
        Exception: If all models fail
    """
    client = get_client()
    models = get_all_alternative_models(feature_name)
    
    last_error = None
    for i, model in enumerate(models):
        try:
            # Add small delay between retries (except first attempt)
            if i > 0:
                time.sleep(0.5)
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response
            
        except Exception as e:
            error_str = str(e)
            last_error = e
            
            # Check if it's a rate limit error
            if "429" in error_str or "rate limit" in error_str.lower():
                # Try next model
                if i < len(models) - 1:
                    print(f"Rate limit hit on {model}, trying alternative: {models[i+1]}")
                    continue
                else:
                    # No more alternatives
                    raise Exception(f"All models exhausted. Last error: {error_str}")
            else:
                # Not a rate limit error, raise immediately
                raise e
    
    # Should not reach here, but just in case
    raise last_error if last_error else Exception("Unknown error in call_with_fallback")
