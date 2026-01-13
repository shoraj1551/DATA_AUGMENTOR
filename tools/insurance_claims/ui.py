"""
Insurance Claims Review & Reconciliation UI
Automate policy analysis and claims validation
"""
import streamlit as st
import json
from common.ui.navigation import render_page_header
from tools.insurance_claims.policy_analyzer import PolicyAnalyzer
from tools.insurance_claims.validator import ClaimsValidator


def render():
    """Render the Insurance Claims page"""
    render_page_header(
        title="Insurance Claims Review & Reconciliation",
        subtitle="Analyze policies, validate claims, and streamline the approval process",
        icon="🏥",
        status="gamma"
    )
    
    st.info("🧪 **Gamma Version** - Experimental feature. Feedback welcome!")
    
    # Initialize
    if 'policy_analyzer' not in st.session_state:
        st.session_state.policy_analyzer = PolicyAnalyzer()
    if 'claims_validator' not in st.session_state:
        st.session_state.claims_validator = ClaimsValidator()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📄 Analyze Policy", "✅ Validate Claim", "📚 Knowledge Base"])
    
    # Tab 1: Policy Analysis
    with tab1:
        st.markdown("### 📄 Upload Insurance Policy")
        st.caption("Upload your policy document to extract rules, coverage, exclusions, and contacts")
        
        policy_file = st.file_uploader(
            "Choose policy document",
            type=['txt', 'pdf'],
            help="Upload policy document in TXT or PDF format"
        )
        
        policy_text = st.text_area(
            "Or paste policy text here",
            height=200,
            placeholder="Paste your insurance policy document text here..."
        )
        
        if st.button("🔍 Analyze Policy", type="primary", disabled=not (policy_file or policy_text)):
            with st.spinner("Analyzing policy document..."):
                # Get policy text
                if policy_file:
                    if policy_file.type == 'text/plain':
                        policy_content = policy_file.read().decode('utf-8')
                    else:
                        st.warning("PDF parsing not yet implemented. Please paste text or use TXT file.")
                        policy_content = policy_text
                else:
                    policy_content = policy_text
                
                # Analyze
                analysis = st.session_state.policy_analyzer.analyze_policy(policy_content)
                st.session_state.policy_analysis = analysis
            
            st.success("✅ Policy analyzed successfully!")
            st.rerun()
        
        # Display analysis
        if 'policy_analysis' in st.session_state:
            display_policy_analysis(st.session_state.policy_analysis)
    
    # Tab 2: Claims Validation
    with tab2:
        if 'policy_analysis' not in st.session_state:
            st.warning("⚠️ Please analyze a policy first in the 'Analyze Policy' tab")
        else:
            st.markdown("### ✅ Enter Claim Details")
            
            with st.form("claim_form"):
                claim_type = st.selectbox(
                    "Claim Type",
                    options=['Medical', 'Dental', 'Vision', 'Prescription', 'Other']
                )
                
                claim_amount = st.number_input(
                    "Claim Amount ($)",
                    min_value=0.0,
                    step=0.01
                )
                
                treatment_date = st.date_input("Treatment/Service Date")
                
                provider_name = st.text_input("Provider/Facility Name")
                
                diagnosis_code = st.text_input(
                    "Diagnosis/Procedure Code",
                    placeholder="e.g., ICD-10 code"
                )
                
                additional_info = st.text_area(
                    "Additional Information",
                    height=100,
                    placeholder="Any additional details about the claim..."
                )
                
                submitted = st.form_submit_button("🔍 Validate Claim", type="primary")
            
            if submitted:
                with st.spinner("Validating claim against policy..."):
                    claim_details = {
                        'claim_type': claim_type,
                        'amount': claim_amount,
                        'treatment_date': str(treatment_date),
                        'provider': provider_name,
                        'diagnosis_code': diagnosis_code,
                        'additional_info': additional_info
                    }
                    
                    validation = st.session_state.claims_validator.validate_claim(
                        claim_details,
                        st.session_state.policy_analysis
                    )
                    st.session_state.claim_validation = validation
                
                st.success("✅ Claim validated!")
                st.rerun()
            
            # Display validation
            if 'claim_validation' in st.session_state:
                display_claim_validation(st.session_state.claim_validation)
    
    # Tab 3: Knowledge Base
    with tab3:
        st.markdown("### 📚 Insurance Claims Knowledge Base")
        
        st.markdown("#### 💡 Quick Tips")
        st.info("""
        **Before Submitting a Claim:**
        1. ✅ Review your policy coverage rules
        2. ✅ Check exclusions and limitations
        3. ✅ Gather all required documents
        4. ✅ Verify provider is in-network
        5. ✅ Submit within policy deadlines
        """)
        
        st.markdown("#### 📋 Common Documents Needed")
        st.markdown("""
        - Medical bills and receipts
        - Treatment records
        - Prescription details
        - Provider information
        - Diagnosis codes
        - Pre-authorization (if required)
        """)
        
        st.markdown("#### ⚠️ Common Denial Reasons")
        st.warning("""
        - Service not covered under policy
        - Out-of-network provider
        - Missing documentation
        - Exceeded coverage limits
        - Pre-authorization not obtained
        - Claim submitted after deadline
        """)


def display_policy_analysis(analysis):
    """Display policy analysis results"""
    st.markdown("---")
    st.markdown("## 📊 Policy Analysis Results")
    
    # Coverage Rules
    if analysis.get('coverage_rules'):
        st.markdown("### ✅ Coverage Rules")
        for rule in analysis['coverage_rules']:
            st.success(f"✓ {rule}")
    
    # Exclusions
    if analysis.get('exclusions'):
        st.markdown("### ⛔ Exclusions & Limitations")
        for exclusion in analysis['exclusions']:
            st.error(f"✗ {exclusion}")
    
    # Loopholes
    if analysis.get('loopholes'):
        st.markdown("### ⚠️ Loopholes & Ambiguities")
        for loophole in analysis['loopholes']:
            st.warning(f"⚠️ {loophole}")
    
    # Claim Requirements
    if analysis.get('claim_requirements'):
        st.markdown("### 📋 Claim Requirements")
        for req in analysis['claim_requirements']:
            st.info(f"• {req}")
    
    # Contacts
    if analysis.get('contacts'):
        st.markdown("### 📞 Key Contacts")
        for contact, info in analysis['contacts'].items():
            st.markdown(f"**{contact}:** {info}")
    
    # Important Dates
    if analysis.get('important_dates'):
        st.markdown("### 📅 Important Dates")
        for date_type, date_value in analysis['important_dates'].items():
            st.markdown(f"**{date_type}:** {date_value}")
    
    # Export
    st.markdown("---")
    export_data = json.dumps(analysis, indent=2)
    st.download_button(
        label="📥 Download Policy Analysis (JSON)",
        data=export_data,
        file_name="policy_analysis.json",
        mime="application/json",
        use_container_width=True
    )


def display_claim_validation(validation):
    """Display claim validation results"""
    st.markdown("---")
    st.markdown("## 🔍 Claim Validation Results")
    
    # Eligibility Status
    status = validation.get('eligibility_status', 'NEEDS REVIEW')
    if status == 'APPROVED':
        st.success(f"### ✅ Status: {status}")
    elif status == 'DENIED':
        st.error(f"### ❌ Status: {status}")
    else:
        st.warning(f"### ⚠️ Status: {status}")
    
    # Validation Results
    if validation.get('validation_results'):
        st.markdown("### 📊 Validation Checks")
        for result in validation['validation_results']:
            st.info(f"• {result}")
    
    # Issues
    if validation.get('issues'):
        st.markdown("### ⚠️ Identified Issues")
        for issue in validation['issues']:
            st.error(f"❌ {issue}")
    
    # Discrepancies
    if validation.get('discrepancies'):
        st.markdown("### 🔍 Discrepancies Found")
        for disc in validation['discrepancies']:
            st.warning(f"⚠️ {disc}")
    
    # Next Steps
    if validation.get('next_steps'):
        st.markdown("### 🎯 Next Steps for You")
        st.success("**Follow these steps to proceed:**")
        for i, step in enumerate(validation['next_steps'], 1):
            st.markdown(f"{i}. {step}")
    
    # Approval Probability
    if validation.get('approval_probability'):
        st.markdown("### 📈 Approval Probability")
        st.info(validation['approval_probability'])
    
    # Export
    st.markdown("---")
    export_data = json.dumps(validation, indent=2)
    st.download_button(
        label="📥 Download Validation Report (JSON)",
        data=export_data,
        file_name="claim_validation.json",
        mime="application/json",
        use_container_width=True
    )
