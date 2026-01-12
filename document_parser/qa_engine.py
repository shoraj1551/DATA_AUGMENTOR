from config.settings import get_model_for_feature, FREE_MODELS_BY_USE_CASE
from llm.client import get_client
import json
import time
import streamlit as st

def _call_with_retry(client, messages, response_format=None, max_retries=3):
    """
    Helper to call LLM with retry logic for 429 Rate Limits.
    Falls back to alternative model if primary fails.
    """
    # Get primary and alternative models
    feature_config = FREE_MODELS_BY_USE_CASE.get("document_parser")
    models_to_try = [feature_config["default"]] + feature_config.get("alternatives", [])
    
    last_exception = None

    for model in models_to_try:
        for attempt in range(max_retries):
            try:
                # Call API
                if response_format:
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        response_format=response_format
                    )
                else:
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages
                    )
                return response
            
            except Exception as e:
                error_str = str(e)
                last_exception = e
                # Check for Rate Limit (429)
                if "429" in error_str or "rate-limited" in error_str.lower():
                    wait_time = (2 ** attempt) + 1  # Exponential backoff: 2s, 3s, 5s...
                    print(f"Rate limit hit on {model}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Non-retryable error (e.g. context length exceeded), try next model immediately or raise
                    print(f"Error on {model}: {e}")
                    break # Break inner loop to try next model
        
        print(f"Model {model} failed after retries. Switching to fallback...")

    # If all models failed
    raise last_exception

def generate_story_highlights(text, image_data=None):
    """
    Generate top 5 key insights/story from the document.
    """
    client = get_client()
    
    system_prompt = """You are an expert Analyst. 
    Analyze the provided document content and extract the "Top 5 Key Information" as a Story.
    Focus on the most valuable, high-level insights.
    
    Output Format:
    Return a list of 5 strings.
    Example:
    [
      "Revenue grew by 20% compared to last year.",
      "New product launch is scheduled for Q3.",
      ...
    ]
    Return ONLY valid JSON."""
    
    user_content = []
    if text:
        user_content.append({"type": "text", "text": f"Document Content:\n{text[:500000]}"}) # Limit to avoid overflow
    
    try:
        response = _call_with_retry(
            client=client,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content if len(user_content) > 0 else "No content"}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        
        # Handle various return formats
        if isinstance(data, list): return data
        if "highlights" in data: return data["highlights"]
        if "story" in data: return data["story"]
        # Fallback
        return list(data.values())[0] if data else []
        
    except Exception as e:
        return [f"Server Busy (Rate Limit). Please try again in a moment. ({str(e)[:100]}...)"]

def ask_document_question(text, chat_history, question):
    """
    Q&A with the document using full context.
    """
    client = get_client()
    
    system_prompt = """You are a helpful Document Assistant.
    Answer the user's question based strictly on the provided document content.
    If the answer is not in the document, say so.
    Keep answers concise and professional."""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Inject Context
    if text:
         messages.append({"role": "user", "content": f"Reference Document Content:\n{text[:800000]}"})
         
    # Add Chat History
    for msg in chat_history:
        messages.append(msg)
        
    messages.append({"role": "user", "content": question})
    
    try:
        response = _call_with_retry(
            client=client,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ API Error: {str(e)[:200]}... (Please try again)"
