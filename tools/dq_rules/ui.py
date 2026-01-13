"""
Data Quality Rule Generator UI
Automatically generate intelligent DQ rules
"""
import streamlit as st
import pandas as pd
import json
from common.ui.navigation import render_page_header
from tools.dq_rules.pattern_analyzer import PatternAnalyzer
from tools.dq_rules.rule_generator import RuleGenerator
from tools.dq_rules.explainer import RuleExplainer


def render():
    """Render the DQ Rule Generator page"""
    render_page_header(
        title="Data Quality Rule Generator",
        subtitle="Generate intelligent, context-aware data quality rules automatically",
        icon="✅",
        status="gamma"
    )
    
    st.info("🧪 **Gamma Version** - Experimental feature. Feedback welcome!")
    
    # File Upload
    st.markdown("### 📤 Upload Dataset Sample")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a sample of your dataset to generate DQ rules"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded dataset: {len(df)} rows × {len(df.columns)} columns")
            
            # Business criticality tags
            with st.expander("⚙️ Configuration"):
                st.markdown("**Business Criticality Tags** (Optional)")
                st.caption("Mark critical columns for higher priority rules")
                
                criticality = {}
                cols = st.columns(3)
                for i, col in enumerate(df.columns):
                    with cols[i % 3]:
                        crit = st.selectbox(
                            col,
                            options=['medium', 'high', 'low'],
                            key=f"crit_{col}",
                            label_visibility="visible"
                        )
                        criticality[col] = crit
                
                st.markdown("---")
                framework = st.selectbox(
                    "Validation Framework",
                    options=['pandas', 'great_expectations'],
                    help="Choose framework for generated validation code"
                )
                
                generate_explanations = st.checkbox(
                    "Generate AI Explanations",
                    value=True,
                    help="Use LLM to explain rules in business terms"
                )
            
            # Generate button
            if st.button("🔍 Generate DQ Rules", type="primary", use_container_width=True):
                with st.spinner("Analyzing data patterns..."):
                    # Analyze patterns
                    analyzer = PatternAnalyzer(df)
                    patterns = analyzer.analyze_patterns()
                    
                    # Generate rules
                    generator = RuleGenerator()
                    rules = generator.generate_rules(patterns, criticality)
                    
                    # Store in session state
                    st.session_state.dq_rules = rules
                    st.session_state.dq_patterns = patterns
                    st.session_state.dq_framework = framework
                    
                    # Generate explanations if requested
                    if generate_explanations:
                        with st.spinner("Generating AI explanations..."):
                            explainer = RuleExplainer()
                            explanations = explainer.explain_rules(rules)
                            st.session_state.dq_explanations = explanations
                
                st.success(f"✅ Generated {len(rules)} DQ rules!")
                st.rerun()
            
            # Display results
            if 'dq_rules' in st.session_state:
                display_results(
                    st.session_state.dq_rules,
                    st.session_state.get('dq_explanations'),
                    st.session_state.dq_framework
                )
                
        except Exception as e:
            st.error(f"❌ Error loading dataset: {str(e)}")
    
    else:
        # Empty state
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.info("👆 Upload a dataset sample to generate DQ rules!")
        
        # Features
        st.markdown("### 💡 What You'll Get")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📋 DQ Rules**
            - Null checks
            - Type validation
            - Range validation
            - Format validation
            """)
        
        with col2:
            st.markdown("""
            **💻 Validation Code**
            - Pandas code
            - Great Expectations
            - Ready to deploy
            - Customizable
            """)
        
        with col3:
            st.markdown("""
            **🤖 AI Explanations**
            - Business impact
            - Priority ranking
            - Implementation guide
            - Failure scenarios
            """)


def display_results(rules, explanations, framework):
    """Display generated DQ rules"""
    
    # AI Explanations
    if explanations:
        st.markdown("---")
        st.markdown("## 🤖 AI-Generated Insights")
        
        st.markdown(f"**Summary:** {explanations['summary']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔴 Critical Rules")
            for rule in explanations.get('critical_rules', []):
                st.markdown(f"• {rule}")
        
        with col2:
            st.markdown("### 📊 Business Impact")
            for impact in explanations.get('business_impact', []):
                st.markdown(f"• {impact}")
        
        if explanations.get('priority'):
            st.markdown("### 🎯 Implementation Priority")
            for i, priority in enumerate(explanations['priority'], 1):
                st.markdown(f"{i}. {priority}")
    
    # Rules Table
    st.markdown("---")
    st.markdown("## 📋 Generated DQ Rules")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rules", len(rules))
    with col2:
        critical = sum(1 for r in rules if r.get('severity') == 'critical')
        st.metric("Critical", critical)
    with col3:
        high = sum(1 for r in rules if r.get('severity') == 'high')
        st.metric("High", high)
    with col4:
        medium = sum(1 for r in rules if r.get('severity') == 'medium')
        st.metric("Medium", medium)
    
    # Rules details
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    for i, rule in enumerate(rules, 1):
        severity_color = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(rule.get('severity', 'medium'), '⚪')
        
        with st.expander(f"{severity_color} Rule {i}: {rule['column']} - {rule['rule_type']}"):
            st.markdown(f"**Description:** {rule['description']}")
            st.markdown(f"**Severity:** {rule.get('severity', 'medium').upper()}")
            st.code(rule['validation_code'], language='python')
            st.caption(f"Failure Message: {rule['failure_message']}")
    
    # Validation Code
    st.markdown("---")
    st.markdown("## 💻 Validation Code")
    
    generator = RuleGenerator()
    validation_code = generator.generate_validation_code(rules, framework)
    
    st.code(validation_code, language='python')
    
    # Download options
    st.markdown("---")
    st.markdown("## 📥 Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON export
        rules_json = json.dumps(rules, indent=2)
        st.download_button(
            label="📥 Download Rules (JSON)",
            data=rules_json,
            file_name="dq_rules.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Code export
        st.download_button(
            label="📥 Download Validation Code",
            data=validation_code,
            file_name=f"dq_validation_{framework}.py",
            mime="text/plain",
            use_container_width=True
        )
