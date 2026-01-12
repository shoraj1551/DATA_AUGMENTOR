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
    Suggest website URLs using an Agentic Workflow:
    1. Reason: Generate search query.
    2. Act: Search web using DBG.
    3. Synthesize: Pick best real links.
    """
    from web_scraper.validator import is_scraping_allowed
    from web_scraper.search_agent import get_formatted_search_results
    
    # Model 
    model = get_model_for_feature("web_scraper") 
    client = get_client()

    # --- Step 1: Generate Search Query ---
    query_prompt = f"Convert this data requirement into a single effective Google search query: '{requirements}'. Return ONLY the query string."
    try:
        q_response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": query_prompt}]
        )
        search_query = q_response.choices[0].message.content.strip().replace('"', '')
    except:
        search_query = requirements # Fallback

    # --- Step 2: Perform Real Web Search ---
    # This gets real URLs and snippets from DuckDuckGo
    search_context = get_formatted_search_results(search_query)

    # --- Step 3: Synthesize & Select ---
    system_prompt = """You are a clever Research Agent.
You have been given a list of REAL-TIME SEARCH RESULTS.
Your job is to select the Top 3 BEST sources from the results to satisfy the user's data requirement.

RULES:
1. **Factuality**: ONLY suggest URLs represented in the Search Results. Do not hallucinate new ones.
2. **Prioritization**: Prefer 'List' or 'Database' type pages over news articles.
3. **Blocking**: If a known blocked site (LinkedIn/Twitter) appears and is relevant, include it but mark as likely restricted.

JSON FORMAT (List of objects):
{
  "suggestions": [
    {
      "url": "https://actual-link-from-results...",
      "reason": "Contains a comprehensive table of...",
      "access_tips": "Static HTML, easy to scrape" 
    }
  ]
}"""

    user_prompt = f"""
    User Requirement: {requirements}
    
    Used Search Query: {search_query}
    
    {search_context}
    
    Select the best sources from the search results above.
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
        data = json.loads(content)
        suggestions = data.get("suggestions", [])
        
        # Enrich with permission check
        for item in suggestions:
            url = item.get("url", "")
            if url:
                item["is_allowed"] = is_scraping_allowed(url)
            else:
                item["is_allowed"] = False
                
        return suggestions

    except Exception as e:
        return [{"url": "", "reason": f"Agent Error: {str(e)}", "access_tips": "Try manual search", "is_allowed": False}]
