"""
Footer component - Sidebar footer with resources
"""
import streamlit as st


def render_footer():
    """Render sidebar footer with resources and tips"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Resources")
    st.sidebar.markdown("[📖 Documentation](https://github.com)")
    st.sidebar.markdown("[🐛 Report Issue](https://github.com)")
    st.sidebar.info("💡 **Tip:** Use sample files from the `sample_data/` folder for demo!")
