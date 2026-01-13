"""
Requirement Interpreter UI
Translate business requirements into data specifications
"""
import streamlit as st
import json
from common.ui.navigation import render_page_header
from tools.requirement_interpreter.nlp_parser import NLPParser
from tools.requirement_interpreter.spec_generator import SpecGenerator


def render():
    """Render the Requirement Interpreter page"""
    render_page_header(
        title="Requirement Interpreter",
        subtitle="Translate business questions into precise data specifications automatically",
        icon="🔄",
        status="gamma"
    )
    
    st.info("🧪 **Gamma Version** - Experimental feature. Feedback welcome!")
    
    # Input Section
    st.markdown("### 📝 Business Requirement")
    st.caption("Paste text from email, Jira, Slack, or any business communication")
    
    requirement_text = st.text_area(
        "Enter business requirement",
        height=150,
        placeholder="Example: Show me total revenue by product category for last quarter, excluding returns",
        label_visibility="collapsed"
    )
    
    # Optional inputs
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Domain Glossary** (Optional)")
            glossary_text = st.text_area(
                "Domain glossary (JSON)",
                height=100,
                placeholder='{"revenue": "Total sales amount", "churn": "Customer cancellation rate"}',
                help="Define domain-specific terms"
            )
        
        with col2:
            st.markdown("**Metrics Catalog** (Optional)")
            catalog_text = st.text_area(
                "Existing metrics (JSON)",
                height=100,
                placeholder='{"MRR": "Monthly Recurring Revenue", "CAC": "Customer Acquisition Cost"}',
                help="Reference existing metric definitions"
            )
    
    # Interpret button
    if st.button("🔍 Interpret Requirement", type="primary", use_container_width=True, 
                disabled=not requirement_text):
        
        # Parse glossary and catalog
        glossary = None
        metrics_catalog = None
        
        try:
            if glossary_text.strip():
                glossary = json.loads(glossary_text)
        except:
            st.warning("⚠️ Invalid glossary JSON, proceeding without it")
        
        try:
            if catalog_text.strip():
                metrics_catalog = json.loads(catalog_text)
        except:
            st.warning("⚠️ Invalid metrics catalog JSON, proceeding without it")
        
        with st.spinner("Parsing requirement..."):
            # Parse with NLP
            parser = NLPParser()
            parsed = parser.parse_requirement(requirement_text)
            
            st.session_state.parsed_req = parsed
        
        with st.spinner("Generating specification..."):
            # Generate spec with LLM
            generator = SpecGenerator()
            spec = generator.generate_spec(parsed, glossary, metrics_catalog)
            
            st.session_state.spec = spec
        
        st.success("✅ Requirement interpreted successfully!")
        st.rerun()
    
    # Display results
    if 'spec' in st.session_state and 'parsed_req' in st.session_state:
        display_results(st.session_state.spec, st.session_state.parsed_req)
    
    else:
        # Empty state
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.info("👆 Enter a business requirement to get started!")
        
        # Example use cases
        st.markdown("### 💡 Example Requirements")
        
        examples = [
            "Show me monthly active users trend for the last 6 months",
            "What's the average order value by region for Q4 2023?",
            "Compare revenue growth between product lines year over year",
            "Calculate customer churn rate by subscription tier"
        ]
        
        for example in examples:
            if st.button(f"📋 {example}", key=f"ex_{hash(example)}", use_container_width=True):
                st.session_state.example_req = example
                st.rerun()
        
        # Load example if clicked
        if 'example_req' in st.session_state:
            st.text_area("", value=st.session_state.example_req, key="loaded_example")
            del st.session_state.example_req


def display_results(spec, parsed_req):
    """Display interpretation results"""
    
    # Parsed Entities
    st.markdown("---")
    st.markdown("## 🔍 Parsed Entities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Metrics Detected**")
        if parsed_req['metrics']:
            for metric in parsed_req['metrics']:
                st.markdown(f"• `{metric}`")
        else:
            st.caption("None detected")
    
    with col2:
        st.markdown("**Time Dimensions**")
        if parsed_req['time_dimensions']:
            for dim in parsed_req['time_dimensions']:
                st.markdown(f"• `{dim}`")
        else:
            st.caption("None detected")
    
    with col3:
        st.markdown("**Intent**")
        st.info(f"**{parsed_req['intent'].replace('_', ' ').title()}**")
    
    # Metric Definitions
    if spec.get('metric_definitions'):
        st.markdown("---")
        st.markdown("## 📊 Metric Definitions")
        
        for metric_def in spec['metric_definitions']:
            st.markdown(f"• {metric_def}")
    
    # Grain & Filters
    if spec.get('grain_and_filters'):
        st.markdown("---")
        st.markdown("## 🎯 Grain & Filters")
        
        for key, value in spec['grain_and_filters'].items():
            st.markdown(f"**{key}:** {value}")
    
    # Clarifying Questions
    if spec.get('clarifying_questions'):
        st.markdown("---")
        st.markdown("## ❓ Clarifying Questions")
        st.warning("These questions should be answered before implementation:")
        
        for i, question in enumerate(spec['clarifying_questions'], 1):
            st.markdown(f"{i}. {question}")
    
    # SQL Specification
    if spec.get('sql_spec'):
        st.markdown("---")
        st.markdown("## 💻 SQL Specification")
        
        st.code(spec['sql_spec'], language='sql')
    
    # Assumptions
    if spec.get('assumptions'):
        st.markdown("---")
        st.markdown("## 📋 Assumptions")
        
        for assumption in spec['assumptions']:
            st.markdown(f"• {assumption}")
    
    # Export
    st.markdown("---")
    st.markdown("## 📥 Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON export
        export_data = {
            'requirement': spec['original_requirement'],
            'specification': spec
        }
        st.download_button(
            label="📥 Download Specification (JSON)",
            data=json.dumps(export_data, indent=2),
            file_name="requirement_spec.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # SQL export
        if spec.get('sql_spec'):
            st.download_button(
                label="📥 Download SQL",
                data=spec['sql_spec'],
                file_name="query.sql",
                mime="text/plain",
                use_container_width=True
            )
