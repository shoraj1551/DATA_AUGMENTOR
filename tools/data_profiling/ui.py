"""
Data Profiling & Auto-EDA UI
Automated dataset profiling and insights
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from common.ui.navigation import render_page_header
from tools.data_profiling.profiler import DataProfiler
from tools.data_profiling.insights import InsightGenerator
from tools.data_profiling.narrator import InsightNarrator


def render():
    """Render the Data Profiling page"""
    render_page_header(
        title="Data Profiling & Auto-EDA",
        subtitle="Automatically profile datasets and generate actionable insights",
        icon="📊",
        status="beta"
    )
    
    st.info("✨ **Beta Version** - Enhanced with AI Insights & Multi-format Support")
    
    # File Upload
    # File Upload
    st.markdown("### 📤 Upload Dataset")
    
    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Choose a file (CSV, Excel, Parquet, JSON)",
            type=['csv', 'xlsx', 'xls', 'parquet', 'json'],
            help="Upload a dataset to automatically profile. Supports CSV, Excel, Parquet, and JSON."
        )
    
    with col_up2:
        # Template download (optional, maybe later)
        st.info("💡 **Supported Formats:**\n- CSV (.csv)\n- Excel (.xlsx, .xls)\n- Parquet (.parquet)\n- JSON (.json)")
    
    if uploaded_file:
        # Load dataset based on file extension
        try:
            file_ext = uploaded_file.name.split('.')[-1].lower()
            
            if file_ext == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
            elif file_ext == 'parquet':
                df = pd.read_parquet(uploaded_file)
            elif file_ext == 'json':
                df = pd.read_json(uploaded_file)
            else:
                st.error(f"❌ Unsupported file format: {file_ext}")
                return

            st.success(f"✅ Loaded dataset: {len(df)} rows × {len(df.columns)} columns")
            
            # Sampling options
            with st.expander("⚙️ Profiling Settings"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    sample_size = st.number_input(
                        "Sample size (0 = all rows)",
                        min_value=0,
                        max_value=len(df),
                        value=min(10000, len(df)),
                        help="Number of rows to analyze (for large datasets)"
                    )
                with col2:
                    generate_insights = st.checkbox(
                        "Generate AI Insights",
                        value=True,
                        help="Use LLM to generate insights (requires API key)"
                    )
                with col3:
                    audience_sel = st.selectbox(
                        "Narrative Audience",
                        options=['Technical', 'Executive', 'Business'],
                        index=0,
                        help="Target audience for narrative generation"
                    )
                    audience = audience_sel.lower()
            
            # Check for audience change if profile exists
            if 'profile' in st.session_state and 'audience' in st.session_state:
                current_audience_val = st.session_state.audience
                if current_audience_val != audience:
                    st.warning(f"⚠️ Audience changed to '{audience_sel}'. Update the narrative to match.")
                    if st.button(f"🔄 Update Narrative for {audience_sel}", type="primary"):
                         with st.spinner(f"Updating narrative for {audience_sel}..."):
                             narrator = InsightNarrator()
                             narrative = narrator.generate_narrative(
                                 st.session_state.profile, 
                                 st.session_state.anomalies, 
                                 audience
                             )
                             st.session_state.narrative = narrative
                             st.session_state.audience = audience
                             st.rerun()

            # Profile button
            if st.button("🔍 Profile Dataset", type="primary", use_container_width=True):
                with st.spinner("Profiling dataset..."):
                    # Create profiler
                    profiler = DataProfiler(
                        df=df,
                        sample_size=sample_size if sample_size > 0 else None
                    )
                    
                    # Generate profile
                    profile = profiler.profile_dataset()
                    anomalies = profiler.detect_anomalies()
                    
                    # Store in session state
                    st.session_state.profile = profile
                    st.session_state.anomalies = anomalies
                    st.session_state.df = df
                    st.session_state.audience = audience
                    
                    # Generate insights if requested
                    if generate_insights:
                        with st.spinner("Generating AI insights..."):
                            insight_gen = InsightGenerator()
                            insights = insight_gen.generate_insights(profile, anomalies)
                            st.session_state.insights = insights
                        
                        # Generate narrative
                        with st.spinner(f"Creating {audience} narrative..."):
                            narrator = InsightNarrator()
                            narrative = narrator.generate_narrative(profile, anomalies, audience)
                            st.session_state.narrative = narrative
                
                st.success("✅ Profiling complete!")
                st.rerun()
            
            # Display results if available
            if 'profile' in st.session_state:
                display_profile_results(
                    st.session_state.profile,
                    st.session_state.anomalies,
                    st.session_state.get('insights'),
                    st.session_state.df,
                    st.session_state.get('narrative'),
                    st.session_state.get('audience', 'technical')
                )
                
        except Exception as e:
            st.error(f"❌ Error loading dataset: {str(e)}")
    
    else:
        # Empty state
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.info("👆 Upload a dataset (CSV, Excel, Parquet, JSON) to get started with automated profiling!")
        
        # Example features
        st.markdown("### 💡 What You'll Get")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📈 Statistics**
            - Column profiles
            - Missing data analysis
            - Duplicate detection
            """)
        
        with col2:
            st.markdown("""
            **🔍 Anomalies**
            - Outlier detection
            - Data quality issues
            - Pattern recognition
            """)
        
        with col3:
            st.markdown("""
            **🤖 AI Insights**
            - Automated analysis
            - Recommendations
            - Next steps
            """)


def display_profile_results(profile, anomalies, insights, df, narrative=None, audience='technical'):
    """Display profiling results"""
    
    # Narrative (if available) - Show first for executive summary
    if narrative:
        st.markdown("## 📖 Data Story")
        st.markdown(f"*Tailored for {audience.title()} audience*")
        
        # Executive Summary
        st.markdown("### Executive Summary")
        st.info(narrative['executive_summary'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Key Insights
            st.markdown("### 💡 Key Insights")
            for insight in narrative['insights']:
                st.success(f"✓ {insight}")
            
            # Recommended Actions
            st.markdown("### 🎯 Recommended Actions")
            for i, action in enumerate(narrative['actions'], 1):
                st.markdown(f"{i}. {action}")
        
        with col2:
            # Risk Alerts
            if narrative.get('risks'):
                st.markdown("### ⚠️ Risk Alerts")
                for risk in narrative['risks']:
                    st.warning(f"⚠️ {risk}")
    
    # AI Insights (if available)
    if insights:
        st.markdown("---")
        st.markdown("## 🤖 AI-Generated Insights")
        
        st.markdown(f"**Summary:** {insights['summary']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔍 Key Findings")
            for finding in insights['key_findings']:
                st.markdown(f"• {finding}")
        
        with col2:
            st.markdown("### 💡 Recommendations")
            for rec in insights['recommendations']:
                st.markdown(f"• {rec}")
        
        if insights.get('quality_issues'):
            st.markdown("### ⚠️ Data Quality Issues")
            for issue in insights['quality_issues']:
                st.warning(f"• {issue}")
    
    # Overview
    st.markdown("---")
    st.markdown("## 📊 Dataset Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Rows", f"{profile['overview']['rows']:,}")
    with col2:
        st.metric("Columns", profile['overview']['columns'])
    with col3:
        st.metric("Memory", f"{profile['overview']['memory_usage_mb']} MB")
    with col4:
        st.metric("Duplicates", profile['overview']['duplicate_rows'])
    with col5:
        st.metric("Missing", profile['overview']['total_missing'])
    
    # Anomalies
    if anomalies:
        st.markdown("---")
        st.markdown("## 🚨 Anomalies Detected")
        
        for anomaly in anomalies:
            severity_color = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(anomaly['severity'], '⚪')
            
            st.warning(f"{severity_color} **{anomaly['type']}** in `{anomaly['column']}`: {anomaly['detail']}")
    
    # Column Statistics
    st.markdown("---")
    st.markdown("## 📋 Column Statistics")
    
    columns_df = pd.DataFrame(profile['columns'])
    st.dataframe(columns_df, use_container_width=True, height=400)
    
    # Missing Data Visualization
    if profile['missing_data']['columns_with_missing'] > 0:
        st.markdown("---")
        st.markdown("## 📉 Missing Data Analysis")
        
        missing_data = profile['missing_data']['missing_by_column']
        fig = px.bar(
            x=list(missing_data.keys()),
            y=list(missing_data.values()),
            labels={'x': 'Column', 'y': 'Missing Count'},
            title='Missing Values by Column'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Download Report
    st.markdown("---")
    st.markdown("## 📥 Export Report")
    
    import json
    report = {
        'profile': profile,
        'anomalies': anomalies,
        'insights': insights if insights else {}
    }
    
    st.download_button(
        label="📥 Download JSON Report",
        data=json.dumps(report, indent=2),
        file_name="data_profile_report.json",
        mime="application/json",
        use_container_width=True
    )
