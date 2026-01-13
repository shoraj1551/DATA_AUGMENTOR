"""
DataAugmentor Suite - Main Application
Professional Streamlit application with FAANG-level UI/UX
"""
import streamlit as st

# Import shared components
from common.ui import styles, navigation
from app_components import footer

# Page configuration
st.set_page_config(
    page_title="DataAugmentor Suite - AI Productivity Tools",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "DataAugmentor Suite v2.0 - Professional AI-powered productivity tools"
    }
)

# Apply enhanced styles
styles.apply_custom_styles()

# Render navigation and get selected tool
tool = navigation.render_navigation()

# Route to appropriate page based on selection
if tool == "home":
    from page_modules import home
    home.render()
elif tool == "data_augmentor":
    from tools.data_augmentor import ui
    ui.render()
elif tool == "file_comparison":
    from tools.file_comparison import ui
    ui.render()
elif tool == "code_review":
    from tools.code_review import ui
    ui.render()
elif tool == "delivery_intelligence":
    from tools.delivery_intelligence import ui
    ui.render()
elif tool == "web_scraper":
    from tools.web_scraper import ui
    ui.render()
elif tool == "document_parser":
    from tools.document_parser import ui
    ui.render()
elif tool == "ocr_intelligence":
    from tools.ocr_intelligence import ui
    ui.render()
elif tool == "data_profiling":
    from tools.data_profiling import ui
    ui.render()
elif tool == "dq_rules":
    from tools.dq_rules import ui
    ui.render()
elif tool == "requirement_interpreter":
    from tools.requirement_interpreter import ui
    ui.render()

# Render footer
footer.render_footer()
