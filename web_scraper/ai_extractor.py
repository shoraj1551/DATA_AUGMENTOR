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
    Suggest website URLs based on data requirements using LLM.
    Returns top 3 options with access tips and permission checks.
    
    Args:
        requirements (str): User's description of needed data.
        
    Returns:
        list: List of dicts [{"url", "reason", "access_tips", "is_allowed"}]
    """
    from web_scraper.validator import is_scraping_allowed
    
    # Use the Web Scraper model (Gemini 2.0 Flash) as it has better world knowledge/search capabilities than Llama
    model = get_model_for_feature("web_scraper") 
    client = get_client()

    system_prompt = """You are a resourceful Data Engineer.
Your goal is to find the Top 3 BEST URLs to scrape the requested data.

RULES:
1. **Always Return Sources**: Never say "I cannot find". If specific URL is unknown, provide the top-level domain search URL or the closest category page.
2. **Prioritize Accessibility**: Prefer static HTML sites (Wikipedia, Govt portals) over heavy JS apps.
3. **Handle Blocking**: If a site blocks scrapers (like LinkedIn/Twitter), you MUST still suggest it but mark it as "Hard/Blocked" in the reason.

JSON FORMAT:
Return a JSON object with a key "suggestions" containing a list.
Example:
{
  "suggestions": [
    {
      "url": "https://www.wikipedia.org/wiki/List_of_companies",
      "reason": "High quality static database",
      "access_tips": "None required"
    },
    {
      "url": "https://twitter.com/search?q=data",
      "reason": "Real-time data but requires login",
      "access_tips": "Requires Authentication Headers"
    }
  ]
}"""

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
        
        content = response.choices[0].message.content
        data = json.loads(content)
        suggestions = data.get("suggestions", [])
        
        # Enrich with permission check
        for item in suggestions:
            # Default to False if url missing
            url = item.get("url", "")
            if url:
                item["is_allowed"] = is_scraping_allowed(url)
            else:
                item["is_allowed"] = False
                
        return suggestions

    except Exception as e:
        return [{"url": "", "reason": f"Error: {str(e)}", "access_tips": "None", "is_allowed": False}]
