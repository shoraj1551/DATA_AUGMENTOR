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
    add_comments_and_documentation,
    fix_all_issues
)
from utils.code_analyzer import validate_code_syntax
from utils.safe_llm_parser import SafeLLMParser
from tools.code_review.state_manager import CodeReviewStateManager
import traceback

def show_error_with_details(error: Exception, context: str = "Error"):
    """Show error with expandable technical details"""
    st.error(f"❌ **{context}:** {str(error)}")
    with st.expander("🛠️ Technical Details (For Debugging)"):
        st.code(traceback.format_exc(), language="python")


def show_side_by_side_comparison(original_code: str, modified_code: str, language: str, original_label: str = "Original", modified_label: str = "Modified"):
    """Show side-by-side comparison of original and modified code with visual highlighting"""
    
    # Check if we should use HTML diff for better highlighting
    # Logic: diff changed lines, keep context
    
    # 1. Split lines
    orig_lines = original_code.splitlines()
    mod_lines = modified_code.splitlines()
    
    # 2. Use difflib to find changes
    d = difflib.Differ()
    diff = list(d.compare(orig_lines, mod_lines))
    
    # Build HTML for side by side
    html = """
    <style>
        .diff-container { display: flex; width: 100%; font-family: monospace; font-size: 12px; border: 1px solid #ccc; border-radius: 5px; overflow: hidden; }
        .diff-col { width: 50%; overflow-x: auto; padding: 0; background: #fff; }
        .diff-line { display: flex; min-height: 20px; line-height: 1.5; white-space: pre; }
        .diff-num { width: 30px; text-align: right; padding-right: 5px; color: #999; user-select: none; background: #f0f0f0; border-right: 1px solid #ddd; }
        .diff-content { flex: 1; padding-left: 5px; }
        .diff-added { background-color: #e6ffec; } /* Light Green */
        .diff-removed { background-color: #ffebe9; } /* Light Red */
        .diff-empty { background-color: #f8f9fa; }
        .diff-header { background: #f1f8ff; padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd; text-align: center; }
    </style>
    <div class="diff-container">
        <div class="diff-col">
            <div class="diff-header">""" + original_label + """</div>
    """
    
    left_html = ""
    right_html = ""
    
    # Process diff
    left_line_num = 1
    right_line_num = 1
    
    for line in diff:
        marker = line[0]
        content = line[2:]
        safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        if marker == ' ':  # No change
            left_html += f'<div class="diff-line"><span class="diff-num">{left_line_num}</span><span class="diff-content">{safe_content}</span></div>'
            right_html += f'<div class="diff-line"><span class="diff-num">{right_line_num}</span><span class="diff-content">{safe_content}</span></div>'
            left_line_num += 1
            right_line_num += 1
        elif marker == '-':  # Removed
            left_html += f'<div class="diff-line diff-removed"><span class="diff-num">{left_line_num}</span><span class="diff-content">{safe_content}</span></div>'
            right_html += f'<div class="diff-line diff-empty"><span class="diff-num"></span><span class="diff-content"></span></div>'
            left_line_num += 1
        elif marker == '+':  # Added
            left_html += f'<div class="diff-line diff-empty"><span class="diff-num"></span><span class="diff-content"></span></div>'
            right_html += f'<div class="diff-line diff-added"><span class="diff-num">{right_line_num}</span><span class="diff-content">{safe_content}</span></div>'
            right_line_num += 1
            
    html += left_html + '</div><div class="diff-col"><div class="diff-header">' + modified_label + '</div>' + right_html + '</div></div>'
    
    st.markdown(html, unsafe_allow_html=True)



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
    # Initialize State Manager
    CodeReviewStateManager.initialize()
    
    back_to_home("CodeReview")
    st.markdown('<h2 class="main-header">Code Review & Testing <span style="font-size: 0.6em; vertical-align: middle; background-color: #FF4B4B; color: white; padding: 2px 8px; border-radius: 4px;">BETA</span></h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-powered code quality assurance (Experimental)</p>', unsafe_allow_html=True)
    
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
                                     type=['py', 'ipynb', 'js', 'ts', 'java', 'sql', 'go', 'rs', 'cpp', 'rb', 'php'],
                                     key="code_uploader")
    
    if uploaded_file:
        # Detect or use selected language
        if selected_lang == "Auto-detect":
            language = detect_language(uploaded_file.name)
        else:
            language = languages[selected_lang]
        
        st.info(f"**Language:** {language.upper()}")
        
        # Reset state if new file is loaded (check if file changed)
        # We use name + size to be robust
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        current_file_id = st.session_state.get('last_file_id', '')
        
        if file_id != current_file_id:
            # Use State Manager to safely reset and switch files
            CodeReviewStateManager.set_new_file(uploaded_file.name, "", language) # Code set later
            st.session_state.last_file_id = file_id
            st.rerun()


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
                # Update State via Manager logic (explicitly set fields)
                st.session_state.review_report = ""
                st.session_state.failure_scenarios = []
                st.session_state.original_code = code
                st.session_state.original_filename = uploaded_file.name
                st.session_state.language = language
                st.session_state.analysis_complete = False
                
                tabs = st.tabs([
                    "📋 Code Review", 
                    "🧪 Unit Tests", 
                    "🔗 Functional Tests", 
                    "⚠️ Failure Scenarios"
                ])
                
                # Code Review
                with tabs[0]:
                    if do_review:
                        with st.spinner("⏳ Analyzing code for issues..."):
                            try:
                                # Get Markdown Report
                                review_report = review_code_with_llm(code, language, uploaded_file.name)
                                
                                if not review_report:
                                    st.error("Received empty response from LLM")
                                else:
                                    st.session_state.review_report = review_report
                                    st.markdown(review_report)
                                    
                            except Exception as e:
                                show_error_with_details(e, "Error during analysis")
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
                                show_error_with_details(e, "Error generating unit tests")
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
                                show_error_with_details(e, "Error generating functional tests")
                    else:
                        st.info("Functional test generation not requested")
                
                # Failure Scenarios
                with tabs[3]:
                    if do_failures:
                        with st.spinner("⏳ Generating failure scenarios..."):
                            try:
                                failures_json = generate_failure_scenarios_with_llm(code, language)
                                if not failures_json:
                                    raise ValueError("Empty response from LLM")
                                
                                try:
                                    # Use safe parser (returns dict or raises error)
                                    failures = SafeLLMParser.parse_json(failures_json, default={"scenarios": []})
                                except Exception as e:
                                    st.warning(f"⚠️ Partially failed to parse scenarios. Showing raw output below.")
                                    st.write(failures_json[:200] + "...")
                                    failures = {"scenarios": []}
                                
                                for scenario in failures.get('scenarios', []):
                                    st.warning(f"**Function:** {scenario.get('function', 'General')}")
                                    st.write(f"**Input:** `{scenario.get('input')}`")
                                    st.write(f"**Reason:** {scenario.get('reason')}")
                                    st.write(f"**Expected:** {scenario.get('expected')}")
                                    st.divider()
                                
                                # Store for fix_all_issues
                                st.session_state.failure_scenarios = failures.get('scenarios', [])
                            except Exception as e:
                                show_error_with_details(e, "Error generating failure scenarios")
                    else:
                        st.info("Failure scenario generation not requested")
                
                # Mark analysis as complete via Manager
                CodeReviewStateManager.mark_analysis_complete()
        
        # ============================================
        # SECTION 2: SOLUTIONS (Sequential)
        # ============================================
        if st.session_state.get('analysis_complete', False):
            st.markdown("---")
            st.markdown("## 💡 Solutions")
            st.info("ℹ️ **Workflow:** Documentation → Fix Issues. Results cascade separately.")
            
            # Solution 1: Add Documentation
            st.markdown("### 📝 Step 1: Add Comments & Documentation")
            st.markdown("Add comprehensive inline comments and documentation to make the code more maintainable.")
            st.info("ℹ️ **This ONLY adds comments** - No code logic will be changed")
            
            # Buttons row
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                add_docs_btn = st.button("📝 Add Documentation", type="secondary", key="add_docs")
            
            with col2:
                if st.session_state.get('documented_code'):
                    undo_docs_btn = st.button("↩️ Undo", help="Revert to original code", key="undo_docs")
                else:
                    undo_docs_btn = False
            
            with col3:
                if st.session_state.get('documented_code'):
                    retry_docs_btn = st.button("🔄 Retry", help="Regenerate documentation", key="retry_docs")
                else:
                    retry_docs_btn = False


            with col4:

                skip_docs_btn = st.button("⏭️ Skip", help="Skip documentation, go to Fix Issues", key="skip_docs", type="primary")
            
            # Handle button clicks
            if add_docs_btn or retry_docs_btn:
                with st.spinner("⏳ Adding documentation... Please wait"):
                    try:
                        documented_code = add_comments_and_documentation(st.session_state.original_code, st.session_state.language)
                        
                        if not documented_code or not documented_code.strip():
                            st.error("❌ AI returned empty response. Please try again.")
                        else:
                            st.session_state.documented_code = documented_code
                            st.rerun()  # Refresh to show the result
                    except Exception as e:
                        show_error_with_details(e, "Error adding documentation")
                        st.session_state.documented_code = None # Ensure clear on error
                    except Exception as e:
                        show_error_with_details(e, "Error adding documentation")
                        
                    # Validate syntax of generated code
                    if st.session_state.get('documented_code'):
                        if not validate_code_syntax(st.session_state.documented_code, st.session_state.language):
                            st.warning("⚠️ **Warning:** The generated code seems to have syntax errors. Please check the diff carefully before accepting.")
                        else:
                            st.info("✅ Code syntax validated successfully.")

            
            elif skip_docs_btn:
                st.session_state.skip_documentation = True
                st.info("✅ Skipped documentation - You can now go to Fix Issues")
                st.rerun()
            
            elif undo_docs_btn:
                # Remove documented code
                if 'documented_code' in st.session_state:
                    del st.session_state.documented_code
                st.success("✅ Reverted to original code")
                st.rerun()
            
            # Display documented code if it exists and is not None
            if st.session_state.get('documented_code'):
                st.success("✅ Documentation added successfully!")
                st.info("ℹ️ **Only comments were added** - No code logic will be changed")
                
                # Side-by-side comparison
                st.markdown("#### 📊 Side-by-Side Comparison")
                show_side_by_side_comparison(
                    st.session_state.original_code, 
                    st.session_state.documented_code, 
                    st.session_state.language,
                    "📄 Original Code",
                    "📝 With Documentation"
                )
                
                # Accept and Download workflow
                st.markdown("---")
                col_accept, col_download = st.columns(2)
                
                with col_accept:
                    if st.button("✅ Accept Documentation", type="primary", key="accept_docs"):
                        st.session_state.docs_accepted = True
                        st.success("✅ Documentation accepted!")
                        st.rerun()
                
                with col_download:
                    if st.session_state.get('docs_accepted', False):
                        st.download_button(
                            "📥 Download Documented Code",
                            st.session_state.documented_code,
                            st.session_state.original_filename,
                            help="Download the code with documentation",
                            key="download_docs"
                        )
                    else:
                        st.button("📥 Download (Accept First)", disabled=True, help="Please accept the documentation before downloading")
                
                # Button to use documented code for fixing
                st.markdown("---")
                if st.button("➡️ Use Documented Code for Fix Issues", help="Fix Issues will use the documented code instead of original", key="use_docs_for_fix"):
                    st.session_state.use_documented_for_fix = True
                    st.success("✅ Fix Issues will now use the documented code!")
                    st.rerun()
                
                if st.session_state.get('use_documented_for_fix', False):
                    st.info("ℹ️ **Fix Issues will use the documented code**")


            
            # Solution 2: Fix All Issues
            st.markdown("---")
            st.markdown("### 🔧 Step 2: Fix All Issues")
            st.markdown("Auto-fix all identified issues and add error handling for failure scenarios.")
            
            # Determine which code to use as base
            if st.session_state.get('use_documented_for_fix', False) and 'documented_code' in st.session_state:
                base_code = st.session_state.documented_code
                base_label = "📝 documented code"
            else:
                base_code = st.session_state.original_code
                base_label = "📄 original code"
            
            st.info(f"ℹ️ Will fix issues in the **{base_label}**")
            
            if st.button("🔧 Fix All Issues", type="primary", key="fix_issues_btn"):
                # Check if we have issues to fix
                if not st.session_state.get('review_report') and not st.session_state.failure_scenarios:
                    st.warning("⚠️ No issues or failure scenarios found to fix. Run Code Review and Failure Scenarios first!")
                else:
                    st.error("⚠️ **CRITICAL WARNING:** AI-generated fixes may introduce new bugs or change functionality!")
                    st.warning("🔍 **You MUST:**\n- Review every change carefully\n- Test the fixed code thoroughly\n- Validate it doesn't break existing functionality\n- Check for security issues")
                    
                    with st.spinner("⏳ Fixing all issues... Please wait"):
                        try:
                            result = fix_all_issues(
                                base_code, 
                                st.session_state.language, 
                                st.session_state.get('review_report', 'Fix general issues'), 
                                st.session_state.failure_scenarios
                            )
                            
                            # Handle structured response (dict) or legacy response (str)
                            if not result:
                                st.error("❌ AI returned empty response for fixes.")
                            elif isinstance(result, dict):
                                st.session_state.fixed_code = result.get('fixed_code', '')
                                st.session_state.fix_details = result.get('changes', [])
                            else:
                                st.session_state.fixed_code = str(result)
                                st.session_state.fix_details = []
                                
                            st.rerun()
                            st.rerun()
                        except Exception as e:
                            show_error_with_details(e, "Error fixing issues")
                            
                        # Validate syntax of fixed code
                        if 'fixed_code' in st.session_state:
                             if not validate_code_syntax(st.session_state.fixed_code, st.session_state.language):
                                st.warning("⚠️ **Warning:** The fixed code seems to have syntax errors. Please check carefully.")

            
            # Display fixed code if it exists and is not None
            if st.session_state.get('fixed_code'):
                st.success("✅ Code fixed successfully!")
                st.info(f"**Fixed:** Issues from report and {len(st.session_state.failure_scenarios)} failure scenarios")
                
                # Show Detailed Fix Log
                if 'fix_details' in st.session_state and st.session_state.fix_details:
                    with st.expander("🛠️ Detailed Fix Log (Click to view changes)", expanded=False):
                        for change in st.session_state.fix_details:
                            st.markdown(f"**Issue:** {change.get('issue_summary', 'Unknown')}")
                            st.markdown(f"**Fix:** {change.get('fix_explanation', 'No explanation')}")
                            st.caption(f"📍 Approx. Line: {change.get('line_number', 'N/A')}")
                            st.divider()
                
                # Determine comparison base
                if st.session_state.get('use_documented_for_fix', False) and 'documented_code' in st.session_state:
                    comparison_base = st.session_state.documented_code
                    comparison_label = "📝 Documented Code"
                else:
                    comparison_base = st.session_state.original_code
                    comparison_label = "📄 Original Code"
                
                # Side-by-side comparison
                st.markdown("#### 📊 Side-by-Side Comparison")
                show_side_by_side_comparison(
                    comparison_base,
                    st.session_state.fixed_code,
                    st.session_state.language,
                    comparison_label,
                    "🔧 Fixed Code"
                )
                
                # Accept and Download workflow
                st.markdown("---")
                col_accept, col_download = st.columns(2)
                
                with col_accept:
                    if st.button("✅ Accept Fixed Code", type="primary", key="accept_fixed"):
                        st.session_state.fixed_accepted = True
                        st.success("✅ Fixed code accepted!")
                        st.rerun()
                
                with col_download:
                    if st.session_state.get('fixed_accepted', False):
                        st.download_button(
                            "📥 Download Fixed Code",
                            st.session_state.fixed_code,
                            st.session_state.original_filename,
                            help="Download the fixed code",
                            key="download_fixed"
                        )
                    else:
                        st.button("📥 Download (Accept First)", disabled=True, help="Please accept the fixed code before downloading")

    # Debug Helper (Safe to keep in prod as it is collapsed)
    with st.expander("🛠️ Debug Information (Developer Only)", expanded=False):
        st.write("Current Session State IDs:")
        st.json({
            "original_filename": st.session_state.get('original_filename'),
            "has_doc_code": bool(st.session_state.get('documented_code')),
            "has_fixed_code": bool(st.session_state.get('fixed_code')),
            "analysis_complete": st.session_state.get('analysis_complete'),
            "file_id": st.session_state.get('last_file_id')
        })
