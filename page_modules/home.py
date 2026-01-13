"""
Home Page - Clean Professional Dashboard
Simple, effective tool cards without complex HTML
"""
import streamlit as st
from common.ui.navigation import go_to_tool, TOOL_REGISTRY


def render():
    """Render the home page"""
    
    # Hero Section
    st.markdown("# 🚀 DataAugmentor Suite")
    st.markdown("### Professional AI-Powered Productivity Tools for Data Engineering")
    st.caption("Secure, scalable, and enterprise-ready tools for modern data teams")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
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
        st.markdown(f"## {category_info['name']}")
        st.caption(category_info['desc'])
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Tool Cards Grid
        cols = st.columns(3)
        for idx, (tool_id, tool_data) in enumerate(category_tools):
            with cols[idx % 3]:
                render_tool_card(tool_id, tool_data)
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Footer CTA
    st.info("💡 **Ready to boost your productivity?** Select a tool from the sidebar to get started!")


def render_tool_card(tool_id, tool_data):
    """Render a clean tool card"""
    
    name = tool_data["name"]
    description = tool_data.get("description", "")
    status = tool_data.get("status", "")
    
    # Status badge
    status_emoji = ""
    if status == "beta":
        status_emoji = "🔶 Beta"
    elif status == "new":
        status_emoji = "✨ New"
    elif status == "stable":
        status_emoji = "✅ Stable"
    
    # Container for card
    with st.container():
        # Card header
        if status_emoji:
            st.markdown(f"### {name} {status_emoji}")
        else:
            st.markdown(f"### {name}")
        
        # Description
        st.caption(description)
        
        # Features
        features = get_tool_features(tool_id)
        if features:
            st.markdown("**Key Features:**")
            for feature in features:
                st.markdown(f"• {feature}")
        
        # Stats
        stats = get_tool_stats(tool_id)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Uses", stats['uses'], label_visibility="visible")
        with col2:
            st.metric("Rating", stats['rating'], label_visibility="visible")
        
        # Launch button
        if st.button(f"Launch {name}", key=f"launch_{tool_id}", type="primary", use_container_width=True):
            go_to_tool(tool_id)
            st.rerun()
        
        st.markdown("---")


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
            "Extract text from PDF/TXT/PPT",
            "Chat with documents (RAG)",
            "OCR tool coming soon"
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
    return features_map.get(tool_id, [])


def get_tool_stats(tool_id):
    """Get usage statistics for each tool"""
    stats_map = {
        "code_review": {"uses": "1.2k", "rating": "4.8★"},
        "data_augmentor": {"uses": "2.5k", "rating": "4.9★"},
        "file_comparison": {"uses": "850", "rating": "4.7★"},
        "document_parser": {"uses": "640", "rating": "4.6★"},
        "web_scraper": {"uses": "420", "rating": "4.5★"},
        "delivery_intelligence": {"uses": "380", "rating": "4.7★"}
    }
    return stats_map.get(tool_id, {"uses": "0", "rating": "N/A"})
