"""
Company Intelligence & Market Research Copilot UI
Structured company intelligence with natural language Q&A
"""
import streamlit as st
import json
import logging
from datetime import datetime

from common.ui.navigation import render_page_header
from common.llm.client import get_client

# Import new services and models
from .services.registry import RegistryService
from .services.scraper import WebsiteScraper
from .utils.risk_engine import RiskEngine
from .models.company_profile import CompanyProfile, VerificationStatus, DigitalPresence, RiskAssessment

# Initialize services
registry_service = RegistryService()
scraper_service = WebsiteScraper()
risk_engine = RiskEngine()

logger = logging.getLogger(__name__)

def render():
    """Render the Company Intelligence page"""
    render_page_header(
        title="Company Intelligence & Market Research Copilot",
        subtitle="Convert scattered company data into structured, queryable intelligence",
        icon="🏢",
        status="gamma"
    )
    
    st.info("ℹ️ **MVP Version** - Real-time Verification + Web Scraping + Risk Assessment")
    
    # Tabs
    tab1, tab2 = st.tabs(["🔍 Company Profile", "💬 Ask Questions"])
    
    # Tab 1: Company Profile
    with tab1:
        render_profile_generation()
    
    # Tab 2: Q&A
    with tab2:
        render_qa_section()

def render_profile_generation():
    """Render the profile generation form and results"""
    st.markdown("### 🏢 Generate Intelligence Profile")
    
    with st.form("company_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", placeholder="e.g., Strike or Google")
            industry = st.selectbox("Industry", ['', 'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Other'])
        
        with col2:
            country = st.text_input("Country *", placeholder="e.g., United States, India, UK")
            website = st.text_input("Website (Optional - for scraping)", placeholder="e.g., stripe.com")
        
        submitted = st.form_submit_button("🔍 Generate Profile", type="primary")
    
    if submitted:
        if not company_name or not country:
            st.error("Please provide Company Name and Country")
            return

        # Clear previous session state
        if 'company_profile' in st.session_state:
            del st.session_state.company_profile
        if 'qa_answer' in st.session_state:
            del st.session_state.qa_answer

        with st.spinner("🕵️‍♂️ Investigating company... (Verifying registry, scraping web, assessing risk)"):
            try:
                profile = build_company_profile(company_name, country, website, industry)
                st.session_state.company_profile = profile
                st.success("✅ Company profile generated successfully!")
                
                # Force rerun to show results
                st.rerun()
            except Exception as e:
                st.error(f"Error generating profile: {str(e)}")
                logger.error(f"Profile generation error: {str(e)}", exc_info=True)
    
    # Display Profile if exists
    if 'company_profile' in st.session_state:
        display_structured_profile(st.session_state.company_profile)

def build_company_profile(name: str, country: str, website: str, industry: str) -> CompanyProfile:
    """Orchestrate the profile building process"""
    
    # 1. Verify Company
    verification = registry_service.verify_company(name, country)
    
    # 2. Scrape Website
    # If website not provided, we might be able to guess or skip
    # For MVP, we stick to provided website or skip scraping if empty
    digital_data = {}
    if website:
        digital_data = scraper_service.scrape_basic_info(website)
    
    # 3. Build Profile Object
    profile = CompanyProfile(
        name=name,
        industry=industry,
        query_country=country,
        verification=verification,
        digital_presence=DigitalPresence(
            website=website,
            description=digital_data.get('description'),
            tech_stack=digital_data.get('tech_stack', []),
            linkedin_url=digital_data.get('social_links', {}).get('linkedin'),
            twitter_url=digital_data.get('social_links', {}).get('twitter'),
            facebook_url=digital_data.get('social_links', {}).get('facebook')
        )
    )
    
    # 4. Assess Risk
    risk_assessment = risk_engine.assess_risk(profile)
    profile.risk_assessment = risk_assessment
    
    return profile

def display_structured_profile(profile: CompanyProfile):
    """Display the structured profile with UI polish"""
    
    st.markdown("---")
    
    # --- Header Section with Verification Badge ---
    col_header, col_badge = st.columns([3, 1])
    with col_header:
        st.markdown(f"## {profile.name}")
        if profile.verification.registration_number:
            st.caption(f"ID: {profile.verification.registration_number} | {profile.verification.jurisdiction or profile.query_country}")
    
    with col_badge:
        render_verification_badge(profile.verification)
        render_risk_badge(profile.risk_assessment)

    # --- Metrics Row ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Status", profile.verification.status)
    m2.metric("Founded", profile.verification.incorporation_date or "Unknown")
    m3.metric("Tech Stack", len(profile.digital_presence.tech_stack))
    m4.metric("Risk Score", f"{profile.risk_assessment.score}/100", 
             delta=profile.risk_assessment.score-100 if profile.risk_assessment.score < 100 else 0)

    st.markdown("---")

    # --- Detailed Tabs ---
    tab_overview, tab_digital, tab_raw = st.tabs(["📊 Overview", "🌐 Digital Presence", "📜 Raw Data"])
    
    with tab_overview:
        col_ov1, col_ov2 = st.columns([2, 1])
        with col_ov1:
            st.subheader("Business Description")
            if profile.digital_presence.description:
                st.info(profile.digital_presence.description)
            else:
                st.warning("No description available (Website not provided or scraped)")
            
            st.subheader("Registration Details")
            st.markdown(f"**Address:** {profile.verification.registered_address or 'Not available'}")
            st.markdown(f"**Source:** {profile.verification.source}")
        
        with col_ov2:
            st.subheader("🚨 Risk Alerts")
            if profile.risk_assessment.alerts:
                for alert in profile.risk_assessment.alerts:
                    st.error(f"• {alert}")
            else:
                st.success("No major risk alerts detected")
    
    with tab_digital:
        st.subheader("Online Footprint")
        if profile.digital_presence.website:
            st.markdown(f"**Website:** [{profile.digital_presence.website}]({profile.digital_presence.website})")
        
        st.markdown("#### Social Media")
        cols = st.columns(4)
        if profile.digital_presence.linkedin_url:
            cols[0].markdown(f"[LinkedIn]({profile.digital_presence.linkedin_url})")
        if profile.digital_presence.twitter_url:
            cols[1].markdown(f"[Twitter]({profile.digital_presence.twitter_url})")
        
        st.markdown("#### Technology Stack")
        if profile.digital_presence.tech_stack:
            st.write(", ".join([f"`{t}`" for t in profile.digital_presence.tech_stack]))
        else:
            st.text("No technologies detected")

    with tab_raw:
        st.json(profile.model_dump())
    
    # Export
    st.markdown("---")
    st.download_button(
        "📥 Download Verified Profile (JSON)",
        data=profile.model_dump_json(indent=2),
        file_name=f"{profile.name}_verified_profile.json",
        mime="application/json"
    )

def render_verification_badge(verification: VerificationStatus):
    """Render a visual badge for verification status"""
    if verification.is_verified:
        if verification.status.lower() in ['active', 'open', 'registered']:
            st.success("✅ VERIFIED & ACTIVE", icon="✅")
        else:
            st.warning(f"⚠️ VERIFIED: {verification.status.upper()}", icon="⚠️")
    else:
        st.error("❌ NOT FOUND IN REGISTRY", icon="❌")

def render_risk_badge(risk: RiskAssessment):
    """Render risk level badge"""
    if risk.risk_level == "Low":
        st.success(f"Risk: {risk.risk_level}")
    elif risk.risk_level == "Medium":
        st.warning(f"Risk: {risk.risk_level}")
    else:
        st.error(f"Risk: {risk.risk_level}")

def render_qa_section():
    """Render Q&A section"""
    if 'company_profile' not in st.session_state:
        st.warning("⚠️ Generate a company profile first to ask questions.")
        return

    st.markdown("### 💬 Ask Questions")
    st.info("Ask questions based on the verified data and scraped content.")
    
    question = st.text_input("Your question", placeholder="What technologies do they use?")
    
    if question and st.button("🔍 Get Answer", type="primary"):
        with st.spinner("Analyzing profile data..."):
            answer = answer_company_question(st.session_state.company_profile, question)
            st.session_state.qa_answer = answer
    
    if 'qa_answer' in st.session_state:
        st.markdown("### 💡 Answer")
        st.markdown(st.session_state.qa_answer)

def answer_company_question(profile: CompanyProfile, question: str) -> str:
    """Answer natural language questions about company using the structured profile"""
    client = get_client()
    
    # Convert profile to text context
    context = profile.model_dump_json(indent=2)
    
    prompt = f"""
    Based on this VALIDATED company profile, answer the question.
    
    COMPANY PROFILE DATA:
    {context}
    
    QUESTION:
    {question}
    
    Provide a clear, concise answer based ONLY on the provided data. 
    If the information is not in the profile, say "I don't have that information in the validated profile."
    """
    
    try:
        response = client.call_with_fallback(
            feature_name="company_intelligence",
            messages=[
                {"role": "system", "content": "You are a factual intelligence analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response
    except Exception as e:
        return f"Error generation answer: {str(e)}"
