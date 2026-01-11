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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .tool-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
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
    st.markdown("### AI-Powered Data & Code Tools Platform")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 DataAugmentor")
        st.write("- Generate synthetic data")
        st.write("- Augment existing datasets")
        st.write("- Mask PII data")
        st.write("- Generate edge cases")
    
    with col2:
        st.markdown("### 📁 File Comparison")
        st.write("- Compare CSV files")
        st.write("- Compare TXT files")
        st.write("- Compare JSON files")
        st.write("- Detailed statistics")
    
    with col3:
        st.markdown("### 🔍 Code Review")
        st.write("- 20+ languages supported")
        st.write("- Automated code review")
        st.write("- Generate unit tests")
        st.write("- Failure scenarios")
    
    st.info("👈 Select a tool from the sidebar to get started!")

# DATAAUGMENTOR
elif tool == "📊 DataAugmentor":
    st.title("📊 DataAugmentor")
    
    operation = st.selectbox(
        "Select Operation:",
        ["Generate Synthetic Data", "Augment Existing Data", "Mask PII Data", "Generate Edge Case Data"]
    )
    
    if operation == "Generate Synthetic Data":
        st.subheader("Generate Synthetic Data")
        
        prompt = st.text_area("Describe the data you want:", 
                             placeholder="E.g., Customer data with name, email, age, and city",
                             height=100)
        num_rows = st.slider("Number of rows:", 1, 1000, 10)
        
        if st.button("Generate Data"):
            if prompt:
                with st.spinner("Generating synthetic data..."):
                    try:
                        df = generate_synthetic_data(prompt, num_rows)
                        st.success(f"✅ Generated {len(df)} rows!")
                        st.dataframe(df)
                        
                        csv = df.to_csv(index=False)
                        st.download_button("📥 Download CSV", csv, "synthetic_data.csv", "text/csv")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
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
