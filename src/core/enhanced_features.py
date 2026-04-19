"""
Phase 52: Advanced Features Optimization
Enhanced existing features with better performance and usability.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Callable

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class EnhancedSignalGenerator:
    """
    Enhanced signal generator with multi-timeframe analysis.
    """
    
    def __init__(self):
        pass
        
    def multi_timeframe_analysis(self, df: pd.DataFrame, 
                                 timeframes: Dict[str, int] = None) -> Dict:
        """
        Analyze signals across multiple timeframes.
        
        Args:
            df: OHLCV DataFrame
            timeframes: Dict of {name: period}
            
        Returns:
            Multi-timeframe analysis results
        """
        if timeframes is None:
            timeframes = {
                'short': 5,
                'medium': 20,
                'long': 60
            }
            
        results = {}
        
        for tf_name, period in timeframes.items():
            # Calculate indicators for each timeframe
            ma = df['close'].rolling(period).mean()
            rsi = self._calculate_rsi(df['close'], min(14, period))
            macd, signal, hist = self._calculate_macd(df['close'])
            
            # Determine signal
            bullish = 0
            if df['close'].iloc[-1] > ma.iloc[-1]:
                bullish += 1
            if rsi.iloc[-1] > 50:
                bullish += 1
            if hist.iloc[-1] > 0:
                bullish += 1
                
            results[tf_name] = {
                'ma': ma.iloc[-1],
                'rsi': rsi.iloc[-1],
                'macd_hist': hist.iloc[-1],
                'signal': 'bullish' if bullish >= 2 else 'bearish',
                'strength': bullish / 3
            }
            
        # Aggregate signals
        bullish_count = sum(1 for r in results.values() if r['signal'] == 'bullish')
        total = len(results)
        
        results['aggregate'] = {
            'bullish_count': bullish_count,
            'bearish_count': total - bullish_count,
            'consensus': 'bullish' if bullish_count > total/2 else 'bearish',
            'confidence': bullish_count / total
        }
        
        return results
        
    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI."""
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def _calculate_macd(self, series: pd.Series, fast: int = 12, 
                       slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD."""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
        
    def generate_report(self, multi_tf_results: Dict) -> str:
        """Generate multi-timeframe report."""
        lines = []
        lines.append("=" * 60)
        lines.append("📊 多时间框架分析报告")
        lines.append("=" * 60)
        
        for tf_name, result in multi_tf_results.items():
            if tf_name == 'aggregate':
                continue
            lines.append(f"\n📈 {tf_name} 周期")
            lines.append(f"  MA: {result['ma']:.2f}")
            lines.append(f"  RSI: {result['rsi']:.2f}")
            lines.append(f"  MACD 柱: {result['macd_hist']:.4f}")
            lines.append(f"  信号: {'🔺 看涨' if result['signal'] == 'bullish' else '🔻 看跌'}")
            lines.append(f"  强度: {result['strength']:.0%}")
            
        agg = multi_tf_results.get('aggregate', {})
        lines.append(f"\n🎯 综合信号")
        lines.append(f"  看涨: {agg.get('bullish_count', 0)} | 看跌: {agg.get('bearish_count', 0)}")
        lines.append(f"  共识: {'🔺 看涨' if agg.get('consensus') == 'bullish' else '🔻 看跌'}")
        lines.append(f"  置信度: {agg.get('confidence', 0):.0%}")
        
        return "\n".join(lines)


class EnhancedRiskManager:
    """
    Enhanced risk manager with position sizing optimization.
    """
    
    def __init__(self):
        pass
        
    def kelly_criterion(self, win_rate: float, win_loss_ratio: float,
                       max_position_pct: float = 0.10) -> float:
        """
        Calculate optimal position size using Kelly Criterion.
        """
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        # Use half-Kelly for safety
        kelly = kelly / 2
        # Cap at max position
        return min(max(kelly, 0), max_position_pct)
        
    def optimal_f(self, trade_results: List[float]) -> float:
        """
        Calculate optimal f using Ralph Vince's method.
        """
        if not trade_results:
            return 0
            
        largest_loss = abs(min(trade_results))
        if largest_loss == 0:
            return 0
            
        # Test different f values
        best_f = 0
        best_terminal = 0
        
        for f in np.linspace(0.01, 0.5, 50):
            terminal = 1.0
            for trade in trade_results:
                hpr = 1 + (f * trade / largest_loss)
                terminal *= hpr
                
            if terminal > best_terminal:
                best_terminal = terminal
                best_f = f
                
        return best_f
        
    def dynamic_position_sizing(self, volatility: float, account_size: float,
                                risk_per_trade: float = 0.02,
                                atr_multiplier: float = 2.0) -> float:
        """
        Calculate position size based on volatility (ATR method).
        """
        risk_amount = account_size * risk_per_trade
        position_size = risk_amount / (volatility * atr_multiplier)
        return position_size


class EnhancedBacktester:
    """
    Enhanced backtester with walk-forward optimization.
    """
    
    def __init__(self):
        pass
        
    def walk_forward_optimization(self, data: pd.DataFrame, 
                                  strategy_func: Callable,
                                  train_periods: int = 120,
                                  test_periods: int = 30,
                                  param_grid: Dict = None) -> Dict:
        """
        Walk-forward optimization.
        """
        results = []
        n = len(data)
        
        start_idx = train_periods
        while start_idx + test_periods <= n:
            train_data = data.iloc[start_idx - train_periods:start_idx]
            test_data = data.iloc[start_idx:start_idx + test_periods]
            
            # Optimize on training data
            if param_grid:
                best_params = self._optimize_params(train_data, strategy_func, param_grid)
            else:
                best_params = {}
                
            # Test on out-of-sample data
            test_result = strategy_func(test_data, best_params)
            
            results.append({
                'train_start': start_idx - train_periods,
                'train_end': start_idx,
                'test_start': start_idx,
                'test_end': start_idx + test_periods,
                'params': best_params,
                'result': test_result
            })
            
            start_idx += test_periods
            
        return {
            'windows': results,
            'avg_result': np.mean([r['result'] for r in results if r['result'] is not None]),
            'consistency': self._calculate_consistency(results)
        }
        
    def _optimize_params(self, data: pd.DataFrame, strategy_func: Callable,
                        param_grid: Dict) -> Dict:
        """Optimize parameters on training data."""
        from itertools import product
        
        best_result = -float('inf')
        best_params = {}
        
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        for values in product(*param_values):
            params = dict(zip(param_names, values))
            result = strategy_func(data, params)
            
            if result > best_result:
                best_result = result
                best_params = params.copy()
                
        return best_params
        
    def _calculate_consistency(self, results: List[Dict]) -> float:
        """Calculate strategy consistency across windows."""
        if not results:
            return 0
            
        values = [r['result'] for r in results if r['result'] is not None]
        if not values:
            return 0
            
        mean = np.mean(values)
        std = np.std(values)
        
        return mean / std if std > 0 else 0


if __name__ == "__main__":
    # Test enhanced signal generator
    np.random.seed(42)
    dates = pd.bdate_range('2024-01-01', periods=200)
    df = pd.DataFrame({
        'date': dates,
        'close': np.cumprod(1 + np.random.normal(0.0005, 0.015, 200)) * 100,
        'volume': np.random.uniform(1e6, 1e8, 200)
    })
    
    signal_gen = EnhancedSignalGenerator()
    results = signal_gen.multi_timeframe_analysis(df)
    print(signal_gen.generate_report(results))
