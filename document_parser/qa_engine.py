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
    
    CRITICAL INSTRUCTIONS:
    1. Returns EXACTLY 5 bullet points. No more, no less.
    2. Focus on the most valuable, high-level insights.
    3. Output MUST be a valid JSON list of strings.
    
    Output Format Example:
    ["Insight 1", "Insight 2", "Insight 3", "Insight 4", "Insight 5"]
    """
    
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
        
        content = response.choices[0].message.content
        
        # Robust JSON Parsing
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: Try to find list in string if JSON wrapping failed (common with smaller models)
            import re
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                return ["Error: Could not parse AI response."]

        # Handle various return formats
        highlights = []
        if isinstance(data, list): 
            highlights = data
        elif isinstance(data, dict):
            # Check for common keys
            for key in ["highlights", "story", "points", "insights"]:
                if key in data and isinstance(data[key], list):
                    highlights = data[key]
                    break
            # If no key matched, try first list value
            if not highlights:
                 first_list = next((v for v in data.values() if isinstance(v, list)), [])
                 highlights = first_list

        # STRICTLY ENFORCE LIMIT
        return highlights[:5] if highlights else []
        
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
