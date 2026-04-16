"""
Technical Analysis Module
Calculates common indicators (MA, RSI, MACD, Bollinger Bands).
"""

import pandas as pd
import numpy as np
import talib
from datetime import datetime

def calculate_indicators(df):
    """
    Calculate technical indicators for a DataFrame.
    Expects columns: ['open', 'high', 'low', 'close', 'volume']
    """
    # 1. Moving Averages
    df['ma5'] = talib.SMA(df['close'], timeperiod=5)
    df['ma10'] = talib.SMA(df['close'], timeperiod=10)
    df['ma20'] = talib.SMA(df['close'], timeperiod=20)
    
    # 2. MACD
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    
    # 3. RSI
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    
    # 4. Bollinger Bands
    df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2)
    
    return df

def analyze_latest(stock_code: str, df: pd.DataFrame):
    """
    Analyze the latest row of the DataFrame and return a signal dict.
    """
    if df.empty:
        return None
        
    row = df.iloc[-1]
    prev_row = df.iloc[-2] if len(df) > 1 else row
    
    signal = {
        'code': stock_code,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'close': row['close'],
        'score': 0.0,
        'signals': []
    }
    
    # Logic 1: RSI Signal
    rsi = row['rsi']
    if not np.isnan(rsi):
        if rsi < 30:
            signal['score'] += 2.0
            signal['signals'].append('RSI_OverSold')
        elif rsi > 70:
            signal['score'] -= 2.0
            signal['signals'].append('RSI_OverBought')
            
    # Logic 2: MACD Golden/Death Cross
    if not np.isnan(row['macd']) and not np.isnan(row['macd_signal']):
        # Check if Cross happened recently
        if prev_row['macd'] < prev_row['macd_signal'] and row['macd'] > row['macd_signal']:
            signal['score'] += 3.0
            signal['signals'].append('MACD_GoldenCross')
        elif prev_row['macd'] > prev_row['macd_signal'] and row['macd'] < row['macd_signal']:
            signal['score'] -= 3.0
            signal['signals'].append('MACD_DeathCross')
            
    # Logic 3: MA Trend (Simple: Close > MA20)
    if not np.isnan(row['ma20']):
        if row['close'] > row['ma20']:
            signal['score'] += 1.0
            signal['signals'].append('Above_MA20')
            
    return signal
