# .env File Setup Guide

## ✅ Created Files

1. **`.env`** - For Flask app (local development)
2. **`.streamlit/secrets.toml`** - For Streamlit app (local & cloud)

Both files are in `.gitignore` and will **NOT** be pushed to GitHub.

---

## 🔑 Setup Instructions

### For Flask App (Local)

Edit `.env` file:
```env
OPENROUTER_API_KEY=your-actual-api-key-here
```

### For Streamlit App (Local)

Edit `.streamlit/secrets.toml` file:
```toml
OPENROUTER_API_KEY = "your-actual-api-key-here"
```

### For Streamlit Cloud (Production)

1. Go to https://share.streamlit.io
2. Click your app
3. Click "⚙️ Settings" → "Secrets"
4. Add:
```toml
OPENROUTER_API_KEY = "your-actual-api-key-here"
```
5. Click "Save"

---

## ✅ Security Verified

- ✅ `.env` is in `.gitignore`
- ✅ `.streamlit/secrets.toml` is in `.gitignore`
- ✅ API key will NOT be pushed to GitHub
- ✅ Code updated to use Streamlit secrets

---

## 🔄 How It Works

**`config/settings.py` now:**
1. Tries to load from Streamlit secrets (if running Streamlit)
2. Falls back to environment variable (if running Flask)
3. Shows warning if not configured

This works for both Flask and Streamlit apps automatically!

---

## 📝 Next Steps

1. **Add your API key** to `.streamlit/secrets.toml`
2. **Test locally**: `streamlit run streamlit_app.py`
3. **Deploy to Streamlit Cloud** and add secrets there
4. **Never commit** these secret files to git

**Your API key is now secure!** 🔒
