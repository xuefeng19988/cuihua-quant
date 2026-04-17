"""
ML Trainer
Trains and saves ML models for stock prediction.
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from sklearn.model_selection import train_test_split

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.analysis.feature_engineering import FeatureEngineer

class MLTrainer:
    """
    Trains ML models for stock prediction.
    Supports: LightGBM, RandomForest, LogisticRegression
    """
    
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(project_root, 'models')
        os.makedirs(model_dir, exist_ok=True)
        self.model_dir = model_dir
        self.feature_engineer = FeatureEngineer()
        
    def prepare_data(self, codes: List[str], train_start: str = '2023-01-01', 
                     train_end: str = '2025-12-31') -> pd.DataFrame:
        """Prepare training data from database."""
        all_features = self.feature_engineer.extract_all_stocks(codes)
        if all_features.empty:
            return pd.DataFrame()
            
        # Filter by date
        all_features['date'] = pd.to_datetime(all_features['date'])
        mask = (all_features['date'] >= train_start) & (all_features['date'] <= train_end)
        return all_features[mask].dropna()
        
    def train_lightgbm(self, codes: List[str], train_start: str = '2023-01-01',
                       train_end: str = '2025-12-31', test_size: float = 0.2) -> Dict:
        """Train LightGBM model."""
        try:
            import lightgbm as lgb
        except ImportError:
            return {'status': 'ERROR', 'message': 'LightGBM not installed'}
            
        df = self.prepare_data(codes, train_start, train_end)
        if df.empty:
            return {'status': 'ERROR', 'message': 'No training data'}
            
        # Prepare features and target
        feature_cols = self.feature_engineer.get_feature_names()
        feature_cols = [c for c in feature_cols if c in df.columns]
        
        df = df.dropna(subset=feature_cols + ['target_return'])
        if len(df) < 100:
            return {'status': 'ERROR', 'message': 'Insufficient data'}
            
        X = df[feature_cols]
        y = (df['target_return'] > 0).astype(int)  # Binary classification
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        # Train model
        model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)
        
        # Feature importance
        importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        
        # Save model
        model_path = os.path.join(self.model_dir, 'lgb_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': feature_cols,
                'train_date': datetime.now().strftime('%Y-%m-%d'),
                'train_samples': len(X_train),
                'test_samples': len(X_test)
            }, f)
            
        return {
            'status': 'OK',
            'model': 'LightGBM',
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_importance': importance,
            'model_path': model_path
        }
        
    def train_random_forest(self, codes: List[str], train_start: str = '2023-01-01',
                            train_end: str = '2025-12-31', test_size: float = 0.2) -> Dict:
        """Train RandomForest model."""
        from sklearn.ensemble import RandomForestClassifier
        
        df = self.prepare_data(codes, train_start, train_end)
        if df.empty:
            return {'status': 'ERROR', 'message': 'No training data'}
            
        feature_cols = self.feature_engineer.get_feature_names()
        feature_cols = [c for c in feature_cols if c in df.columns]
        
        df = df.dropna(subset=feature_cols + ['target_return'])
        if len(df) < 100:
            return {'status': 'ERROR', 'message': 'Insufficient data'}
            
        X = df[feature_cols]
        y = (df['target_return'] > 0).astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)
        
        importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        
        model_path = os.path.join(self.model_dir, 'rf_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': feature_cols,
                'train_date': datetime.now().strftime('%Y-%m-%d')
            }, f)
            
        return {
            'status': 'OK',
            'model': 'RandomForest',
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'feature_importance': importance
        }
        
    def generate_training_report(self, results: Dict) -> str:
        """Generate training report."""
        lines = []
        lines.append("=" * 50)
        lines.append("🤖 ML 模型训练报告")
        lines.append("=" * 50)
        
        lines.append(f"\n📊 模型: {results.get('model', 'Unknown')}")
        lines.append(f"📅 训练日期: {results.get('train_date', 'Unknown')}")
        lines.append(f"📈 训练准确率: {results.get('train_accuracy', 0):.2%}")
        lines.append(f"📉 测试准确率: {results.get('test_accuracy', 0):.2%}")
        lines.append(f"📦 训练样本: {results.get('train_samples', 0)}")
        lines.append(f"📦 测试样本: {results.get('test_samples', 0)}")
        
        if 'feature_importance' in results:
            lines.append(f"\n🔑 Top 10 特征重要性")
            importance = results['feature_importance']
            sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
            for feat, imp in sorted_imp:
                lines.append(f"  {feat}: {imp}")
                
        return "\n".join(lines)


if __name__ == "__main__":
    trainer = MLTrainer()
    codes = ['SH.600519', 'SZ.002594', 'SH.601318', 'SZ.300750']
    result = trainer.train_lightgbm(codes)
    if result['status'] == 'OK':
        print(trainer.generate_training_report(result))
    else:
        print(f"训练失败: {result['message']}")
