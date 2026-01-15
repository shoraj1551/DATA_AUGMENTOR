"""
Code Review page - AI-powered code quality assurance
REDESIGNED: Documentation and Fix as sequential solutions below analysis
"""
import streamlit as st
import json
import difflib
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


def show_diff(original_code: str, modified_code: str, language: str):
    """Show color-coded diff between original and modified code"""
    diff = list(difflib.unified_diff(
        original_code.splitlines(keepends=True),
        modified_code.splitlines(keepends=True),
        lineterm='',
        n=3
    ))
    
    if not diff:
        st.info("No changes detected")
        return
    
    # Display diff with color coding
    diff_text = ""
    for line in diff[2:]:  # Skip the first two header lines
        if line.startswith('+'):
            diff_text += f'<span style="background-color: #d4edda; color: #155724;">+ {line[1:]}</span>\n'
        elif line.startswith('-'):
            diff_text += f'<span style="background-color: #f8d7da; color: #721c24;">- {line[1:]}</span>\n'
        else:
            diff_text += f'{line}\n'
    
    st.markdown(f'<pre style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.25rem; overflow-x: auto;">{diff_text}</pre>', unsafe_allow_html=True)


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
        
        # ============================================
        # SECTION 1: ANALYSIS
        # ============================================
        st.markdown("---")
        st.subheader("🔍 Analysis Options")
        col1, col2 = st.columns(2)
        
        with col1:
            do_review = st.checkbox("Code Review", value=True)
            do_unit_tests = st.checkbox("Generate Unit Tests", value=True)
        
        with col2:
            do_functional_tests = st.checkbox("Generate Functional Tests", value=False)
            do_failures = st.checkbox("Generate Failure Scenarios", value=True)
        
        if st.button("🔍 Analyze Code", type="primary"):
            with st.spinner("⏳ Analyzing code... Please wait"):
                structure = analyze_code_structure(code, language)
                
                # Store results
                st.session_state.review_issues = []
                st.session_state.failure_scenarios = []
                st.session_state.original_code = code
                st.session_state.original_filename = uploaded_file.name
                st.session_state.language = language
                
                tabs = st.tabs([
                    "📋 Code Review", 
                    "🧪 Unit Tests", 
                    "🔗 Functional Tests", 
                    "⚠️ Failure Scenarios"
                ])
                
                # Code Review
                with tabs[0]:
                    if do_review:
                        with st.spinner("⏳ Reviewing code..."):
                            try:
                                review_json = review_code_with_llm(code, language, uploaded_file.name)
                                
                                if not review_json:
                                    st.error("Received empty response from LLM")
                                else:
                                    try:
                                        review = json.loads(review_json)
                                    except json.JSONDecodeError:
                                        st.warning("LLM returned raw text instead of structured JSON")
                                        st.write(review_json)
                                        review = {}

                                    issues = review.get('issues', [])
                                    # Store for fix_all_issues
                                    st.session_state.review_issues = issues if isinstance(issues, list) else []
                                    
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
                                        if review:
                                            st.success("✅ No major issues found!")
                            except Exception as e:
                                st.error(f"Error during analysis: {str(e)}")
                    else:
                        st.info("Code review not requested")
                
                # Unit Tests
                with tabs[1]:
                    if do_unit_tests:
                        with st.spinner("⏳ Generating unit tests..."):
                            try:
                                unit_tests = generate_unit_tests_with_llm(code, language, structure['test_framework'])
                                if unit_tests:
                                    st.code(unit_tests, language=language)
                                    st.download_button("📥 Download Tests", str(unit_tests), f"test_{uploaded_file.name}")
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
                        with st.spinner("⏳ Generating functional tests..."):
                            try:
                                from llm.code_review_llm import calculate_code_similarity
                                
                                functional_tests = generate_functional_tests_with_llm(code, language, structure['test_framework'])
                                
                                if functional_tests and "SAME AS UNIT TEST" in functional_tests:
                                    st.info("ℹ️ **Functional tests are identical to Unit Tests for this simple code.**\n\nThis code has no integration points, database calls, or multi-component workflows that would require different functional testing.")
                                elif functional_tests:
                                    if 'unit_tests' in st.session_state:
                                        similarity = calculate_code_similarity(st.session_state['unit_tests'], functional_tests)
                                        
                                        if similarity > 0.90:
                                            st.info(f"ℹ️ **Functional tests are {int(similarity*100)}% identical to Unit Tests.**\n\nThis code appears to be a simple function without integration points. Functional testing would be redundant.\n\n**Recommendation:** Focus on the unit tests above, which already cover this code comprehensively.")
                                        else:
                                            st.success(f"✅ **Distinct Functional Tests Generated** (Similarity: {int(similarity*100)}%)")
                                            st.code(functional_tests, language=language)
                                            st.download_button("📥 Download Tests", str(functional_tests), f"functional_test_{uploaded_file.name}")
                                    else:
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
                        with st.spinner("⏳ Generating failure scenarios..."):
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
                                st.session_state.failure_scenarios = failures.get('scenarios', [])
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    else:
                        st.info("Failure scenario generation not requested")
        
        # ============================================
        # SECTION 2: SOLUTIONS (Sequential)
        # ============================================
        if 'original_code' in st.session_state:
            st.markdown("---")
            st.markdown("## 💡 Solutions")
            st.info("**These are sequential operations:** Documentation → Fix Issues. Each step uses the output from the previous step.")
            
            # Solution 1: Add Documentation
            st.markdown("### 📝 Step 1: Add Comments & Documentation")
            st.markdown("Add comprehensive inline comments and documentation to make the code more maintainable.")
            
            if st.button("📝 Add Documentation", type="secondary"):
                with st.spinner("⏳ Adding documentation... Please wait"):
                    try:
                        documented_code = add_comments_and_documentation(st.session_state.original_code, st.session_state.language)
                        st.session_state.documented_code = documented_code
                        
                        st.success("✅ Documentation added successfully!")
                        
                        # Show diff
                        st.markdown("#### 📊 Changes Preview (Color-coded)")
                        show_diff(st.session_state.original_code, documented_code, st.session_state.language)
                        
                        # Show full code
                        with st.expander("📄 View Complete Documented Code"):
                            st.code(documented_code, language=st.session_state.language)
                        
                        # Download with original filename
                        st.warning("⚠️ **Please review the documentation before downloading!**")
                        st.download_button(
                            "📥 Download Documented Code",
                            documented_code,
                            st.session_state.original_filename,  # Keep original filename
                            help="⚠️ Validate the output before using in production"
                        )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # Solution 2: Fix All Issues
            st.markdown("---")
            st.markdown("### 🔧 Step 2: Fix All Issues")
            st.markdown("Auto-fix all identified issues and add error handling for failure scenarios.")
            
            # Determine which code to use as base
            base_code = st.session_state.get('documented_code', st.session_state.original_code)
            base_label = "documented code" if 'documented_code' in st.session_state else "original code"
            
            st.info(f"ℹ️ Will fix issues in the **{base_label}**")
            
            if st.button("🔧 Fix All Issues", type="secondary"):
                # Check if we have issues to fix
                if not st.session_state.review_issues and not st.session_state.failure_scenarios:
                    st.warning("⚠️ No issues or failure scenarios found to fix. Run Code Review and Failure Scenarios first!")
                else:
                    st.error("⚠️ **CRITICAL WARNING:** AI-generated fixes may introduce new bugs or change functionality!")
                    st.warning("🔍 **You MUST:**\n- Review every change carefully\n- Test the fixed code thoroughly\n- Validate it doesn't break existing functionality\n- Check for security issues")
                    
                    with st.spinner("⏳ Fixing all issues... Please wait"):
                        try:
                            fixed_code = fix_all_issues(
                                base_code, 
                                st.session_state.language, 
                                st.session_state.review_issues, 
                                st.session_state.failure_scenarios
                            )
                            st.session_state.fixed_code = fixed_code
                            
                            st.success("✅ Code fixed successfully!")
                            st.info(f"**Fixed:** {len(st.session_state.review_issues)} issues and {len(st.session_state.failure_scenarios)} failure scenarios")
                            
                            # Show diff
                            st.markdown("#### 📊 Changes Preview (Color-coded)")
                            show_diff(base_code, fixed_code, st.session_state.language)
                            
                            # Show full code
                            with st.expander("📄 View Complete Fixed Code"):
                                st.code(fixed_code, language=st.session_state.language)
                            
                            # Download with original filename
                            st.error("🚨 **VALIDATE OUTPUT BEFORE DOWNLOAD!**")
                            st.warning("⚠️ The AI may have:\n- Changed functionality\n- Introduced new bugs\n- Missed edge cases\n- Added unnecessary code")
                            
                            st.download_button(
                                "📥 Download Fixed Code (Review First!)",
                                fixed_code,
                                st.session_state.original_filename,  # Keep original filename
                                help="⚠️⚠️⚠️ CRITICAL: Validate thoroughly before using!"
                            )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
