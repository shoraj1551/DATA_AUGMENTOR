"""
File Comparison page - Compare datasets with precision
"""
import streamlit as st
from app_components.navigation import back_to_home
from utils.file_comparator import compare_files


def render():
    """Render the File Comparison page"""
    back_to_home("FileComparison")
    st.markdown('<h2 class="main-header">File Comparison</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Compare datasets with precision</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("File 1")
        file1 = st.file_uploader("Upload first file:", type=['csv', 'txt', 'json'], key="file1")
    
    with col2:
        st.subheader("File 2")
        file2 = st.file_uploader("Upload second file:", type=['csv', 'txt', 'json'], key="file2")
    
    if file1 and file2:
        if st.button("Compare Files"):
            with st.spinner("Comparing files..."):
                try:
                    content1 = file1.read().decode('utf-8')
                    content2 = file2.read().decode('utf-8')
                    
                    result = compare_files(file1.name, file2.name, content1, content2)
                    
                    # Status
                    if result['stats']['only_in_file1'] == 0 and result['stats']['only_in_file2'] == 0:
                        st.success("✅ Files are IDENTICAL")
                    else:
                        st.warning("⚠️ Files are DIFFERENT")
                    
                    # Statistics
                    st.markdown("### 📊 Statistics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total in File 1", result['stats']['total_file1'])
                    with col2:
                        st.metric("Total in File 2", result['stats']['total_file2'])
                    with col3:
                        st.metric("Common Items", result['stats']['common'])
                    
                    col4, col5 = st.columns(2)
                    with col4:
                        st.metric("Only in File 1", result['stats']['only_in_file1'])
                    with col5:
                        st.metric("Only in File 2", result['stats']['only_in_file2'])
                    
                    # Differences
                    if result['only_in_file1']:
                        with st.expander(f"📄 Only in {file1.name} ({len(result['only_in_file1'])} items)"):
                            for item in result['only_in_file1'][:50]:
                                st.write(item)
                    
                    if result['only_in_file2']:
                        with st.expander(f"📄 Only in {file2.name} ({len(result['only_in_file2'])} items)"):
                            for item in result['only_in_file2'][:50]:
                                st.write(item)
                    
                    if result['common']:
                        with st.expander(f"✅ Common Data ({len(result['common'])} items)"):
                            for item in result['common'][:50]:
                                st.write(item)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
