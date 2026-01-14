"""
Data Profiling Visualizations
Generate charts and graphs for technical analysis
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def create_distribution_plots(df: pd.DataFrame, max_cols: int = 6):
    """
    Create distribution plots for numeric columns
    
    Args:
        df: DataFrame to analyze
        max_cols: Maximum number of columns to plot
        
    Returns:
        Plotly figure or None if no numeric columns
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return None
    
    # Limit to max_cols
    numeric_cols = numeric_cols[:max_cols]
    
    # Create subplots
    n_cols = min(3, len(numeric_cols))
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
    
    fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=numeric_cols
    )
    
    for idx, col in enumerate(numeric_cols):
        row = idx // n_cols + 1
        col_pos = idx % n_cols + 1
        
        # Create histogram
        fig.add_trace(
            go.Histogram(x=df[col], name=col, showlegend=False),
            row=row, col=col_pos
        )
    
    fig.update_layout(
        height=300 * n_rows,
        title_text="Distribution Plots",
        showlegend=False
    )
    
    return fig


def create_box_plots(df: pd.DataFrame, max_cols: int = 6):
    """
    Create box plots for outlier detection
    
    Args:
        df: DataFrame to analyze
        max_cols: Maximum number of columns to plot
        
    Returns:
        Plotly figure or None if no numeric columns
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return None
    
    # Limit to max_cols
    numeric_cols = numeric_cols[:max_cols]
    
    fig = go.Figure()
    
    for col in numeric_cols:
        fig.add_trace(go.Box(y=df[col], name=col))
    
    fig.update_layout(
        title="Box Plots - Outlier Detection",
        yaxis_title="Value",
        height=400
    )
    
    return fig


def create_correlation_heatmap(df: pd.DataFrame):
    """
    Create correlation heatmap for numeric columns
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Plotly figure or None if insufficient numeric columns
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return None
    
    # Calculate correlation matrix
    corr_matrix = df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Correlation Heatmap",
        height=600,
        width=700
    )
    
    return fig


def create_quality_gauge(quality_score: float):
    """
    Create gauge chart for data quality score (Executive view)
    
    Args:
        quality_score: Score from 0-100
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=quality_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Data Quality Score"},
        delta={'reference': 90, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "gray"},
                {'range': [75, 90], 'color': "lightgreen"},
                {'range': [90, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig
