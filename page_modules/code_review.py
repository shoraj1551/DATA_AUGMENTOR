"""
Code Review page - AI-powered code quality assurance
"""
import streamlit as st
import json
from app_components.navigation import back_to_home
from utils.code_analyzer import detect_language, parse_notebook, analyze_code_structure
from llm.code_review_llm import (
    review_code_with_llm,
    generate_unit_tests_with_llm,
    generate_functional_tests_with_llm,
    generate_failure_scenarios_with_llm
)


def render():
    """Render the Code Review page"""
    back_to_home("CodeReview")
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
                            
                            if not review_json:
                                st.error("Received empty response from LLM")
                            else:
                                try:
                                    review = json.loads(review_json)
                                except json.JSONDecodeError:
                                    # Fallback if LLM returns text instead of JSON
                                    st.warning("LLM returned raw text instead of structured JSON")
                                    st.write(review_json)
                                    review = {}

                                issues = review.get('issues', [])
                                if issues and isinstance(issues, list):
                                    for issue in issues:
                                        if isinstance(issue, dict):
                                            line = str(issue.get('line', 'N/A'))
                                            message = str(issue.get('message', 'No description'))
                                            suggestion = str(issue.get('suggestion', 'No suggestion'))
                                            severity = str(issue.get('severity', 'low')).lower()
                                            
                                            display_text = f"**Line {line}**: {message}"
                                            
                                            if severity == 'high':
                                                st.error(display_text)
                                            elif severity == 'medium':
                                                st.warning(display_text)
                                            else:
                                                st.info(display_text)
                                                
                                            st.markdown(f"💡 **Suggestion:** {suggestion}")
                                            st.divider()
                                        else:
                                            st.warning(f"Unstructured issue: {str(issue)}")
                                else:
                                    if review: # If we parsed generic JSON but no issues
                                        st.success("✅ No major issues found!")
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                            # Log the raw response for debugging if possible
                            if 'review_json' in locals():
                                with st.expander("Debug Raw Response"):
                                    st.code(review_json)
                else:
                    st.info("Code review not requested")
            
            # Unit Tests
            with tabs[1]:
                if do_unit_tests:
                    with st.spinner("Generating unit tests..."):
                        try:
                            tests = generate_unit_tests_with_llm(code, language, structure['test_framework'])
                            if tests:
                                st.code(tests, language=language)
                                st.download_button("📥 Download Tests", str(tests), f"test_{uploaded_file.name}")
                            else:
                                st.warning("No tests generated.")
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
                            
                            if tests and "SAME AS UNIT TEST" in tests:
                                st.info("ℹ️ Functional tests are identical to Unit Tests for this code section.")
                            elif tests:
                                st.code(tests, language=language)
                                st.download_button("📥 Download Tests", str(tests), f"functional_test_{uploaded_file.name}")
                            else:
                                st.warning("No functional tests generated.")
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
