"""
Contact Intelligence & Confidence Engine UI
Find, verify, and score business contacts
"""
import streamlit as st
import json
from common.ui.navigation import render_page_header
from tools.contact_intelligence.contact_finder import ContactFinder
from tools.contact_intelligence.confidence_scorer import ConfidenceScorer


def render():
    """Render the Contact Intelligence page"""
    render_page_header(
        title="Contact Intelligence & Confidence Engine",
        subtitle="Find, generate, verify, and score business contacts with AI",
        icon="👤",
        status="gamma"
    )
    
    st.info("🧪 **Gamma Version** - Experimental feature. ZoomInfo-lite with GenAI reasoning.")
    
    # Initialize
    if 'contact_finder' not in st.session_state:
        st.session_state.contact_finder = ContactFinder()
    if 'confidence_scorer' not in st.session_state:
        st.session_state.confidence_scorer = ConfidenceScorer()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Find Contact", "📊 Confidence Analysis", "💡 Tips"])
    
    # Tab 1: Find Contact
    with tab1:
        st.markdown("### 🔍 Search for Business Contact")
        
        with st.form("contact_search"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input(
                    "Company Name / Domain *",
                    placeholder="e.g., Microsoft or microsoft.com"
                )
                
                role = st.text_input(
                    "Role / Job Title",
                    placeholder="e.g., VP of Sales, Head of Marketing"
                )
            
            with col2:
                industry = st.selectbox(
                    "Industry",
                    options=['', 'Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing', 'Other']
                )
                
                geography = st.text_input(
                    "Geography / Location",
                    placeholder="e.g., San Francisco, CA"
                )
            
            submitted = st.form_submit_button("🔍 Find Contact", type="primary")
        
        if submitted and company_name:
            with st.spinner("Searching for contact information..."):
                contact = st.session_state.contact_finder.find_contact(
                    company_name=company_name,
                    role=role if role else None,
                    industry=industry if industry else None,
                    geography=geography if geography else None
                )
                st.session_state.contact_result = contact
            
            # Auto-score confidence
            with st.spinner("Analyzing confidence..."):
                scoring = st.session_state.confidence_scorer.score_contact(contact)
                st.session_state.confidence_result = scoring
            
            st.success("✅ Contact found and analyzed!")
            st.rerun()
        
        # Display results
        if 'contact_result' in st.session_state:
            display_contact_result(
                st.session_state.contact_result,
                st.session_state.get('confidence_result')
            )
    
    # Tab 2: Confidence Analysis
    with tab2:
        if 'confidence_result' not in st.session_state:
            st.warning("⚠️ Please find a contact first in the 'Find Contact' tab")
        else:
            display_confidence_analysis(st.session_state.confidence_result)
    
    # Tab 3: Tips
    with tab3:
        st.markdown("### 💡 Contact Intelligence Tips")
        
        st.markdown("#### 🎯 Best Practices")
        st.success("""
        **For Best Results:**
        1. ✅ Use company domain (e.g., microsoft.com) for better accuracy
        2. ✅ Be specific with role titles
        3. ✅ Include industry for better context
        4. ✅ Verify contacts through multiple sources
        5. ✅ Check confidence scores before outreach
        """)
        
        st.markdown("#### 📧 Common Email Patterns")
        st.info("""
        **Most Common Formats:**
        - firstname.lastname@company.com (60%)
        - firstnamelastname@company.com (20%)
        - first.last@company.com (10%)
        - flastname@company.com (5%)
        - Other variations (5%)
        """)
        
        st.markdown("#### ⚠️ Verification Tips")
        st.warning("""
        **Always Verify:**
        - Check LinkedIn profile
        - Verify on company website
        - Use email verification tools
        - Test with professional outreach
        - Respect privacy and compliance
        """)


def display_contact_result(contact, scoring):
    """Display contact search results"""
    st.markdown("---")
    st.markdown("## 👤 Contact Information")
    
    # Confidence Score Badge
    if scoring:
        score = scoring.get('overall_score', 0)
        if score >= 80:
            st.success(f"### ✅ Confidence Score: {score}/100 (High)")
        elif score >= 50:
            st.warning(f"### ⚠️ Confidence Score: {score}/100 (Medium)")
        else:
            st.error(f"### ❌ Confidence Score: {score}/100 (Low)")
    
    # Contact Details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Basic Information")
        st.markdown(f"**Company:** {contact.get('company', 'N/A')}")
        st.markdown(f"**Name:** {contact.get('name', 'N/A')}")
        st.markdown(f"**Title:** {contact.get('title', 'N/A')}")
    
    with col2:
        st.markdown("### 📞 Contact Details")
        st.markdown(f"**Email:** `{contact.get('email', 'N/A')}`")
        st.markdown(f"**Phone:** {contact.get('phone', 'Not Available')}")
        if contact.get('linkedin'):
            st.markdown(f"**LinkedIn:** {contact.get('linkedin', 'N/A')}")
    
    # Email Pattern
    if contact.get('email_pattern'):
        st.markdown("### 📧 Email Pattern Reasoning")
        st.info(contact['email_pattern'])
    
    # Email Variations
    if contact.get('name') and contact.get('company'):
        st.markdown("### 🔄 Email Variations to Try")
        finder = st.session_state.contact_finder
        variations = finder.generate_email_variations(
            contact['name'],
            contact['company']
        )
        if variations:
            for i, email in enumerate(variations[:5], 1):
                st.code(email)
    
    # Sources
    if contact.get('sources'):
        st.markdown("### 📚 Source References")
        for source in contact['sources']:
            st.markdown(f"• {source}")
    
    # Verification Steps
    if contact.get('verification_steps'):
        st.markdown("### ✅ Verification Steps")
        for i, step in enumerate(contact['verification_steps'], 1):
            st.markdown(f"{i}. {step}")
    
    # Alternatives
    if contact.get('alternatives'):
        st.markdown("### 🔄 Alternative Contacts")
        for alt in contact['alternatives']:
            st.markdown(f"• {alt}")
    
    # Export
    st.markdown("---")
    export_data = json.dumps(contact, indent=2)
    st.download_button(
        label="📥 Download Contact Info (JSON)",
        data=export_data,
        file_name=f"contact_{contact.get('company', 'unknown')}.json",
        mime="application/json",
        use_container_width=True
    )


def display_confidence_analysis(scoring):
    """Display confidence analysis"""
    st.markdown("## 📊 Confidence Analysis")
    
    # Overall Score
    score = scoring.get('overall_score', 0)
    st.metric("Overall Confidence Score", f"{score}/100")
    
    # Breakdown
    if scoring.get('breakdown'):
        st.markdown("### 📈 Score Breakdown")
        for metric, value in scoring['breakdown'].items():
            st.markdown(f"**{metric}:** {value}")
    
    # Reasoning
    if scoring.get('reasoning'):
        st.markdown("### 💭 Confidence Reasoning")
        st.info(scoring['reasoning'])
    
    # Flags
    col1, col2 = st.columns(2)
    
    with col1:
        if scoring.get('green_flags'):
            st.markdown("### ✅ Green Flags")
            for flag in scoring['green_flags']:
                st.success(f"✓ {flag}")
    
    with col2:
        if scoring.get('red_flags'):
            st.markdown("### ⚠️ Red Flags")
            for flag in scoring['red_flags']:
                st.error(f"✗ {flag}")
    
    # Improvements
    if scoring.get('improvements'):
        st.markdown("### 🎯 Improvement Suggestions")
        for i, improvement in enumerate(scoring['improvements'], 1):
            st.markdown(f"{i}. {improvement}")
