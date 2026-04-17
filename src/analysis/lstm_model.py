"""
Phase 13.1: LSTM Time Series Model
LSTM-based stock price prediction model.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.analysis.feature_engineering import FeatureEngineer

class LSTMModel:
    """
    LSTM-based time series prediction for stock prices.
    Architecture: Multiple LSTM layers + Dense output
    """
    
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(project_root, 'models')
        os.makedirs(model_dir, exist_ok=True)
        self.model_dir = model_dir
        self.engine = get_db_engine()
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def prepare_sequence_data(self, code: str, lookback: int = 60, 
                               prediction_days: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequence data for LSTM training.
        
        Args:
            code: Stock code
            lookback: Number of past days to use as input
            prediction_days: Number of days to predict ahead
            
        Returns:
            X: Input sequences (samples, lookback, features)
            y: Target values (samples, prediction_days)
        """
        df = pd.read_sql(
            f"SELECT close_price, volume, turnover_rate FROM stock_daily "
            f"WHERE code='{code}' ORDER BY date ASC",
            self.engine
        )
        
        if df.empty or len(df) < lookback + prediction_days:
            return np.array([]), np.array([])
            
        # Scale data
        scaled_data = self.scaler.fit_transform(df[['close_price', 'volume', 'turnover_rate']].values)
        
        X, y = [], []
        for i in range(lookback, len(scaled_data) - prediction_days):
            X.append(scaled_data[i-lookback:i])
            y.append(scaled_data[i+prediction_days-1, 0])  # Close price
            
        return np.array(X), np.array(y)
        
    def build_model(self, input_shape: Tuple, lstm_units: List[int] = [128, 64], 
                    dropout_rate: float = 0.2) -> bool:
        """
        Build LSTM model architecture.
        
        Args:
            input_shape: (lookback, features)
            lstm_units: List of LSTM layer units
            dropout_rate: Dropout rate for regularization
        """
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.optimizers import Adam
            from tensorflow.keras.callbacks import EarlyStopping
            
            model = Sequential()
            
            # LSTM layers
            for i, units in enumerate(lstm_units):
                return_sequences = i < len(lstm_units) - 1
                model.add(LSTM(units, return_sequences=return_sequences, 
                             input_shape=input_shape if i == 0 else None))
                model.add(Dropout(dropout_rate))
                
            # Dense layers
            model.add(Dense(32, activation='relu'))
            model.add(Dropout(0.1))
            model.add(Dense(1))  # Output: predicted close price
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            self.model = model
            print(f"✅ LSTM model built: {model.summary()}")
            return True
            
        except ImportError:
            print("⚠️ TensorFlow not installed. Run: pip install tensorflow")
            return False
            
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray,
              epochs: int = 100, batch_size: int = 32) -> Dict:
        """
        Train the LSTM model.
        
        Returns:
            Training history and metrics
        """
        if self.model is None:
            return {'status': 'ERROR', 'message': 'Model not built'}
            
        try:
            import tensorflow as tf
            from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
            
            early_stop = EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            )
            
            checkpoint = ModelCheckpoint(
                os.path.join(self.model_dir, 'lstm_best.h5'),
                save_best_only=True,
                verbose=0
            )
            
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=[early_stop, checkpoint],
                verbose=1
            )
            
            # Evaluate
            y_pred = self.model.predict(X_val)
            mse = mean_squared_error(y_val, y_pred)
            mae = mean_absolute_error(y_val, y_pred)
            
            return {
                'status': 'OK',
                'history': history.history,
                'val_mse': mse,
                'val_mae': mae,
                'val_rmse': np.sqrt(mse),
                'epochs_trained': len(history.history['loss'])
            }
            
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
            
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.predict(X)
        
    def save_model(self, filename: str = 'lstm_model.h5'):
        """Save trained model."""
        if self.model:
            path = os.path.join(self.model_dir, filename)
            self.model.save(path)
            print(f"✅ Model saved: {path}")
            
    def load_model(self, filename: str = 'lstm_model.h5'):
        """Load trained model."""
        try:
            import tensorflow as tf
            path = os.path.join(self.model_dir, filename)
            if os.path.exists(path):
                self.model = tf.keras.models.load_model(path)
                print(f"✅ Model loaded: {path}")
                return True
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
        return False


if __name__ == "__main__":
    # Test LSTM model setup
    lstm = LSTMModel()
    print("LSTM Model initialized")
    print("Note: Requires TensorFlow for full functionality")
