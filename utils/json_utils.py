import json
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def parse_records(response):
    """
    Parse LLM response and convert to DataFrame.
    
    Args:
        response: LLM API response object
        
    Returns:
        pd.DataFrame: Parsed data
        
    Raises:
        ValueError: If response format is invalid
    """
    try:
        content = response.choices[0].message.content
        
        if not content:
            raise ValueError("LLM returned empty response")
        
        # Log the raw response for debugging
        logger.debug(f"LLM Response content (first 500 chars): {content[:500]}")
        
        parsed = json.loads(content)
        
        # Check if parsed is empty
        if not parsed or len(parsed) == 0:
            logger.error(f"LLM returned empty JSON object. Full response: {content}")
            raise ValueError("LLM returned empty JSON object. Please try again.")
        
        if "records" not in parsed:
            logger.error(f"Missing 'records' field. Got keys: {list(parsed.keys())}. Full response: {content[:500]}")
            raise ValueError(
                "Invalid LLM response format: missing 'records' field. "
                f"Got keys: {list(parsed.keys())}"
            )
        
        if not isinstance(parsed["records"], list):
            raise ValueError(
                f"Invalid LLM response format: 'records' must be a list, "
                f"got {type(parsed['records']).__name__}"
            )
        
        if len(parsed["records"]) == 0:
            logger.warning(f"LLM returned empty records list. Full response: {content}")
            raise ValueError("LLM returned no records")
        
        df = pd.DataFrame(parsed["records"])
        
        if df.empty:
            logger.warning(f"DataFrame is empty after parsing. Records: {parsed['records']}")
            raise ValueError("Generated DataFrame is empty")
        
        logger.info(f"Successfully parsed {len(df)} rows with {len(df.columns)} columns")
        return df
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}. Content: {content[:200]}")
        raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
    except IndexError:
        raise ValueError("LLM response has no choices")
    except Exception as e:
        logger.exception(f"Unexpected error parsing LLM response")
        raise ValueError(f"Error parsing LLM response: {str(e)}")


