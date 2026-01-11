# DataAugmentor - AI-Powered Data & Code Tools Platform

A comprehensive suite of AI-powered tools for data augmentation, file comparison, and code review with support for 20+ programming languages.

---

## 🚀 Features

### 1. **DataAugmentor** (AI-Powered)
- Generate synthetic data from scratch
- Augment existing datasets
- Mask PII (Personally Identifiable Information)
- Generate edge case test data
- Smart PII column detection
- Configurable row counts
- LLM response caching for performance

### 2. **File Comparison**
- Compare CSV, TXT, and JSON files
- Identify unique data in each file
- Find common data between files
- Detailed statistics (total, unique, common counts)
- Visual status indicators

### 3. **Code Review & Testing Engine**
- **Supported Languages**: Python, PySpark, SQL, Spark SQL, JavaScript, TypeScript, Java, Scala, Kotlin, C#, Go, Rust, C++, Ruby, PHP, and more (20+ languages)
- Automated code review with AI
- Generate unit tests automatically
- Generate functional/integration tests
- Create failure test scenarios
- Language-specific configurations
- Customizable review rules via JSON config

---

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **OpenRouter API Key**: For LLM-powered features

---

## 🛠️ Installation & Setup

### Step 1: Clone or Download the Repository

```bash
cd DataAugmentor
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `Flask==3.1.2` - Web framework
- `pandas==2.3.3` - Data manipulation
- `openai==2.14.0` - OpenRouter API client

### Step 3: Configure API Key

1. Get your OpenRouter API key from [https://openrouter.ai/](https://openrouter.ai/)

2. Set the environment variable:

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENROUTER_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

**Alternative:** Edit `config/settings.py` and add your API key directly:
```python
OPENROUTER_API_KEY = "your-api-key-here"
```

### Step 4: Run the Application

```bash
python app.py
```

The server will start at: **http://127.0.0.1:5000**

---

## 🎯 Using the Tools

### **Landing Page**
Navigate to `http://127.0.0.1:5000` to see all available tools.

---

### **Tool 1: DataAugmentor**

**URL**: `http://127.0.0.1:5000/data-augmentor`

#### Operations:

**1. Generate Synthetic Data**
- Describe the data you want (e.g., "Customer data with name, email, age")
- Set number of rows (1-1000)
- Click "Generate Data"
- Preview and download CSV

**2. Augment Existing Data**
- Upload a CSV file
- Optionally describe additional requirements
- Set number of rows to add (1-100)
- Get augmented dataset

**3. Mask PII Data**
- Upload a CSV file
- PII columns are auto-detected
- Uncheck columns you DON'T want to mask
- Download masked data

**4. Generate Edge Case Data**
- Upload a CSV file
- Describe edge cases (optional)
- Set number of edge cases (1-50)
- Get edge case test data

#### Tips:
- LLM responses are cached for 1 hour (configurable in `config/settings.py`)
- Use the "Retry" button if results aren't satisfactory
- PII detection uses pattern matching (name, email, phone, address, SSN, etc.)

---

### **Tool 2: File Comparison**

**URL**: `http://127.0.0.1:5000/file-comparison`

#### Supported Formats:
- **CSV**: Row-by-row comparison
- **TXT**: Line-by-line comparison
- **JSON**: Deep structure comparison

#### How to Use:
1. Upload File 1
2. Upload File 2 (must be same type as File 1)
3. Click "Compare Files"
4. View results:
   - Status badge (Identical/Different)
   - Statistics (total, unique, common)
   - Data only in File 1
   - Data only in File 2
   - Common data

#### Error Handling:
- File type mismatches are detected
- Parsing errors show which file failed
- Malformed files are handled gracefully

---

### **Tool 3: Code Review & Testing Engine**

**URL**: `http://127.0.0.1:5000/code-review`

#### Supported Languages (20+):

**Detailed Configs (Comprehensive Rules):**
- 🐍 **Python** - PEP 8, type hints, best practices
- ⚡ **PySpark** - DataFrame optimization, shuffle checks, caching
- 🗄️ **SQL** - Query optimization, index usage, security
- ⚡ **Spark SQL** - Partition pruning, broadcast hints

**Generic Config (Basic Rules):**
- JavaScript, TypeScript, Java, Scala, Kotlin
- C#, VB.NET, F#, Go, Rust, C++, C
- Ruby, PHP, Perl, Lua, Bash
- Hive, R, Swift, Dart, Groovy

#### How to Use:

**Step 1: Select Language**
- Choose from dropdown (or leave blank for auto-detect)
- Main languages at top with larger font

**Step 2: Upload Code File**
- Supported: `.py`, `.ipynb`, `.js`, `.ts`, `.java`, `.sql`, `.scala`, `.go`, etc.

**Step 3: Configure Review (Optional)**
- Download language-specific config JSON
- Modify rules as needed
- Upload custom config

**Step 4: Select Analysis Options**
- ✅ Code Review (quality, security, performance)
- ✅ Generate Unit Tests
- ☐ Generate Functional Tests
- ✅ Generate Failure Scenarios

**Step 5: Analyze Code**
- Click "Analyze Code"
- View results in tabs
- Download generated tests

#### Configuration Files:

Located in `config/` directory:

- `code_review_config_python.json` - Python-specific
- `code_review_config_pyspark.json` - PySpark-specific
- `code_review_config_sql.json` - SQL-specific
- `code_review_config_sparksql.json` - Spark SQL-specific
- `code_review_config_generic.json` - For other languages
- `code_review_config.json` - Default fallback

**Customization:**
1. Download config for your language
2. Edit JSON to enable/disable checks
3. Adjust severity levels, thresholds
4. Upload modified config before analysis

---

## 📁 Project Structure

```
DataAugmentor/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── config/
│   ├── settings.py                 # App configuration
│   ├── code_review_config.json     # Default config
│   ├── code_review_config_python.json
│   ├── code_review_config_pyspark.json
│   ├── code_review_config_sql.json
│   ├── code_review_config_sparksql.json
│   └── code_review_config_generic.json
│
├── llm/
│   ├── client.py                   # OpenRouter client
│   ├── generate_synthetic_data.py  # Synthetic data generation
│   ├── augment_existing_data.py    # Data augmentation
│   ├── mask_pii_data.py            # PII masking
│   ├── generate_edge_case_data.py  # Edge case generation
│   └── code_review_llm.py          # Code review LLM calls
│
├── utils/
│   ├── cache.py                    # LLM response caching
│   ├── json_utils.py               # JSON parsing utilities
│   ├── validators.py               # Input validation
│   ├── file_comparator.py          # File comparison logic
│   └── code_analyzer.py            # Code analysis utilities
│
└── templates/
    ├── landing.html                # Landing page
    ├── index.html                  # DataAugmentor UI
    ├── file_comparison.html        # File Comparison UI
    ├── code_review.html            # Code Review UI
    └── partials/                   # Reusable UI components
        ├── styles.html
        ├── submit.js.html
        ├── ui.js.html
        └── schema.js.html
```

---

## ⚙️ Configuration

### Cache Settings (`config/settings.py`)

```python
CACHE_TTL = 3600  # Cache duration in seconds (1 hour)
CACHE_MAX_SIZE = 100  # Maximum cached items
```

### LLM Model

Default model: `openai/gpt-4o-mini` (used for PII masking and code review)

To change model, edit the respective files in `llm/` directory.

---

## 🐛 Troubleshooting

### Issue: "Failed to fetch" or API errors

**Solution:**
1. Check if `OPENROUTER_API_KEY` is set correctly
2. Verify API key is valid at [OpenRouter](https://openrouter.ai/)
3. Check internet connection
4. Review server logs for detailed error messages

### Issue: Server won't start

**Solution:**
1. Ensure Python 3.8+ is installed: `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Check if port 5000 is available
4. Run with debug: `python app.py` (debug mode is on by default)

### Issue: PII masking returns empty data

**Solution:**
1. Check that PII columns are detected (shown in UI)
2. Ensure at least one PII column is checked for masking
3. Try with a smaller dataset first
4. Check server logs for LLM response issues

### Issue: Code review fails

**Solution:**
1. Ensure file type is supported
2. Check file is valid (no syntax errors for auto-detect)
3. Select language manually if auto-detect fails
4. Try with a smaller code file first

---

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **PII Data**: Masked data is generated by AI and should be verified
- **Code Upload**: Uploaded code is NOT executed, only analyzed
- **File Comparison**: Files are processed in memory, not stored

---

## 📊 Performance Tips

1. **Caching**: LLM responses are cached for 1 hour by default
2. **File Size**: Keep files under 10,000 lines for optimal performance
3. **Row Limits**: Use appropriate row counts to avoid timeouts
4. **Batch Processing**: For large datasets, process in smaller batches

---

## 🤝 Contributing

To add a new language to Code Review:

1. Create `config/code_review_config_<language>.json`
2. Add language to `utils/code_analyzer.py` in `detect_language()`
3. Add test framework to `get_test_framework()`
4. Update dropdown in `templates/code_review.html`
5. Add to `detailed_languages` list in `app.py` if detailed config

---

## 📝 License

This project is provided as-is for educational and development purposes.

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs in the terminal
3. Verify all dependencies are installed
4. Ensure API key is configured correctly

---

## 🎉 Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key (Windows PowerShell)
$env:OPENROUTER_API_KEY="your-api-key-here"

# 3. Run the app
python app.py

# 4. Open browser
# Navigate to http://127.0.0.1:5000
```

**Enjoy using DataAugmentor! 🚀**
