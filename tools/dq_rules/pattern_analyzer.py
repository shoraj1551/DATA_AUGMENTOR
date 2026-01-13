"""
Pattern Analyzer - Detect data patterns for rule generation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any


class PatternAnalyzer:
    """Analyze data patterns to infer quality rules"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize pattern analyzer"""
        self.df = df
        self.patterns = {}
    
    def analyze_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze all columns for patterns"""
        patterns = {}
        
        for col in self.df.columns:
            patterns[col] = self._analyze_column(col)
        
        return patterns
    
    def _analyze_column(self, col: str) -> List[Dict[str, Any]]:
        """Analyze a single column for patterns"""
        col_data = self.df[col]
        patterns = []
        
        # Null pattern
        null_count = col_data.isnull().sum()
        if null_count > 0:
            patterns.append({
                'type': 'null_check',
                'severity': 'high' if null_count / len(col_data) > 0.1 else 'medium',
                'detail': f'{null_count} null values ({null_count/len(col_data)*100:.1f}%)'
            })
        
        # Data type pattern
        dtype = str(col_data.dtype)
        patterns.append({
            'type': 'type_check',
            'severity': 'high',
            'detail': f'Expected type: {dtype}'
        })
        
        # Numeric patterns
        if pd.api.types.is_numeric_dtype(col_data):
            patterns.extend(self._analyze_numeric(col, col_data))
        
        # String patterns
        elif pd.api.types.is_object_dtype(col_data):
            patterns.extend(self._analyze_string(col, col_data))
        
        # Uniqueness pattern
        unique_count = col_data.nunique()
        if unique_count == len(col_data.dropna()):
            patterns.append({
                'type': 'uniqueness',
                'severity': 'high',
                'detail': 'Column appears to be a unique identifier'
            })
        
        return patterns
    
    def _analyze_numeric(self, col: str, data: pd.Series) -> List[Dict[str, Any]]:
        """Analyze numeric column patterns"""
        patterns = []
        
        # Range pattern
        min_val = data.min()
        max_val = data.max()
        patterns.append({
            'type': 'range_check',
            'severity': 'high',
            'detail': f'Range: [{min_val}, {max_val}]',
            'min': min_val,
            'max': max_val
        })
        
        # Negative values
        if (data < 0).any():
            patterns.append({
                'type': 'sign_check',
                'severity': 'medium',
                'detail': 'Contains negative values'
            })
        
        # Zero values
        zero_count = (data == 0).sum()
        if zero_count > 0:
            patterns.append({
                'type': 'zero_check',
                'severity': 'low',
                'detail': f'{zero_count} zero values'
            })
        
        return patterns
    
    def _analyze_string(self, col: str, data: pd.Series) -> List[Dict[str, Any]]:
        """Analyze string column patterns"""
        patterns = []
        
        # Length pattern
        lengths = data.dropna().astype(str).str.len()
        if len(lengths) > 0:
            patterns.append({
                'type': 'length_check',
                'severity': 'medium',
                'detail': f'Length range: [{lengths.min()}, {lengths.max()}]',
                'min_length': int(lengths.min()),
                'max_length': int(lengths.max())
            })
        
        # Format pattern (email, phone, etc.)
        sample = data.dropna().astype(str).head(100)
        
        # Email pattern
        if sample.str.contains('@', regex=False).sum() > len(sample) * 0.8:
            patterns.append({
                'type': 'format_check',
                'severity': 'high',
                'detail': 'Appears to be email format',
                'format': 'email'
            })
        
        # Phone pattern
        elif sample.str.match(r'^\+?\d{10,}$').sum() > len(sample) * 0.8:
            patterns.append({
                'type': 'format_check',
                'severity': 'high',
                'detail': 'Appears to be phone number',
                'format': 'phone'
            })
        
        # Cardinality
        unique_ratio = data.nunique() / len(data)
        if unique_ratio < 0.05:  # Low cardinality
            patterns.append({
                'type': 'cardinality_check',
                'severity': 'medium',
                'detail': f'Low cardinality: {data.nunique()} unique values',
                'allowed_values': data.value_counts().head(20).index.tolist()
            })
        
        return patterns
