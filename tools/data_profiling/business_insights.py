"""
Business Intelligence Helpers
Calculate business-friendly metrics and insights
"""
import pandas as pd
import numpy as np
from datetime import datetime


def calculate_usability_score(profile):
    """
    Calculate overall data usability score (0-100)
    
    Args:
        profile: Dataset profile dictionary
        
    Returns:
        dict with score, grade, and breakdown
    """
    total_cells = profile['overview']['rows'] * profile['overview']['columns']
    
    # Completeness (0-60 points)
    completeness_pct = ((total_cells - profile['overview']['total_missing']) / total_cells * 100) if total_cells > 0 else 0
    completeness_score = (completeness_pct / 100) * 60
    
    # Duplicate penalty (0-20 points deduction)
    duplicate_rate = (profile['overview']['duplicate_rows'] / profile['overview']['rows'] * 100) if profile['overview']['rows'] > 0 else 0
    duplicate_penalty = min(duplicate_rate * 2, 20)
    
    # Data type diversity bonus (0-20 points)
    type_diversity = len(set([col.get('dtype', 'object') for col in profile['columns']])) / 4  # Assume max 4 types
    diversity_score = min(type_diversity, 1) * 20
    
    # Calculate final score
    usability_score = max(0, min(100, completeness_score - duplicate_penalty + diversity_score))
    
    # Assign grade
    if usability_score >= 90:
        grade = 'A'
    elif usability_score >= 80:
        grade = 'B'
    elif usability_score >= 70:
        grade = 'C'
    elif usability_score >= 60:
        grade = 'D'
    else:
        grade = 'F'
    
    return {
        'score': round(usability_score, 1),
        'grade': grade,
        'completeness_pct': round(completeness_pct, 1),
        'duplicate_rate': round(duplicate_rate, 1),
        'breakdown': {
            'completeness': round(completeness_score, 1),
            'duplicate_penalty': round(duplicate_penalty, 1),
            'diversity_bonus': round(diversity_score, 1)
        }
    }


def find_critical_missing_fields(profile):
    """
    Identify columns with critical missing data (>20%)
    
    Args:
        profile: Dataset profile dictionary
        
    Returns:
        list of critical fields with impact assessment
    """
    critical_fields = []
    
    for col in profile['columns']:
        missing_pct = (col['missing'] / profile['overview']['rows'] * 100) if profile['overview']['rows'] > 0 else 0
        
        if missing_pct > 20:
            # Assess impact
            if missing_pct > 50:
                impact = 'High'
                severity = '🔴'
            elif missing_pct > 35:
                impact = 'Medium'
                severity = '🟡'
            else:
                impact = 'Low'
                severity = '🟢'
            
            critical_fields.append({
                'column': col['name'],
                'missing_pct': round(missing_pct, 1),
                'missing_count': col['missing'],
                'impact': impact,
                'severity': severity
            })
    
    # Sort by missing percentage (descending)
    critical_fields.sort(key=lambda x: x['missing_pct'], reverse=True)
    
    return critical_fields


def analyze_data_freshness(df):
    """
    Analyze data freshness based on date columns
    
    Args:
        df: DataFrame
        
    Returns:
        dict with freshness info or None
    """
    try:
        # Try to find date columns
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Also check for columns with 'date', 'time', 'created', 'updated' in name
        potential_date_cols = [col for col in df.columns if any(keyword in col.lower() 
                               for keyword in ['date', 'time', 'created', 'updated', 'timestamp'])]
        
        if not date_cols and potential_date_cols:
            # Try to parse potential date columns
            for col in potential_date_cols[:3]:  # Check first 3
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    if df[col].notna().sum() > 0:
                        date_cols.append(col)
                except:
                    continue
        
        if date_cols:
            col = date_cols[0]  # Use first date column
            latest = df[col].max()
            oldest = df[col].min()
            
            if pd.notna(latest) and pd.notna(oldest):
                days_old = (datetime.now() - latest).days if isinstance(latest, pd.Timestamp) else None
                
                return {
                    'has_dates': True,
                    'latest': latest,
                    'oldest': oldest,
                    'days_old': days_old,
                    'column': col,
                    'freshness': 'Fresh' if days_old and days_old < 7 else 
                                'Recent' if days_old and days_old < 30 else 
                                'Stale' if days_old and days_old < 90 else 'Old'
                }
    except Exception:
        pass
    
    return {'has_dates': False}


def identify_key_columns(profile, df):
    """
    Identify the most important columns based on multiple factors
    
    Args:
        profile: Dataset profile dictionary
        df: DataFrame
        
    Returns:
        list of top 5 key columns with scores
    """
    scored_cols = []
    
    for col in profile['columns']:
        score = 0
        reasons = []
        
        # Completeness (0-40 points)
        completeness = (1 - col['missing'] / profile['overview']['rows']) if profile['overview']['rows'] > 0 else 0
        score += completeness * 40
        if completeness > 0.95:
            reasons.append('Complete')
        
        # Uniqueness (0-30 points)
        uniqueness = min(col['unique'] / profile['overview']['rows'], 1) if profile['overview']['rows'] > 0 else 0
        score += uniqueness * 30
        if uniqueness > 0.9:
            reasons.append('Unique')
        
        # Data type importance (0-20 points)
        col_type = col.get('dtype', 'object')
        if col_type in ['int64', 'float64']:
            score += 15
            reasons.append('Numeric')
        elif col_type in ['datetime64[ns]', 'datetime']:
            score += 20
            reasons.append('Date')
        elif col_type == 'object' and col['unique'] < 20:
            score += 10
            reasons.append('Categorical')
        
        # Name-based importance (0-10 points)
        important_keywords = ['id', 'name', 'email', 'phone', 'amount', 'price', 'revenue', 'status', 'date']
        if any(keyword in col['name'].lower() for keyword in important_keywords):
            score += 10
            reasons.append('Key Field')
        
        scored_cols.append({
            'name': col['name'],
            'score': round(score, 1),
            'type': col.get('dtype', 'object'),
            'reasons': ', '.join(reasons) if reasons else 'Standard'
        })
    
    # Sort by score and return top 5
    scored_cols.sort(key=lambda x: x['score'], reverse=True)
    return scored_cols[:5]


def generate_prioritized_actions(profile, critical_fields, usability):
    """
    Generate prioritized action items with effort estimates
    
    Args:
        profile: Dataset profile dictionary
        critical_fields: List of critical missing fields
        usability: Usability score dict
        
    Returns:
        list of prioritized actions
    """
    actions = []
    
    # Action 1: Remove duplicates (if any)
    if profile['overview']['duplicate_rows'] > 0:
        effort = 'Low' if profile['overview']['duplicate_rows'] < 100 else 'Medium'
        impact = round((profile['overview']['duplicate_rows'] / profile['overview']['rows'] * 100), 1)
        actions.append({
            'priority': '🔴 High',
            'action': f"Remove {profile['overview']['duplicate_rows']} duplicate records",
            'effort': effort,
            'impact': f"+{impact}% usability",
            'time_estimate': '5-10 min'
        })
    
    # Action 2: Address critical missing fields
    if critical_fields:
        top_field = critical_fields[0]
        effort = 'High' if top_field['missing_count'] > 500 else 'Medium' if top_field['missing_count'] > 100 else 'Low'
        actions.append({
            'priority': '🔴 High' if top_field['impact'] == 'High' else '🟡 Medium',
            'action': f"Fill missing values in '{top_field['column']}' ({top_field['missing_count']} records)",
            'effort': effort,
            'impact': f"Enables use of {top_field['column']} field",
            'time_estimate': '30-60 min' if effort == 'High' else '15-30 min'
        })
    
    # Action 3: Improve completeness
    if usability['completeness_pct'] < 95:
        target_improvement = 95 - usability['completeness_pct']
        actions.append({
            'priority': '🟡 Medium',
            'action': f"Improve data completeness from {usability['completeness_pct']:.1f}% to 95%",
            'effort': 'Medium',
            'impact': f"+{target_improvement:.1f}% completeness",
            'time_estimate': '1-2 hours'
        })
    
    # Action 4: Standardize formats (if mixed types detected)
    # This is a placeholder - would need anomaly detection
    if len(actions) < 3:
        actions.append({
            'priority': '🟢 Low',
            'action': "Review and standardize data formats",
            'effort': 'Low',
            'impact': 'Improved consistency',
            'time_estimate': '15-30 min'
        })
    
    return actions[:3]  # Return top 3


def calculate_cleanup_effort(profile, critical_fields):
    """
    Estimate overall cleanup effort
    
    Args:
        profile: Dataset profile dictionary
        critical_fields: List of critical missing fields
        
    Returns:
        str: 'Low', 'Medium', or 'High'
    """
    issues_count = 0
    
    # Count issues
    if profile['overview']['duplicate_rows'] > 0:
        issues_count += 1
    
    issues_count += len(critical_fields)
    
    if profile['overview']['total_missing'] > profile['overview']['rows'] * 0.1:
        issues_count += 1
    
    # Estimate effort
    if issues_count == 0:
        return 'None'
    elif issues_count <= 2:
        return 'Low (< 1 hour)'
    elif issues_count <= 4:
        return 'Medium (1-2 hours)'
    else:
        return 'High (2+ hours)'


def get_top_categorical_values(df, max_cols=3, max_values=5):
    """
    Get top values for categorical columns
    
    Args:
        df: DataFrame
        max_cols: Maximum number of columns to analyze
        max_values: Maximum number of top values per column
        
    Returns:
        dict of column -> top values
    """
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    top_values = {}
    
    for col in categorical_cols[:max_cols]:
        if df[col].nunique() < 50:  # Only for columns with reasonable cardinality
            value_counts = df[col].value_counts().head(max_values)
            top_values[col] = [
                {'value': str(val), 'count': int(count), 'pct': round(count/len(df)*100, 1)}
                for val, count in value_counts.items()
            ]
    
    return top_values


def detect_outliers_by_column(df, max_cols=10):
    """
    Detect outliers in numeric columns using IQR method
    
    Args:
        df: DataFrame
        max_cols: Maximum number of columns to analyze
        
    Returns:
        dict of column -> outlier info
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    outlier_info = {}
    
    for col in numeric_cols[:max_cols]:
        try:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            outlier_count = len(outliers)
            outlier_pct = (outlier_count / len(df) * 100) if len(df) > 0 else 0
            
            if outlier_count > 0:
                outlier_info[col] = {
                    'count': outlier_count,
                    'percentage': round(outlier_pct, 1),
                    'lower_bound': round(lower_bound, 2),
                    'upper_bound': round(upper_bound, 2),
                    'severity': '🔴 High' if outlier_pct > 10 else '🟡 Medium' if outlier_pct > 5 else '🟢 Low'
                }
        except Exception:
            continue
    
    return outlier_info


def get_column_quality_summary(profile, df):
    """
    Get quality summary for each column (null %, outliers)
    
    Args:
        profile: Dataset profile dictionary
        df: DataFrame
        
    Returns:
        DataFrame with column quality metrics
    """
    outliers = detect_outliers_by_column(df)
    
    quality_data = []
    
    for col in profile['columns']:
        col_name = col['name']
        missing_pct = (col['missing'] / profile['overview']['rows'] * 100) if profile['overview']['rows'] > 0 else 0
        
        # Quality status
        if missing_pct > 20:
            quality_status = '🔴 Poor'
        elif missing_pct > 10:
            quality_status = '🟡 Fair'
        else:
            quality_status = '✅ Good'
        
        # Check for outliers
        outlier_info = outliers.get(col_name, {})
        outlier_status = outlier_info.get('severity', 'N/A') if outlier_info else 'N/A'
        
        quality_data.append({
            'Column': col_name,
            'Type': col.get('dtype', 'object'),
            'Missing %': f"{missing_pct:.1f}%",
            'Quality': quality_status,
            'Outliers': f"{outlier_info.get('count', 0)} ({outlier_info.get('percentage', 0):.1f}%)" if outlier_info else 'None',
            'Outlier Severity': outlier_status
        })
    
    return pd.DataFrame(quality_data)
