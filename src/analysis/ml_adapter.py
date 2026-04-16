"""
ML Model Adapter
Integrates ML predictions (LightGBM, RandomForest) into the strategy pipeline.
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class MLModelAdapter:
    """
    Wraps ML models for use in the trading pipeline.
    Supports:
    - LightGBM
    - RandomForest
    - Ensemble (weighted average)
    """
    
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
        """
        Generate predictions from features.
        
        Args:
            features: DataFrame with feature columns
            model_name: Which model to use. If None, uses all and averages.
            
        Returns:
            Series of predictions
        """
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
        """
        Convert predictions to trading signals.
        Assumes predictions are probabilities (0 to 1).
        """
        signals = []
        for i, pred in enumerate(predictions):
            if i >= len(codes):
                break
                
            code = codes[i]
            
            if pred >= buy_threshold:
                signals.append({
                    'code': code,
                    'action': 'BUY',
                    'ml_score': pred,
                    'confidence': (pred - buy_threshold) / (1 - buy_threshold),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            elif pred <= sell_threshold:
                signals.append({
                    'code': code,
                    'action': 'SELL',
                    'ml_score': pred,
                    'confidence': (sell_threshold - pred) / sell_threshold,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
        return signals
