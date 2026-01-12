"""
Navigation component - Sidebar navigation and session state management
"""
import streamlit as st


def initialize_session_state():
    """Initialize session state variables"""
    if "tool" not in st.session_state:
        st.session_state.tool = "Home"


def go_to_tool(tool_name):
    """Navigate to a specific tool (callback)"""
    st.session_state.tool = tool_name
    st.session_state.sidebar_tool_radio = tool_name


def back_to_home(tool_name):
    """Render back to home button"""
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.button("← Back to Home", key=f"back_{tool_name}", type="secondary", help="Return to Dashboard", on_click=go_to_tool, args=("Home",))


def render_sidebar():
    """Render sidebar navigation and return selected tool"""
    st.sidebar.markdown("### 🧭 Navigation")
    
    # Initialize session state
    initialize_session_state()
    
    # Update sidebar selection from session state logic (bi-directional sync)
    selection = st.sidebar.radio(
        "Go to:",
        ["Home", "DataAugmentor", "File Comparison", "Code Review", "Delivery Intelligence", "Web Data Scraper", "Document Parser"],
        index=["Home", "DataAugmentor", "File Comparison", "Code Review", "Delivery Intelligence", "Web Data Scraper", "Document Parser"].index(st.session_state.tool) if st.session_state.tool in ["Home", "DataAugmentor", "File Comparison", "Code Review", "Delivery Intelligence", "Web Data Scraper", "Document Parser"] else 0,
        label_visibility="collapsed",
        key="sidebar_tool_radio"
    )
    
    # Update session state when sidebar changes (but don't rerun - let the main loop handle it)
    if selection != st.session_state.tool:
        st.session_state.tool = selection
    
    tool = st.session_state.tool
    
    # Check API key using the centralized settings
    from config import settings
    if not settings.OPENROUTER_API_KEY:
        st.sidebar.warning("⚠️ API Key missing")
        st.sidebar.markdown(
            """
            <div style="font-size:0.8em; color:#64748b; margin-top:-10px; margin-bottom:10px;">
            Set <code>OPENROUTER_API_KEY</code> in secrets or env vars to enable AI features.
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    return tool
