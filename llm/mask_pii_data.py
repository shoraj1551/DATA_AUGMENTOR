from llm.client import get_client
from utils.json_utils import parse_records
from utils.cache import llm_cache
from config.settings import MODEL_NAME


@llm_cache.cached
def _call_llm_for_pii_masking(data_json: str, exclude_columns_str: str):
    """
    Internal function to call LLM API for PII masking (cacheable).
    """
    system_prompt = """You are a data privacy expert. Your job is to MASK personally identifiable information (PII).

CRITICAL: You MUST change the PII values to masked versions. DO NOT return original values!

PII columns to MASK (change these values):
- Age: Replace with random ages (e.g., 25, 42, 38)
- Income: Replace with masked values (e.g., "XXXXX", "MASKED", or random numbers)
- Names: Replace with "Person_1", "Person_2", etc.
- Emails: Replace with "user1@example.com", "user2@example.com"
- Phone: Replace with "XXX-XXX-XXXX"
- Addresses: Replace with "123 Main St", "456 Oak Ave"

EXAMPLE:
Input: {"Age": 35, "Income": 75000, "Score": 720}
Output: {"Age": 42, "Income": "XXXXX", "Score": 720}

Return JSON: {"records": [...]}"""

    user_prompt = f"""Mask PII in this data: {data_json[:2000]}

Columns to NOT mask (keep original): {exclude_columns_str}

IMPORTANT: CHANGE the PII values! Return masked data in JSON format."""

    response = get_client().chat.completions.create(
        model="openai/gpt-4o-mini",  # Using better model for instruction following
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return response


def mask_pii_data(df, exclude_columns=None):
    """
    Automatically detects and masks PII data in a DataFrame.

    Args:
        df (pd.DataFrame): Input data
        exclude_columns (list[str], optional): Columns that must NOT be masked

    Returns:
        pd.DataFrame: PII-masked data
    """
    exclude_columns = exclude_columns or []
    
    # Convert ALL data to JSON for masking (not just sample)
    data_dict = df.to_dict(orient="records")
    data_json = str(data_dict)
    
    # Limit the size if too large (max ~5000 chars to avoid token limits)
    if len(data_json) > 5000:
        # If data is too large, process in smaller chunks or use sample
        data_sample = df.head(50).to_dict(orient="records")
        data_json = str(data_sample)
    
    exclude_columns_str = str(exclude_columns if exclude_columns else "None")
    
    # Call cached LLM function
    response = _call_llm_for_pii_masking(data_json, exclude_columns_str)

    return parse_records(response)

