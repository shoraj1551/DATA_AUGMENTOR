"""
Web Search Agent Module using DuckDuckGo
"""
from duckduckgo_search import DDGS
import time

def search_web(query, max_results=5):
    """
    Perform a real web search using DuckDuckGo.
    """
    try:
        results = []
        with DDGS() as ddgs:
            # Simple text search
            ddgs_gen = ddgs.text(query, max_results=max_results)
            if ddgs_gen:
                for r in ddgs_gen:
                    results.append(r)
        return results
    except Exception as e:
        print(f"Search Agent Error ({query}): {str(e)}")
        return []

def smart_search(requirements, specific_query, max_total=6):
    """
    Smart Search Strategy:
    1. Try specific LLM-generated query.
    2. If low results, try 'requirements' + ' data list'.
    3. If still low, try broad 'requirements'.
    """
    seen_urls = set()
    all_results = []
    
    # 1. Specific Query
    results = search_web(specific_query, max_results=5)
    for r in results:
        if r['href'] not in seen_urls:
            all_results.append(r)
            seen_urls.add(r['href'])
            
    # 2. Broad Query fallback if needed
    if len(all_results) < 3:
        broad_query = f"{requirements} data list"
        results = search_web(broad_query, max_results=5)
        for r in results:
            if r['href'] not in seen_urls:
                all_results.append(r)
                seen_urls.add(r['href'])
                
    # 3. Last Resort
    if len(all_results) == 0:
        general_query = requirements
        results = search_web(general_query, max_results=5)
        for r in results:
            if r['href'] not in seen_urls:
                all_results.append(r)
                seen_urls.add(r['href'])

    return all_results[:max_total]

def get_formatted_search_results(requirements, specific_query):
    """Refined search that returns a formatted string context for LLM"""
    
    # Use smart search strategy
    raw_results = smart_search(requirements, specific_query)
    
    if not raw_results:
        # Absolute fallback to generic URLs if DDG fails completely (e.g. rate limit)
        return (
            "WARNING: Live search failed. Suggest these generic search URLs:\n"
            f"1. Google Search: https://www.google.com/search?q={requirements.replace(' ', '+')}\n"
            f"2. Bing Search: https://www.bing.com/search?q={requirements.replace(' ', '+')}\n"
        )
        
    context = f"Real-Time Web Search Results (Query: {specific_query}):\n"
    for i, res in enumerate(raw_results):
        context += f"{i+1}. Title: {res.get('title')}\n   URL: {res.get('href')}\n   Snippet: {res.get('body')}\n\n"
        
    return context
