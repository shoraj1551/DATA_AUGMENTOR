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
    generate_failure_scenarios_with_llm,
    add_comments_and_documentation,
    fix_all_issues
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
        try:
            if uploaded_file.name.endswith('.ipynb'):
                content = uploaded_file.read().decode('utf-8')
                # Debug: Show first 100 chars
                if not content.strip():
                    st.error("❌ The uploaded .ipynb file appears to be empty!")
                    st.stop()
                code = parse_notebook(content)
            else:
                code = uploaded_file.read().decode('utf-8')
        except ValueError as ve:
            # Show specific parsing error
            st.error(f"❌ **Error parsing notebook:** {str(ve)}")
            st.info("💡 **Troubleshooting:**\n- Ensure the file is a valid Jupyter notebook (.ipynb)\n- Try opening it in Jupyter to verify it's not corrupted\n- Check that it contains at least one code cell")
            st.stop()
        except Exception as e:
            st.error(f"❌ **Error reading file:** {str(e)}")
            st.stop()
        
        # Show code preview
        with st.expander("📄 Code Preview"):
            st.code(code[:1000] + ("..." if len(code) > 1000 else ""), language=language)
        
        # Analysis options
        st.subheader("Analysis Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            do_review = st.checkbox("Code Review", value=True)
            do_unit_tests = st.checkbox("Generate Unit Tests", value=True)
        
        with col2:
            do_functional_tests = st.checkbox("Generate Functional Tests", value=False)
            do_failures = st.checkbox("Generate Failure Scenarios", value=True)
        
        with col3:
            do_add_docs = st.checkbox("📝 Add Comments & Documentation", value=False)
            do_fix_issues = st.checkbox("🔧 Fix All Issues", value=False)
        
        if st.button("🔍 Analyze Code"):
            structure = analyze_code_structure(code, language)
            
            # Store results for fix_all_issues
            review_issues = []
            failure_scenarios_list = []
            
            tabs = st.tabs([
                "📋 Code Review", 
                "🧪 Unit Tests", 
                "🔗 Functional Tests", 
                "⚠️ Failure Scenarios",
                "📝 Add Documentation",
                "🔧 Fix All Issues"
            ])
            
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
                                # Store for fix_all_issues
                                review_issues = issues if isinstance(issues, list) else []
                                
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
                            unit_tests = generate_unit_tests_with_llm(code, language, structure['test_framework'])
                            if unit_tests:
                                st.code(unit_tests, language=language)
                                st.download_button("📥 Download Tests", str(unit_tests), f"test_{uploaded_file.name}")
                                # Store in session for comparison
                                st.session_state['unit_tests'] = unit_tests
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
                            from llm.code_review_llm import calculate_code_similarity
                            
                            functional_tests = generate_functional_tests_with_llm(code, language, structure['test_framework'])
                            
                            # Check if AI returned "SAME AS UNIT TEST"
                            if functional_tests and "SAME AS UNIT TEST" in functional_tests:
                                st.info("ℹ️ **Functional tests are identical to Unit Tests for this simple code.**\n\nThis code has no integration points, database calls, or multi-component workflows that would require different functional testing.")
                            elif functional_tests:
                                # CRITICAL: Check similarity with unit tests if both exist
                                if 'unit_tests' in st.session_state:
                                    similarity = calculate_code_similarity(st.session_state['unit_tests'], functional_tests)
                                    
                                    if similarity > 0.90:  # More than 90% similar
                                        st.info(f"ℹ️ **Functional tests are {int(similarity*100)}% identical to Unit Tests.**\n\nThis code appears to be a simple function without integration points. Functional testing would be redundant.\n\n**Recommendation:** Focus on the unit tests above, which already cover this code comprehensively.")
                                    else:
                                        st.success(f"✅ **Distinct Functional Tests Generated** (Similarity: {int(similarity*100)}%)")
                                        st.code(functional_tests, language=language)
                                        st.download_button("📥 Download Tests", str(functional_tests), f"functional_test_{uploaded_file.name}")
                                else:
                                    # No unit tests to compare against
                                    st.code(functional_tests, language=language)
                                    st.download_button("📥 Download Tests", str(functional_tests), f"functional_test_{uploaded_file.name}")
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
                            
                            # Store for fix_all_issues
                            failure_scenarios_list = failures.get('scenarios', [])
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("Failure scenario generation not requested")
            
            # Add Documentation
            with tabs[4]:
                if do_add_docs:
                    st.warning("⚠️ **IMPORTANT:** Always validate the generated documentation before using it in production!")
                    with st.spinner("Adding comments and documentation..."):
                        try:
                            documented_code = add_comments_and_documentation(code, language)
                            
                            st.success("✅ Documentation added successfully!")
                            st.code(documented_code, language=language)
                            
                            # Download button with warning
                            st.warning("🔍 **Please review the code carefully before downloading!**")
                            st.download_button(
                                "📥 Download Documented Code",
                                documented_code,
                                f"documented_{uploaded_file.name}",
                                help="⚠️ Validate the output before using in production"
                            )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("📝 Add Comments & Documentation not requested")
                    st.markdown("""
                    **This feature will:**
                    - Add comprehensive docstrings/documentation blocks
                    - Add inline comments explaining complex logic
                    - Document parameters, return values, and exceptions
                    - Follow language-specific documentation conventions
                    """)
            
            # Fix All Issues
            with tabs[5]:
                if do_fix_issues:
                    # Check if we have issues or failures to fix
                    if not review_issues and not failure_scenarios_list:
                        st.warning("⚠️ No issues or failure scenarios found to fix. Run Code Review and Failure Scenarios first!")
                    else:
                        st.error("⚠️ **CRITICAL WARNING:** AI-generated fixes may introduce new bugs or change functionality!")
                        st.warning("🔍 **You MUST:**\n- Review every change carefully\n- Test the fixed code thoroughly\n- Validate it doesn't break existing functionality\n- Check for security issues")
                        
                        with st.spinner("Fixing all issues and handling failure scenarios..."):
                            try:
                                fixed_code = fix_all_issues(code, language, review_issues, failure_scenarios_list)
                                
                                st.success("✅ Code fixed successfully!")
                                
                                # Show what was fixed
                                st.info(f"**Fixed:** {len(review_issues)} issues and {len(failure_scenarios_list)} failure scenarios")
                                
                                st.code(fixed_code, language=language)
                                
                                # Download button with strong warning
                                st.error("🚨 **VALIDATE OUTPUT BEFORE DOWNLOAD!**")
                                st.warning("⚠️ The AI may have:\n- Changed functionality\n- Introduced new bugs\n- Missed edge cases\n- Added unnecessary code")
                                
                                st.download_button(
                                    "📥 Download Fixed Code (Review First!)",
                                    fixed_code,
                                    f"fixed_{uploaded_file.name}",
                                    help="⚠️⚠️⚠️ CRITICAL: Validate thoroughly before using!"
                                )
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                else:
                    st.info("🔧 Fix All Issues not requested")
                    st.markdown("""
                    **This feature will:**
                    - Fix all identified code review issues
                    - Add error handling for all failure scenarios
                    - Add input validation
                    - Add defensive programming checks
                    - Maintain original functionality
                    
                    ⚠️ **Note:** You must run Code Review and/or Failure Scenarios first to identify issues to fix.
                    """)
