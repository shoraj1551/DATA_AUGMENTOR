# Sample Data Files for Demo

This folder contains sample files to demonstrate each functionality of the DataAugmentor Suite.

## Files Overview

### For DataAugmentor Tool:

**`customers.csv`**
- Sample customer data with PII (name, email, phone)
- Use for: Augment Data, Mask PII, Generate Edge Cases
- 5 rows of customer information

### For File Comparison Tool:

**`products_v1.csv` & `products_v2.csv`**
- Two versions of product data
- Differences: Price change (P003), Item swap (P005 vs P006)
- Use for: CSV file comparison demo

**`config_v1.json` & `config_v2.json`**
- Two versions of configuration JSON
- Differences: User role changes, new settings
- Use for: JSON file comparison demo

### For Code Review Tool:

**`sample_code.py`**
- Basic Python functions
- Issues: Missing error handling, no type hints
- Use for: Python code review demo

**`sample_pyspark.py`**
- PySpark data processing code
- Issues: Using collect() on large data, performance concerns
- Use for: PySpark code review demo

**`sample_queries.sql`**
- SQL queries
- Issues: SELECT *, implicit joins, missing indexes
- Use for: SQL code review demo

## How to Use in Demo

### DataAugmentor:
1. Upload `customers.csv`
2. Try "Augment Data" to add more rows
3. Try "Mask PII" to anonymize names/emails/phones
4. Try "Generate Edge Cases" for testing data

### File Comparison:
1. Upload `products_v1.csv` and `products_v2.csv`
2. Compare to see differences
3. Try with `config_v1.json` and `config_v2.json` for JSON comparison

### Code Review:
1. Upload `sample_code.py` for Python review
2. Upload `sample_pyspark.py` for PySpark-specific review
3. Upload `sample_queries.sql` for SQL review
4. Generate tests and see failure scenarios
