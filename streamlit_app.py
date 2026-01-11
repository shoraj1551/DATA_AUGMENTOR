import streamlit as st
import pandas as pd
import os
from io import StringIO
import json

# Import existing modules
from llm.generate_synthetic_data import generate_synthetic_data
from llm.augment_existing_data import augment_existing_data
from llm.mask_pii_data import mask_pii_data
from llm.generate_edge_case_data import generate_edge_case_data
from utils.file_comparator import compare_files
from utils.code_analyzer import detect_language, parse_notebook, analyze_code_structure
from llm.code_review_llm import (
    review_code_with_llm,
    generate_unit_tests_with_llm,
    generate_functional_tests_with_llm,
    generate_failure_scenarios_with_llm
)

# Page config
st.set_page_config(
    page_title="DataAugmentor Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS matching Flask App
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Gradient Headers */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 30px;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 50px;
    }

    /* Card Styling */
    .tool-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid #f0f0f0;
        height: 100%;
        transition: transform 0.3s ease;
    }
    
    .tool-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .card-top-border {
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 20px 20px 0 0;
        margin: -30px -30px 20px -30px;
    }

    /* Buttons */
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8;
        transform: scale(1.02);
    }

    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 6px;
        border-color: #d1d5db;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        background: #f0f0f0;
        border-radius: 20px;
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 10px;
    }
    .badge.new {
        background: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🚀 Navigation")
tool = st.sidebar.radio(
    "Select Tool:",
    ["🏠 Home", "📊 DataAugmentor", "📁 File Comparison", "🔍 Code Review & Testing"]
)

# Check API key
api_key_status = os.getenv("OPENROUTER_API_KEY")
if not api_key_status:
    st.sidebar.warning("⚠️ API Key not set! Set OPENROUTER_API_KEY in Streamlit secrets or environment.")
else:
    st.sidebar.success("✅ API Key configured")

# HOME PAGE
if tool == "🏠 Home":
    st.markdown('<h1 class="main-header">🚀 DataAugmentor Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Powerful AI tools for data manipulation, file comparison, and code review</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="tool-card">
            <div class="card-top-border"></div>
            <div style="font-size: 3rem; margin-bottom: 10px;">🤖</div>
            <span class="badge new">AI-Powered</span>
            <h3>DataAugmentor</h3>
            <p style="color: #666; font-size: 0.95rem; margin-bottom: 20px;">
                Generate synthetic data, augment datasets, mask PII, and create edge cases.
            </p>
            <ul style="color: #555; padding-left: 20px; font-size: 0.9rem; margin-bottom: 20px;">
                <li>Generate synthetic data</li>
                <li>Augment existing data</li>
                <li>Mask PII automatically</li>
                <li>Generate edge cases</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tool-card">
            <div class="card-top-border"></div>
            <div style="font-size: 3rem; margin-bottom: 10px;">📊</div>
            <span class="badge new">Analytics</span>
            <h3>File Comparison</h3>
            <p style="color: #666; font-size: 0.95rem; margin-bottom: 20px;">
                Compare files and identify differences with detailed statistics.
            </p>
            <ul style="color: #555; padding-left: 20px; font-size: 0.9rem; margin-bottom: 20px;">
                <li>Compare CSV, TXT, JSON</li>
                <li>Row-level comparison</li>
                <li>Detailed statistics</li>
                <li>Export differences</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="tool-card">
            <div class="card-top-border"></div>
            <div style="font-size: 3rem; margin-bottom: 10px;">🔍</div>
            <span class="badge new">DevTools</span>
            <h3>Code Review</h3>
            <p style="color: #666; font-size: 0.95rem; margin-bottom: 20px;">
                AI-powered code analysis, test generation, and failure detection.
            </p>
            <ul style="color: #555; padding-left: 20px; font-size: 0.9rem; margin-bottom: 20px;">
                <li>Support 20+ languages</li>
                <li>Automated code review</li>
                <li>Generate unit tests</li>
                <li>Failure scenarios</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("👈 Select a tool from the sidebar to get started!", icon="ℹ️")

# DATAAUGMENTOR
elif tool == "📊 DataAugmentor":
    st.title("📊 DataAugmentor")
    
    operation = st.selectbox(
        "Select Operation:",
        ["Generate Synthetic Data", "Augment Existing Data", "Mask PII Data", "Generate Edge Case Data"]
    )
    
    if operation == "Generate Synthetic Data":
        st.subheader("Generate Synthetic Data")
        
        # Initialize session state for retry
        if 'last_synthetic_prompt' not in st.session_state:
            st.session_state.last_synthetic_prompt = ""
        if 'last_synthetic_rows' not in st.session_state:
            st.session_state.last_synthetic_rows = 10
        if 'synthetic_result' not in st.session_state:
            st.session_state.synthetic_result = None
        
        prompt = st.text_area("Describe the data you want:", 
                             value=st.session_state.last_synthetic_prompt,
                             placeholder="E.g., Customer data with name, email, age, and city",
                             height=100)
        num_rows = st.slider("Number of rows:", 1, 1000, st.session_state.last_synthetic_rows)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            generate_clicked = st.button("Generate Data", use_container_width=True)
        
        with col2:
            retry_clicked = st.button("🔄 Retry (New Data)", use_container_width=True)
        
        if generate_clicked or retry_clicked:
            if prompt:
                # Store for retry
                st.session_state.last_synthetic_prompt = prompt
                st.session_state.last_synthetic_rows = num_rows
                
                with st.spinner("Generating synthetic data..."):
                    try:
                        # For retry, add timestamp to bypass cache and get fresh data
                        import time
                        if retry_clicked:
                            actual_prompt = f"{prompt}\n\n[Variation {int(time.time())}]"
                        else:
                            actual_prompt = prompt
                        
                        df = generate_synthetic_data(actual_prompt, num_rows)
                        st.session_state.synthetic_result = df
                        st.success(f"✅ Generated {len(df)} rows!")
                        st.dataframe(df)
                        
                        csv = df.to_csv(index=False)
                        st.download_button("📥 Download CSV", csv, "synthetic_data.csv", "text/csv")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.synthetic_result = None
            else:
                st.warning("Please describe the data you want to generate.")
    
    elif operation == "Augment Existing Data":
        st.subheader("Augment Existing Data")
        
        uploaded_file = st.file_uploader("Upload CSV file:", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("**Original Data:**")
            st.dataframe(df.head())
            
            prompt = st.text_area("Additional requirements (optional):", height=80)
            num_rows = st.slider("Number of rows to add:", 1, 100, 5)
            
            if st.button("Augment Data"):
                with st.spinner("Augmenting data..."):
                    try:
                        augmented_df = augment_existing_data(df, prompt, num_rows)
                        st.success(f"✅ Added {num_rows} rows!")
                        st.dataframe(augmented_df.tail(num_rows))
                        
                        csv = augmented_df.to_csv(index=False)
                        st.download_button("📥 Download Augmented CSV", csv, "augmented_data.csv", "text/csv")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    elif operation == "Mask PII Data":
        st.subheader("Mask PII Data")
        
        uploaded_file = st.file_uploader("Upload CSV file:", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("**Original Data:**")
            st.dataframe(df.head())
            
            # Detect PII columns
            pii_patterns = ['name', 'email', 'phone', 'address', 'ssn', 'social', 'dob', 'birth']
            pii_columns = [col for col in df.columns if any(pattern in col.lower() for pattern in pii_patterns)]
            
            if pii_columns:
                st.write("**Detected PII Columns:**")
                exclude_cols = st.multiselect("Select columns to EXCLUDE from masking:", pii_columns)
                
                if st.button("Mask PII"):
                    with st.spinner("Masking PII data..."):
                        try:
                            masked_df = mask_pii_data(df, exclude_cols)
                            st.success("✅ PII data masked!")
                            st.dataframe(masked_df.head())
                            
                            csv = masked_df.to_csv(index=False)
                            st.download_button("📥 Download Masked CSV", csv, "masked_data.csv", "text/csv")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.info("No PII columns detected in this dataset.")
    
    elif operation == "Generate Edge Case Data":
        st.subheader("Generate Edge Case Data")
        
        uploaded_file = st.file_uploader("Upload CSV file:", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("**Original Data:**")
            st.dataframe(df.head())
            
            prompt = st.text_area("Describe edge cases (optional):", height=80)
            num_rows = st.slider("Number of edge cases:", 1, 50, 5)
            
            if st.button("Generate Edge Cases"):
                with st.spinner("Generating edge cases..."):
                    try:
                        edge_df = generate_edge_case_data(df, prompt, num_rows)
                        st.success(f"✅ Generated {num_rows} edge cases!")
                        st.dataframe(edge_df)
                        
                        csv = edge_df.to_csv(index=False)
                        st.download_button("📥 Download Edge Cases CSV", csv, "edge_cases.csv", "text/csv")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# FILE COMPARISON
elif tool == "📁 File Comparison":
    st.title("📁 File Comparison")
    
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
                    st.subheader("📊 Statistics")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total in File 1", result['stats']['total_file1'])
                    col2.metric("Total in File 2", result['stats']['total_file2'])
                    col3.metric("Common Items", result['stats']['common'])
                    
                    col4, col5 = st.columns(2)
                    col4.metric("Only in File 1", result['stats']['only_in_file1'])
                    col5.metric("Only in File 2", result['stats']['only_in_file2'])
                    
                    # Differences
                    if result['only_in_file1']:
                        with st.expander(f"📄 Only in {file1.name} ({len(result['only_in_file1'])} items)"):
                            for item in result['only_in_file1'][:50]:
                                st.text(item)
                    
                    if result['only_in_file2']:
                        with st.expander(f"📄 Only in {file2.name} ({len(result['only_in_file2'])} items)"):
                            for item in result['only_in_file2'][:50]:
                                st.text(item)
                    
                    if result['common']:
                        with st.expander(f"✅ Common Data ({len(result['common'])} items)"):
                            for item in result['common'][:50]:
                                st.text(item)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# CODE REVIEW
elif tool == "🔍 Code Review & Testing":
    st.title("🔍 Code Review & Testing Engine")
    
    # Language selection
    languages = {
        "Python": "python", "PySpark": "pyspark", "SQL": "sql", "Spark SQL": "sparksql",
        "JavaScript": "javascript", "TypeScript": "typescript", "Java": "java",
        "Go": "go", "Rust": "rust", "C++": "cpp", "Ruby": "ruby", "PHP": "php"
    }
    
    selected_lang = st.selectbox("Select Language (or auto-detect):", ["Auto-detect"] + list(languages.keys()))
    
    # Config download/upload section
    st.markdown("---")
    st.subheader("📋 Code Review Configuration (Optional)")
    st.info("**Python, PySpark, SQL, Spark SQL** have detailed configs. Other languages use generic config.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download config button
        if st.button("📥 Download Config for Selected Language"):
            # Determine which config to load
            if selected_lang != "Auto-detect":
                lang_key = languages[selected_lang]
            else:
                lang_key = "python"  # Default
            
            # Load appropriate config
            detailed_languages = ['python', 'pyspark', 'sql', 'sparksql']
            if lang_key in detailed_languages:
                config_file = f'config/code_review_config_{lang_key}.json'
            else:
                config_file = 'config/code_review_config_generic.json'
            
            try:
                with open(config_file, 'r') as f:
                    config_content = f.read()
                st.download_button(
                    label=f"💾 Save {lang_key}_config.json",
                    data=config_content,
                    file_name=f"code_review_config_{lang_key}.json",
                    mime="application/json",
                    key="download_config"
                )
            except FileNotFoundError:
                # Fallback to default
                with open('config/code_review_config.json', 'r') as f:
                    config_content = f.read()
                st.download_button(
                    label=f"💾 Save default_config.json",
                    data=config_content,
                    file_name="code_review_config.json",
                    mime="application/json",
                    key="download_config_fallback"
                )
    
    with col2:
        # Upload custom config
        uploaded_config = st.file_uploader("📤 Upload Custom Config (JSON)", type=['json'], key="config_upload")
        if uploaded_config:
            try:
                custom_config = json.load(uploaded_config)
                st.success(f"✅ Custom config loaded: {uploaded_config.name}")
                with st.expander("View Config"):
                    st.json(custom_config)
            except Exception as e:
                st.error(f"Invalid JSON config: {str(e)}")
                uploaded_config = None
    
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader("Upload code file:", 
                                     type=['py', 'ipynb', 'js', 'ts', 'java', 'sql', 'go', 'rs', 'cpp', 'rb', 'php'])
    
    if uploaded_file:
        # Detect or use selected language
        if selected_lang == "Auto-detect":
            language = detect_language(uploaded_file.name)
        else:
            language = languages[selected_lang]
        
        st.info(f"**Language:** {language.upper()}")
        
        # Read file
        if uploaded_file.name.endswith('.ipynb'):
            content = uploaded_file.read().decode('utf-8')
            code = parse_notebook(content)
        else:
            code = uploaded_file.read().decode('utf-8')
        
        # Show code preview
        with st.expander("📄 Code Preview"):
            st.code(code[:1000] + ("..." if len(code) > 1000 else ""), language=language)
        
        # Analysis options
        st.subheader("Analysis Options")
        col1, col2 = st.columns(2)
        
        with col1:
            do_review = st.checkbox("Code Review", value=True)
            do_unit_tests = st.checkbox("Generate Unit Tests", value=True)
        
        with col2:
            do_functional_tests = st.checkbox("Generate Functional Tests", value=False)
            do_failures = st.checkbox("Generate Failure Scenarios", value=True)
        
        if st.button("🔍 Analyze Code"):
            structure = analyze_code_structure(code, language)
            
            tabs = st.tabs(["📋 Code Review", "🧪 Unit Tests", "🔗 Functional Tests", "⚠️ Failure Scenarios"])
            
            # Code Review
            with tabs[0]:
                if do_review:
                    with st.spinner("Reviewing code..."):
                        try:
                            review_json = review_code_with_llm(code, language, uploaded_file.name)
                            review = json.loads(review_json)
                            
                            if review.get('issues'):
                                for issue in review['issues']:
                                    severity = issue.get('severity', 'low')
                                    if severity == 'high':
                                        st.error(f"**Line {issue.get('line', 'N/A')}**: {issue.get('message')}")
                                    elif severity == 'medium':
                                        st.warning(f"**Line {issue.get('line', 'N/A')}**: {issue.get('message')}")
                                    else:
                                        st.info(f"**Line {issue.get('line', 'N/A')}**: {issue.get('message')}")
                                    st.write(f"💡 **Suggestion:** {issue.get('suggestion')}")
                                    st.divider()
                            else:
                                st.success("✅ No major issues found!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("Code review not requested")
            
            # Unit Tests
            with tabs[1]:
                if do_unit_tests:
                    with st.spinner("Generating unit tests..."):
                        try:
                            tests = generate_unit_tests_with_llm(code, language, structure['test_framework'])
                            st.code(tests, language=language)
                            st.download_button("📥 Download Tests", tests, f"test_{uploaded_file.name}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("Unit test generation not requested")
            
            # Functional Tests
            with tabs[2]:
                if do_functional_tests:
                    with st.spinner("Generating functional tests..."):
                        try:
                            tests = generate_functional_tests_with_llm(code, language, structure['test_framework'])
                            st.code(tests, language=language)
                            st.download_button("📥 Download Tests", tests, f"functional_test_{uploaded_file.name}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("Functional test generation not requested")
            
            # Failure Scenarios
            with tabs[3]:
                if do_failures:
                    with st.spinner("Generating failure scenarios..."):
                        try:
                            failures_json = generate_failure_scenarios_with_llm(code, language)
                            failures = json.loads(failures_json)
                            
                            for scenario in failures.get('scenarios', []):
                                st.warning(f"**Function:** {scenario.get('function', 'General')}")
                                st.write(f"**Input:** `{scenario.get('input')}`")
                                st.write(f"**Reason:** {scenario.get('reason')}")
                                st.write(f"**Expected:** {scenario.get('expected')}")
                                st.divider()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("Failure scenario generation not requested")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Resources")
st.sidebar.markdown("[📖 Documentation](https://github.com)")
st.sidebar.markdown("[🐛 Report Issue](https://github.com)")
st.sidebar.info("💡 **Tip:** Use sample files from the `sample_data/` folder for demo!")
