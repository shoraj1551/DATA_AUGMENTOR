"""
DataAugmentor Suite - Main Application
Modular Streamlit application with multiple AI-powered tools
"""
import streamlit as st

# Import shared components
from app_components import styles, navigation, footer

# Import page modules
from page_modules import home, data_augmentor, file_comparison, code_review, delivery_intelligence, web_scraper, document_parser

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
    from tools.data_augmentor import ui
    ui.render()
elif tool == "File Comparison":
    from tools.file_comparison import ui
    ui.render()
elif tool == "Code Review":
    from tools.code_review import ui
    ui.render()
elif tool == "Delivery Intelligence":
    from tools.delivery_intelligence import ui
    ui.render()
elif tool == "Web Data Scraper":
    from tools.web_scraper import ui
    ui.render()
elif tool == "Document Parser":
    from tools.document_parser import ui
    ui.render()

# Render footer
footer.render_footer()
