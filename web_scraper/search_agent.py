"""
Web Search Agent Module using DuckDuckGo
"""
from duckduckgo_search import DDGS
import time

def search_web(query, max_results=5):
    """
    Perform a real web search using DuckDuckGo.
    
    Args:
        query (str): Search query.
        max_results (int): Number of results to return.
        
    Returns:
        list: List of dicts [{'title', 'href', 'body'}]
    """
    try:
        results = []
        with DDGS() as ddgs:
            # Simple text search
            # region="wt-wt" (global), safesearch="off", timelimit=None
            ddgs_gen = ddgs.text(query, max_results=max_results)
            
            for r in ddgs_gen:
                results.append(r)
                
        return results
    except Exception as e:
        print(f"Search Agent Error: {str(e)}")
        # Fallback empty list so the LLM handles it gracefully
        return []

def get_formatted_search_results(query):
    """Refined search that returns a formatted string context for LLM"""
    raw_results = search_web(query, max_results=5)
    
    if not raw_results:
        return "No real-time web search results found."
        
    context = "Real-Time Web Search Results:\n"
    for i, res in enumerate(raw_results):
        context += f"{i+1}. Title: {res.get('title')}\n   URL: {res.get('href')}\n   Snippet: {res.get('body')}\n\n"
        
    return context
