from llm.client import get_client
from utils.json_utils import parse_records
from config.settings import get_model_for_feature

def generate_edge_case_data(df, prompt="", num_rows=10):
    """
    Generate edge case data based on input schema.
    """
    system_prompt = """You are a data testing expert.

Generate edge case test data with extreme but valid values.

CRITICAL RULES:
- Return ONLY valid JSON
- NO explanations
- NO analysis
- NO markdown

Mandatory format: {"records": [...]}"""

    # Use only first 10 rows as sample
    data_sample = df.head(10).to_dict(orient="records")
    
    user_prompt = f"""Input data sample: {str(data_sample)[:1000]}

Generate exactly {num_rows} edge-case records with IDENTICAL schema.
"""
    if prompt:
        user_prompt += f"Focus on these specific edge cases: {prompt}\n"

    user_prompt += 'Return ONLY the JSON object with "records" field.'

    response = get_client().chat.completions.create(
        model=get_model_for_feature("data_augmentor"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    return parse_records(response)

