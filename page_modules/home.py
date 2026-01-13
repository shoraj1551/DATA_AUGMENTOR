"""
Home Page - Professional Dashboard with Enhanced Tool Cards
FAANG-level design with usage stats, feature lists, and CTAs
"""
import streamlit as st
from common.ui.navigation import go_to_tool, TOOL_REGISTRY


def render():
    """Render the enhanced home page"""
    
    # Hero Section
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0 3rem 0;">
            <h1 class="main-header" style="margin-bottom: 0.5rem;">
                🚀 DataAugmentor Suite
            </h1>
            <p class="subtitle" style="font-size: 1.25rem; margin-bottom: 1rem;">
                Professional AI-Powered Productivity Tools for Data Engineering
            </p>
            <p style="color: var(--color-slate-500); font-size: 0.95rem;">
                Secure, scalable, and enterprise-ready tools for modern data teams
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tools Available", "6", delta="2 new")
    with col2:
        st.metric("AI Models", "3", delta="Gemini 2.0")
    with col3:
        st.metric("Uptime", "99.9%", delta="Reliable")
    with col4:
        st.metric("Version", "2.0.0", delta="Latest")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Tool Cards by Category
    categories = {
        "core": {"name": "Core Tools", "desc": "Essential AI-powered productivity tools"},
        "utilities": {"name": "Utilities", "desc": "Specialized tools for data operations"},
        "planning": {"name": "Planning & Intelligence", "desc": "Project management and delivery tools"}
    }
    
    for category_id, category_info in categories.items():
        # Get tools in this category
        category_tools = [
            (tool_id, tool_data) 
            for tool_id, tool_data in TOOL_REGISTRY.items() 
            if tool_data.get("category") == category_id and tool_id != "home"
        ]
        
        if not category_tools:
            continue
        
        # Category Header
        st.markdown(f"""
            <div style="margin: 2rem 0 1rem 0;">
                <h2 style="font-size: 1.5rem; font-weight: 600; color: var(--color-slate-900); margin-bottom: 0.25rem;">
                    {category_info['name']}
                </h2>
                <p style="color: var(--color-slate-500); font-size: 0.9rem;">
                    {category_info['desc']}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Tool Cards Grid
        cols = st.columns(3)
        for idx, (tool_id, tool_data) in enumerate(category_tools):
            with cols[idx % 3]:
                render_tool_card(tool_id, tool_data)
    
    # Footer CTA
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; color: white;">
            <h3 style="color: white; margin-bottom: 0.5rem;">Ready to boost your productivity?</h3>
            <p style="color: rgba(255,255,255,0.9); margin-bottom: 1.5rem;">
                Select a tool from the sidebar to get started
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_tool_card(tool_id, tool_data):
    """Render an enhanced tool card with features and stats"""
    
    icon = tool_data.get("icon", "📦")
    name = tool_data["name"]
    description = tool_data.get("description", "")
    status = tool_data.get("status", "")
    
    # Status badge
    status_badge = ""
    if status:
        status_colors = {
            "beta": ("#f59e0b", "#fef3c7", "🔶"),
            "new": ("#3b82f6", "#dbeafe", "✨"),
            "stable": ("#10b981", "#d1fae5", "✅")
        }
        color, bg, emoji = status_colors.get(status, ("#64748b", "#f1f5f9", ""))
        status_badge = f'''
            <span style="
                background: {bg};
                color: {color};
                font-size: 0.7rem;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-weight: 600;
                text-transform: uppercase;
            ">{emoji} {status}</span>
        '''
    
    # Feature list based on tool
    features = get_tool_features(tool_id)
    features_html = "".join([f"<li style='margin-bottom: 0.5rem;'>• {feature}</li>" for feature in features])
    
    # Usage stats (mock data for now)
    stats = get_tool_stats(tool_id)
    
    # Card HTML
    st.markdown(f"""
        <div class="tool-card" style="position: relative;">
            <div style="display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1rem;">
                <div class="card-icon">{icon}</div>
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 1.25rem;">
                        {name}
                    </h3>
                    {status_badge}
                </div>
            </div>
            
            <p style="color: var(--color-slate-600); font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem;">
                {description}
            </p>
            
            <div style="margin-bottom: 1rem;">
                <p style="font-size: 0.75rem; font-weight: 600; color: var(--color-slate-700); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                    Key Features
                </p>
                <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem; color: var(--color-slate-600);">
                    {features_html}
                </ul>
            </div>
            
            <div style="display: flex; gap: 1rem; padding-top: 1rem; border-top: 1px solid var(--color-slate-200); margin-top: auto;">
                <div style="flex: 1; text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: var(--color-slate-900);">{stats['uses']}</div>
                    <div style="font-size: 0.7rem; color: var(--color-slate-500);">Uses</div>
                </div>
                <div style="flex: 1; text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: var(--color-slate-900);">{stats['rating']}</div>
                    <div style="font-size: 0.7rem; color: var(--color-slate-500);">Rating</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button(f"Launch {name}", key=f"launch_{tool_id}", type="primary", use_container_width=True):
            go_to_tool(tool_id)
            st.rerun()
    with col2:
        st.button("ℹ️", key=f"info_{tool_id}", help=f"Learn more about {name}", use_container_width=True)


def get_tool_features(tool_id):
    """Get feature list for each tool"""
    features_map = {
        "code_review": [
            "Generate unit & functional tests",
            "Identify code issues",
            "Best practices analysis"
        ],
        "data_augmentor": [
            "Generate synthetic data",
            "PII masking & anonymization",
            "Edge case generation"
        ],
        "file_comparison": [
            "Compare CSV, JSON, TXT files",
            "Identify differences",
            "Export comparison reports"
        ],
        "document_parser": [
            "Extract text from PDFs/Docs",
            "Chat with documents (RAG)",
            "Generate insights"
        ],
        "web_scraper": [
            "Compliant web scraping",
            "AI-powered extraction",
            "Robots.txt validation"
        ],
        "delivery_intelligence": [
            "AI execution planning",
            "Epic/Story/Task generation",
            "Team workload distribution"
        ]
    }
    return features_map.get(tool_id, ["Feature 1", "Feature 2", "Feature 3"])


def get_tool_stats(tool_id):
    """Get usage statistics for each tool (mock data)"""
    stats_map = {
        "code_review": {"uses": "1.2k", "rating": "4.8★"},
        "data_augmentor": {"uses": "2.5k", "rating": "4.9★"},
        "file_comparison": {"uses": "850", "rating": "4.7★"},
        "document_parser": {"uses": "640", "rating": "4.6★"},
        "web_scraper": {"uses": "420", "rating": "4.5★"},
        "delivery_intelligence": {"uses": "380", "rating": "4.7★"}
    }
    return stats_map.get(tool_id, {"uses": "0", "rating": "N/A"})
