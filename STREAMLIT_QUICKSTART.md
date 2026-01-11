# Quick Start: Running Streamlit App

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (Windows PowerShell)
$env:OPENROUTER_API_KEY="your-api-key-here"

# Or create .streamlit/secrets.toml
mkdir .streamlit
echo 'OPENROUTER_API_KEY = "your-key"' > .streamlit/secrets.toml
```

## Run Streamlit App

```bash
streamlit run streamlit_app.py
```

App opens at: **http://localhost:8501**

## Demo with Sample Data

### DataAugmentor
1. Navigate to "📊 DataAugmentor"
2. Try "Augment Existing Data"
3. Upload: `sample_data/customers.csv`
4. Click "Augment Data"

### File Comparison
1. Navigate to "📁 File Comparison"
2. Upload File 1: `sample_data/products_v1.csv`
3. Upload File 2: `sample_data/products_v2.csv`
4. Click "Compare Files"

### Code Review
1. Navigate to "🔍 Code Review & Testing"
2. Select Language: "Python"
3. Upload: `sample_data/sample_code.py`
4. Click "🔍 Analyze Code"

## Deploy to Streamlit Cloud

See: [docs/streamlit_deployment.md](./docs/streamlit_deployment.md)

---

**Enjoy! 🚀**
