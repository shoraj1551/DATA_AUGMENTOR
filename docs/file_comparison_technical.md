# File Comparison Tool - Technical Documentation

Complete technical guide for the File Comparison tool, explaining how CSV, TXT, and JSON file comparison works.

---

## Overview

File Comparison tool compares two files of the same type and identifies differences, unique data, and common data.

**Route**: `/file-comparison`  
**Backend File**: `app.py`, `utils/file_comparator.py`  
**Supported Formats**: CSV, TXT, JSON

---

## Architecture

### Frontend Flow

```
User uploads File 1 (CSV)
User uploads File 2 (CSV)
    ↓
JavaScript reads files
    ↓
POST to /compare endpoint
    ↓
Display results:
  - Status (Identical/Different)
  - Statistics
  - Only in File 1
  - Only in File 2
  - Common data
```

### Backend Flow

```python
# app.py - /compare route
@app.route("/compare", methods=["POST"])
def compare():
    file1 = request.files.get("file1")
    file2 = request.files.get("file2")
    
    # Read contents
    content1 = file1.read().decode('utf-8')
    content2 = file2.read().decode('utf-8')
    
    # Call comparator
    result = compare_files(
        file1.filename, 
        file2.filename,
        content1,
        content2
    )
    
    return jsonify(result)
```

---

## 1. CSV Comparison

### Algorithm

**File**: `utils/file_comparator.py`

```python
def compare_csv(file1_content, file2_content, file1_name, file2_name):
    # 1. Parse CSV to DataFrames
    try:
        df1 = pd.read_csv(StringIO(file1_content))
    except Exception as e:
        raise ValueError(f"Error parsing CSV in '{file1_name}': {e}")
    
    try:
        df2 = pd.read_csv(StringIO(file2_content))
    except Exception as e:
        raise ValueError(f"Error parsing CSV in '{file2_name}': {e}")
    
    # 2. Convert rows to tuples for set comparison
    set1 = set(df1.apply(tuple, axis=1))
    set2 = set(df2.apply(tuple, axis=1))
    
    # 3. Find differences using set operations
    only_in_file1 = set1 - set2  # Rows only in file1
    only_in_file2 = set2 - set1  # Rows only in file2
    common = set1 & set2          # Common rows
    
    # 4. Format for display
    def format_row(row_tuple):
        return " | ".join(str(x) for x in row_tuple)
    
    # 5. Return results
    return {
        "only_in_file1": [format_row(r) for r in only_in_file1],
        "only_in_file2": [format_row(r) for r in only_in_file2],
        "common": [format_row(r) for r in common],
        "stats": {
            "total_file1": len(df1),
            "total_file2": len(df2),
            "only_in_file1": len(only_in_file1),
            "only_in_file2": len(only_in_file2),
            "common": len(common)
        }
    }
```

### How It Works

1. **Parse CSV**: Convert to Pandas DataFrame
2. **Row Tuples**: Each row becomes a tuple (immutable, hashable)
3. **Set Operations**: 
   - `set1 - set2` = Rows only in file1
   - `set2 - set1` = Rows only in file2
   - `set1 & set2` = Common rows
4. **Format**: Convert tuples back to readable strings
5. **Statistics**: Count totals and differences

### Example

**File 1** (products_v1.csv):
```csv
id,name,price
1,Laptop,999
2,Mouse,29
3,Keyboard,79
```

**File 2** (products_v2.csv):
```csv
id,name,price
1,Laptop,999
2,Mouse,29
4,Monitor,299
```

**Result**:
- Only in File 1: `3 | Keyboard | 79`
- Only in File 2: `4 | Monitor | 299`
- Common: `1 | Laptop | 999`, `2 | Mouse | 29`

---

## 2. TXT Comparison

### Algorithm

```python
def compare_txt(file1_content, file2_content, file1_name, file2_name):
    # 1. Split into lines
    lines1 = set(file1_content.strip().split('\n'))
    lines2 = set(file2_content.strip().split('\n'))
    
    # 2. Set operations
    only_in_file1 = lines1 - lines2
    only_in_file2 = lines2 - lines1
    common = lines1 & lines2
    
    # 3. Return sorted results
    return {
        "only_in_file1": sorted(list(only_in_file1)),
        "only_in_file2": sorted(list(only_in_file2)),
        "common": sorted(list(common)),
        "stats": {
            "total_file1": len(lines1),
            "total_file2": len(lines2),
            "only_in_file1": len(only_in_file1),
            "only_in_file2": len(only_in_file2),
            "common": len(common)
        }
    }
```

### How It Works

1. **Split Lines**: Each line becomes a set element
2. **Set Operations**: Same as CSV
3. **Sort**: Results sorted alphabetically
4. **Case Sensitive**: "Hello" ≠ "hello"

### Example

**File 1**:
```
apple
banana
cherry
```

**File 2**:
```
banana
cherry
date
```

**Result**:
- Only in File 1: `apple`
- Only in File 2: `date`
- Common: `banana`, `cherry`

---

## 3. JSON Comparison

### Algorithm

```python
def compare_json(file1_content, file2_content, file1_name, file2_name):
    # 1. Parse JSON
    try:
        json1 = json.loads(file1_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON in '{file1_name}': {e}")
    
    try:
        json2 = json.loads(file2_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON in '{file2_name}': {e}")
    
    # 2. Handle different JSON types
    if isinstance(json1, list) and isinstance(json2, list):
        # Compare as lists
        set1 = set(json.dumps(item, sort_keys=True) for item in json1)
        set2 = set(json.dumps(item, sort_keys=True) for item in json2)
    
    elif isinstance(json1, dict) and isinstance(json2, dict):
        # Compare key-value pairs
        set1 = set(f"{k}: {json.dumps(v, sort_keys=True)}" 
                   for k, v in json1.items())
        set2 = set(f"{k}: {json.dumps(v, sort_keys=True)}" 
                   for k, v in json2.items())
    
    else:
        # Direct comparison
        set1 = {json.dumps(json1, sort_keys=True)}
        set2 = {json.dumps(json2, sort_keys=True)}
    
    # 3. Set operations
    only_in_file1 = set1 - set2
    only_in_file2 = set2 - set1
    common = set1 & set2
    
    # 4. Return results
    return {
        "only_in_file1": sorted(list(only_in_file1)),
        "only_in_file2": sorted(list(only_in_file2)),
        "common": sorted(list(common)),
        "stats": {...}
    }
```

### How It Works

1. **Parse JSON**: Convert string to Python objects
2. **Type Detection**: Handle lists, dicts, or primitives
3. **Serialization**: Convert to strings for comparison
4. **sort_keys=True**: Ensures consistent ordering
5. **Set Operations**: Same as CSV/TXT

### Example

**File 1** (config_v1.json):
```json
{
  "users": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ],
  "theme": "dark"
}
```

**File 2** (config_v2.json):
```json
{
  "users": [
    {"id": 1, "name": "Alice"},
    {"id": 3, "name": "Charlie"}
  ],
  "theme": "light"
}
```

**Result**:
- Only in File 1: `{"id": 2, "name": "Bob"}`, `theme: "dark"`
- Only in File 2: `{"id": 3, "name": "Charlie"}`, `theme: "light"`
- Common: `{"id": 1, "name": "Alice"}`

---

## File Type Detection

### Algorithm

```python
def compare_files(file1_path, file2_path, file1_content, file2_content):
    # 1. Extract extensions
    ext1 = file1_path.lower().split('.')[-1]
    ext2 = file2_path.lower().split('.')[-1]
    
    # 2. Validate matching types
    if ext1 != ext2:
        raise ValueError(
            f"File types must match. "
            f"'{file1_path}' is {ext1.upper()} "
            f"but '{file2_path}' is {ext2.upper()}"
        )
    
    # 3. Route to appropriate comparator
    if ext1 == 'csv':
        return compare_csv(file1_content, file2_content, 
                          file1_path, file2_path)
    elif ext1 == 'txt':
        return compare_txt(file1_content, file2_content,
                          file1_path, file2_path)
    elif ext1 == 'json':
        return compare_json(file1_content, file2_content,
                           file1_path, file2_path)
    else:
        raise ValueError(
            f"Unsupported file type: {ext1.upper()}. "
            f"Supported: CSV, TXT, JSON"
        )
```

---

## Error Handling

### File-Specific Errors

**CSV Parsing Error**:
```
Error parsing CSV in 'products.csv': 
Expected 3 fields, got 2 on line 5
```

**JSON Parsing Error**:
```
Error parsing JSON in 'config.json': 
Expecting ',' delimiter: line 10 column 5 (char 245)
```

**Type Mismatch**:
```
File types must match. 
'data.csv' is CSV but 'data.json' is JSON
```

### Frontend Display

```javascript
// templates/file_comparison.html
fetch('/compare', {method: 'POST', body: formData})
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            showError(data.error);  // Shows filename in error
        } else {
            displayResults(data);
        }
    });
```

---

## Performance Considerations

### Memory Usage

- **In-Memory Processing**: Files loaded entirely in memory
- **Set Operations**: O(n) time complexity
- **Recommended Limit**: Files under 100MB

### Optimization

1. **Streaming**: For very large files, use streaming comparison
2. **Sampling**: Compare sample if files are huge
3. **Indexing**: For repeated comparisons, index data

---

## Frontend Integration

### File Upload

```javascript
// templates/file_comparison.html
const formData = new FormData();
formData.append('file1', file1Input.files[0]);
formData.append('file2', file2Input.files[0]);

fetch('/compare', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(displayResults);
```

### Results Display

```javascript
function displayResults(result) {
    // Status badge
    if (result.stats.only_in_file1 === 0 && 
        result.stats.only_in_file2 === 0) {
        showStatus("IDENTICAL", "success");
    } else {
        showStatus("DIFFERENT", "warning");
    }
    
    // Statistics
    showStat("Total File 1", result.stats.total_file1);
    showStat("Total File 2", result.stats.total_file2);
    showStat("Common", result.stats.common);
    
    // Differences
    showList("Only in File 1", result.only_in_file1);
    showList("Only in File 2", result.only_in_file2);
    showList("Common Data", result.common);
}
```

---

## Testing

### Unit Tests

```python
def test_csv_comparison():
    csv1 = "id,name\n1,Alice\n2,Bob"
    csv2 = "id,name\n1,Alice\n3,Charlie"
    
    result = compare_csv(csv1, csv2, "file1.csv", "file2.csv")
    
    assert result['stats']['common'] == 1
    assert result['stats']['only_in_file1'] == 1
    assert result['stats']['only_in_file2'] == 1

def test_json_comparison():
    json1 = '{"users": [{"id": 1}]}'
    json2 = '{"users": [{"id": 2}]}'
    
    result = compare_json(json1, json2, "f1.json", "f2.json")
    
    assert len(result['only_in_file1']) > 0
```

---

## Use Cases

1. **Data Validation**: Compare prod vs staging data
2. **Config Management**: Track configuration changes
3. **Testing**: Verify test data matches expected
4. **Auditing**: Find differences in datasets
5. **Migration**: Validate data migration

---

## Next Steps

- [Code Review Technical Guide](./code_review_technical.md)
- [DataAugmentor Technical Guide](./dataaugmentor_technical.md)
- [System Architecture](./architecture.md)
