"""
Enhanced Navigation - Clean, Scalable Sidebar Design
Professional navigation with proper collapsible categories
"""
import streamlit as st


# Tool Registry - Single source of truth for all tools
TOOL_REGISTRY = {
    "code_review": {
        "name": "Code Review",
        "category": "core",
        "description": "AI-powered code analysis",
        "status": "stable"
    },
    "data_augmentor": {
        "name": "Data Augmentor",
        "category": "core",
        "description": "Generate and mask data",
        "status": "stable"
    },
    "file_comparison": {
        "name": "File Comparison",
        "category": "utilities",
        "description": "Compare datasets precisely",
        "status": "stable"
    },
    "document_parser": {
        "name": "Text Document Parser",
        "category": "utilities",
        "description": "Extract text from PDF, TXT, and PPT files",
        "status": "beta"
    },
    "web_scraper": {
        "name": "Web Scraper",
        "category": "utilities",
        "description": "Compliant web scraping with AI extraction",
        "status": "beta"
    },
    "insurance_claims": {
        "name": "Insurance Claims Review",
        "category": "utilities",
        "description": "Analyze policies and validate claims automatically",
        "status": "gamma"
    },
    "contact_intelligence": {
        "name": "Contact Intelligence",
        "category": "utilities",
        "description": "Find and score business contacts with AI",
        "status": "gamma"
    },
    "delivery_intelligence": {
        "name": "Delivery Intelligence",
        "category": "planning",
        "description": "AI execution planning",
        "status": "beta"
    },
    "ocr_intelligence": {
        "name": "OCR Image Intelligence",
        "category": "utilities",
        "description": "Extract text from images and scanned documents",
        "status": "beta"
    },
    "data_profiling": {
        "name": "Data Profiling & Auto-EDA",
        "category": "analytics",
        "description": "Automatically profile datasets and generate insights",
        "status": "gamma"
    },
    "dq_rules": {
        "name": "DQ Rule Generator",
        "category": "analytics",
        "description": "Generate intelligent data quality rules automatically",
        "status": "gamma"
    },
    "requirement_interpreter": {
        "name": "Requirement Interpreter",
        "category": "analytics",
        "description": "Translate business questions into data specifications",
        "status": "gamma"
    },
    "knowledge_base": {
        "name": "Knowledge Base Builder",
        "category": "analytics",
        "description": "Capture and query project knowledge with natural language",
        "status": "gamma"
    },
    "company_intelligence": {
        "name": "Company Intelligence",
        "category": "sales",
        "description": "Structured company profiles with natural language Q&A",
        "status": "gamma"
    },
    "selling_opportunity": {
        "name": "Selling Opportunity Finder",
        "category": "sales",
        "description": "Identify selling opportunities from market signals",
        "status": "gamma"
    },
    "strategic_sales": {
        "name": "Strategic Sales Intelligence",
        "category": "sales",
        "description": "4-in-1: Decision history, competitive narrative, procurement & risk analysis",
        "status": "gamma"
    }
}

# Category Configuration
CATEGORIES = {
    "core": {
        "label": "Core Tools",
        "order": 1
    },
    "utilities": {
        "label": "Utilities",
        "order": 2
    },
    "planning": {
        "label": "Planning",
        "order": 3
    },
    "analytics": {
        "label": "Analytics & Insights",
        "order": 4
    },
    "sales": {
        "label": "Sales Intelligence",
        "order": 5
    }
}


def initialize_session_state():
    """Initialize session state variables with URL query parameter support"""
    # Check URL query parameters first for persistence across refreshes
    query_params = st.query_params
    url_tool = query_params.get("tool", None)
    
    if "tool" not in st.session_state:
        # Use URL parameter if available, otherwise default to home
        st.session_state.tool = url_tool if url_tool else "home"
    elif url_tool and url_tool != st.session_state.tool:
        # URL changed (e.g., user clicked back button), update session state
        st.session_state.tool = url_tool
    
    # Initialize category collapse states - all expanded by default
    if "collapsed_categories" not in st.session_state:
        st.session_state.collapsed_categories = set()
    # Initialize favorites from persistent storage
    if "favorite_tools" not in st.session_state:
        from common.utils.preferences import UserPreferences
        prefs = UserPreferences()
        st.session_state.favorite_tools = prefs.get_favorites()
    # Store preferences instance
    if "user_prefs" not in st.session_state:
        from common.utils.preferences import UserPreferences
        st.session_state.user_prefs = UserPreferences()


def toggle_favorite(tool_id):
    """Toggle a tool's favorite status with persistent storage"""
    # Toggle in session state
    if tool_id in st.session_state.favorite_tools:
        st.session_state.favorite_tools.remove(tool_id)
    else:
        st.session_state.favorite_tools.add(tool_id)
    
    # Save to persistent storage
    st.session_state.user_prefs.toggle_favorite(tool_id)


def go_to_tool(tool_id):
    """Navigate to a specific tool (callback) and update URL"""
    st.session_state.tool = tool_id
    # Update URL query parameter for persistence across refreshes
    st.query_params["tool"] = tool_id


def back_to_home(tool_name):
    """Render back to home button"""
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("← Back", key=f"back_{tool_name}", type="secondary", help="Return to Home"):
            go_to_tool("home")
            st.rerun()


def render_navigation():
    """Render clean sidebar navigation"""
    initialize_session_state()
    
    # Sidebar Header - Larger Logo
    st.sidebar.markdown("""
        <div style="padding: 1.5rem 0.75rem 2rem 0.75rem; border-bottom: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                <span style="font-size: 2.5rem;">🚀</span>
                <div>
                    <h1 style="font-size: 1.25rem; font-weight: 700; margin: 0; color: #0f172a; line-height: 1.2;">
                        DataAugmentor
                    </h1>
                    <p style="font-size: 0.7rem; color: #64748b; margin: 0.25rem 0 0 0;">
                        AI Productivity Suite
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    # Home Button - Separate from tools
    is_home_active = st.session_state.tool == "home"
    home_button_type = "primary" if is_home_active else "secondary"
    
    if st.sidebar.button(
        "🏠 Home",
        key="nav_home_button",
        type=home_button_type,
        use_container_width=True,
        help="Return to dashboard"
    ):
        go_to_tool("home")
        st.rerun()
    
    st.sidebar.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    # Favorites Section (if any favorites exist)
    if st.session_state.favorite_tools:
        with st.sidebar.expander("⭐ **Favorites**", expanded=True):
            for tool_id in st.session_state.favorite_tools:
                if tool_id in TOOL_REGISTRY:
                    tool_info = TOOL_REGISTRY[tool_id]
                    name = tool_info["name"]
                    status = tool_info.get("status", "")
                    
                    # Status indicator
                    status_badge = ""
                    if status == "beta":
                        status_badge = " 🔶"
                    elif status == "new":
                        status_badge = " ✨"
                    
                    # Create columns for button and star
                    col1, col2 = st.columns([0.85, 0.15])
                    
                    with col1:
                        # Tool button
                        is_active = st.session_state.tool == tool_id
                        button_type = "primary" if is_active else "secondary"
                        
                        if st.button(
                            f"{name}{status_badge}",
                            key=f"fav_{tool_id}",
                            type=button_type,
                            use_container_width=True,
                            help=tool_info.get("description", "")
                        ):
                            go_to_tool(tool_id)
                            st.rerun()
                    
                    with col2:
                        # Unstar button
                        if st.button("⭐", key=f"unfav_{tool_id}", help="Remove from favorites"):
                            toggle_favorite(tool_id)
                            st.rerun()
        
        st.sidebar.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    # Group tools by category
    tools_by_category = {}
    for tool_id, tool_info in TOOL_REGISTRY.items():
        category = tool_info.get("category", "other")
        if category not in tools_by_category:
            tools_by_category[category] = []
        tools_by_category[category].append((tool_id, tool_info))
    
    # Sort categories by order
    sorted_categories = sorted(
        tools_by_category.items(),
        key=lambda x: CATEGORIES.get(x[0], {}).get("order", 999)
    )
    
    # Render each category
    for category_id, tools in sorted_categories:
        category_info = CATEGORIES.get(category_id, {})
        category_label = category_info.get("label", category_id.upper())
        is_collapsed = category_id in st.session_state.collapsed_categories
        
        # Category Header (clickable to toggle)
        arrow = "▼" if not is_collapsed else "▶"
        
        # Use expander for cleaner collapsible sections
        with st.sidebar.expander(f"**{category_label}**", expanded=not is_collapsed):
            # Show tools
            for tool_id, tool_info in tools:
                name = tool_info["name"]
                status = tool_info.get("status", "")
                
                # Status indicator
                status_badge = ""
                if status == "beta":
                    status_badge = " 🔶"
                elif status == "new":
                    status_badge = " ✨"
                elif status == "gamma":
                    status_badge = " 🧪"
                
                # Create columns for button and star
                col1, col2 = st.columns([0.85, 0.15])
                
                with col1:
                    # Tool button
                    is_active = st.session_state.tool == tool_id
                    button_type = "primary" if is_active else "secondary"
                    
                    if st.button(
                        f"{name}{status_badge}",
                        key=f"nav_{tool_id}",
                        type=button_type,
                        use_container_width=True,
                        help=tool_info.get("description", "")
                    ):
                        go_to_tool(tool_id)
                        st.rerun()
                
                with col2:
                    # Star/Unstar button
                    is_favorited = tool_id in st.session_state.favorite_tools
                    star_icon = "⭐" if is_favorited else "☆"
                    star_help = "Remove from favorites" if is_favorited else "Add to favorites"
                    
                    if st.button(star_icon, key=f"star_{tool_id}", help=star_help):
                        toggle_favorite(tool_id)
                        st.rerun()
    
    # Divider
    st.sidebar.markdown("<div style='margin: 1.5rem 0; border-top: 1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
    
    # API Key Status
    from config import settings
    api_key = settings.get_api_key()
    
    if not api_key or api_key.strip() == "":
        st.sidebar.warning("⚠️ API Key Missing")
        st.sidebar.caption("Set `OPENROUTER_API_KEY` in secrets")
    else:
        st.sidebar.success("✅ API Key Active")
    
    # Resources Section
    st.sidebar.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    
    with st.sidebar.expander("**Resources**", expanded=False):
        if st.button("📖 Documentation", use_container_width=True):
            st.info("Documentation coming soon!")
        
        if st.button("🐛 Report Issue", use_container_width=True):
            st.info("Issue reporting coming soon!")
    
    # Footer
    st.sidebar.markdown("""
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; text-align: center;">
            <div style="font-size: 0.7rem; color: #94a3b8;">
                Version 2.0.0
            </div>
            <div style="font-size: 0.65rem; color: #cbd5e1; margin-top: 0.25rem;">
                © 2026 DataAugmentor
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    return st.session_state.tool


def render_page_header(title, subtitle, icon="", status=""):
    """Render standardized page header"""
    # Back button
    back_to_home(title.lower().replace(" ", "_"))
    
    # Header with icon and status
    header_html = f'<h1 class="main-header">'
    
    if icon:
        header_html += f'{icon} '
    
    header_html += title
    
    if status:
        status_colors = {
            "beta": ("🔶", "#f59e0b", "#fef3c7"),
            "new": ("✨", "#3b82f6", "#dbeafe"),
            "stable": ("✅", "#10b981", "#d1fae5"),
            "gamma": ("🧪", "#8b5cf6", "#ede9fe")
        }
        emoji, color, bg = status_colors.get(status.lower(), ("", "#64748b", "#f1f5f9"))
        header_html += f'''
            <span style="
                background: {bg};
                color: {color};
                font-size: 0.4em;
                vertical-align: middle;
                padding: 4px 12px;
                border-radius: 12px;
                margin-left: 12px;
                font-weight: 600;
            ">{status.upper()}</span>
        '''
    
    header_html += '</h1>'
    
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)
