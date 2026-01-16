import json
import re
from typing import Any, Dict, List, Union

class SafeLLMParser:
    """
    Robust parser for handling LLM outputs.
    Can extract JSON from markdown, mixed text, and handle common syntax errors.
    """
    
    @staticmethod
    def strip_markdown(text: str) -> str:
        """
        Remove markdown code blocks from text.
        Handles ```json, ```python, or just ``` blocks.
        """
        if not text:
            return ""
            
        # Pattern to find code blocks: ```(optional language)\n(content)\n```
        # We use re.DOTALL to match across newlines
        pattern = r"```(?:\w+)?\s*(.*?)\s*```"
        
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            # If multiple blocks, join them or take the largest one
            # For now, return the content of the first block as it's usually the main output
            return matches[0].strip()
        
        # If no code blocks but text looks like code (starts with imports or {), return as is
        return text.strip()

    @staticmethod
    def parse_json(text: str, default: Any = None) -> Union[Dict, List, Any]:
        """
        Safely parse JSON from a string that might contain other text.
        
        Strategies:
        1. Direct JSON parse
        2. Strip markdown and parse
        3. Regex search for first JSON object/array
        """
        if not text:
            return default if default is not None else {}

        cleaned_text = text.strip()

        # Strategy 1: Direct Parse
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            pass
            
        # Strategy 2: Strip Markdown
        try:
            cleaned_text = SafeLLMParser.strip_markdown(text)
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            pass
            
        # Strategy 3: Regex Search for JSON Object {} or Array []
        try:
            # Look for outermost {} or []
            # This is a naive regex but works for 90% of LLM chatter cases
            json_pattern = r"(\{.*\}|\[.*\])"
            match = re.search(json_pattern, text, re.DOTALL)
            if match:
                potential_json = match.group(1)
                return json.loads(potential_json)
        except json.JSONDecodeError:
            pass
            
        # If all fail, return default
        return default if default is not None else {}
