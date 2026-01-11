"""
Navigation component - Sidebar navigation and session state management
"""
import streamlit as st


def initialize_session_state():
    """Initialize session state variables"""
    if "tool" not in st.session_state:
        st.session_state.tool = "Home"


def back_to_home(tool_name):
    """Render back to home button"""
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("← Back to Home", key=f"back_{tool_name}", type="secondary", help="Return to Dashboard"):
            st.session_state.tool = "Home"
            st.rerun()


def render_sidebar():
    """Render sidebar navigation and return selected tool"""
    st.sidebar.markdown("### 🧭 Navigation")
    
    # Initialize session state
    initialize_session_state()
    
    # Update sidebar selection from session state logic (bi-directional sync)
    selection = st.sidebar.radio(
        "Go to:",
        ["Home", "DataAugmentor", "File Comparison", "Code Review", "Delivery Intelligence"],
        index=["Home", "DataAugmentor", "File Comparison", "Code Review", "Delivery Intelligence"].index(st.session_state.tool) if st.session_state.tool in ["Home", "DataAugmentor", "File Comparison", "Code Review", "Delivery Intelligence"] else 0,
        label_visibility="collapsed",
        key="sidebar_tool_radio"
    )
    
    # Update session state when sidebar changes (but don't rerun - let the main loop handle it)
    if selection != st.session_state.tool:
        st.session_state.tool = selection
    
    tool = st.session_state.tool
    
    # Check API key
    import os
    if not os.getenv("OPENROUTER_API_KEY"):
        st.sidebar.error("⚠️ API Key missing")
    
    return tool
