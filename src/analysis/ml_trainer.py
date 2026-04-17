"""
Phase 8.3: ML Model Trainer
Train LightGBM/RandomForest on real stock data.
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.analysis.feature_engineering import FeatureEngineer

class MLModelTrainer:
    """
    Trains ML models for stock prediction using real market data.
    Supports: LightGBM, RandomForest, XGBoost
    """
    
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(project_root, 'models')
        os.makedirs(model_dir, exist_ok=True)
        self.model_dir = model_dir
        self.engine = get_db_engine()
        self.feature_engineer = FeatureEngineer()
        
    def prepare_dataset(self, codes: List[str], start_date: str = '2023-01-01',
                        end_date: str = None) -> pd.DataFrame:
        """
        Prepare training dataset with features.
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        all_data = []
        for code in codes:
            features = self.feature_engineer.extract_features(code)
            if not features.empty:
                features['code'] = code
                all_data.append(features)
                
        if not all_data:
            return pd.DataFrame()
            
        df = pd.concat(all_data, ignore_index=True)
        df['date'] = pd.to_datetime(df['date'])
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        return df[mask].dropna()
        
    def train_lightgbm(self, codes: List[str], train_start: str = '2023-01-01',
                       train_end: str = '2025-12-31') -> Dict:
        """Train LightGBM model."""
        try:
            import lightgbm as lgb
        except ImportError:
            return {'status': 'ERROR', 'message': 'LightGBM not installed'}
            
        df = self.prepare_dataset(codes, train_start, train_end)
        if df.empty:
            return {'status': 'ERROR', 'message': 'No training data'}
            
        feature_cols = self.feature_engineer.get_feature_names()
        feature_cols = [c for c in feature_cols if c in df.columns and c != 'target_return']
        
        df = df.dropna(subset=feature_cols + ['target_return'])
        if len(df) < 100:
            return {'status': 'ERROR', 'message': f'Insufficient data: {len(df)} rows'}
            
        X = df[feature_cols]
        y = (df['target_return'] > 0).astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        model = lgb.LGBMClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_samples=20,
            random_state=42,
            verbose=-1
        )
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        
        model_path = os.path.join(self.model_dir, 'lgb_model_v2.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': feature_cols,
                'train_date': datetime.now().strftime('%Y-%m-%d'),
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'accuracy': accuracy,
                'codes': codes
            }, f)
            
        return {
            'status': 'OK',
            'model': 'LightGBM',
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_importance': importance,
            'model_path': model_path,
            'report': classification_report(y_test, y_pred, output_dict=True)
        }
        
    def train_random_forest(self, codes: List[str], train_start: str = '2023-01-01',
                            train_end: str = '2025-12-31') -> Dict:
        """Train RandomForest model."""
        from sklearn.ensemble import RandomForestClassifier
        
        df = self.prepare_dataset(codes, train_start, train_end)
        if df.empty:
            return {'status': 'ERROR', 'message': 'No training data'}
            
        feature_cols = self.feature_engineer.get_feature_names()
        feature_cols = [c for c in feature_cols if c in df.columns and c != 'target_return']
        
        df = df.dropna(subset=feature_cols + ['target_return'])
        if len(df) < 100:
            return {'status': 'ERROR', 'message': 'Insufficient data'}
            
        X = df[feature_cols]
        y = (df['target_return'] > 0).astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        
        model_path = os.path.join(self.model_dir, 'rf_model_v2.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': feature_cols,
                'train_date': datetime.now().strftime('%Y-%m-%d'),
                'accuracy': accuracy,
                'codes': codes
            }, f)
            
        return {
            'status': 'OK',
            'model': 'RandomForest',
            'accuracy': accuracy,
            'feature_importance': importance,
            'model_path': model_path,
            'report': classification_report(y_test, y_pred, output_dict=True)
        }
        
    def generate_training_report(self, result: Dict) -> str:
        """Generate training report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🤖 ML 模型训练报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 模型: {result.get('model', 'Unknown')}")
        lines.append(f"🎯 准确率: {result.get('accuracy', 0):.2%}")
        lines.append(f"📦 训练样本: {result.get('train_samples', 0)}")
        lines.append(f"📦 测试样本: {result.get('test_samples', 0)}")
        
        if 'report' in result:
            report = result['report']
            if '1' in report:
                lines.append(f"\n📈 分类报告")
                lines.append(f"  Precision: {report['1']['precision']:.3f}")
                lines.append(f"  Recall: {report['1']['recall']:.3f}")
                lines.append(f"  F1-Score: {report['1']['f1-score']:.3f}")
                
        if 'feature_importance' in result:
            lines.append(f"\n🔑 Top 10 特征")
            importance = result['feature_importance']
            sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
            for feat, imp in sorted_imp:
                lines.append(f"  {feat}: {imp}")
                
        return "\n".join(lines)


if __name__ == "__main__":
    trainer = MLModelTrainer()
    codes = ['SH.600519', 'SZ.002594', 'SH.601318', 'SZ.300750', 'SZ.000858']
    result = trainer.train_lightgbm(codes, train_start='2023-01-01')
    if result['status'] == 'OK':
        print(trainer.generate_training_report(result))
    else:
        print(f"训练失败: {result['message']}")
