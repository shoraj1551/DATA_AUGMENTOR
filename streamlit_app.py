"""
DataAugmentor Suite - Main Application
Professional Streamlit application with FAANG-level UI/UX
OPTIMIZED: Preloads favorite tools for instant navigation
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

# ============================================
# PERFORMANCE OPTIMIZATION: Smart Preloading
# ============================================

# Get user's favorite tools from preferences
from common.utils.preferences import UserPreferences
user_prefs = UserPreferences()
favorite_tools = user_prefs.get_favorites()

# Preload favorite tools for instant navigation
PRELOADED_MODULES = {}

# Always preload home
from page_modules import home
PRELOADED_MODULES['home'] = home

# Preload favorite tools
if 'data_profiling' in favorite_tools:
    from tools.data_profiling import ui as data_profiling_ui
    PRELOADED_MODULES['data_profiling'] = data_profiling_ui

if 'company_intelligence' in favorite_tools:
    from tools.company_intelligence import ui as company_intelligence_ui
    PRELOADED_MODULES['company_intelligence'] = company_intelligence_ui

if 'code_review' in favorite_tools:
    from tools.code_review import ui as code_review_ui
    PRELOADED_MODULES['code_review'] = code_review_ui

if 'data_augmentor' in favorite_tools:
    from tools.data_augmentor import ui as data_augmentor_ui
    PRELOADED_MODULES['data_augmentor'] = data_augmentor_ui

if 'file_comparison' in favorite_tools:
    from tools.file_comparison import ui as file_comparison_ui
    PRELOADED_MODULES['file_comparison'] = file_comparison_ui

if 'delivery_intelligence' in favorite_tools:
    from tools.delivery_intelligence import ui as delivery_intelligence_ui
    PRELOADED_MODULES['delivery_intelligence'] = delivery_intelligence_ui

if 'web_scraper' in favorite_tools:
    from tools.web_scraper import ui as web_scraper_ui
    PRELOADED_MODULES['web_scraper'] = web_scraper_ui

if 'document_parser' in favorite_tools:
    from tools.document_parser import ui as document_parser_ui
    PRELOADED_MODULES['document_parser'] = document_parser_ui

if 'ocr_intelligence' in favorite_tools:
    from tools.ocr_intelligence import ui as ocr_intelligence_ui
    PRELOADED_MODULES['ocr_intelligence'] = ocr_intelligence_ui

if 'dq_rules' in favorite_tools:
    from tools.dq_rules import ui as dq_rules_ui
    PRELOADED_MODULES['dq_rules'] = dq_rules_ui

if 'requirement_interpreter' in favorite_tools:
    from tools.requirement_interpreter import ui as requirement_interpreter_ui
    PRELOADED_MODULES['requirement_interpreter'] = requirement_interpreter_ui

if 'knowledge_base' in favorite_tools:
    from tools.knowledge_base import ui as knowledge_base_ui
    PRELOADED_MODULES['knowledge_base'] = knowledge_base_ui

if 'insurance_claims' in favorite_tools:
    from tools.insurance_claims import ui as insurance_claims_ui
    PRELOADED_MODULES['insurance_claims'] = insurance_claims_ui

if 'contact_intelligence' in favorite_tools:
    from tools.contact_intelligence import ui as contact_intelligence_ui
    PRELOADED_MODULES['contact_intelligence'] = contact_intelligence_ui

if 'selling_opportunity' in favorite_tools:
    from tools.selling_opportunity import ui as selling_opportunity_ui
    PRELOADED_MODULES['selling_opportunity'] = selling_opportunity_ui

if 'strategic_sales' in favorite_tools:
    from tools.strategic_sales import ui as strategic_sales_ui
    PRELOADED_MODULES['strategic_sales'] = strategic_sales_ui

# ============================================
# Navigation & Routing
# ============================================

# Render navigation and get selected tool
tool = navigation.render_navigation()

# Check if tool is preloaded (instant) or needs lazy loading (with spinner)
if tool in PRELOADED_MODULES:
    # INSTANT LOAD - Favorite tool
    PRELOADED_MODULES[tool].render()
else:
    # LAZY LOAD - Non-favorite tool with spinner
    with st.spinner("⏳ Loading... Thanks for your patience!"):
        if tool == "data_augmentor":
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
        elif tool == "knowledge_base":
            from tools.knowledge_base import ui
            ui.render()
        elif tool == "insurance_claims":
            from tools.insurance_claims import ui
            ui.render()
        elif tool == "contact_intelligence":
            from tools.contact_intelligence import ui
            ui.render()
        elif tool == "company_intelligence":
            from tools.company_intelligence import ui
            ui.render()
        elif tool == "selling_opportunity":
            from tools.selling_opportunity import ui
            ui.render()
        elif tool == "strategic_sales":
            from tools.strategic_sales import ui
            ui.render()

# Render footer
footer.render_footer()
