import io
import pandas as pd
from llm.client import get_client
from utils.json_utils import parse_records
from utils.cache import llm_cache
from config.settings import get_model_for_feature, DEFAULT_ROWS, MAX_ROWS


@llm_cache.cached
def _call_llm_for_synthetic_data(user_prompt: str):
    """
    Internal function to call LLM API (cacheable).
    """
    system_instruction = f"""
    You are an expert synthetic data architect.

    Your task:
        - Infer schema from the user request
        - Infer number of rows (default={DEFAULT_ROWS}, max={MAX_ROWS})
        - Generate realistic synthetic tabular data

    Rules:
        - Return ONLY valid JSON
        - No explanations
        - No markdown
        - No comments

    Mandatory output format: {{
        "records": [{{ "column": "value" }}]
    }}"""

    response = get_client().chat.completions.create(
        model=get_model_for_feature("data_augmentor"),
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return response


def generate_synthetic_data(user_prompt: str, num_rows: int = DEFAULT_ROWS, return_csv: bool = False):
    """
    Generate synthetic tabular data from a natural language prompt.
    
    Args:
        user_prompt: Description of the data to generate
        num_rows: Number of rows to generate
        return_csv: If True, return CSV StringIO; if False, return DataFrame
    
    Returns:
        - pandas DataFrame (default)
        - CSV StringIO if return_csv=True (ready for download)
    """
    # Add row count to prompt
    full_prompt = f"{user_prompt}\n\nGenerate exactly {num_rows} rows of data."
    
    # Call cached LLM function
    response = _call_llm_for_synthetic_data(full_prompt)

    # Parse → DataFrame
    df = parse_records(response)

    if df.empty:
        raise ValueError("Generated DataFrame is empty")

    if not return_csv:
        return df

    # Convert DataFrame → CSV (in memory)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return csv_buffer
