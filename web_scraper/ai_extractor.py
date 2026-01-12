from config.settings import get_model_for_feature
from llm.client import get_client
import json

def extract_structured_data(html_content, url=""):
    """
    Use LLM to extract structured data from raw HTML content.
    
    Args:
        html_content (str): The raw HTML string.
        url (str): The source URL context.
        
    Returns:
        list: A list of dictionaries representing the extracted structured data.
    """
    model = get_model_for_feature("web_scraper")
    client = get_client()

    # Truncate HTML if extremely large (approx 100k chars is safe for large context models like gemini-flash)
    # Gemini 2.0 Flash has 1M context, so we can be generous.
    safe_content = html_content[:200000] 

    system_prompt = """You are an expert web scraper and data extractor. 
Your goal is to analyze the provided HTML content and extract the primary structured data into a JSON list.
1. Identify the main list of items on the page (e.g., products, articles, companies, jobs).
2. For each item, extract relevant fields (title, price, date, link, description, etc.).
3. If no clear list exists, extract the main entity information.
4. Output ONLY valid JSON array. No markdown formatting."""

    user_prompt = f"""
    URL: {url}
    
    HTML Content:
    {safe_content}
    
    Extract the main structured data as a JSON list.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON
        data = json.loads(content)
        
        # Handle if wrapped in a key like "items" or returned as list directly
        if isinstance(data, dict):
            # Return the first list value found, or the dict itself in a list
            for key, val in data.items():
                if isinstance(val, list):
                    return val
            return [data]
        elif isinstance(data, list):
            return data
        else:
            return []

    except Exception as e:
        raise Exception(f"AI Extraction Failed: {str(e)}")


def suggest_website_source(requirements):
    """
    Suggest a website URL based on data requirements using LLM.
    
    Args:
        requirements (str): User's description of needed data.
        
    Returns:
        dict: {"url": "...", "reason": "..."}
    """
    # Use a reasoning model for this
    model = get_model_for_feature("delivery_intelligence") # Llama 3.1 is good for general knowledge
    client = get_client()

    system_prompt = """You are a helpful data assistant. 
Based on the user's data requirements, suggest the SINGLE BEST public website URL to scrap this data from.
Prefer clean, static websites (like Wikipedia, government sites, public datasets) over complex dynamic apps.
verify the URL is likely to exist and contain the data.
Return ONLY a JSON object with keys: "url" (the full https link) and "reason" (short explanation)."""

    user_prompt = f"Data Requirements: {requirements}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"url": "", "reason": f"Error: {str(e)}"}
