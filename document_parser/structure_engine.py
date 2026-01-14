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
    from common.llm.client import call_with_fallback
    
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
        response = call_with_fallback(
            feature_name="document_parser",
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
    Returns tuple: (fields_list, error_message)
    """
    from common.llm.client import call_with_fallback
    import json
    
    system_prompt = """You are an expert Data Architect and Document Analyst.
    Analyze the document carefully and identify ALL extractable data fields.
    
    Look for:
    - Structured data (tables, forms, invoices)
    - Key-value pairs (labels and values)
    - Dates, numbers, amounts
    - Names, addresses, identifiers
    - Any repeated patterns or data structures
    
    Return a comprehensive list of field names that can be extracted.
    Be thorough - suggest 5-15 fields if possible.
    
    Return JSON format: {"fields": ["Field 1", "Field 2", ...]}
    """
    
    try:
        response = call_with_fallback(
            feature_name="document_parser",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this document and suggest ALL extractable fields:\n\n{text[:50000]}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            timeout=30  # 30 second timeout to prevent hanging
        )
        data = json.loads(response.choices[0].message.content)
        
        # Extract fields from various possible formats
        fields = []
        if isinstance(data, list):
            fields = data
        elif "fields" in data:
            fields = data["fields"]
        elif "suggested_fields" in data:
            fields = data["suggested_fields"]
        elif "extractable_fields" in data:
            fields = data["extractable_fields"]
        else:
            # Try to get any list value
            for value in data.values():
                if isinstance(value, list):
                    fields = value
                    break
        
        # If we got fields, return them
        if fields and len(fields) > 0:
            return (fields, None)
        else:
            # No fields found - return helpful message
            return ([], "No structured data fields detected in the document. The document may contain only unstructured text.")
        
    except json.JSONDecodeError as e:
        # JSON parsing error - likely malformed response from AI
        return ([], f"Unable to extract structured data patterns from this document. The document may be too complex or contain unstructured text only.")
    except Exception as e:
        error_str = str(e)
        # Provide specific error messages based on error type
        if "429" in error_str or "rate limit" in error_str.lower():
            return ([], "Rate limit reached. Please wait a moment and try again.")
        elif "timeout" in error_str.lower():
            return ([], "Request timed out. The document may be too large. Try with a smaller document.")
        elif "api" in error_str.lower() and "key" in error_str.lower():
            return ([], "API key issue detected. Please check your OpenRouter API key configuration.")
        else:
            # Generic error with actual error message
            return ([], f"Analysis failed: {error_str}")
