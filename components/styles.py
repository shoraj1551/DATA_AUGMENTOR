"""
Styles component - Custom CSS for the Streamlit app
"""
import streamlit as st


def apply_custom_styles():
    """Apply all custom CSS styles for the application"""
    st.markdown("""
<style>
    /* 1. Global Typography & Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1e293b; /* Slate-800 for high contrast text */
        background-color: #f8fafc; /* Very light slate background */
    }

    /* 2. Headers */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: #0f172a; /* Slate-900 */
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #64748b; /* Slate-500 */
        font-weight: 400;
        margin-bottom: 3rem;
    }
    
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    /* 3. Cards (Minimalist) */
    .tool-card {
        background: #ffffff;
        border: 1px solid #e2e8f0; /* Slate-200 */
        border-radius: 12px;
        padding: 2rem;
        height: 100%;
        transition: all 0.2s ease-in-out;
    }

    .tool-card:hover {
        border-color: #cbd5e1; /* Slate-300 */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transform: translateY(-2px);
    }
    
    .card-icon {
        font-size: 2rem;
        margin-bottom: 1.5rem;
        background: #f1f5f9;
        width: 3.5rem;
        height: 3.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
    }

    /* 4. Buttons (Professional Blue) */
    .stButton > button {
        background-color: #2563eb; /* Blue-600 */
        color: #ffffff;
        border: 1px solid transparent;
        padding: 0.625rem 1.25rem;
        font-size: 0.95rem;
        font-weight: 500;
        border-radius: 8px;
        transition: background-color 0.15s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .stButton > button:hover {
        background-color: #1d4ed8; /* Blue-700 */
        border-color: transparent;
        color: #ffffff;
    }
    
    .stButton > button:active {
        background-color: #1e40af; /* Blue-800 */
    }

    /* 5. Inputs & Dropdowns (High Visibility) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff;
        color: #0f172a !important; /* Ensure text is dark and visible */
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: #2563eb;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    /* Fix dropdown text visibility */
    div[data-baseweb="select"] span {
        color: #0f172a !important; /* Force dark text for selected option */
    }
    
    /* Dropdown menu items */
    ul[data-baseweb="menu"] li {
        color: #0f172a !important;
    }

    /* 6. Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] .css-17lntkn {
        color: #475569;
    }

    /* 7. Utilities */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        background-color: #f1f5f9; /* Slate-100 */
        color: #475569; /* Slate-600 */
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    
    hr {
        margin: 2rem 0;
        border-color: #e2e8f0;
    }

    /* 8. Back Button */
    .back-btn {
        display: inline-flex;
        align-items: center;
        text-decoration: none;
        color: #64748b;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 20px;
        cursor: pointer;
        border: 1px solid #e2e8f0;
        padding: 5px 12px;
        border-radius: 6px;
        background: white;
        transition: all 0.2s;
    }
    
    .back-btn:hover {
        background: #f8fafc;
        color: #2563eb;
        border-color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)
