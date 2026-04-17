"""
Phase 53: Machine Learning Pipeline
End-to-end ML pipeline for trading.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class MLTradingPipeline:
    """
    End-to-end ML pipeline for trading.
    """
    
    def __init__(self, model_type: str = 'lightgbm'):
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        self.scaler = None
        
    def prepare_features(self, df: pd.DataFrame, 
                        feature_config: Dict = None) -> pd.DataFrame:
        """
        Prepare features for ML model.
        """
        if feature_config is None:
            feature_config = {
                'returns': [1, 3, 5, 10, 20],
                'volatility': [5, 10, 20],
                'volume': [5, 10, 20],
                'ma': [5, 10, 20, 60]
            }
            
        features = pd.DataFrame(index=df.index)
        
        # Returns
        for period in feature_config['returns']:
            features[f'return_{period}d'] = df['close'].pct_change(period)
            
        # Volatility
        for period in feature_config['volatility']:
            features[f'vol_{period}d'] = df['close'].pct_change().rolling(period).std()
            
        # Volume
        for period in feature_config['volume']:
            vol_ma = df['volume'].rolling(period).mean()
            features[f'vol_ratio_{period}d'] = df['volume'] / vol_ma
            
        # Moving averages
        for period in feature_config['ma']:
            ma = df['close'].rolling(period).mean()
            features[f'ma_ratio_{period}'] = df['close'] / ma
            
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        features['macd'] = ema12 - ema26
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_hist'] = features['macd'] - features['macd_signal']
        
        # Target: next day return direction
        features['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        
        return features.dropna()
        
    def train_with_cv(self, features: pd.DataFrame, 
                     n_splits: int = 5) -> Dict:
        """
        Train model with time series cross-validation.
        """
        feature_cols = [c for c in features.columns if c != 'target']
        X = features[feature_cols]
        y = features['target']
        
        self.feature_names = feature_cols
        
        # Scale features
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Time series CV
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_scores = []
        
        if self.model_type == 'lightgbm':
            import lightgbm as lgb
            self.model = lgb.LGBMClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1
            )
        elif self.model_type == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
        for train_idx, test_idx in tscv.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            score = accuracy_score(y_test, y_pred)
            cv_scores.append(score)
            
        # Train on full data
        self.model.fit(X_scaled, y)
        
        return {
            'cv_scores': cv_scores,
            'mean_cv_score': np.mean(cv_scores),
            'std_cv_score': np.std(cv_scores),
            'model_type': self.model_type
        }
        
    def predict(self, features: pd.DataFrame) -> pd.Series:
        """
        Make predictions.
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained. Call train_with_cv() first.")
            
        feature_cols = [c for c in features.columns if c != 'target']
        X = features[feature_cols]
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        
        return pd.Series(predictions, index=features.index), \
               pd.Series(probabilities, index=features.index)
        
    def feature_importance(self) -> pd.DataFrame:
        """Get feature importance."""
        if self.model is None:
            return pd.DataFrame()
            
        importance = self.model.feature_importances_
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
    def generate_report(self, cv_results: Dict) -> str:
        """Generate ML pipeline report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🤖 ML 交易流水线报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 模型: {cv_results['model_type']}")
        lines.append(f"📈 交叉验证得分: {cv_results['mean_cv_score']:.4f} ± {cv_results['std_cv_score']:.4f}")
        
        if self.model is not None:
            lines.append(f"\n🔑 特征重要性 Top 10")
            importance = self.feature_importance()
            for _, row in importance.head(10).iterrows():
                lines.append(f"  {row['feature']}: {row['importance']}")
                
        return "\n".join(lines)


if __name__ == "__main__":
    # Test ML pipeline
    np.random.seed(42)
    dates = pd.bdate_range('2024-01-01', periods=500)
    df = pd.DataFrame({
        'date': dates,
        'close': np.cumprod(1 + np.random.normal(0.0005, 0.015, 500)) * 100,
        'volume': np.random.uniform(1e6, 1e8, 500)
    })
    
    pipeline = MLTradingPipeline(model_type='lightgbm')
    features = pipeline.prepare_features(df)
    cv_results = pipeline.train_with_cv(features)
    print(pipeline.generate_report(cv_results))
