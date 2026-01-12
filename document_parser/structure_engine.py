from config.settings import get_model_for_feature
from llm.client import get_client
import json
import pandas as pd
import io

def parse_structured_data(text, requirements):
    """
    Extract structured data (tables) from document text based on user requirements.
    Retuns a list of pandas DataFrames.
    """
    model = get_model_for_feature("document_parser")
    client = get_client()
    
    system_prompt = """You are a Data Extraction Specialist.
    Extract the requested data from the document text into a structured JSON format (list of dicts).
    If multiple unrelated tables are needed, return a dict with keys as table names.
    
    Ensure all numbers are converted to proper formats.
    Return ONLY valid JSON.
    """
    
    user_prompt = f"""
    Requirement: {requirements}
    
    Document Text:
    {text[:500000]}
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
        
        dfs = []
        
        # Heuristic to convert JSON to DataFrame(s)
        if isinstance(data, list):
            dfs.append(("Extracted Data", pd.DataFrame(data)))
        elif isinstance(data, dict):
             # Check if it's a wrapper like {"data": [...]}
            if len(data) == 1 and isinstance(list(data.values())[0], list):
                 key = list(data.keys())[0]
                 dfs.append((key, pd.DataFrame(data[key])))
            else:
                # Multiple tables
                for key, val in data.items():
                    if isinstance(val, list):
                        dfs.append((key, pd.DataFrame(val)))
        
        return dfs
        
    except Exception as e:
        raise Exception(f"Extraction Error: {str(e)}")

def suggest_schema(text):
    """
    Introspect document and suggest available fields for extraction.
    """
    model = get_model_for_feature("document_parser")
    client = get_client()
    
    system_prompt = """You are a Data Architect.
    Analyze the document excerpt and suggest a list of available data fields that can be extracted.
    Return a list of strings (field names).
    Example: ["Invoice Number", "Date", "Total Amount", "Vendor Name"]
    """
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Document Snippet:\n{text[:50000]}"}
            ],
             response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        
        if isinstance(data, list): return data
        if "fields" in data: return data["fields"]
        return list(data.values())[0] if data else []
        
    except Exception:
        return []
