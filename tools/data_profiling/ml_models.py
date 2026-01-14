"""
Basic ML Models for Data Profiling
Train simple regression and classification models
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    mean_squared_error, r2_score, mean_absolute_error,
    accuracy_score, precision_score, recall_score, f1_score, classification_report
)
from sklearn.preprocessing import LabelEncoder
import plotly.graph_objects as go


class BasicMLTrainer:
    """Train and evaluate basic ML models"""
    
    def __init__(self, df: pd.DataFrame, target_col: str, model_type: str = 'regression'):
        """
        Initialize ML trainer
        
        Args:
            df: DataFrame with features and target
            target_col: Name of target column
            model_type: 'regression' or 'classification'
        """
        self.df = df
        self.target_col = target_col
        self.model_type = model_type
        self.models = {}
        self.results = {}
        
    def prepare_data(self, test_size: float = 0.2):
        """Prepare train/test split"""
        # Get numeric columns only
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if self.target_col not in numeric_cols:
            # Try to encode target if categorical
            if self.model_type == 'classification':
                le = LabelEncoder()
                self.df[self.target_col] = le.fit_transform(self.df[self.target_col])
                self.label_encoder = le
            else:
                raise ValueError(f"Target column '{self.target_col}' must be numeric for regression")
        
        # Features (all numeric except target)
        feature_cols = [col for col in numeric_cols if col != self.target_col]
        
        if not feature_cols:
            raise ValueError("No numeric features available for modeling")
        
        X = self.df[feature_cols].fillna(self.df[feature_cols].mean())
        y = self.df[self.target_col]
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        self.feature_names = feature_cols
        
    def train_regression_models(self):
        """Train regression models"""
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=1.0),
            'Decision Tree': DecisionTreeRegressor(max_depth=5, random_state=42),
            'Random Forest': RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
        }
        
        for name, model in models.items():
            model.fit(self.X_train, self.y_train)
            y_pred = model.predict(self.X_test)
            
            self.results[name] = {
                'model': model,
                'mse': mean_squared_error(self.y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(self.y_test, y_pred)),
                'mae': mean_absolute_error(self.y_test, y_pred),
                'r2': r2_score(self.y_test, y_pred)
            }
            
    def train_classification_models(self):
        """Train classification models"""
        models = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
        }
        
        for name, model in models.items():
            model.fit(self.X_train, self.y_train)
            y_pred = model.predict(self.X_test)
            
            # Handle binary vs multiclass
            average = 'binary' if len(np.unique(self.y_test)) == 2 else 'weighted'
            
            self.results[name] = {
                'model': model,
                'accuracy': accuracy_score(self.y_test, y_pred),
                'precision': precision_score(self.y_test, y_pred, average=average, zero_division=0),
                'recall': recall_score(self.y_test, y_pred, average=average, zero_division=0),
                'f1': f1_score(self.y_test, y_pred, average=average, zero_division=0)
            }
    
    def get_feature_importance(self, model_name: str):
        """Get feature importance for tree-based models"""
        if model_name not in self.results:
            return None
            
        model = self.results[model_name]['model']
        
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
        
        return None
    
    def create_performance_chart(self):
        """Create performance comparison chart"""
        if self.model_type == 'regression':
            metric = 'r2'
            title = "Model Comparison (R² Score)"
        else:
            metric = 'accuracy'
            title = "Model Comparison (Accuracy)"
        
        models = list(self.results.keys())
        scores = [self.results[m][metric] for m in models]
        
        fig = go.Figure(data=[
            go.Bar(x=models, y=scores, text=[f"{s:.3f}" for s in scores], textposition='auto')
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title="Model",
            yaxis_title=metric.upper(),
            height=400
        )
        
        return fig
