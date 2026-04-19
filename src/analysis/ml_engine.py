"""
ML Engine - Unified Machine Learning module
Combines: MLModelAdapter (prediction/inference), MLTradingPipeline (feature engineering + CV training), MLModelTrainer (model training with real data)
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class MLModelAdapter:
    """Wraps trained ML models for use in the trading pipeline."""

    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(project_root, 'models')
        self.model_dir = model_dir
        self.models = {}
        self.feature_names = None

    def load_model(self, name: str, filename: str = None) -> bool:
        """Load a trained model from disk."""
        if filename is None:
            filename = f"{name}.pkl"
        filepath = os.path.join(self.model_dir, filename)
        if not os.path.exists(filepath):
            print(f"⚠️ Model not found: {filepath}")
            return False
        try:
            with open(filepath, 'rb') as f:
                self.models[name] = pickle.load(f)
            print(f"✅ Loaded model: {name}")
            return True
        except Exception as e:
            print(f"❌ Failed to load model {name}: {e}")
            return False

    def predict(self, features: pd.DataFrame, model_name: str = None) -> pd.Series:
        """Generate predictions from features."""
        if not self.models:
            print("⚠️ No models loaded.")
            return pd.Series(dtype=float)
        if model_name:
            if model_name not in self.models:
                print(f"⚠️ Model '{model_name}' not found.")
                return pd.Series(dtype=float)
            return self.models[model_name].predict(features)
        # Ensemble: average all models
        predictions = []
        for name, model in self.models.items():
            try:
                pred = model.predict(features)
                predictions.append(pred)
            except Exception as e:
                print(f"⚠️ Prediction error for {name}: {e}")
        if not predictions:
            return pd.Series(dtype=float)
        return pd.DataFrame(predictions).mean()

    def generate_signals(self, predictions: pd.Series, codes: List[str],
                         buy_threshold: float = 0.55,
                         sell_threshold: float = 0.45) -> List[Dict]:
        """Convert predictions to trading signals."""
        signals = []
        for i, pred in enumerate(predictions):
            if i >= len(codes):
                break
            code = codes[i]
            if pred >= buy_threshold:
                signals.append({
                    'code': code, 'action': 'BUY', 'ml_score': pred,
                    'confidence': (pred - buy_threshold) / (1 - buy_threshold),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            elif pred <= sell_threshold:
                signals.append({
                    'code': code, 'action': 'SELL', 'ml_score': pred,
                    'confidence': (sell_threshold - pred) / sell_threshold,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        return signals


class MLTradingPipeline:
    """End-to-end ML pipeline for trading: feature engineering + CV training + prediction."""

    def __init__(self, model_type: str = 'lightgbm'):
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        self.scaler = None

    def prepare_features(self, df: pd.DataFrame,
                         feature_config: Dict = None) -> pd.DataFrame:
        """Prepare features for ML model."""
        if feature_config is None:
            feature_config = {
                'returns': [1, 3, 5, 10, 20], 'volatility': [5, 10, 20],
                'volume': [5, 10, 20], 'ma': [5, 10, 20, 60]
            }
        features = pd.DataFrame(index=df.index)
        for period in feature_config['returns']:
            features[f'return_{period}d'] = df['close'].pct_change(period)
        for period in feature_config['volatility']:
            features[f'vol_{period}d'] = df['close'].pct_change().rolling(period).std()
        for period in feature_config['volume']:
            vol_ma = df['volume'].rolling(period).mean()
            features[f'vol_ratio_{period}d'] = df['volume'] / vol_ma
        for period in feature_config['ma']:
            ma = df['close'].rolling(period).mean()
            features[f'ma_ratio_{period}'] = df['close'] / ma
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['rsi_14'] = 100 - (100 / (1 + rs))
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        features['macd'] = ema12 - ema26
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_hist'] = features['macd'] - features['macd_signal']
        features['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        return features.dropna()

    def train_with_cv(self, features: pd.DataFrame, n_splits: int = 5) -> Dict:
        """Train model with time series cross-validation."""
        feature_cols = [c for c in features.columns if c != 'target']
        X = features[feature_cols]
        y = features['target']
        self.feature_names = feature_cols
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_scores = []

        if self.model_type == 'lightgbm':
            import lightgbm as lgb
            self.model = lgb.LGBMClassifier(
                n_estimators=200, max_depth=6, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, random_state=42, verbose=-1)
        elif self.model_type == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(
                n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)

        for train_idx, test_idx in tscv.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            cv_scores.append(accuracy_score(y_test, y_pred))

        self.model.fit(X_scaled, y)
        return {
            'cv_scores': cv_scores, 'mean_cv_score': np.mean(cv_scores),
            'std_cv_score': np.std(cv_scores), 'model_type': self.model_type
        }

    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Make predictions. Returns (predictions, probabilities)."""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained. Call train_with_cv() first.")
        feature_cols = [c for c in features.columns if c != 'target']
        X = features[feature_cols]
        X_scaled = self.scaler.transform(X)
        return (pd.Series(self.model.predict(X_scaled), index=features.index),
                pd.Series(self.model.predict_proba(X_scaled)[:, 1], index=features.index))

    def feature_importance(self) -> pd.DataFrame:
        if self.model is None:
            return pd.DataFrame()
        return pd.DataFrame({
            'feature': self.feature_names, 'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

    def generate_report(self, cv_results: Dict) -> str:
        lines = ["=" * 60, "🤖 ML 交易流水线报告", "=" * 60]
        lines.append(f"\n📊 模型: {cv_results['model_type']}")
        lines.append(f"📈 交叉验证得分: {cv_results['mean_cv_score']:.4f} ± {cv_results['std_cv_score']:.4f}")
        if self.model is not None:
            lines.append(f"\n🔑 特征重要性 Top 10")
            for _, row in self.feature_importance().head(10).iterrows():
                lines.append(f"  {row['feature']}: {row['importance']}")
        return "\n".join(lines)


class MLModelTrainer:
    """Trains ML models for stock prediction using real market data. Supports: LightGBM, RandomForest."""

    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(project_root, 'models')
        os.makedirs(model_dir, exist_ok=True)
        self.model_dir = model_dir
        try:
            from src.data.database import get_db_engine
            self.engine = get_db_engine()
        except Exception:
            self.engine = None
        try:
            from src.analysis.feature_engineering import FeatureEngineer
            self.feature_engineer = FeatureEngineer()
        except Exception:
            self.feature_engineer = None

    def prepare_dataset(self, codes: List[str], start_date: str = '2023-01-01',
                        end_date: str = None) -> pd.DataFrame:
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if self.feature_engineer is None:
            return pd.DataFrame()
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
        try:
            import lightgbm as lgb
        except ImportError:
            return {'status': 'ERROR', 'message': 'LightGBM not installed'}
        df = self.prepare_dataset(codes, train_start, train_end)
        if df.empty:
            return {'status': 'ERROR', 'message': 'No training data'}
        feature_cols = self.feature_engineer.get_feature_names() if self.feature_engineer else []
        feature_cols = [c for c in feature_cols if c in df.columns and c != 'target_return']
        df = df.dropna(subset=feature_cols + ['target_return'])
        if len(df) < 100:
            return {'status': 'ERROR', 'message': f'Insufficient data: {len(df)} rows'}
        X = df[feature_cols]
        y = (df['target_return'] > 0).astype(int)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = lgb.LGBMClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, min_child_samples=20,
            random_state=42, verbose=-1)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        model_path = os.path.join(self.model_dir, 'lgb_model_v2.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model, 'features': feature_cols,
                'train_date': datetime.now().strftime('%Y-%m-%d'),
                'train_samples': len(X_train), 'test_samples': len(X_test),
                'accuracy': accuracy, 'codes': codes
            }, f)
        return {
            'status': 'OK', 'model': 'LightGBM', 'accuracy': accuracy,
            'train_samples': len(X_train), 'test_samples': len(X_test),
            'feature_importance': importance, 'model_path': model_path,
            'report': classification_report(y_test, y_pred, output_dict=True)
        }

    def train_random_forest(self, codes: List[str], train_start: str = '2023-01-01',
                            train_end: str = '2025-12-31') -> Dict:
        from sklearn.ensemble import RandomForestClassifier
        df = self.prepare_dataset(codes, train_start, train_end)
        if df.empty:
            return {'status': 'ERROR', 'message': 'No training data'}
        feature_cols = self.feature_engineer.get_feature_names() if self.feature_engineer else []
        feature_cols = [c for c in feature_cols if c in df.columns and c != 'target_return']
        df = df.dropna(subset=feature_cols + ['target_return'])
        if len(df) < 100:
            return {'status': 'ERROR', 'message': 'Insufficient data'}
        X = df[feature_cols]
        y = (df['target_return'] > 0).astype(int)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_split=10,
            min_samples_leaf=5, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        model_path = os.path.join(self.model_dir, 'rf_model_v2.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model, 'features': feature_cols,
                'train_date': datetime.now().strftime('%Y-%m-%d'),
                'accuracy': accuracy, 'codes': codes
            }, f)
        return {
            'status': 'OK', 'model': 'RandomForest', 'accuracy': accuracy,
            'feature_importance': importance, 'model_path': model_path,
            'report': classification_report(y_test, y_pred, output_dict=True)
        }

    def generate_training_report(self, result: Dict) -> str:
        lines = ["=" * 60, "🤖 ML 模型训练报告", "=" * 60]
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
            sorted_imp = sorted(result['feature_importance'].items(), key=lambda x: x[1], reverse=True)[:10]
            for feat, imp in sorted_imp:
                lines.append(f"  {feat}: {imp}")
        return "\n".join(lines)
