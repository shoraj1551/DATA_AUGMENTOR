"""
Enhanced Navigation - FAANG-Level Professional Navigation System
Categorized tools, search functionality, scalable architecture
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
        "icon": "🤖",
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
        "label": "CORE TOOLS",
        "icon": "📊",
        "order": 1
    },
    "utilities": {
        "label": "UTILITIES",
        "icon": "🔧",
        "order": 2
    },
    "planning": {
        "label": "PLANNING",
        "icon": "🎯",
        "order": 3
    }
}


def initialize_session_state():
    """Initialize session state variables"""
    if "tool" not in st.session_state:
        st.session_state.tool = "home"
    if "sidebar_expanded" not in st.session_state:
        st.session_state.sidebar_expanded = True


def go_to_tool(tool_id):
    """Navigate to a specific tool (callback)"""
    st.session_state.tool = tool_id
    st.session_state.sidebar_tool_radio = tool_id


def back_to_home(tool_name):
    """Render back to home button with enhanced styling"""
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("← Back to Home", key=f"back_{tool_name}", type="secondary", help="Return to Dashboard"):
            go_to_tool("home")
            st.rerun()


def render_tool_button(tool_id, tool_info, is_active=False):
    """Render a single tool navigation button"""
    icon = tool_info.get("icon", "📦")
    name = tool_info["name"]
    status = tool_info.get("status", "")
    
    # Build button label with icon
    label = f"{icon}  {name}"
    
    # Add status badge if present
    if status:
        status_emoji = {"beta": "🔶", "new": "✨", "stable": "✅"}.get(status, "")
        if status_emoji:
            label += f" {status_emoji}"
    
    return label


def render_navigation():
    """Render enhanced sidebar navigation"""
    initialize_session_state()
    
    # Sidebar Header
    st.sidebar.markdown("""
        <div style="padding: 0 0.5rem 1.5rem 0.5rem; border-bottom: 1px solid var(--color-slate-200);">
            <h1 style="font-size: 1.25rem; font-weight: 700; margin: 0; color: var(--color-slate-900);">
                🚀 DataAugmentor
            </h1>
            <p style="font-size: 0.75rem; color: var(--color-slate-500); margin: 0.25rem 0 0 0;">
                AI-Powered Productivity Suite
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
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
    
    # Render tools by category
    all_tool_ids = []
    all_tool_labels = []
    
    for category_id, tools in sorted_categories:
        category_info = CATEGORIES.get(category_id, {})
        category_label = category_info.get("label", category_id.upper())
        
        # Category Header
        st.sidebar.markdown(
            f'<div class="nav-category">{category_label}</div>',
            unsafe_allow_html=True
        )
        
        # Tools in this category
        for tool_id, tool_info in tools:
            all_tool_ids.append(tool_id)
            all_tool_labels.append(render_tool_button(tool_id, tool_info))
    
    # Radio button for navigation
    current_index = all_tool_ids.index(st.session_state.tool) if st.session_state.tool in all_tool_ids else 0
    
    selected_label = st.sidebar.radio(
        "Navigation",
        all_tool_labels,
        index=current_index,
        label_visibility="collapsed",
        key="sidebar_tool_radio"
    )
    
    # Get selected tool ID from label
    selected_index = all_tool_labels.index(selected_label)
    selected_tool_id = all_tool_ids[selected_index]
    
    # Update session state
    if selected_tool_id != st.session_state.tool:
        st.session_state.tool = selected_tool_id
    
    # Divider
    st.sidebar.markdown("<div style='margin: 1.5rem 0; border-top: 1px solid var(--color-slate-200);'></div>", unsafe_allow_html=True)
    
    # API Key Status
    from config import settings
    api_key = settings.get_api_key()
    
    if not api_key or api_key.strip() == "":
        st.sidebar.warning("⚠️ API Key Missing")
        st.sidebar.markdown("""
            <div style="font-size: 0.75rem; color: var(--color-slate-500); margin-top: -0.5rem; padding: 0 0.5rem;">
                Set <code>OPENROUTER_API_KEY</code> in secrets to enable AI features.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.success("✅ API Key Configured")
    
    # Footer
    st.sidebar.markdown("<div style='margin-top: auto; padding-top: 2rem;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("""
        <div style="font-size: 0.7rem; color: var(--color-slate-400); text-align: center; padding: 1rem 0.5rem;">
            <div>Version 2.0.0</div>
            <div style="margin-top: 0.25rem;">© 2026 DataAugmentor</div>
        </div>
    """, unsafe_allow_html=True)
    
    return st.session_state.tool


def render_page_header(title, subtitle, icon="", status=""):
    """Render standardized page header"""
    # Back button
    back_to_home(title.lower().replace(" ", "_"))
    
    # Header with icon and status
    header_html = f'<h1 class="main-header">{icon} {title}'
    
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
            ">{emoji} {status.upper()}</span>
        '''
    
    header_html += '</h1>'
    
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)
