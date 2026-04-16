"""
ML Model Adapter
Integrates pre-trained ML models into the signal pipeline.
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

class MLAdapter:
    """
    Wraps ML models for prediction.
    Supports: LightGBM, RandomForest, etc.
    """
    
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(project_root, 'models')
        self.model_dir = model_dir
        self.models = {}
        
    def load_model(self, name: str, filename: str = None) -> bool:
        """Load a model from disk."""
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
            print(f"❌ Failed to load {name}: {e}")
            return False
            
    def predict(self, features: pd.DataFrame, model_name: str = None) -> pd.Series:
        """Generate predictions. If multiple models, ensemble average."""
        if not self.models:
            return pd.Series(dtype=float)
            
        if model_name and model_name in self.models:
            return pd.Series(self.models[model_name].predict(features), index=features.index)
            
        # Ensemble: average all
        preds = []
        for name, model in self.models.items():
            try:
                p = model.predict(features)
                preds.append(pd.Series(p, index=features.index))
            except Exception as e:
                print(f"⚠️ {name} predict error: {e}")
                
        return pd.DataFrame(preds).mean() if preds else pd.Series(dtype=float)
