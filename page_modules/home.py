"""
Home page - Landing page with tool cards
"""
import streamlit as st
from components.navigation import go_to_tool


"""
Home page - Landing page with tool cards
"""
import streamlit as st
from components.navigation import go_to_tool

def render():
    """Render the home page with tool cards"""
    # Renamed Main Header
    st.markdown('<h1 class="main-header">Data Engineering Productivity Suite <span style="font-size:0.6em; color:#64748b; font-weight:normal">by DataAugmentor</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Secure, AI-powered tools for enterprise data operations</p>', unsafe_allow_html=True)
    
    # --- 1. Initialize Favorites ---
    if "favorite_tools" not in st.session_state:
        st.session_state.favorite_tools = set()

    # --- 2. Tool Data Definition ---
    tools = [
        {
            "id": "DataAugmentor",
            "icon": "🤖",
            "badge": "AI Core",
            "title": "DataAugmentor",
            "desc": "Generate synthetic data, augment datasets, mask PII, and create edge cases.",
            "beta": False
        },
        {
            "id": "File Comparison",
            "icon": "📊",
            "badge": "Analytics",
            "title": "File Comparison",
            "desc": "Compare files (CSV, TXT, JSON) and identify differences with precision.",
            "beta": False
        },
        {
            "id": "Code Review",
            "icon": "🔍",
            "badge": "DevTools",
            "title": "Code Review",
            "desc": "Automated code analysis, test generation, and failure scenario detection.",
            "beta": False
        },
        {
            "id": "Delivery Intelligence",
            "icon": "🎯",
            "badge": "Planning",
            "title": "Delivery Intelligence",
            "desc": "AI-assisted execution planning with automated epic, story, and task generation.",
            "beta": True
        },
        {
            "id": "Web Data Scraper",
            "icon": "🌐",
            "badge": "Utility",
            "title": "Web Data Scraper",
            "desc": "Extract structured data, tables, and content from websites compliant with robots.txt.",
            "beta": True
        },
        {
            "id": "Document Parser",
            "icon": "📄",
            "badge": "Intelligence",
            "title": "Document Parser",
            "desc": "Chat with documents, generate story highlights, and extract structured tables.",
            "beta": True
        }
    ]
    
    # --- 3. Sort Tools (Favorites First) ---
    # Sort key: (is_favorite desc, title asc)
    sorted_tools = sorted(
        tools, 
        key=lambda t: (t['id'] not in st.session_state.favorite_tools, t['title'])
    )
    
    # --- 4. Render Grid ---
    
    # Split into chunks of 3 for rows
    rows = [sorted_tools[i:i + 3] for i in range(0, len(sorted_tools), 3)]
    
    for row_tools in rows:
        cols = st.columns(3)
        for idx, tool in enumerate(row_tools):
            with cols[idx]:
                tool_id = tool['id']
                is_fav = tool_id in st.session_state.favorite_tools
                
                # Card HTML
                beta_badge = '<span style="background:#2563eb; color:white; font-size:0.5em; vertical-align:middle; padding:2px 8px; border-radius:10px;">BETA</span>' if tool['beta'] else ''
                fav_icon = "⭐" if is_fav else "☆"
                fav_color = "#eab308" if is_fav else "#cbd5e1"
                
                st.markdown(f"""
                <div class="tool-card" style="position: relative;">
                    <div style="position: absolute; top: 10px; right: 10px; font-size: 1.2rem; cursor: pointer; color: {fav_color};">
                        {fav_icon}
                    </div>
                    <div class="card-icon">{tool['icon']}</div>
                    <div class="badge">{tool['badge']}</div>
                    <h3>{tool['title']} {beta_badge}</h3>
                    <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                        {tool['desc']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Actions Row
                c_open, c_fav = st.columns([0.8, 0.2])
                with c_open:
                    st.button(f"Open {tool['title'].split()[0]}", key=f"btn_{tool_id}", use_container_width=True, on_click=go_to_tool, args=(tool_id,))
                with c_fav:
                    # Favorite Toggle
                    if st.button(fav_icon, key=f"fav_{tool_id}", help="Toggle Favorite"):
                        if is_fav:
                            st.session_state.favorite_tools.remove(tool_id)
                        else:
                            st.session_state.favorite_tools.add(tool_id)
                        st.rerun()
