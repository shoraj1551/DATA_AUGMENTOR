"""
Selling Opportunity & Market Signal Finder UI
Identify selling opportunities based on market signals
"""
import streamlit as st
import json
from common.ui.navigation import render_page_header
from common.llm.client import get_client


def render():
    """Render the Selling Opportunity page"""
    render_page_header(
        title="Selling Opportunity & Market Signal Finder",
        subtitle="Identify where and who to sell to based on real-world signals",
        icon="📈",
        status="gamma"
    )
    
    st.info("🧪 **Gamma Version** - CB Insights + Apollo + Strategy Analyst")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Find Opportunities", "📊 Signals", "💡 Tips"])
    
    # Tab 1: Find Opportunities
    with tab1:
        st.markdown("### 🎯 Search for Selling Opportunities")
        
        with st.form("opportunity_form"):
            product_category = st.text_input("Product Category *", placeholder="e.g., CRM Software, Cloud Infrastructure")
            
            col1, col2 = st.columns(2)
            with col1:
                target_industries = st.multiselect(
                    "Target Industries",
                    ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing', 'Education']
                )
            with col2:
                target_countries = st.multiselect(
                    "Target Countries",
                    ['United States', 'United Kingdom', 'India', 'Germany', 'Singapore', 'Other']
                )
            
            icp_description = st.text_area(
                "Ideal Customer Profile (ICP)",
                height=100,
                placeholder="Describe your ideal customer: company size, revenue, pain points..."
            )
            
            submitted = st.form_submit_button("🔍 Find Opportunities", type="primary")
        
        if submitted and product_category:
            with st.spinner("Analyzing market signals..."):
                opportunities = find_opportunities(
                    product_category,
                    target_industries,
                    target_countries,
                    icp_description
                )
                st.session_state.opportunities = opportunities
            st.success("✅ Opportunities identified!")
            st.rerun()
        
        if 'opportunities' in st.session_state:
            display_opportunities(st.session_state.opportunities)
    
    # Tab 2: Signals
    with tab2:
        st.markdown("### 📊 Market Signals We Track")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚀 Growth Signals")
            st.success("""
            - Hiring sprees
            - Funding announcements
            - Office expansions
            - New product launches
            """)
        
        with col2:
            st.markdown("#### 📢 Market Signals")
            st.info("""
            - New regulations
            - Industry shifts
            - Technology adoption
            - Competitive moves
            """)
    
    # Tab 3: Tips
    with tab3:
        st.markdown("### 💡 Sales Intelligence Tips")
        st.warning("""
        **Best Practices:**
        1. ✅ Define clear ICP criteria
        2. ✅ Monitor signals regularly
        3. ✅ Act fast on hot opportunities
        4. ✅ Personalize outreach angles
        5. ✅ Track conversion rates
        """)


def find_opportunities(product: str, industries: list, countries: list, icp: str) -> dict:
    """Find selling opportunities"""
    client = get_client()
    
    prompt = f"""
Identify selling opportunities for this product:

PRODUCT: {product}
TARGET INDUSTRIES: {', '.join(industries) if industries else 'Any'}
TARGET COUNTRIES: {', '.join(countries) if countries else 'Any'}
IDEAL CUSTOMER PROFILE: {icp or 'Not specified'}

Provide:

TOP OPPORTUNITIES (Ranked):
1. [Company/Segment] - [Why this is an opportunity]
2. [Company/Segment] - [Why this is an opportunity]
3. [Company/Segment] - [Why this is an opportunity]

MARKET SIGNALS:
- [Signal 1: Hiring/Funding/Expansion]
- [Signal 2: Regulatory/Technology change]

BUYING INTENT INDICATORS:
- [Indicator 1]
- [Indicator 2]

SUGGESTED OUTREACH ANGLES:
- [Angle 1: How to approach]
- [Angle 2: Value proposition]

TIMING RECOMMENDATION:
[When to reach out and why]
"""
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": "You are a sales strategy analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return {'product': product, 'analysis': response.choices[0].message.content}
    except Exception as e:
        return {'product': product, 'analysis': f'Error: {str(e)}'}


def display_opportunities(opportunities):
    """Display opportunities"""
    st.markdown("---")
    st.markdown(f"## 📈 Opportunities for {opportunities['product']}")
    st.markdown(opportunities['analysis'])
    
    # Export
    st.markdown("---")
    st.download_button(
        "📥 Download Opportunities (JSON)",
        data=json.dumps(opportunities, indent=2),
        file_name=f"opportunities_{opportunities['product']}.json",
        mime="application/json",
        use_container_width=True
    )
