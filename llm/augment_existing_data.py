from llm.client import client
from utils.json_utils import parse_records
from utils.cache import llm_cache
from config.settings import MODEL_NAME


@llm_cache.cached
def _call_llm_for_augmentation(data_json: str, num_rows: int):
    """
    Internal function to call LLM API for data augmentation (cacheable).
    """
    system_prompt = """You are a data augmentation expert.

Your task:
- Generate new records that match the schema of the input data
- Keep the schema EXACTLY identical
- Generate realistic, varied data

CRITICAL RULES:
- Return ONLY valid JSON
- NO explanations
- NO analysis
- NO markdown
- NO comments
- NO additional fields

Mandatory output format:
{
  "records": [
    {"column1": "value1", "column2": "value2"},
    {"column1": "value3", "column2": "value4"}
  ]
}"""

    user_prompt = f"""Input data sample: {data_json[:1000]}

Generate exactly {num_rows} new records with IDENTICAL schema.
Return ONLY the JSON object with "records" field."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return response


def augment_existing_data(df, num_rows=10):
    """
    Augment existing data with new rows.
    """
    # Convert DataFrame to JSON string for caching (limit size)
    data_dict = df.head(10).to_dict(orient="records")  # Use only first 10 rows as sample
    data_json = str(data_dict)
    
    # Call cached LLM function
    response = _call_llm_for_augmentation(data_json, num_rows)
    
    new_rows = parse_records(response)
    return df._append(new_rows, ignore_index=True)

