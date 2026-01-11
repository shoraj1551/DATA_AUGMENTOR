"""
Home page - Landing page with tool cards
"""
import streamlit as st


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
        if st.button("Open DataAugmentor", key="btn_da"):
            st.session_state.tool = "DataAugmentor"
            st.rerun()
    
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
        if st.button("Open Comparison", key="btn_fc"):
            st.session_state.tool = "File Comparison"
            st.rerun()
    
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
        if st.button("Open Code Review", key="btn_cr"):
            st.session_state.tool = "Code Review"
            st.rerun()
    
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
        if st.button("Open Delivery Intelligence", key="btn_di"):
            st.session_state.tool = "Delivery Intelligence"
            st.rerun()
