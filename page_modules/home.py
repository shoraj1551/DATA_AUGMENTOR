"""
Home page - Landing page with tool cards
"""
import streamlit as st
from components.navigation import go_to_tool


def render():
    """Render the home page with tool cards"""
    st.markdown('<h1 class="main-header">DataAugmentor Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Secure, AI-powered tools for enterprise data operations</p>', unsafe_allow_html=True)
    
    # First row - 3 tools
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="tool-card">
            <div class="card-icon">🤖</div>
            <div class="badge">AI Core</div>
            <h3>DataAugmentor</h3>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                Generate synthetic data, augment datasets, mask PII, and create edge cases.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open DataAugmentor", key="btn_da", use_container_width=True, on_click=go_to_tool, args=("DataAugmentor",))
    
    with col2:
        st.markdown("""
        <div class="tool-card">
            <div class="card-icon">📊</div>
            <div class="badge">Analytics</div>
            <h3>File Comparison</h3>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                Compare files (CSV, TXT, JSON) and identify differences with precision.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Comparison", key="btn_fc", use_container_width=True, on_click=go_to_tool, args=("File Comparison",))
    
    with col3:
        st.markdown("""
        <div class="tool-card">
            <div class="card-icon">🔍</div>
            <div class="badge">DevTools</div>
            <h3>Code Review</h3>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                Automated code analysis, test generation, and failure scenario detection.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Code Review", key="btn_cr", use_container_width=True, on_click=go_to_tool, args=("Code Review",))
    
    # Second row - Delivery Intelligence aligned under first column
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="tool-card">
            <div class="card-icon">🎯</div>
            <div class="badge">Planning</div>
            <h3>Delivery Intelligence</h3>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                AI-assisted execution planning with automated epic, story, and task generation.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Delivery Intelligence", key="btn_di", use_container_width=True, on_click=go_to_tool, args=("Delivery Intelligence",))
    
    with col5:
        st.markdown("""
        <div class="tool-card">
            <div class="card-icon">🌐</div>
            <div class="badge">Utility</div>
            <h3>Web Data Scraper <span style="background:#2563eb; color:white; font-size:0.5em; vertical-align:middle; padding:2px 8px; border-radius:10px;">BETA</span></h3>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                Extract structured data, tables, and content from websites compliant with robots.txt.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Web Scraper", key="btn_ws", use_container_width=True, on_click=go_to_tool, args=("Web Data Scraper",))

    with col6:
        st.markdown("""
        <div class="tool-card">
            <div class="card-icon">📄</div>
            <div class="badge">Intelligence</div>
            <h3>Document Parser <span style="background:#2563eb; color:white; font-size:0.5em; vertical-align:middle; padding:2px 8px; border-radius:10px;">BETA</span></h3>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                Chat with documents, generate story highlights, and extract structured tables from files.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Document Parser", key="btn_dp", use_container_width=True, on_click=go_to_tool, args=("Document Parser",))
