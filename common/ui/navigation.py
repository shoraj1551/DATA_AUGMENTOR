"""
Enhanced Navigation - Professional Sidebar with Collapsible Categories
Clean, minimal design with improved UX
"""
import streamlit as st


# Tool Registry - Single source of truth for all tools
TOOL_REGISTRY = {
    "home": {
        "name": "Home",
        "icon": "🏠",
        "category": "core",
        "description": "Dashboard and tool overview"
    },
    "code_review": {
        "name": "Code Review",
        "icon": "🔍",
        "category": "core",
        "description": "AI-powered code analysis",
        "status": "stable"
    },
    "data_augmentor": {
        "name": "Data Augmentor",
        "icon": "🔄",
        "category": "core",
        "description": "Generate and mask data",
        "status": "stable"
    },
    "file_comparison": {
        "name": "File Comparison",
        "icon": "📊",
        "category": "utilities",
        "description": "Compare datasets precisely"
    },
    "document_parser": {
        "name": "Document Parser",
        "icon": "📄",
        "category": "utilities",
        "description": "Extract text from documents",
        "status": "beta"
    },
    "web_scraper": {
        "name": "Web Scraper",
        "icon": "🌐",
        "category": "utilities",
        "description": "Extract web data compliantly",
        "status": "beta"
    },
    "delivery_intelligence": {
        "name": "Delivery Intelligence",
        "icon": "🎯",
        "category": "planning",
        "description": "AI execution planning",
        "status": "beta"
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
    }
}


def initialize_session_state():
    """Initialize session state variables"""
    if "tool" not in st.session_state:
        st.session_state.tool = "home"
    if "sidebar_expanded" not in st.session_state:
        st.session_state.sidebar_expanded = True
    # Initialize category collapse states
    if "collapsed_categories" not in st.session_state:
        st.session_state.collapsed_categories = set()


def go_to_tool(tool_id):
    """Navigate to a specific tool (callback)"""
    st.session_state.tool = tool_id


def back_to_home(tool_name):
    """Render back to home button with enhanced styling"""
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("← Back", key=f"back_{tool_name}", type="secondary", help="Return to Home"):
            go_to_tool("home")
            st.rerun()


def render_navigation():
    """Render enhanced sidebar navigation with collapsible categories"""
    initialize_session_state()
    
    # Sidebar Header
    st.sidebar.markdown("""
        <div style="padding: 1rem 0.5rem 1.5rem 0.5rem; border-bottom: 1px solid var(--color-slate-200);">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">🚀</span>
                <h1 style="font-size: 1.1rem; font-weight: 700; margin: 0; color: var(--color-slate-900);">
                    DataAugmentor
                </h1>
            </div>
            <p style="font-size: 0.7rem; color: var(--color-slate-500); margin: 0; padding-left: 2rem;">
                AI Productivity Suite
            </p>
        </div>
    """, unsafe_allow_html=True)
    
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
    
    # Render each category with tools
    for category_id, tools in sorted_categories:
        category_info = CATEGORIES.get(category_id, {})
        category_label = category_info.get("label", category_id.upper())
        
        # Category Header (collapsible)
        is_collapsed = category_id in st.session_state.collapsed_categories
        arrow = "▼" if not is_collapsed else "▶"
        
        # Use a container for the category
        category_container = st.sidebar.container()
        
        with category_container:
            # Category header with collapse button
            st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin: 1rem 0.5rem 0.5rem;
                    cursor: pointer;
                ">
                    <div style="
                        font-size: 0.7rem;
                        font-weight: 600;
                        color: var(--color-slate-500);
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">
                        {category_label}
                    </div>
                    <div style="
                        font-size: 0.7rem;
                        color: var(--color-slate-400);
                        cursor: pointer;
                        user-select: none;
                    " onclick="this.click()">
                        {arrow}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Small collapse button
            if st.sidebar.button(arrow, key=f"collapse_{category_id}", help=f"Toggle {category_label}"):
                if is_collapsed:
                    st.session_state.collapsed_categories.discard(category_id)
                else:
                    st.session_state.collapsed_categories.add(category_id)
                st.rerun()
            
            # Show tools if not collapsed
            if not is_collapsed:
                for tool_id, tool_info in tools:
                    name = tool_info["name"]
                    status = tool_info.get("status", "")
                    
                    # Status indicator
                    status_indicator = ""
                    if status == "beta":
                        status_indicator = " 🔶"
                    elif status == "new":
                        status_indicator = " ✨"
                    
                    # Tool button
                    is_active = st.session_state.tool == tool_id
                    button_type = "primary" if is_active else "secondary"
                    
                    if st.sidebar.button(
                        f"{name}{status_indicator}",
                        key=f"nav_{tool_id}",
                        type=button_type,
                        use_container_width=True,
                        help=tool_info.get("description", "")
                    ):
                        go_to_tool(tool_id)
                        st.rerun()
    
    # Divider
    st.sidebar.markdown("<div style='margin: 1.5rem 0; border-top: 1px solid var(--color-slate-200);'></div>", unsafe_allow_html=True)
    
    # API Key Status
    from config import settings
    api_key = settings.get_api_key()
    
    if not api_key or api_key.strip() == "":
        st.sidebar.warning("⚠️ API Key Missing", icon="⚠️")
        st.sidebar.caption("Set `OPENROUTER_API_KEY` in secrets")
    else:
        st.sidebar.success("✅ API Key Active", icon="✅")
    
    # Resources Section
    st.sidebar.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("""
        <div style="font-size: 0.7rem; font-weight: 600; color: var(--color-slate-500); text-transform: uppercase; letter-spacing: 0.05em; margin: 0.5rem 0.5rem;">
            Resources
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("📖 Documentation", use_container_width=True, help="View documentation"):
        st.sidebar.info("Documentation coming soon!")
    
    if st.sidebar.button("🐛 Report Issue", use_container_width=True, help="Report a bug"):
        st.sidebar.info("Issue reporting coming soon!")
    
    # Footer
    st.sidebar.markdown("""
        <div style="margin-top: auto; padding-top: 2rem; text-align: center;">
            <div style="font-size: 0.65rem; color: var(--color-slate-400);">
                Version 2.0.0
            </div>
            <div style="font-size: 0.6rem; color: var(--color-slate-400); margin-top: 0.25rem;">
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
            "stable": ("✅", "#10b981", "#d1fae5")
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
