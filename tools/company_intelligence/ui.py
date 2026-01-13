"""
Company Intelligence & Market Research Copilot UI
Structured company intelligence with natural language Q&A
"""
import streamlit as st
import json
from common.ui.navigation import render_page_header
from common.llm.client import get_client


def render():
    """Render the Company Intelligence page"""
    render_page_header(
        title="Company Intelligence & Market Research Copilot",
        subtitle="Convert scattered company data into structured, queryable intelligence",
        icon="🏢",
        status="gamma"
    )
    
    st.info("🧪 **Gamma Version** - Crunchbase + SimilarWeb + Analyst Brain")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Company Profile", "💬 Ask Questions", "📊 Insights"])
    
    # Tab 1: Company Profile
    with tab1:
        st.markdown("### 🏢 Generate Company Profile")
        
        with st.form("company_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name / URL *", placeholder="e.g., Stripe or stripe.com")
                industry = st.selectbox("Industry", ['', 'Technology', 'Healthcare', 'Finance', 'Retail', 'Other'])
            
            with col2:
                country = st.text_input("Country", placeholder="e.g., United States")
                competitors = st.text_input("Competitors (optional)", placeholder="e.g., Square, PayPal")
            
            submitted = st.form_submit_button("🔍 Generate Profile", type="primary")
        
        if submitted and company_name:
            with st.spinner("Analyzing company data..."):
                profile = generate_company_profile(company_name, industry, country, competitors)
                st.session_state.company_profile = profile
            st.success("✅ Company profile generated!")
            st.rerun()
        
        if 'company_profile' in st.session_state:
            display_company_profile(st.session_state.company_profile)
    
    # Tab 2: Q&A
    with tab2:
        if 'company_profile' not in st.session_state:
            st.warning("⚠️ Generate a company profile first")
        else:
            st.markdown("### 💬 Ask Questions About the Company")
            question = st.text_input("Your question", placeholder="What does this company sell in India?")
            
            if question and st.button("🔍 Get Answer", type="primary"):
                with st.spinner("Analyzing..."):
                    answer = answer_company_question(st.session_state.company_profile, question)
                    st.session_state.qa_answer = answer
                st.rerun()
            
            if 'qa_answer' in st.session_state:
                st.markdown("### 💡 Answer")
                st.success(st.session_state.qa_answer)
    
    # Tab 3: Insights
    with tab3:
        st.markdown("### 📊 Market Research Capabilities")
        st.info("""
        **What You Can Research:**
        - Product offerings by market
        - Revenue indicators & growth signals
        - Technology stack analysis
        - Hiring trends & expansion signals
        - Competitive positioning
        """)


def generate_company_profile(company: str, industry: str, country: str, competitors: str) -> dict:
    """Generate structured company profile"""
    client = get_client()
    
    prompt = f"""
Analyze this company and create a structured intelligence profile:

Company: {company}
Industry: {industry or 'Unknown'}
Country: {country or 'Unknown'}
Competitors: {competitors or 'None provided'}

Provide:

PRODUCTS & SERVICES:
- [Product 1]
- [Product 2]

TARGET MARKETS:
- [Market 1]
- [Market 2]

REVENUE INDICATORS:
- Estimated size: [Range]
- Growth signals: [Indicators]

HIRING SIGNALS:
- Recent hiring: [Yes/No]
- Key roles: [Roles]

TECHNOLOGY STACK (inferred):
- [Tech 1]
- [Tech 2]

EXPANSION SIGNALS:
- [Signal 1]
- [Signal 2]
"""
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": "You are a market research analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return {'company': company, 'analysis': response.choices[0].message.content}
    except Exception as e:
        return {'company': company, 'analysis': f'Error: {str(e)}'}


def answer_company_question(profile: dict, question: str) -> str:
    """Answer natural language questions about company"""
    client = get_client()
    
    prompt = f"""
Based on this company profile, answer the question:

PROFILE:
{profile.get('analysis', '')}

QUESTION:
{question}

Provide a clear, concise answer based on the profile data.
"""
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": "You are a business analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def display_company_profile(profile):
    """Display company profile"""
    st.markdown("---")
    st.markdown(f"## 🏢 {profile['company']} - Company Profile")
    st.markdown(profile['analysis'])
    
    # Export
    st.markdown("---")
    st.download_button(
        "📥 Download Profile (JSON)",
        data=json.dumps(profile, indent=2),
        file_name=f"{profile['company']}_profile.json",
        mime="application/json",
        use_container_width=True
    )
