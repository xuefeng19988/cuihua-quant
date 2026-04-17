"""
Phase 13.4: Ensemble Learning Model
Combines multiple ML models using voting and stacking.
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier, StackingClassifier
from sklearn.metrics import accuracy_score

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.analysis.feature_engineering import FeatureEngineer

class EnsembleModel:
    """
    Ensemble learning combining multiple ML models.
    Supports: Voting, Stacking, Weighted Average
    """
    
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(project_root, 'models')
        os.makedirs(model_dir, exist_ok=True)
        self.model_dir = model_dir
        self.engine = get_db_engine()
        self.feature_engineer = FeatureEngineer()
        self.model = None
        
    def prepare_data(self, codes: List[str], train_start: str = '2023-01-01',
                     train_end: str = '2025-12-31') -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare training data for ensemble."""
        all_data = []
        for code in codes:
            features = self.feature_engineer.extract_features(code)
            if not features.empty:
                features['code'] = code
                all_data.append(features)
                
        if not all_data:
            return pd.DataFrame(), pd.Series(dtype=float)
            
        df = pd.concat(all_data, ignore_index=True)
        df['date'] = pd.to_datetime(df['date'])
        mask = (df['date'] >= train_start) & (df['date'] <= train_end)
        df = df[mask].dropna()
        
        feature_cols = self.feature_engineer.get_feature_names()
        feature_cols = [c for c in feature_cols if c in df.columns and c != 'target_return']
        
        df = df.dropna(subset=feature_cols + ['target_return'])
        X = df[feature_cols]
        y = (df['target_return'] > 0).astype(int)
        
        return X, y
        
    def build_voting_ensemble(self) -> bool:
        """Build voting ensemble model."""
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.svm import SVC
            from sklearn.neighbors import KNeighborsClassifier
            
            estimators = [
                ('lr', LogisticRegression(max_iter=1000, random_state=42)),
                ('rf', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)),
                ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
                ('knn', KNeighborsClassifier(n_neighbors=5))
            ]
            
            self.model = VotingClassifier(
                estimators=estimators,
                voting='soft'
            )
            return True
            
        except Exception as e:
            print(f"❌ Failed to build voting ensemble: {e}")
            return False
            
    def build_stacking_ensemble(self) -> bool:
        """Build stacking ensemble model."""
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            
            estimators = [
                ('rf', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)),
                ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
            ]
            
            self.model = StackingClassifier(
                estimators=estimators,
                final_estimator=LogisticRegression(max_iter=1000),
                cv=5
            )
            return True
            
        except Exception as e:
            print(f"❌ Failed to build stacking ensemble: {e}")
            return False
            
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict:
        """Train ensemble model."""
        if self.model is None:
            return {'status': 'ERROR', 'message': 'Model not built'}
            
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        return {
            'status': 'OK',
            'train_accuracy': self.model.score(X_train, y_train),
            'test_accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
    def save_model(self, filename: str = 'ensemble_model.pkl'):
        """Save ensemble model."""
        if self.model:
            path = os.path.join(self.model_dir, filename)
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"✅ Model saved: {path}")
            
    def load_model(self, filename: str = 'ensemble_model.pkl') -> bool:
        """Load ensemble model."""
        path = os.path.join(self.model_dir, filename)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✅ Model loaded: {path}")
            return True
        return False


if __name__ == "__main__":
    ensemble = EnsembleModel()
    print("Ensemble model initialized")
    print("Note: Requires scikit-learn for full functionality")
