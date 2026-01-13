"""
Profiler Engine - Dataset statistics and analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any


class DataProfiler:
    """Automated dataset profiling engine"""
    
    def __init__(self, df: pd.DataFrame, sample_size: int = None):
        """
        Initialize profiler
        
        Args:
            df: DataFrame to profile
            sample_size: Number of rows to sample (None = all rows)
        """
        self.df = df if sample_size is None else df.sample(min(sample_size, len(df)))
        self.profile = {}
    
    def profile_dataset(self) -> Dict[str, Any]:
        """Generate comprehensive dataset profile"""
        self.profile = {
            'overview': self._get_overview(),
            'columns': self._profile_columns(),
            'missing_data': self._analyze_missing_data(),
            'duplicates': self._check_duplicates(),
            'correlations': self._get_correlations()
        }
        return self.profile
    
    def _get_overview(self) -> Dict[str, Any]:
        """Get dataset overview statistics"""
        return {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / 1024**2, 2),
            'duplicate_rows': self.df.duplicated().sum(),
            'total_missing': self.df.isnull().sum().sum()
        }
    
    def _profile_columns(self) -> List[Dict[str, Any]]:
        """Profile each column"""
        columns_profile = []
        
        for col in self.df.columns:
            col_data = self.df[col]
            dtype = str(col_data.dtype)
            
            profile = {
                'name': col,
                'dtype': dtype,
                'missing': col_data.isnull().sum(),
                'missing_pct': round(col_data.isnull().sum() / len(col_data) * 100, 2),
                'unique': col_data.nunique(),
                'unique_pct': round(col_data.nunique() / len(col_data) * 100, 2)
            }
            
            # Numeric columns
            if pd.api.types.is_numeric_dtype(col_data):
                profile.update({
                    'mean': round(col_data.mean(), 2) if not col_data.isnull().all() else None,
                    'median': round(col_data.median(), 2) if not col_data.isnull().all() else None,
                    'std': round(col_data.std(), 2) if not col_data.isnull().all() else None,
                    'min': round(col_data.min(), 2) if not col_data.isnull().all() else None,
                    'max': round(col_data.max(), 2) if not col_data.isnull().all() else None,
                    'zeros': (col_data == 0).sum(),
                    'negatives': (col_data < 0).sum() if not col_data.isnull().all() else 0
                })
            
            # Categorical columns
            elif pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
                value_counts = col_data.value_counts()
                profile.update({
                    'top_value': value_counts.index[0] if len(value_counts) > 0 else None,
                    'top_frequency': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    'avg_length': round(col_data.astype(str).str.len().mean(), 2) if not col_data.isnull().all() else None
                })
            
            columns_profile.append(profile)
        
        return columns_profile
    
    def _analyze_missing_data(self) -> Dict[str, Any]:
        """Analyze missing data patterns"""
        missing_counts = self.df.isnull().sum()
        missing_cols = missing_counts[missing_counts > 0].to_dict()
        
        return {
            'total_missing': int(missing_counts.sum()),
            'columns_with_missing': len(missing_cols),
            'missing_by_column': {k: int(v) for k, v in missing_cols.items()}
        }
    
    def _check_duplicates(self) -> Dict[str, Any]:
        """Check for duplicate rows"""
        duplicates = self.df.duplicated()
        return {
            'duplicate_rows': int(duplicates.sum()),
            'duplicate_pct': round(duplicates.sum() / len(self.df) * 100, 2)
        }
    
    def _get_correlations(self) -> Dict[str, Any]:
        """Get correlations for numeric columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'message': 'Not enough numeric columns for correlation'}
        
        corr_matrix = self.df[numeric_cols].corr()
        
        # Find high correlations
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Threshold for high correlation
                    high_corr.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': round(corr_value, 3)
                    })
        
        return {
            'high_correlations': high_corr,
            'numeric_columns': len(numeric_cols)
        }
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect data anomalies"""
        anomalies = []
        
        for col in self.df.columns:
            col_data = self.df[col]
            
            # High missing rate
            missing_pct = col_data.isnull().sum() / len(col_data) * 100
            if missing_pct > 50:
                anomalies.append({
                    'type': 'High Missing Rate',
                    'column': col,
                    'severity': 'high',
                    'detail': f'{missing_pct:.1f}% missing values'
                })
            
            # Low cardinality (potential constant column)
            if col_data.nunique() == 1:
                anomalies.append({
                    'type': 'Constant Column',
                    'column': col,
                    'severity': 'medium',
                    'detail': 'Only one unique value'
                })
            
            # Numeric anomalies
            if pd.api.types.is_numeric_dtype(col_data):
                # Check for outliers using IQR
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((col_data < (Q1 - 1.5 * IQR)) | (col_data > (Q3 + 1.5 * IQR))).sum()
                
                if outliers > len(col_data) * 0.1:  # More than 10% outliers
                    anomalies.append({
                        'type': 'High Outlier Count',
                        'column': col,
                        'severity': 'medium',
                        'detail': f'{outliers} outliers detected'
                    })
        
        return anomalies
