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
from tools.data_profiling.visualizations import (
    create_distribution_plots, create_box_plots, 
    create_correlation_heatmap, create_quality_gauge
)
from tools.data_profiling.ml_models import BasicMLTrainer
from tools.data_profiling.persona_layouts import (
    display_technical_persona,
    display_executive_persona,
    display_business_persona
)


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
                # Try to detect delimiter and encoding
                try:
                    # First, try with default settings
                    df = pd.read_csv(uploaded_file)
                except Exception:
                    # If that fails, try common delimiters
                    uploaded_file.seek(0)  # Reset file pointer
                    for delimiter in [',', ';', '\t', '|']:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, delimiter=delimiter)
                            # Check if we got more than 1 column
                            if len(df.columns) > 1:
                                break
                        except Exception:
                            continue
                    else:
                        # If all delimiters fail, try with python engine
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, engine='python', sep=None)
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
    """Display profiling results with persona-specific UX"""
    
    # Get current audience from session state
    current_audience = st.session_state.get('audience', 'technical')
    
    # Route to persona-specific display
    if current_audience == 'technical':
        display_technical_persona(profile, anomalies, insights, df, narrative)
        return
    elif current_audience == 'executive':
        display_executive_persona(profile, anomalies, insights, df, narrative)
        return
    else:  # business
        display_business_persona(profile, anomalies, insights, df, narrative)
        return
    
    # LEGACY CODE BELOW (will be removed after testing)
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
    
    # Overview - Audience-Specific Metrics
    st.markdown("---")
    st.markdown("## 📊 Dataset Overview")
    
    # Get current audience from session state (default to technical if not set)
    current_audience = st.session_state.get('audience', 'technical')
    
    if current_audience == 'technical':
        # Technical: Detailed technical metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
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
        with col6:
            # Calculate null density
            total_cells = profile['overview']['rows'] * profile['overview']['columns']
            null_density = (profile['overview']['total_missing'] / total_cells * 100) if total_cells > 0 else 0
            st.metric("Null Density", f"{null_density:.1f}%")
    
    elif current_audience == 'executive':
        # Executive: High-level business metrics
        total_cells = profile['overview']['rows'] * profile['overview']['columns']
        completeness = ((total_cells - profile['overview']['total_missing']) / total_cells * 100) if total_cells > 0 else 0
        
        # Data Quality Score (simple heuristic: completeness - duplicate penalty)
        duplicate_penalty = (profile['overview']['duplicate_rows'] / profile['overview']['rows'] * 10) if profile['overview']['rows'] > 0 else 0
        quality_score = max(0, completeness - duplicate_penalty)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", f"{profile['overview']['rows']:,}")
        with col2:
            st.metric("Data Quality Score", f"{quality_score:.0f}/100", 
                     delta=f"{completeness:.0f}% complete" if completeness >= 90 else None,
                     delta_color="normal" if completeness >= 90 else "inverse")
        with col3:
            st.metric("Completeness", f"{completeness:.1f}%",
                     delta="Good" if completeness >= 95 else "Needs Attention",
                     delta_color="normal" if completeness >= 95 else "inverse")
        with col4:
            reliability = "High" if profile['overview']['duplicate_rows'] == 0 and completeness > 95 else \
                         "Medium" if completeness > 85 else "Low"
            st.metric("Data Reliability", reliability)
    
    else:  # business
        # Business: Operational metrics
        total_cells = profile['overview']['rows'] * profile['overview']['columns']
        completeness = ((total_cells - profile['overview']['total_missing']) / total_cells * 100) if total_cells > 0 else 0
        usable_records = profile['overview']['rows'] - profile['overview']['duplicate_rows']
        duplicate_rate = (profile['overview']['duplicate_rows'] / profile['overview']['rows'] * 100) if profile['overview']['rows'] > 0 else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Records", f"{profile['overview']['rows']:,}")
        with col2:
            st.metric("Usable Records", f"{usable_records:,}",
                     delta=f"-{profile['overview']['duplicate_rows']} duplicates" if profile['overview']['duplicate_rows'] > 0 else "No duplicates")
        with col3:
            st.metric("Duplicate Rate", f"{duplicate_rate:.1f}%",
                     delta="Clean" if duplicate_rate == 0 else "Action Needed",
                     delta_color="normal" if duplicate_rate == 0 else "inverse")
        with col4:
            st.metric("Missing Values", profile['overview']['total_missing'],
                     delta=f"{completeness:.0f}% complete")
        with col5:
            # Operational readiness
            readiness = "Ready" if completeness > 95 and duplicate_rate < 1 else \
                       "Needs Cleanup" if completeness > 85 else "Critical Issues"
            st.metric("Operational Status", readiness)
    
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
