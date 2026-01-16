"""
Insurance Claims Review & Reconciliation UI
Automate policy analysis and claims validation
"""
import streamlit as st
import json
from common.ui.navigation import render_page_header
from tools.insurance_claims.policy_analyzer import PolicyAnalyzer
from tools.insurance_claims.validator import ClaimsValidator
# Independent local modules
from tools.insurance_claims.document_processor import extract_text_from_file
from tools.insurance_claims.rag_agent import InsurancePolicyAgent
import traceback

def show_error_with_details(error: Exception, context: str = "Error"):
    """Show error with expandable technical details"""
    st.error(f"❌ **{context}:** {str(error)}")
    with st.expander("🛠️ Technical Details (For Debugging)"):
        st.code(traceback.format_exc(), language="python")

def render_hero_section():
    """Render the premium hero section explanation"""
    st.markdown("""
    <style>
    .hero-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6; 
        border: 1px solid #e0e0e0;
        height: 100%;
    }
    .dark-mode .hero-card {
        background-color: #262730;
        border-color: #404040;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="hero-card">
            <h3>📄 Deep Analysis</h3>
            <p>Upload your policy PDF to instantly extract <b>complex coverage rules</b>, exclusions, and hidden terms.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="hero-card">
            <h3>⚖️ Smart Compare</h3>
            <p>Upload <b>multiple policies</b> to see side-by-side comparisons. Find the best plan for your needs.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="hero-card">
            <h3>📋 Claim Strategy</h3>
            <p>Don't just validate. Get a <b>step-by-step checklist</b> of documents and deadlines to win your claim.</p>
        </div>
        """, unsafe_allow_html=True)
    st.divider()

def render_single_policy_view(filename, analysis):
    """Render detailed view for a single policy"""
    st.divider()
    st.markdown(f"## 📄 Policy Dashboard: {filename}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("✅ Coverage Highlights")
        for rule in analysis.get('coverage_rules', [])[:7]:
            st.success(f"{rule}")
            
        st.subheader("⚠️ Critical Exclusions")
        for exc in analysis.get('exclusions', [])[:5]:
            st.error(f"{exc}")
            
    with col2:
        st.subheader("📞 Key Contacts")
        for k, v in analysis.get('contacts', {}).items():
            st.info(f"**{k}**: {v}")
            
        if analysis.get('important_dates'):
             st.subheader("📅 Dates")
             st.json(analysis['important_dates'])

def render_comparison_view(analysis_map):
    """Render side-by-side comparison for multiple policies"""
    st.divider()
    st.subheader(f"📊 Comparison View ({len(analysis_map)} Policies)")
    
    filenames = list(analysis_map.keys())
    cols = st.columns(len(filenames))
    
    for idx, fname in enumerate(filenames):
        analysis = analysis_map[fname]
        with cols[idx]:
            st.markdown(f"### 📄 {fname}")
            
            with st.expander("✅ Coverage", expanded=True):
                for rule in analysis.get('coverage_rules', [])[:5]:
                    st.markdown(f"- {rule}")
            
            with st.expander("⛔ Exclusions", expanded=True):
                 for exc in analysis.get('exclusions', [])[:5]:
                    st.markdown(f":red[- {exc}]")
            
            with st.expander("📞 Contacts"):
                for k, v in analysis.get('contacts', {}).items():
                    st.markdown(f"**{k}**: {v}")

def render():
    """Render the Insurance Claims page"""
    render_page_header(
        title="Insurance Intelligence Hub",
        subtitle="Analyze, Compare, and Validate Insurance Policies with AI Precision",
        icon="🛡️",
        status="beta"
    )
    
    render_hero_section()
    
    # Initialize Session State
    if 'policy_analyzer' not in st.session_state:
        st.session_state.policy_analyzer = PolicyAnalyzer()
    if 'claims_validator' not in st.session_state:
        st.session_state.claims_validator = ClaimsValidator()
    if 'policy_map' not in st.session_state:
        st.session_state.policy_map = {}
    if 'analysis_map' not in st.session_state:
        st.session_state.analysis_map = {}
    if 'agent_map' not in st.session_state:
        st.session_state.agent_map = {}
    
    # Tabs
    tab1, tab2, tab2_chat, tab3 = st.tabs(["📊 Dashboard", "📋 How to Claim", "🤖 Agent Chat", "📚 Resources"])
    
    # ==========================================
    # Tab 1: Dashboard (Smart View)
    # ==========================================
    with tab1:
        st.subheader("1. Upload Policies")
        uploaded_files = st.file_uploader(
            "Upload one or more policy documents (PDF/TXT)",
            type=['txt', 'pdf'],
            accept_multiple_files=True,
            help="Upload 1 file for Deep Dive, or Multiple for Comparison."
        )
        
        if uploaded_files:
            if st.button(f"🔍 Analyze {len(uploaded_files)} Document(s)", type="primary"):
                # Clear state
                st.session_state.policy_map = {}
                st.session_state.analysis_map = {}
                st.session_state.agent_map = {}
                
                progress_bar = st.progress(0, text="Starting analysis...")
                
                try:
                    for i, file in enumerate(uploaded_files):
                        # Extract
                        text = extract_text_from_file(file)
                        if "Error" in text and len(text) < 200:
                            st.error(f"Failed to read {file.name}: {text}")
                            continue

                        # Classify
                        classification = st.session_state.policy_analyzer.is_insurance_policy(text)
                        if not classification.get('is_policy'):
                            st.warning(f"⚠️ '{file.name}' is NOT an insurance policy. Skipped.")
                            continue
                            
                        # Analyze
                        progress_bar.progress((i / len(uploaded_files)) * 0.5, text=f"Analyzing {file.name}...")
                        analysis = st.session_state.policy_analyzer.analyze_policy(text)
                        
                        # Store
                        st.session_state.policy_map[file.name] = text
                        st.session_state.analysis_map[file.name] = analysis
                        st.session_state.agent_map[file.name] = InsurancePolicyAgent(text)
                    
                    progress_bar.progress(1.0, text="Analysis Complete!")
                    st.success(f"Processed {len(st.session_state.analysis_map)} valid policies.")
                    
                except Exception as e:
                    show_error_with_details(e, "Processing Failed")
        
        # Smart View Logic
        if st.session_state.analysis_map:
            count = len(st.session_state.analysis_map)
            if count == 1:
                # Single View
                fname = list(st.session_state.analysis_map.keys())[0]
                render_single_policy_view(fname, st.session_state.analysis_map[fname])
            elif count > 1:
                # Multi View
                render_comparison_view(st.session_state.analysis_map)

    # ==========================================
    # Tab 2: How to Claim (Guidance)
    # ==========================================
    with tab2:
        if not st.session_state.analysis_map:
             st.info("👋 Analyze a policy first to get tailored claim guidance.")
        else:
            st.markdown("### 📋 Claim Strategy Guide")
            st.caption("Don't guess. Get a precise checklist for your specific situation.")
            
            selected_policy = st.selectbox("Select Policy", list(st.session_state.analysis_map.keys()))
            analysis = st.session_state.analysis_map[selected_policy]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                topic = st.text_input("What do you need to claim for?", placeholder="e.g. Knee Surgery, Car Accident, Lost Luggage")
            with col2:
                st.write("") # Spacer
                st.write("") 
                generate = st.button("🚀 Get Checklist", type="primary", use_container_width=True)
            
            if generate and topic:
                with st.spinner(f"Generating strategy for '{topic}'..."):
                    try:
                        guide = st.session_state.claims_validator.generate_claim_checklist(topic, analysis)
                        st.session_state.last_guide = guide
                    except Exception as e:
                        show_error_with_details(e)

            if 'last_guide' in st.session_state:
                guide = st.session_state.last_guide
                st.divider()
                
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.success("✅ Required Documents")
                    for doc in guide.get('required_documents', []):
                        st.markdown(f"- {doc}")
                        
                with c2:
                    st.info("👣 Step-by-Step Process")
                    for idx, step in enumerate(guide.get('steps', []), 1):
                        st.markdown(f"**{idx}.** {step}")
                        
                with c3:
                    st.error("⚠️ Critical Warnings")
                    if not guide.get('critical_warnings'):
                        st.markdown("_None detected_")
                    for warn in guide.get('critical_warnings', []):
                        st.markdown(f"- {warn}")

    # ==========================================
    # Tab 3: Agent Chat
    # ==========================================
    with tab2_chat:
        if not st.session_state.agent_map:
             st.info("👋 Upload policies to start chatting.")
        else:
            st.markdown("### 🤖 Policy Agent")
            
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            query = st.chat_input("Ask about coverage, limits, or specific terms...")
            
            if query:
                answers = {}
                with st.spinner("Consulting policies..."):
                    for fname, agent in st.session_state.agent_map.items():
                        answers[fname] = agent.answer_question(query)
                st.session_state.chat_history.append({"query": query, "answers": answers})
            
            for item in st.session_state.chat_history:
                st.chat_message("user").write(item["query"])
                with st.chat_message("assistant"):
                    if len(item["answers"]) == 1:
                        # Single view
                        val = list(item["answers"].values())[0]
                        st.markdown(val)
                    else:
                        # Multi view columns
                        cols = st.columns(len(item["answers"]))
                        for idx, (fname, ans) in enumerate(item["answers"].items()):
                            with cols[idx]:
                                st.markdown(f"**{fname}**")
                                st.markdown(ans)

    # ==========================================
    # Tab 4: Resources
    # ==========================================
    with tab3:
        st.markdown("### 📚 Insurance Resources")
        st.info("General tips for all policyholders.")
        st.markdown("""
        1. **Always Pre-Auth**: If in doubt, call before the procedure.
        2. **Keep the Bill**: Itemized bills are gold. Credit card slips aren't enough.
        3. **Watch the Clock**: Most policies have a 60-90 day filing window.
        """)
