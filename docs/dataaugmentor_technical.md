# DataAugmentor Tool - Technical Documentation

Complete technical guide for the DataAugmentor tool, explaining how data generation, augmentation, PII masking, and edge case generation work.

---

## Overview

DataAugmentor uses AI (LLM) to generate, augment, mask, and create test data for datasets.

**Route**: `/data-augmentor`  
**Backend File**: `app.py`  
**LLM Modules**: `llm/generate_synthetic_data.py`, `llm/augment_existing_data.py`, `llm/mask_pii_data.py`, `llm/generate_edge_case_data.py`

---

## 1. Generate Synthetic Data

### Frontend Flow

1. User enters description: "Customer data with name, email, age"
2. User sets row count: 10
3. JavaScript sends POST to `/process`
4. Response displayed in preview
5. Download button enabled

### Backend Flow

```python
# app.py - /process route
@app.route("/process", methods=["POST"])
def process():
    action = request.form.get("action")  # "generate"
    prompt = request.form.get("prompt")  # User description
    num_rows = int(request.form.get("num_rows", 10))
    
    # Call LLM module
    df = generate_synthetic_data(prompt, num_rows)
    
    # Return CSV
    return df.to_csv(index=False)
```

### LLM Integration

**File**: `llm/generate_synthetic_data.py`

```python
@llm_cache.cached
def generate_synthetic_data(prompt: str, num_rows: int) -> pd.DataFrame:
    # 1. Build system instruction
    system_instruction = """You are a data generation expert.
    Generate realistic synthetic data in JSON format.
    Return ONLY valid JSON with structure: {"records": [...]}"""
    
    # 2. Build user prompt
    user_prompt = f"""Generate {num_rows} rows of {prompt}.
    Return as JSON array of objects."""
    
    # 3. Call OpenRouter API
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    # 4. Parse JSON response
    json_str = response.choices[0].message.content
    records = parse_records(json_str)  # Extract "records" array
    
    # 5. Convert to DataFrame
    df = pd.DataFrame(records)
    return df
```

### Caching

- **Cache Key**: `hash(function_name + prompt + num_rows)`
- **TTL**: 3600 seconds (1 hour)
- **Benefit**: Same request returns instantly

### Error Handling

- **Invalid JSON**: `parse_records()` validates and extracts
- **Empty Response**: Raises `ValueError` with clear message
- **API Failure**: Logged and returned to user

---

## 2. Augment Existing Data

### Frontend Flow

1. User uploads CSV file
2. Optionally adds description
3. Sets number of rows to add
4. Receives augmented dataset

### Backend Flow

```python
# app.py
file = request.files.get("file")
df = pd.read_csv(file)
prompt = request.form.get("prompt", "")
num_rows = int(request.form.get("augment_row_count", 5))

# Call augmentation
augmented_df = augment_existing_data(df, prompt, num_rows)
```

### LLM Integration

**File**: `llm/augment_existing_data.py`

```python
@llm_cache.cached
def augment_existing_data(df: pd.DataFrame, prompt: str, num_rows: int):
    # 1. Sample existing data (max 10 rows for context)
    sample = df.head(10).to_dict('records')
    
    # 2. Extract schema
    schema = {col: str(df[col].dtype) for col in df.columns}
    
    # 3. Build prompt
    system_instruction = """Generate new data rows matching the schema.
    Return ONLY JSON: {"records": [...]}"""
    
    user_prompt = f"""Schema: {schema}
    Sample data: {sample}
    Generate {num_rows} new rows.
    {prompt if prompt else ""}"""
    
    # 4. Call LLM
    response = client.chat.completions.create(...)
    
    # 5. Parse and append
    new_records = parse_records(response.choices[0].message.content)
    new_df = pd.DataFrame(new_records)
    
    # 6. Concatenate
    return pd.concat([df, new_df], ignore_index=True)
```

### Key Features

- **Schema Preservation**: LLM maintains column types
- **Context Awareness**: Uses sample data as examples
- **Flexible Rows**: User controls how many to add
- **Validation**: Ensures new data matches schema

---

## 3. Mask PII Data

### Frontend Flow

1. User uploads CSV with PII
2. **Auto-detection**: JavaScript identifies PII columns
3. User unchecks columns to EXCLUDE from masking
4. Receives masked dataset

### PII Detection (Frontend)

**File**: `templates/partials/schema.js.html`

```javascript
function detectPIIColumns(columns) {
    const piiPatterns = [
        'name', 'email', 'phone', 'address', 
        'ssn', 'social', 'dob', 'birth', 
        'passport', 'license'
    ];
    
    return columns.filter(col => 
        piiPatterns.some(pattern => 
            col.toLowerCase().includes(pattern)
        )
    );
}
```

### Backend Flow

```python
# app.py
df = pd.read_csv(file)
exclude_columns = request.form.getlist("exclude_columns")

# Mask PII
masked_df = mask_pii_data(df, exclude_columns)
```

### LLM Integration

**File**: `llm/mask_pii_data.py`

```python
@llm_cache.cached
def mask_pii_data(df: pd.DataFrame, exclude_columns: List[str]):
    # 1. Identify PII columns
    pii_columns = [col for col in df.columns 
                   if col not in exclude_columns]
    
    # 2. Sample data (max 50 rows to avoid token limits)
    sample_size = min(len(df), 50)
    sample_df = df.head(sample_size)
    
    # 3. Build masking prompt
    system_instruction = """You are a PII masking expert.
    Replace PII values with realistic fake data.
    Maintain data format and structure.
    Return ONLY JSON: {"records": [...]}"""
    
    user_prompt = f"""Mask PII in these columns: {pii_columns}
    Data: {sample_df.to_dict('records')}
    
    Examples:
    - "John Doe" → "Jane Smith"
    - "john@email.com" → "user123@example.com"
    - "555-1234" → "555-9876"
    
    Return ALL rows with PII masked."""
    
    # 4. Call LLM (using gpt-4o-mini for better accuracy)
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[...]
    )
    
    # 5. Parse and return
    masked_records = parse_records(response.choices[0].message.content)
    return pd.DataFrame(masked_records)
```

### Key Features

- **Smart Detection**: Pattern-based PII identification
- **Selective Masking**: User controls what to mask
- **Realistic Data**: LLM generates believable replacements
- **Format Preservation**: Maintains email/phone formats

---

## 4. Generate Edge Case Data

### Frontend Flow

1. User uploads CSV
2. Optionally describes edge cases
3. Sets number of edge cases
4. Receives test data

### Backend Flow

```python
df = pd.read_csv(file)
prompt = request.form.get("prompt", "")
num_rows = int(request.form.get("edge_case_row_count", 5))

edge_df = generate_edge_case_data(df, prompt, num_rows)
```

### LLM Integration

**File**: `llm/generate_edge_case_data.py`

```python
@llm_cache.cached
def generate_edge_case_data(df: pd.DataFrame, prompt: str, num_rows: int):
    # 1. Analyze schema
    schema = df.dtypes.to_dict()
    sample = df.head(5).to_dict('records')
    
    # 2. Build edge case prompt
    system_instruction = """Generate edge case test data.
    Include: null values, boundary values, special characters,
    extreme values, invalid formats.
    Return ONLY JSON: {"records": [...]}"""
    
    user_prompt = f"""Schema: {schema}
    Sample: {sample}
    
    Generate {num_rows} edge cases for testing:
    - Null/empty values
    - Boundary values (min/max)
    - Special characters
    - Invalid formats
    - Extreme values
    
    {prompt if prompt else ""}"""
    
    # 3. Call LLM
    response = client.chat.completions.create(...)
    
    # 4. Parse and return
    records = parse_records(response.choices[0].message.content)
    return pd.DataFrame(records)
```

### Edge Case Examples

- **Null Values**: `None`, `""`, `NaN`
- **Boundary**: `0`, `-1`, `999999`
- **Special Chars**: `<script>`, `'; DROP TABLE;`
- **Invalid Formats**: `abc@`, `555-ABCD`
- **Extreme**: Very long strings, huge numbers

---

## Common Utilities

### JSON Parsing

**File**: `utils/json_utils.py`

```python
def parse_records(json_str: str) -> List[Dict]:
    # 1. Parse JSON
    data = json.loads(json_str)
    
    # 2. Extract records
    if "records" in data:
        records = data["records"]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError("Invalid JSON structure")
    
    # 3. Validate
    if not records or len(records) == 0:
        raise ValueError("No records found in response")
    
    return records
```

### Caching

**File**: `utils/cache.py`

```python
class LLMCache:
    def __init__(self, ttl=3600, max_size=100):
        self.cache = {}
        self.ttl = ttl
        self.max_size = max_size
    
    def cached(self, func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = self._generate_key(func.__name__, args, kwargs)
            
            # Check cache
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] < self.ttl:
                    return entry['value']  # Cache hit!
            
            # Cache miss - call function
            result = func(*args, **kwargs)
            
            # Store in cache
            self.cache[key] = {
                'value': result,
                'timestamp': time.time()
            }
            
            return result
        return wrapper
```

---

## Performance Considerations

### LLM Token Limits

- **Sample Size**: Limit to 50 rows for PII masking
- **Prompt Length**: Keep under 4000 tokens
- **Response Size**: Monitor and truncate if needed

### Optimization Tips

1. **Use Caching**: Identical requests return instantly
2. **Batch Processing**: Process large datasets in chunks
3. **Sampling**: Send representative sample to LLM
4. **Async**: Consider async processing for large files

---

## Troubleshooting

### Empty DataFrame Returned

**Cause**: LLM returned empty JSON or wrong format  
**Solution**: Check logs for actual LLM response, adjust prompt

### PII Not Masked

**Cause**: LLM didn't change values  
**Solution**: Using gpt-4o-mini model, enhanced prompt with examples

### Slow Response

**Cause**: Large dataset, no cache hit  
**Solution**: Reduce row count, enable caching, use sampling

---

## Testing

### Unit Tests

```python
def test_generate_synthetic_data():
    df = generate_synthetic_data("user data with name and email", 5)
    assert len(df) == 5
    assert 'name' in df.columns or 'email' in df.columns

def test_mask_pii():
    df = pd.DataFrame({
        'name': ['John Doe'],
        'email': ['john@email.com']
    })
    masked = mask_pii_data(df, [])
    assert masked['name'][0] != 'John Doe'
```

### Integration Tests

- Upload sample CSV
- Verify response format
- Check data integrity
- Validate caching

---

## Next Steps

- [File Comparison Technical Guide](./file_comparison_technical.md)
- [Code Review Technical Guide](./code_review_technical.md)
- [LLM Integration Details](./llm_integration.md)
