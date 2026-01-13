"""
Strategic Sales Intelligence UI
Merged: Decision History + Competitive Narrative + Procurement Signals + Market Risk
"""
import streamlit as st
import json
from common.ui.navigation import render_page_header
from common.llm.client import get_client


def render():
    """Render the Strategic Sales Intelligence page"""
    render_page_header(
        title="Strategic Sales Intelligence",
        subtitle="Decision history, competitive narrative, procurement signals & market risk analysis",
        icon="🎯",
        status="gamma"
    )
    
    st.info("🧪 **Gamma Version** - 4-in-1: Behavioral Psychology + Brand Intelligence + Budget Tracking + Risk Analysis")
    
    # Tabs for 4 merged capabilities
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Decision History", 
        "📢 Competitive Narrative", 
        "💰 Procurement Signals", 
        "⚠️ Market Risk"
    ])
    
    # Tab 1: Decision History & Buying Behavior
    with tab1:
        st.markdown("### 🧠 Decision History & Buying Behavior Analyzer")
        st.caption("Understand HOW companies make buying decisions")
        
        company = st.text_input("Company Name", placeholder="e.g., Acme Corp", key="dh_company")
        
        if st.button("🔍 Analyze Decision History", type="primary", disabled=not company):
            with st.spinner("Analyzing decision patterns..."):
                analysis = analyze_decision_history(company)
                st.session_state.decision_history = analysis
            st.rerun()
        
        if 'decision_history' in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 Decision Behavior Profile")
            st.markdown(st.session_state.decision_history)
            
            st.download_button(
                "📥 Download Analysis",
                data=st.session_state.decision_history,
                file_name=f"decision_history_{company}.txt",
                use_container_width=True
            )
    
    # Tab 2: Competitive Narrative
    with tab2:
        st.markdown("### 📢 Competitive Narrative & Messaging Analyzer")
        st.caption("Analyze how companies position themselves vs competitors")
        
        col1, col2 = st.columns(2)
        with col1:
            target_company = st.text_input("Target Company", placeholder="e.g., Stripe", key="cn_company")
        with col2:
            region = st.selectbox("Region", ['Global', 'US', 'EU', 'APAC', 'Other'])
        
        competitors_list = st.text_input("Competitors (comma-separated)", placeholder="e.g., Square, PayPal")
        
        if st.button("🔍 Analyze Narrative", type="primary", disabled=not target_company):
            with st.spinner("Analyzing messaging & positioning..."):
                narrative = analyze_competitive_narrative(target_company, region, competitors_list)
                st.session_state.narrative = narrative
            st.rerun()
        
        if 'narrative' in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 Narrative Intelligence")
            st.markdown(st.session_state.narrative)
            
            st.download_button(
                "📥 Download Narrative Analysis",
                data=st.session_state.narrative,
                file_name=f"narrative_{target_company}.txt",
                use_container_width=True
            )
    
    # Tab 3: Procurement & Budget Signals
    with tab3:
        st.markdown("### 💰 Procurement & Budget Signal Tracker")
        st.caption("Follow the money - detect budget availability and spending intent")
        
        col1, col2 = st.columns(2)
        with col1:
            org_name = st.text_input("Organization/Company", placeholder="e.g., City of Austin", key="ps_org")
        with col2:
            spend_category = st.selectbox("Spend Category", ['', 'Software', 'Hardware', 'Services', 'Consulting', 'Other'])
        
        if st.button("🔍 Track Procurement Signals", type="primary", disabled=not org_name):
            with st.spinner("Tracking budget & procurement signals..."):
                signals = track_procurement_signals(org_name, spend_category)
                st.session_state.procurement = signals
            st.rerun()
        
        if 'procurement' in st.session_state:
            st.markdown("---")
            st.markdown("### 💰 Budget & Spending Intelligence")
            st.markdown(st.session_state.procurement)
            
            st.download_button(
                "📥 Download Procurement Signals",
                data=st.session_state.procurement,
                file_name=f"procurement_{org_name}.txt",
                use_container_width=True
            )
    
    # Tab 4: Market Risk & Entry Barriers
    with tab4:
        st.markdown("### ⚠️ Market Risk & Entry Barrier Analyzer")
        st.caption("Defensive intelligence - understand why selling may FAIL")
        
        col1, col2 = st.columns(2)
        with col1:
            target_country = st.selectbox("Target Country", ['United States', 'Germany', 'Japan', 'India', 'UK', 'Other'])
        with col2:
            target_industry = st.selectbox("Target Industry", ['SaaS', 'Healthcare', 'Finance', 'Retail', 'Other'])
        
        product_type = st.text_input("Product/Service Type", placeholder="e.g., Cloud CRM Software")
        
        if st.button("🔍 Analyze Market Risk", type="primary", disabled=not product_type):
            with st.spinner("Analyzing market barriers & risks..."):
                risk = analyze_market_risk(target_country, target_industry, product_type)
                st.session_state.market_risk = risk
            st.rerun()
        
        if 'market_risk' in st.session_state:
            st.markdown("---")
            st.markdown("### ⚠️ Market Risk Assessment")
            st.markdown(st.session_state.market_risk)
            
            st.download_button(
                "📥 Download Risk Analysis",
                data=st.session_state.market_risk,
                file_name=f"market_risk_{target_country}_{target_industry}.txt",
                use_container_width=True
            )


def analyze_decision_history(company: str) -> str:
    """Analyze company's buying decision patterns"""
    client = get_client()
    
    prompt = f"""
Analyze the buying decision behavior of {company}:

Provide insights on:

BUYING PREFERENCES:
- Build vs Buy tendency
- Vendor switching patterns
- Decision-making style

DECISION DRIVERS:
- What triggers vendor changes?
- Security/compliance influence
- Cost vs innovation balance

BUYING CYCLE:
- Typical evaluation period
- Decision-maker involvement
- Procurement process style

BEHAVIORAL PATTERNS:
- Risk tolerance
- Innovation adoption speed
- Vendor relationship style

Format as a clear, actionable profile.
"""
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": "You are a behavioral psychologist analyzing corporate buying patterns."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_competitive_narrative(company: str, region: str, competitors: str) -> str:
    """Analyze competitive messaging and positioning"""
    client = get_client()
    
    prompt = f"""
Analyze the competitive narrative for {company} in {region}:
Competitors: {competitors or 'Not specified'}

Provide:

CORE VALUE PROPOSITION:
- Main messaging themes
- Unique positioning

REGIONAL DIFFERENCES:
- How messaging varies by region
- Cultural adaptations

COMPETITIVE GAPS:
- What competitors emphasize
- Messaging opportunities
- Overused themes to avoid

NARRATIVE SHIFTS:
- Recent messaging changes
- Strategic pivots

Format as brand intelligence insights.
"""
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": "You are a brand strategist analyzing competitive narratives."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def track_procurement_signals(org: str, category: str) -> str:
    """Track procurement and budget signals"""
    client = get_client()
    
    prompt = f"""
Track procurement and budget signals for {org}:
Spend Category: {category or 'General'}

Analyze:

BUDGET SIGNALS:
- Budget cycle timing
- Spending priorities
- Cost pressure indicators

PROCUREMENT ACTIVITY:
- Recent tenders/RFPs
- Vendor consolidation moves
- Buying vs renewal likelihood

SPENDING INTENT:
- Investment areas
- Budget availability indicators
- Procurement role hiring

TIMING INTELLIGENCE:
- Best time to engage
- Budget approval cycles

Format as actionable procurement intelligence.
"""
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": "You are a procurement analyst tracking budget signals."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_market_risk(country: str, industry: str, product: str) -> str:
    """Analyze market entry risks and barriers"""
    client = get_client()
    
    prompt = f"""
Analyze market entry risks for selling {product} in {country} ({industry} industry):

Provide defensive intelligence:

MARKET RISK SCORE:
- Overall difficulty rating (1-10)
- Risk level assessment

ENTRY BARRIERS:
- Regulatory complexity
- Compliance requirements
- Local competition strength

RED FLAGS:
- Why selling may fail
- Common failure patterns
- Cultural resistance factors

MITIGATION STRATEGIES:
- How to overcome barriers
- Success factors
- Required adaptations

HISTORICAL CONTEXT:
- Past market exits
- Lessons from failures

Format as anti-opportunity intelligence for realistic planning.
"""
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": "You are a market risk analyst providing defensive intelligence."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
