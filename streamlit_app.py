"""
DataAugmentor Suite - Main Application
Modular Streamlit application with multiple AI-powered tools
"""
import streamlit as st

# Import shared components
from components import styles, navigation, footer

# Import page modules
from pages import home, data_augmentor, file_comparison, code_review, delivery_intelligence

# Page configuration
st.set_page_config(
    page_title="DataAugmentor Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
styles.apply_custom_styles()

# Render sidebar navigation and get selected tool
tool = navigation.render_sidebar()

# Route to appropriate page based on selection
if tool == "Home":
    home.render()
elif tool == "DataAugmentor":
    data_augmentor.render()
elif tool == "File Comparison":
    file_comparison.render()
elif tool == "Code Review":
    code_review.render()
elif tool == "Delivery Intelligence":
    delivery_intelligence.render()

# Render footer
footer.render_footer()
