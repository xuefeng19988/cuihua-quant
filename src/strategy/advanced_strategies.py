"""
Phase 63: Advanced Trading Strategies
New strategies: Enhanced Mean Reversion, Event-Driven, Seasonal, Volume-Weighted
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class EnhancedMeanReversionStrategy:
    """
    Enhanced mean reversion with adaptive thresholds and volume confirmation.
    """
    
    def __init__(self, lookback: int = 20, entry_z: float = 2.0, 
                 exit_z: float = 0.5, volume_confirm: bool = True):
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.volume_confirm = volume_confirm
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate mean reversion signals with adaptive thresholds.
        """
        signals = pd.DataFrame(index=df.index)
        
        # Calculate Bollinger Bands
        ma = df['close'].rolling(self.lookback).mean()
        std = df['close'].rolling(self.lookback).std()
        upper = ma + 2 * std
        lower = ma - 2 * std
        
        # Z-score
        signals['z_score'] = (df['close'] - ma) / std
        
        # Volume confirmation
        if self.volume_confirm:
            vol_ma = df['volume'].rolling(self.lookback).mean()
            vol_ratio = df['volume'] / vol_ma
            high_volume = vol_ratio > 1.5
        else:
            high_volume = True
            
        # Generate signals
        signals['signal'] = 0
        
        # Entry: Price below lower band + high volume
        buy_condition = (signals['z_score'] < -self.entry_z) & high_volume
        signals.loc[buy_condition, 'signal'] = 1
        
        # Entry: Price above upper band + high volume
        sell_condition = (signals['z_score'] > self.entry_z) & high_volume
        signals.loc[sell_condition, 'signal'] = -1
        
        # Exit: Price back to mean
        exit_condition = abs(signals['z_score']) < self.exit_z
        signals.loc[exit_condition, 'signal'] = 0
        
        return signals.dropna()


class EventDrivenStrategy:
    """
    Event-driven strategy based on price gaps and earnings surprises.
    """
    
    def __init__(self, gap_threshold: float = 0.03, hold_days: int = 5):
        self.gap_threshold = gap_threshold
        self.hold_days = hold_days
        
    def detect_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect price gaps and generate signals.
        """
        signals = pd.DataFrame(index=df.index)
        
        # Calculate overnight gap
        signals['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        
        # Generate signals based on gap size
        signals['signal'] = 0
        
        # Large gap up → potential reversal → short
        signals.loc[signals['gap'] > self.gap_threshold, 'signal'] = -1
        
        # Large gap down → potential bounce → long
        signals.loc[signals['gap'] < -self.gap_threshold, 'signal'] = 1
        
        # Calculate hold period return
        signals['forward_return'] = df['close'].shift(-self.hold_days) / df['close'] - 1
        
        return signals.dropna()
        
    def generate_report(self, signals: pd.DataFrame) -> str:
        """Generate event-driven strategy report."""
        if signals.empty:
            return "⚠️ 无事件驱动信号"
            
        lines = []
        lines.append("=" * 60)
        lines.append("📊 事件驱动策略报告")
        lines.append("=" * 60)
        
        gaps = signals[abs(signals['gap']) > self.gap_threshold]
        lines.append(f"\n📈 跳空信号: {len(gaps)} 个")
        lines.append(f"  向上跳空: {len(gaps[gaps['gap'] > 0])} 个")
        lines.append(f"  向下跳空: {len(gaps[gaps['gap'] < 0])} 个")
        
        if 'forward_return' in signals.columns:
            win_rate = (signals['forward_return'] > 0).mean()
            avg_return = signals['forward_return'].mean()
            lines.append(f"\n💰 回测结果")
            lines.append(f"  胜率: {win_rate:.1%}")
            lines.append(f"  平均收益: {avg_return:+.4f}")
            
        return "\n".join(lines)


class SeasonalStrategy:
    """
    Seasonal trading strategy based on calendar effects.
    """
    
    def __init__(self):
        self.seasonal_patterns = {
            'january_effect': {'month': 1, 'direction': 1},
            'sell_in_may': {'month': 5, 'direction': -1},
            'year_end_rally': {'month': 12, 'direction': 1},
            'turn_of_month': {'day_range': (25, 5), 'direction': 1},
        }
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate seasonal signals.
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df.get('date', df.index))
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        
        signals = pd.DataFrame(index=df.index)
        signals['signal'] = 0
        
        # January effect
        signals.loc[df['month'] == 1, 'signal'] = 1
        
        # Sell in May
        signals.loc[df['month'].isin([5, 6, 7, 8, 9, 10]), 'signal'] = -0.5
        
        # Year-end rally
        signals.loc[(df['month'] == 12) & (df['day'] > 20), 'signal'] = 1
        
        # Turn of month
        tom_condition = (df['day'] >= 25) | (df['day'] <= 5)
        signals.loc[tom_condition, 'signal'] += 0.5
        
        return signals.dropna()


class VolumeWeightedStrategy:
    """
    Volume-weighted trading strategy.
    """
    
    def __init__(self, volume_lookback: int = 20, price_lookback: int = 10):
        self.volume_lookback = volume_lookback
        self.price_lookback = price_lookback
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate volume-weighted signals.
        VWAP-based strategy.
        """
        signals = pd.DataFrame(index=df.index)
        
        # Calculate VWAP
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        signals['vwap'] = (typical_price * df['volume']).rolling(self.volume_lookback).sum() / \
                         df['volume'].rolling(self.volume_lookback).sum()
        
        # Volume surge
        vol_ma = df['volume'].rolling(self.volume_lookback).mean()
        signals['volume_surge'] = df['volume'] / vol_ma
        
        # Price momentum
        signals['momentum'] = df['close'].pct_change(self.price_lookback)
        
        # Generate signals
        signals['signal'] = 0
        
        # Price above VWAP + volume surge → bullish
        bullish = (df['close'] > signals['vwap']) & (signals['volume_surge'] > 1.5)
        signals.loc[bullish, 'signal'] = 1
        
        # Price below VWAP + volume surge → bearish
        bearish = (df['close'] < signals['vwap']) & (signals['volume_surge'] > 1.5)
        signals.loc[bearish, 'signal'] = -1
        
        return signals.dropna()


class BreakoutStrategy:
    """
    Donchian channel breakout strategy.
    """
    
    def __init__(self, channel_period: int = 20, volume_confirm: bool = True):
        self.channel_period = channel_period
        self.volume_confirm = volume_confirm
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate breakout signals.
        """
        signals = pd.DataFrame(index=df.index)
        
        # Donchian channels
        signals['upper'] = df['high'].rolling(self.channel_period).max()
        signals['lower'] = df['low'].rolling(self.channel_period).min()
        signals['middle'] = (signals['upper'] + signals['lower']) / 2
        
        # Volume confirmation
        if self.volume_confirm:
            vol_ma = df['volume'].rolling(self.channel_period).mean()
            high_volume = df['volume'] > vol_ma * 1.2
        else:
            high_volume = True
            
        # Generate signals
        signals['signal'] = 0
        
        # Breakout above upper channel
        breakout_up = (df['close'] > signals['upper'].shift(1)) & high_volume
        signals.loc[breakout_up, 'signal'] = 1
        
        # Breakdown below lower channel
        breakdown = (df['close'] < signals['lower'].shift(1)) & high_volume
        signals.loc[breakdown, 'signal'] = -1
        
        return signals.dropna()


if __name__ == "__main__":
    # Test new strategies
    np.random.seed(42)
    dates = pd.bdate_range('2024-01-01', periods=200)
    df = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(100, 110, 200),
        'high': np.random.uniform(110, 120, 200),
        'low': np.random.uniform(90, 100, 200),
        'close': np.cumprod(1 + np.random.normal(0.0005, 0.015, 200)) * 100,
        'volume': np.random.uniform(1e6, 1e8, 200)
    })
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    print("📊 测试新策略...\n")
    
    # Test mean reversion
    mr = EnhancedMeanReversionStrategy()
    mr_signals = mr.generate_signals(df)
    print(f"增强均值回归: {len(mr_signals[mr_signals['signal'] != 0])} 个信号")
    
    # Test event-driven
    ed = EventDrivenStrategy()
    ed_signals = ed.detect_gaps(df)
    print(f"事件驱动: {len(ed_signals[abs(ed_signals['gap']) > 0.03])} 个跳空信号")
    
    # Test breakout
    bo = BreakoutStrategy()
    bo_signals = bo.generate_signals(df)
    print(f"突破策略: {len(bo_signals[bo_signals['signal'] != 0])} 个信号")
    
    print("\n✅ 新策略测试完成")
