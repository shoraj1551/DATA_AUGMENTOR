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

# Custom CSS - Minimalist & Professional Design System
st.markdown("""
<style>
    /* 1. Global Typography & Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1e293b; /* Slate-800 for high contrast text */
        background-color: #f8fafc; /* Very light slate background */
    }

    /* 2. Headers */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: #0f172a; /* Slate-900 */
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #64748b; /* Slate-500 */
        font-weight: 400;
        margin-bottom: 3rem;
    }
    
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    /* 3. Cards (Minimalist) */
    .tool-card {
        background: #ffffff;
        border: 1px solid #e2e8f0; /* Slate-200 */
        border-radius: 12px;
        padding: 2rem;
        height: 100%;
        transition: all 0.2s ease-in-out;
    }

    .tool-card:hover {
        border-color: #cbd5e1; /* Slate-300 */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transform: translateY(-2px);
    }
    
    .card-icon {
        font-size: 2rem;
        margin-bottom: 1.5rem;
        background: #f1f5f9;
        width: 3.5rem;
        height: 3.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
    }

    /* 4. Buttons (Professional Blue) */
    .stButton > button {
        background-color: #2563eb; /* Blue-600 */
        color: #ffffff;
        border: 1px solid transparent;
        padding: 0.625rem 1.25rem;
        font-size: 0.95rem;
        font-weight: 500;
        border-radius: 8px;
        transition: background-color 0.15s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .stButton > button:hover {
        background-color: #1d4ed8; /* Blue-700 */
        border-color: transparent;
        color: #ffffff;
    }
    
    .stButton > button:active {
        background-color: #1e40af; /* Blue-800 */
    }

    /* 5. Inputs & Dropdowns (High Visibility) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff;
        color: #0f172a !important; /* Ensure text is dark and visible */
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: #2563eb;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    /* Fix dropdown text visibility */
    div[data-baseweb="select"] span {
        color: #0f172a !important; /* Force dark text for selected option */
    }
    
    /* Dropdown menu items */
    ul[data-baseweb="menu"] li {
        color: #0f172a !important;
    }

    /* 6. Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] .css-17lntkn {
        color: #475569;
    }

    /* 8. Back Button */
    .back-btn {
        display: inline-flex;
        align-items: center;
        text-decoration: none;
        color: #64748b;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 20px;
        cursor: pointer;
        border: 1px solid #e2e8f0;
        padding: 5px 12px;
        border-radius: 6px;
        background: white;
        transition: all 0.2s;
    }
    
    .back-btn:hover {
        background: #f8fafc;
        color: #2563eb;
        border-color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for back button
def back_to_home():
    if st.button("← Back to Home", key=f"back_{tool}", type="secondary", help="Return to Dashboard"):
        st.session_state.tool = "Home"
        st.rerun()

# Sidebar navigation
st.sidebar.markdown("### 🧭 Navigation")
tool = st.sidebar.radio(
    "Go to:",
    ["Home", "DataAugmentor", "File Comparison", "Code Review"],
    index=["Home", "DataAugmentor", "File Comparison", "Code Review"].index(st.session_state.tool) if st.session_state.tool in ["Home", "DataAugmentor", "File Comparison", "Code Review"] else 0,
    label_visibility="collapsed",
    key="sidebar_tool_radio"
)

# Initialize session state for tool
if "tool" not in st.session_state:
    st.session_state.tool = "Home"

# Update sidebar selection from session state logic (bi-directional sync)
# We use a callback or carefully manage state to avoid conflicts
selection = st.sidebar.radio(
    "Go to:",
    ["Home", "DataAugmentor", "File Comparison", "Code Review"],
    index=["Home", "DataAugmentor", "File Comparison", "Code Review"].index(st.session_state.tool) if st.session_state.tool in ["Home", "DataAugmentor", "File Comparison", "Code Review"] else 0,
    label_visibility="collapsed",
    key="sidebar_tool_radio"
)

# Update session state when sidebar changes
if selection != st.session_state.tool:
    st.session_state.tool = selection
    st.rerun()

tool = st.session_state.tool

# Check API key
if not os.getenv("OPENROUTER_API_KEY"):
    st.sidebar.error("⚠️ API Key missing")

# HOME PAGE
# HOME PAGE
if tool == "Home":
    st.markdown('<h1 class="main-header">DataAugmentor Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Secure, AI-powered tools for enterprise data operations</p>', unsafe_allow_html=True)
    
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

# DATAAUGMENTOR
elif tool == "DataAugmentor":
    back_to_home()
    st.markdown('<h2 class="main-header">DataAugmentor</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Generate, augment, and secure your data</p>', unsafe_allow_html=True)
    
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
elif tool == "File Comparison":
    back_to_home()
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
                                st.write(item)  # Use write for better formatting
                    
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

# CODE REVIEW
elif tool == "Code Review":
    back_to_home()
    st.markdown('<h2 class="main-header">Code Review & Testing</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-powered code quality assurance</p>', unsafe_allow_html=True)
    
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
