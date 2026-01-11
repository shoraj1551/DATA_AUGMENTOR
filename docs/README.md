# DataAugmentor - Technical Documentation

Complete technical documentation explaining how each functionality works, including frontend, backend, and LLM integration.

## 📚 Documentation Structure

### Tool-Specific Guides:
1. **[DataAugmentor Tool](./dataaugmentor_technical.md)** - Data generation and augmentation
2. **[File Comparison Tool](./file_comparison_technical.md)** - File comparison engine
3. **[Code Review Tool](./code_review_technical.md)** - AI-powered code analysis

### Architecture Guides:
4. **[System Architecture](./architecture.md)** - Overall system design
5. **[LLM Integration](./llm_integration.md)** - How AI/LLM is used
6. **[Caching Strategy](./caching.md)** - Performance optimization

### Deployment:
7. **[Streamlit Deployment](./streamlit_deployment.md)** - Deploy with Streamlit Cloud

---

## Quick Links

- **Setup**: See [README.md](../README.md)
- **Sample Data**: See [sample_data/](../sample_data/)
- **Configuration**: See [config/](../config/)

---

## Overview

DataAugmentor Suite is a Flask-based web application with three main tools:

1. **DataAugmentor** - AI-powered data generation and manipulation
2. **File Comparison** - Compare CSV/TXT/JSON files
3. **Code Review & Testing** - Automated code analysis for 20+ languages

### Technology Stack

- **Backend**: Flask (Python web framework)
- **LLM**: OpenRouter API (GPT-4o-mini)
- **Data Processing**: Pandas
- **Caching**: Custom TTL cache
- **Frontend**: HTML/CSS/JavaScript
- **Alternative UI**: Streamlit

### Key Features

- **LLM Response Caching** - Reduces API calls and improves performance
- **Language-Specific Configs** - Tailored code review rules
- **PII Detection** - Automatic identification of sensitive data
- **Multi-Format Support** - CSV, JSON, TXT, 20+ code languages

---

## How It Works (High-Level)

### Request Flow

```
User Request
    ↓
Flask Route Handler
    ↓
Input Validation
    ↓
LLM/Processing Module
    ↓
Cache Check → [Cache Hit] → Return Cached Result
    ↓ [Cache Miss]
OpenRouter API Call
    ↓
Response Parsing
    ↓
Cache Storage
    ↓
Return Result to User
```

### Data Flow

```
Frontend (HTML/JS)
    ↓ HTTP POST
Backend (Flask)
    ↓ Function Call
LLM Module
    ↓ API Request
OpenRouter
    ↓ JSON Response
JSON Parser
    ↓ DataFrame/Dict
Frontend Display
```

---

## Security Considerations

### API Key Management

**Environment Variable (Recommended)**:
```bash
export OPENROUTER_API_KEY="your-key"
```

**Streamlit Secrets**:
```toml
# .streamlit/secrets.toml
OPENROUTER_API_KEY = "your-key"
```

**Never**:
- Commit API keys to git
- Hardcode keys in source files
- Share keys publicly

### Data Privacy

- **No Data Storage**: Uploaded files are processed in memory only
- **No Code Execution**: Code is analyzed, never executed
- **PII Masking**: AI-generated, should be verified
- **Local Processing**: File comparison happens locally

---

## Performance Optimization

### Caching Strategy

- **TTL**: 1 hour (configurable)
- **Max Size**: 100 items (configurable)
- **Cache Key**: Hash of (function_name + parameters)
- **Benefits**: 
  - Reduces API costs
  - Faster response times
  - Better user experience

### File Size Limits

- **Code Files**: 10,000 lines recommended
- **CSV Files**: 50 rows for LLM processing (sampled if larger)
- **JSON/TXT**: Reasonable file sizes

---

## Error Handling

### Graceful Degradation

1. **API Failures**: Clear error messages to user
2. **Invalid Input**: Validation before processing
3. **Parsing Errors**: Specific error with filename
4. **Timeout**: Configurable timeout limits

### Logging

- **Level**: DEBUG (development), INFO (production)
- **Location**: Console output
- **Content**: Request details, errors, cache hits/misses

---

## Next Steps

Read the detailed technical documentation for each tool:

1. [DataAugmentor Technical Guide](./dataaugmentor_technical.md)
2. [File Comparison Technical Guide](./file_comparison_technical.md)
3. [Code Review Technical Guide](./code_review_technical.md)
