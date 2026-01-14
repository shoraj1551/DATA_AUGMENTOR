"""
Persona-specific display layouts for Data Profiling
"""
import streamlit as st
import pandas as pd
import numpy as np
from tools.data_profiling.visualizations import (
    create_distribution_plots, create_box_plots,
    create_correlation_heatmap, create_quality_gauge
)
from tools.data_profiling.ml_models import BasicMLTrainer


def display_technical_persona(profile, anomalies, insights, df, narrative):
    """Technical persona: Dense, data-rich with graphs and ML"""
    
    st.markdown("## 🔬 Technical Analysis Dashboard")
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Distributions", "🔗 Correlations", "🤖 ML Models"])
    
    with tab1:
        # Detailed metrics
        st.markdown("### Dataset Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        try:
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
                total_cells = profile['overview']['rows'] * profile['overview']['columns']
                null_density = (profile['overview']['total_missing'] / total_cells * 100) if total_cells > 0 else 0
                st.metric("Null Density", f"{null_density:.1f}%")
        except Exception as e:
            st.error(f"Error displaying metrics: {str(e)}")
        
        # Narrative
        if narrative:
            st.markdown("---")
            st.markdown("### 📖 Technical Summary")
            st.info(narrative.get('executive_summary', 'No summary available'))
            
            col1, col2 = st.columns(2)
            with col1:
                if narrative.get('insights'):
                    st.markdown("**Key Insights:**")
                    for insight in narrative['insights']:
                        st.success(f"✓ {insight}")
            with col2:
                if narrative.get('risks'):
                    st.markdown("**Risk Alerts:**")
                    for risk in narrative['risks']:
                        st.warning(f"⚠️ {risk}")
        
        # Anomalies
        if anomalies:
            st.markdown("---")
            st.markdown("### 🚨 Anomalies")
            for anomaly in anomalies:
                severity_color = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(anomaly['severity'], '⚪')
                st.warning(f"{severity_color} **{anomaly['type']}** in `{anomaly['column']}`: {anomaly['detail']}")
        
        # Column Statistics
        st.markdown("---")
        st.markdown("### 📋 Column Statistics")
        try:
            columns_df = pd.DataFrame(profile['columns'])
            st.dataframe(columns_df, use_container_width=True, height=400)
        except Exception as e:
            st.error(f"Error displaying column statistics: {str(e)}")
    
    with tab2:
        st.markdown("### Distribution Analysis")
        try:
            # Distribution plots
            dist_fig = create_distribution_plots(df, max_cols=6)
            if dist_fig:
                st.plotly_chart(dist_fig, use_container_width=True)
            else:
                st.info("📊 No numeric columns available for distribution plots")
            
            # Box plots
            st.markdown("---")
            box_fig = create_box_plots(df, max_cols=6)
            if box_fig:
                st.plotly_chart(box_fig, use_container_width=True)
            else:
                st.info("📊 No numeric columns available for box plots")
        except Exception as e:
            st.error(f"Error creating distribution plots: {str(e)}")
    
    with tab3:
        st.markdown("### Correlation Analysis")
        try:
            corr_fig = create_correlation_heatmap(df)
            if corr_fig:
                st.plotly_chart(corr_fig, use_container_width=True)
            else:
                st.info("📊 Need at least 2 numeric columns for correlation analysis")
        except Exception as e:
            st.error(f"Error creating correlation heatmap: {str(e)}")
    
    with tab4:
        st.markdown("### Machine Learning Models")
        
        # Check minimum data requirements
        if len(df) < 100:
            st.warning("⚠️ Dataset too small for reliable ML models (minimum 100 rows recommended)")
            st.info(f"Current dataset: {len(df)} rows")
            return
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            st.warning("⚠️ Need at least 2 numeric columns for ML modeling")
            return
        
        # Model configuration
        col1, col2, col3 = st.columns(3)
        with col1:
            target_col = st.selectbox("Target Column", numeric_cols)
        with col2:
            model_type = st.selectbox("Model Type", ["Regression", "Classification"])
        with col3:
            test_size = st.slider("Test Size %", 10, 40, 20) / 100
        
        if st.button("🚀 Train Models", type="primary"):
            try:
                with st.spinner("Training models..."):
                    trainer = BasicMLTrainer(df, target_col, model_type.lower())
                    trainer.prepare_data(test_size=test_size)
                    
                    if model_type == "Regression":
                        trainer.train_regression_models()
                    else:
                        trainer.train_classification_models()
                    
                    # Display results
                    st.success("✅ Models trained successfully!")
                    
                    # Performance chart
                    perf_fig = trainer.create_performance_chart()
                    st.plotly_chart(perf_fig, use_container_width=True)
                    
                    # Detailed metrics
                    st.markdown("### Model Performance")
                    results_df = pd.DataFrame(trainer.results).T
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Feature importance (if available)
                    if model_type == "Regression":
                        importance_df = trainer.get_feature_importance('Random Forest')
                    else:
                        importance_df = trainer.get_feature_importance('Random Forest')
                    
                    if importance_df is not None:
                        st.markdown("### Feature Importance (Random Forest)")
                        st.dataframe(importance_df, use_container_width=True)
                        
            except Exception as e:
                st.error(f"Error training models: {str(e)}")


def display_executive_persona(profile, anomalies, insights, df, narrative):
    """Executive persona: Clean KPI dashboard"""
    
    st.markdown("## 📊 Executive Dashboard")
    
    # Calculate key metrics
    try:
        total_cells = profile['overview']['rows'] * profile['overview']['columns']
        completeness = ((total_cells - profile['overview']['total_missing']) / total_cells * 100) if total_cells > 0 else 0
        duplicate_penalty = (profile['overview']['duplicate_rows'] / profile['overview']['rows'] * 10) if profile['overview']['rows'] > 0 else 0
        quality_score = max(0, completeness - duplicate_penalty)
        
        # Large KPI cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", f"{profile['overview']['rows']:,}", 
                     help="Total number of records in dataset")
        with col2:
            st.metric("Data Quality", f"{quality_score:.0f}/100",
                     delta=f"{completeness:.0f}% complete" if completeness >= 90 else None,
                     delta_color="normal" if completeness >= 90 else "inverse",
                     help="Overall data quality score")
        with col3:
            st.metric("Completeness", f"{completeness:.1f}%",
                     delta="Good" if completeness >= 95 else "Needs Attention",
                     delta_color="normal" if completeness >= 95 else "inverse",
                     help="Percentage of non-missing values")
        with col4:
            reliability = "High" if profile['overview']['duplicate_rows'] == 0 and completeness > 95 else \
                         "Medium" if completeness > 85 else "Low"
            st.metric("Reliability", reliability,
                     help="Data reliability assessment")
        
        # Quality gauge
        st.markdown("---")
        col_gauge, col_summary = st.columns([1, 1])
        
        with col_gauge:
            try:
                gauge_fig = create_quality_gauge(quality_score)
                st.plotly_chart(gauge_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating gauge: {str(e)}")
        
        with col_summary:
            if narrative:
                st.markdown("### 📖 Executive Summary")
                st.info(narrative.get('executive_summary', 'No summary available'))
                
                if narrative.get('actions'):
                    st.markdown("### 🎯 Strategic Recommendations")
                    for i, action in enumerate(narrative['actions'][:3], 1):
                        st.markdown(f"{i}. {action}")
        
        # Risk alerts
        if narrative and narrative.get('risks'):
            st.markdown("---")
            st.markdown("### ⚠️ Strategic Risks")
            for risk in narrative['risks']:
                st.warning(f"⚠️ {risk}")
                
    except Exception as e:
        st.error(f"Error displaying executive dashboard: {str(e)}")


def display_business_persona(profile, anomalies, insights, df, narrative):
    """Business persona: Action-oriented operational view"""
    
    st.markdown("## 💼 Operational Dashboard")
    
    try:
        # Calculate operational metrics
        total_cells = profile['overview']['rows'] * profile['overview']['columns']
        completeness = ((total_cells - profile['overview']['total_missing']) / total_cells * 100) if total_cells > 0 else 0
        usable_records = profile['overview']['rows'] - profile['overview']['duplicate_rows']
        duplicate_rate = (profile['overview']['duplicate_rows'] / profile['overview']['rows'] * 100) if profile['overview']['rows'] > 0 else 0
        
        # Operational readiness
        readiness = "Ready" if completeness > 95 and duplicate_rate < 1 else \
                   "Needs Cleanup" if completeness > 85 else "Critical Issues"
        
        # Status banner
        if readiness == "Ready":
            st.success(f"✅ **Status: {readiness}** - Dataset is ready for operational use")
        elif readiness == "Needs Cleanup":
            st.warning(f"⚠️ **Status: {readiness}** - Minor data quality issues detected")
        else:
            st.error(f"🔴 **Status: {readiness}** - Significant data quality problems")
        
        # Operational metrics
        st.markdown("### 📊 Operational Metrics")
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
            st.metric("Status", readiness)
        
        # Action items
        st.markdown("---")
        st.markdown("### 🎯 Action Items")
        
        action_items = []
        if profile['overview']['duplicate_rows'] > 0:
            action_items.append(f"Remove {profile['overview']['duplicate_rows']} duplicate records")
        if profile['overview']['total_missing'] > 0:
            action_items.append(f"Address {profile['overview']['total_missing']} missing values")
        if completeness < 95:
            action_items.append(f"Improve data completeness from {completeness:.1f}% to 95%+")
        
        if action_items:
            for item in action_items:
                st.warning(f"📋 {item}")
        else:
            st.success("✅ No immediate action items - data quality is excellent!")
        
        # Operational insights from narrative
        if narrative:
            st.markdown("---")
            st.markdown("### 💡 Operational Insights")
            if narrative.get('insights'):
                for insight in narrative['insights']:
                    st.info(f"💡 {insight}")
            
            if narrative.get('actions'):
                st.markdown("### 📝 Recommended Actions")
                for i, action in enumerate(narrative['actions'], 1):
                    st.markdown(f"{i}. {action}")
                    
    except Exception as e:
        st.error(f"Error displaying business dashboard: {str(e)}")
