"""
Enhanced Styles - FAANG-Level Design System
Professional, scalable, and accessible UI components
"""
import streamlit as st


def apply_custom_styles():
    """Apply comprehensive design system styles"""
    st.markdown("""
<style>
    /* ============================================
       DESIGN SYSTEM FOUNDATION
       ============================================ */
    
    /* CSS Variables for Theming */
    :root {
        /* Primary Colors */
        --color-primary-50: #eff6ff;
        --color-primary-100: #dbeafe;
        --color-primary-500: #3b82f6;
        --color-primary-600: #2563eb;
        --color-primary-700: #1d4ed8;
        --color-primary-800: #1e40af;
        
        /* Neutral Colors (Slate) */
        --color-slate-50: #f8fafc;
        --color-slate-100: #f1f5f9;
        --color-slate-200: #e2e8f0;
        --color-slate-300: #cbd5e1;
        --color-slate-400: #94a3b8;
        --color-slate-500: #64748b;
        --color-slate-600: #475569;
        --color-slate-700: #334155;
        --color-slate-800: #1e293b;
        --color-slate-900: #0f172a;
        
        /* Semantic Colors */
        --color-success: #10b981;
        --color-warning: #f59e0b;
        --color-error: #ef4444;
        --color-info: #3b82f6;
        
        /* Spacing Scale (8px base) */
        --space-xs: 0.25rem;  /* 4px */
        --space-sm: 0.5rem;   /* 8px */
        --space-md: 1rem;     /* 16px */
        --space-lg: 1.5rem;   /* 24px */
        --space-xl: 2rem;     /* 32px */
        --space-2xl: 3rem;    /* 48px */
        --space-3xl: 4rem;    /* 64px */
        
        /* Typography */
        --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --font-size-xs: 0.75rem;   /* 12px */
        --font-size-sm: 0.875rem;  /* 14px */
        --font-size-base: 1rem;    /* 16px */
        --font-size-lg: 1.125rem;  /* 18px */
        --font-size-xl: 1.25rem;   /* 20px */
        --font-size-2xl: 1.5rem;   /* 24px */
        --font-size-3xl: 2rem;     /* 32px */
        --font-size-4xl: 2.5rem;   /* 40px */
        
        /* Border Radius */
        --radius-sm: 0.375rem;  /* 6px */
        --radius-md: 0.5rem;    /* 8px */
        --radius-lg: 0.75rem;   /* 12px */
        --radius-xl: 1rem;      /* 16px */
        --radius-full: 9999px;
        
        /* Shadows */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        
        /* Transitions */
        --transition-fast: 150ms ease-in-out;
        --transition-base: 200ms ease-in-out;
        --transition-slow: 300ms ease-in-out;
    }
    
    /* ============================================
       GLOBAL STYLES
       ============================================ */
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: var(--font-family);
        color: var(--color-slate-700);
        background-color: var(--color-slate-50);
        font-size: var(--font-size-base);
        line-height: 1.6;
    }
    
    /* ============================================
       TYPOGRAPHY
       ============================================ */
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--color-slate-900);
        font-weight: 600;
        letter-spacing: -0.01em;
        line-height: 1.2;
        margin-top: 0;
    }
    
    h1 { font-size: var(--font-size-3xl); }
    h2 { font-size: var(--font-size-2xl); }
    h3 { font-size: var(--font-size-xl); }
    
    .main-header {
        font-size: var(--font-size-4xl);
        font-weight: 700;
        color: var(--color-slate-900);
        margin-bottom: var(--space-sm);
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-size: var(--font-size-lg);
        color: var(--color-slate-500);
        font-weight: 400;
        margin-bottom: var(--space-2xl);
    }
    
    /* ============================================
       SIDEBAR NAVIGATION
       ============================================ */
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid var(--color-slate-200);
        padding: var(--space-lg) 0;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 0 var(--space-md);
    }
    
    /* Sidebar Brand */
    [data-testid="stSidebar"] h1 {
        font-size: var(--font-size-xl);
        font-weight: 700;
        color: var(--color-slate-900);
        margin-bottom: var(--space-lg);
        padding: 0 var(--space-sm);
    }
    
    /* Category Headers */
    .nav-category {
        font-size: var(--font-size-xs);
        font-weight: 600;
        color: var(--color-slate-500);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: var(--space-lg) var(--space-sm) var(--space-sm);
    }
    
    /* Navigation Items */
    [data-testid="stSidebar"] .stRadio > label {
        background-color: transparent;
        border-radius: var(--radius-md);
        padding: var(--space-sm) var(--space-md);
        margin: var(--space-xs) 0;
        transition: all var(--transition-fast);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    [data-testid="stSidebar"] .stRadio > label:hover {
        background-color: var(--color-slate-100);
    }
    
    [data-testid="stSidebar"] .stRadio > label[data-checked="true"] {
        background-color: var(--color-primary-50);
        color: var(--color-primary-700);
        font-weight: 500;
    }
    
    /* API Key Warning */
    [data-testid="stSidebar"] .element-container:has(.stAlert) {
        margin-top: var(--space-xl);
        padding: 0 var(--space-sm);
    }
    
    /* ============================================
       BUTTONS
       ============================================ */
    
    .stButton > button {
        font-family: var(--font-family);
        font-size: var(--font-size-sm);
        font-weight: 500;
        padding: 0.625rem 1.25rem;
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
        border: 1px solid transparent;
        cursor: pointer;
        box-shadow: var(--shadow-sm);
    }
    
    /* Primary Button */
    .stButton > button[kind="primary"],
    .stButton > button:not([kind]) {
        background-color: var(--color-primary-600);
        color: #ffffff;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button:not([kind]):hover {
        background-color: var(--color-primary-700);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background-color: #ffffff;
        color: var(--color-slate-700);
        border-color: var(--color-slate-300);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: var(--color-slate-50);
        border-color: var(--color-slate-400);
    }
    
    /* ============================================
       FORM CONTROLS
       ============================================ */
    
    /* Text Inputs */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        background-color: #ffffff;
        color: var(--color-slate-900) !important;
        border: 1px solid var(--color-slate-300);
        border-radius: var(--radius-md);
        padding: var(--space-sm) var(--space-md);
        font-size: var(--font-size-sm);
        transition: all var(--transition-fast);
    }
    
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: var(--color-primary-600);
        box-shadow: 0 0 0 3px var(--color-primary-50);
        outline: none;
    }
    
    /* Select Boxes */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff;
        border: 1px solid var(--color-slate-300);
        border-radius: var(--radius-md);
    }
    
    .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: var(--color-primary-600);
        box-shadow: 0 0 0 3px var(--color-primary-50);
    }
    
    /* Dropdown text visibility */
    div[data-baseweb="select"] span,
    ul[data-baseweb="menu"] li {
        color: var(--color-slate-900) !important;
    }
    
    /* File Uploader */
    .stFileUploader {
        background-color: #ffffff;
        border: 2px dashed var(--color-slate-300);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        transition: all var(--transition-base);
    }
    
    .stFileUploader:hover {
        border-color: var(--color-primary-600);
        background-color: var(--color-primary-50);
    }
    
    /* ============================================
       CARDS
       ============================================ */
    
    .tool-card {
        background: #ffffff;
        border: 1px solid var(--color-slate-200);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        height: 100%;
        min-height: 420px;
        display: flex;
        flex-direction: column;
        transition: all var(--transition-base);
        box-shadow: var(--shadow-sm);
    }
    
    .tool-card:hover {
        border-color: var(--color-slate-300);
        box-shadow: var(--shadow-lg);
        transform: translateY(-4px);
    }
    
    .card-icon {
        font-size: 2rem;
        margin-bottom: var(--space-lg);
        background: var(--color-slate-100);
        width: 3.5rem;
        height: 3.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius-lg);
        flex-shrink: 0;
    }
    
    .tool-card h3 {
        margin-top: 0;
        margin-bottom: var(--space-sm);
        font-size: var(--font-size-xl);
    }
    
    .tool-card p {
        color: var(--color-slate-600);
        font-size: var(--font-size-sm);
        line-height: 1.6;
        margin-bottom: var(--space-lg);
        flex-grow: 1;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    /* ============================================
       BADGES & STATUS
       ============================================ */
    
    .badge {
        display: inline-flex;
        align-items: center;
        padding: var(--space-xs) var(--space-md);
        background-color: var(--color-slate-100);
        color: var(--color-slate-700);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-success { background-color: #d1fae5; color: #065f46; }
    .badge-warning { background-color: #fef3c7; color: #92400e; }
    .badge-error { background-color: #fee2e2; color: #991b1b; }
    .badge-info { background-color: var(--color-primary-50); color: var(--color-primary-700); }
    
    /* ============================================
       ALERTS & NOTIFICATIONS
       ============================================ */
    
    .stAlert {
        border-radius: var(--radius-md);
        padding: var(--space-md);
        border-left: 4px solid;
    }
    
    [data-baseweb="notification"][kind="info"] {
        background-color: var(--color-primary-50);
        border-left-color: var(--color-primary-600);
    }
    
    [data-baseweb="notification"][kind="success"] {
        background-color: #d1fae5;
        border-left-color: var(--color-success);
    }
    
    [data-baseweb="notification"][kind="warning"] {
        background-color: #fef3c7;
        border-left-color: var(--color-warning);
    }
    
    [data-baseweb="notification"][kind="error"] {
        background-color: #fee2e2;
        border-left-color: var(--color-error);
    }
    
    /* ============================================
       DATA DISPLAY
       ============================================ */
    
    /* Tables */
    .stDataFrame {
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: var(--space-lg);
        border-radius: var(--radius-md);
        border: 1px solid var(--color-slate-200);
    }
    
    /* ============================================
       UTILITIES
       ============================================ */
    
    hr {
        margin: var(--space-2xl) 0;
        border: none;
        border-top: 1px solid var(--color-slate-200);
    }
    
    /* Back Button */
    .back-btn {
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        text-decoration: none;
        color: var(--color-slate-600);
        font-weight: 500;
        font-size: var(--font-size-sm);
        margin-bottom: var(--space-lg);
        padding: var(--space-sm) var(--space-md);
        border: 1px solid var(--color-slate-200);
        border-radius: var(--radius-md);
        background: #ffffff;
        transition: all var(--transition-fast);
        cursor: pointer;
    }
    
    .back-btn:hover {
        background: var(--color-slate-50);
        color: var(--color-primary-600);
        border-color: var(--color-slate-300);
    }
    
    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */
    
    @media (max-width: 640px) {
        .main-header {
            font-size: var(--font-size-2xl);
        }
        
        .tool-card {
            min-height: auto;
            padding: var(--space-lg);
        }
    }
    
    /* ============================================
       ACCESSIBILITY
       ============================================ */
    
    /* Focus Indicators */
    *:focus-visible {
        outline: 2px solid var(--color-primary-600);
        outline-offset: 2px;
    }
    
    /* Reduced Motion */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* High Contrast Mode */
    @media (prefers-contrast: high) {
        .tool-card {
            border-width: 2px;
        }
        
        .stButton > button {
            border-width: 2px;
        }
    }
</style>
""", unsafe_allow_html=True)
