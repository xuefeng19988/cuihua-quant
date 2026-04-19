"""
Feature Engineering
Extracts technical features from stock data for ML models.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine

class FeatureEngineer:
    """
    Extracts features from stock data for ML models.
    Features:
    - Price-based: returns, moving averages, momentum
    - Volume-based: volume ratio, turnover
    - Volatility: ATR, Bollinger Bands width
    - Pattern: candlestick patterns
    """
    
    def __init__(self):
        self.engine = get_db_engine()
        
    def extract_features(self, code: str, lookback: int = 60) -> pd.DataFrame:
        """
        Extract all features for a single stock.
        """
        df = pd.read_sql(
f"SELECT * FROM stock_daily WHERE code=:code ORDER BY date ASC",
            self.engine
        )
        if df.empty or len(df) < 20:
            return pd.DataFrame()
            
        # Rename columns
        df = df.rename(columns={
            'close_price': 'close',
            'open_price': 'open',
            'high_price': 'high',
            'low_price': 'low'
        })
        
        features = pd.DataFrame()
        features['date'] = df['date']
        
        # 1. Price returns
        for period in [1, 3, 5, 10, 20]:
            features[f'return_{period}d'] = df['close'].pct_change(period)
            
        # 2. Moving averages
        for period in [5, 10, 20, 60]:
            ma = df['close'].rolling(period).mean()
            features[f'ma_{period}'] = ma
            features[f'close_ma_{period}_ratio'] = df['close'] / ma
            
        # 3. Volume features
        features['volume_ratio_5d'] = df['volume'] / df['volume'].rolling(5).mean()
        features['volume_ratio_20d'] = df['volume'] / df['volume'].rolling(20).mean()
        features['turnover_rate'] = df.get('turnover_rate', 0)
        
        # 4. Volatility
        features['volatility_20d'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)
        
        # 5. RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['rsi_14'] = 100 - (100 / (1 + rs))
        
        # 6. MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        features['macd'] = ema12 - ema26
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_hist'] = features['macd'] - features['macd_signal']
        
        # 7. Bollinger Bands
        ma20 = df['close'].rolling(20).mean()
        std20 = df['close'].rolling(20).std()
        features['bb_upper'] = ma20 + 2 * std20
        features['bb_lower'] = ma20 - 2 * std20
        features['bb_width'] = (features['bb_upper'] - features['bb_lower']) / ma20
        features['bb_position'] = (df['close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
        
        # 8. Target: next day return
        features['target_return'] = df['close'].shift(-1) / df['close'] - 1
        
        # 9. PE ratio
        if 'pe_ratio' in df.columns:
            features['pe_ratio'] = df['pe_ratio']
            
        # Drop NaN rows
        features = features.dropna()
        
        return features
        
    def extract_all_stocks(self, codes: List[str], lookback: int = 60) -> pd.DataFrame:
        """Extract features for multiple stocks."""
        all_features = []
        for code in codes:
            df = self.extract_features(code, lookback)
            if not df.empty:
                df['code'] = code
                all_features.append(df)
                
        if all_features:
            return pd.concat(all_features, ignore_index=True)
        return pd.DataFrame()
        
    def get_feature_names(self) -> List[str]:
        """Get list of feature column names."""
        return [
            'return_1d', 'return_3d', 'return_5d', 'return_10d', 'return_20d',
            'ma_5', 'ma_10', 'ma_20', 'ma_60',
            'close_ma_5_ratio', 'close_ma_10_ratio', 'close_ma_20_ratio', 'close_ma_60_ratio',
            'volume_ratio_5d', 'volume_ratio_20d', 'turnover_rate',
            'volatility_20d', 'rsi_14',
            'macd', 'macd_signal', 'macd_hist',
            'bb_width', 'bb_position',
            'pe_ratio'
        ]


if __name__ == "__main__":
    fe = FeatureEngineer()
    df = fe.extract_features('SH.600519')
    if not df.empty:
        print(f"Features shape: {df.shape}")
        print(df.tail())
