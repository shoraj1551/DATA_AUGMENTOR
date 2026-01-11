# Streamlit Deployment Guide

Complete guide to deploying DataAugmentor Suite on Streamlit Cloud for easy sharing and demo.

---

## Why Streamlit?

- **Easy Deployment**: One-click deploy from GitHub
- **Free Hosting**: Streamlit Community Cloud is free
- **No Server Management**: Fully managed infrastructure
- **Secure Secrets**: Built-in secrets management for API keys
- **Auto-Updates**: Deploys automatically on git push

---

## Prerequisites

1. **GitHub Account**: To host code
2. **Streamlit Account**: Sign up at [streamlit.io](https://streamlit.io)
3. **OpenRouter API Key**: For LLM features

---

## Step 1: Prepare Repository

### 1.1 Add Streamlit to Requirements

```bash
# requirements.txt
Flask==3.1.2
pandas==2.3.3
openai==2.14.0
streamlit==1.29.0  # Add this line
```

### 1.2 Create .streamlit Directory

```bash
mkdir .streamlit
```

### 1.3 Create config.toml

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

### 1.4 Update .gitignore

```gitignore
# Add to .gitignore
.streamlit/secrets.toml  # Don't commit secrets!
```

---

## Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - DataAugmentor Suite"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/DataAugmentor.git
git push -u origin main
```

---

## Step 3: Deploy on Streamlit Cloud

### 3.1 Sign In

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub

### 3.2 Create New App

1. Click "New app"
2. Select your repository: `YOUR_USERNAME/DataAugmentor`
3. Set main file: `streamlit_app.py`
4. Click "Deploy"

### 3.3 Configure Secrets

1. In Streamlit Cloud dashboard, click your app
2. Click "⚙️ Settings"
3. Click "Secrets"
4. Add your API key:

```toml
# Secrets (TOML format)
OPENROUTER_API_KEY = "your-api-key-here"
```

5. Click "Save"

---

## Step 4: Access Your App

Your app will be available at:
```
https://YOUR_USERNAME-dataaugmentor-streamlit-app-XXXXX.streamlit.app
```

Share this URL with friends for demo!

---

## Local Testing

### Run Streamlit Locally

```bash
# Set API key
export OPENROUTER_API_KEY="your-key"

# Run Streamlit
streamlit run streamlit_app.py
```

App opens at: `http://localhost:8501`

### Test All Features

1. **DataAugmentor**: Upload `sample_data/customers.csv`
2. **File Comparison**: Compare `products_v1.csv` and `products_v2.csv`
3. **Code Review**: Upload `sample_code.py`

---

## Streamlit App Features

### Home Page

- Overview of all tools
- Navigation sidebar
- API key status indicator

### DataAugmentor

- All 4 operations in one interface
- File upload with preview
- Download buttons for results
- Progress spinners

### File Comparison

- Side-by-side file upload
- Expandable result sections
- Statistics metrics
- Clean, organized display

### Code Review

- Language selector
- Code preview
- Tabbed results
- Download generated tests

---

## Differences from Flask App

| Feature | Flask App | Streamlit App |
|---------|-----------|---------------|
| UI Framework | HTML/CSS/JS | Streamlit widgets |
| Deployment | Manual server | One-click cloud |
| State Management | Session/cookies | st.session_state |
| File Upload | FormData | st.file_uploader |
| API Key | Environment var | Streamlit secrets |
| Styling | Custom CSS | Streamlit themes |

---

## Security Best Practices

### 1. API Key Management

**❌ Never do this**:
```python
OPENROUTER_API_KEY = "sk-or-v1-xxxxx"  # Hardcoded!
```

**✅ Always do this**:
```python
import os
api_key = os.getenv("OPENROUTER_API_KEY")
# or
api_key = st.secrets["OPENROUTER_API_KEY"]
```

### 2. Secrets in Streamlit

**Local Development** (`.streamlit/secrets.toml`):
```toml
OPENROUTER_API_KEY = "your-local-key"
```

**Production** (Streamlit Cloud):
- Set in web dashboard under Settings → Secrets
- Never commit `secrets.toml` to git

### 3. Environment Variables

```python
# streamlit_app.py
import os
import streamlit as st

# Try Streamlit secrets first, fallback to env var
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except:
    api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("⚠️ API Key not configured!")
    st.stop()
```

---

## Monitoring & Debugging

### View Logs

1. Go to Streamlit Cloud dashboard
2. Click your app
3. Click "Manage app" → "Logs"
4. View real-time logs

### Common Issues

**Issue**: App won't start
- Check `requirements.txt` has all dependencies
- Verify `streamlit_app.py` exists
- Check logs for import errors

**Issue**: API key not working
- Verify secrets are set correctly
- Check for typos in secret name
- Restart app after adding secrets

**Issue**: File upload fails
- Check file size limits (200MB max)
- Verify file type is supported
- Check logs for parsing errors

---

## Performance Optimization

### Caching

```python
@st.cache_data(ttl=3600)
def generate_synthetic_data(prompt, num_rows):
    # Cached for 1 hour
    ...
```

### Session State

```python
# Store results in session
if 'results' not in st.session_state:
    st.session_state.results = None

# Reuse without recomputing
if st.button("Analyze"):
    st.session_state.results = analyze_code(...)
```

### Resource Limits

- **Memory**: 1GB per app (free tier)
- **CPU**: Shared resources
- **Timeout**: 10 minutes max execution
- **File Size**: 200MB upload limit

---

## Updating Your App

### Auto-Deploy

1. Make changes locally
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Update feature X"
git push
```
3. Streamlit Cloud auto-deploys in ~2 minutes

### Manual Reboot

1. Go to Streamlit Cloud dashboard
2. Click "⋮" menu
3. Click "Reboot app"

---

## Sharing Your App

### Public Link

Share the URL:
```
https://YOUR_USERNAME-dataaugmentor-streamlit-app-XXXXX.streamlit.app
```

### Embed in Website

```html
<iframe
  src="https://YOUR_APP_URL.streamlit.app/?embed=true"
  height="600"
  width="100%"
></iframe>
```

### Password Protection

In Streamlit Cloud:
1. Settings → Sharing
2. Enable "Require password"
3. Set password
4. Share password with authorized users

---

## Cost Considerations

### Free Tier (Community Cloud)

- **Cost**: $0
- **Apps**: Unlimited public apps
- **Resources**: 1GB RAM, shared CPU
- **Support**: Community forum

### Paid Tier (Streamlit for Teams)

- **Cost**: $250/month (5 users)
- **Apps**: Unlimited private apps
- **Resources**: More RAM/CPU
- **Support**: Email support

**Recommendation**: Start with free tier for demos

---

## Alternative: Run Flask + Streamlit

You can run both simultaneously:

```bash
# Terminal 1: Flask app
python app.py  # http://localhost:5000

# Terminal 2: Streamlit app
streamlit run streamlit_app.py  # http://localhost:8501
```

**Use Cases**:
- Flask: Production API
- Streamlit: Internal demo/testing

---

## Next Steps

1. ✅ Deploy to Streamlit Cloud
2. ✅ Test all features with sample data
3. ✅ Share URL with friends
4. 📖 Read [Streamlit Docs](https://docs.streamlit.io)
5. 🎨 Customize theme in `config.toml`

---

## Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Deployment Guide**: https://docs.streamlit.io/streamlit-community-cloud
- **Sample Apps**: https://streamlit.io/gallery
- **Community Forum**: https://discuss.streamlit.io

---

## Troubleshooting Checklist

- [ ] API key set in Streamlit secrets
- [ ] All dependencies in `requirements.txt`
- [ ] `streamlit_app.py` exists in root
- [ ] No hardcoded secrets in code
- [ ] `.streamlit/secrets.toml` in `.gitignore`
- [ ] Sample data files included
- [ ] App tested locally first
- [ ] GitHub repo is public (for free tier)

---

**Ready to deploy? Follow the steps above and share your app!** 🚀
