"""
Phase 44: Factor Research Platform
Platform for researching and testing alpha factors.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Callable

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class FactorResearcher:
    """
    Factor research and testing platform.
    """
    
    def __init__(self):
        self.factor_library: Dict[str, Callable] = {}
        self.research_log: List[Dict] = []
        self._register_builtin_factors()
        
    def _register_builtin_factors(self):
        """Register built-in factors."""
        self.factor_library['momentum_20d'] = lambda df: df['close'].pct_change(20)
        self.factor_library['momentum_60d'] = lambda df: df['close'].pct_change(60)
        self.factor_library['volatility_20d'] = lambda df: df['close'].pct_change().rolling(20).std()
        self.factor_library['volume_ratio'] = lambda df: df['volume'] / df['volume'].rolling(20).mean()
        self.factor_library['ma_ratio_5_20'] = lambda df: df['close'].rolling(5).mean() / df['close'].rolling(20).mean()
        self.factor_library['rsi_14'] = self._rsi_factor
        self.factor_library['turnover_rate'] = lambda df: df.get('turnover_rate', pd.Series(0, index=df.index))
        
    def _rsi_factor(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """RSI factor."""
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def register_factor(self, name: str, func: Callable):
        """Register a custom factor."""
        self.factor_library[name] = func
        
    def calculate_factor(self, df: pd.DataFrame, factor_name: str) -> pd.Series:
        """Calculate a single factor."""
        if factor_name not in self.factor_library:
            raise ValueError(f"Unknown factor: {factor_name}")
        return self.factor_library[factor_name](df)
        
    def calculate_all_factors(self, df: pd.DataFrame, 
                             factors: List[str] = None) -> pd.DataFrame:
        """Calculate multiple factors."""
        if factors is None:
            factors = list(self.factor_library.keys())
            
        result = pd.DataFrame(index=df.index)
        result['date'] = df.get('date', pd.Series(index=df.index))
        
        for factor_name in factors:
            try:
                result[factor_name] = self.calculate_factor(df, factor_name)
            except Exception as e:
                result[factor_name] = np.nan
                
        return result
        
    def factor_ic_analysis(self, factor_values: pd.Series, 
                          forward_returns: pd.Series) -> Dict:
        """
        Calculate factor IC (Information Coefficient).
        
        Args:
            factor_values: Factor values
            forward_returns: Forward returns
            
        Returns:
            IC analysis results
        """
        # Align data
        aligned = pd.DataFrame({
            'factor': factor_values,
            'return': forward_returns
        }).dropna()
        
        if len(aligned) < 10:
            return {'error': 'Insufficient data'}
            
        # Calculate IC
        ic = aligned['factor'].corr(aligned['return'])
        
        # Rolling IC
        rolling_ic = aligned['factor'].rolling(60).corr(aligned['return'])
        
        # IC statistics
        ic_stats = {
            'ic': ic,
            'ic_mean': rolling_ic.mean(),
            'ic_std': rolling_ic.std(),
            'icir': rolling_ic.mean() / rolling_ic.std() if rolling_ic.std() > 0 else 0,
            'ic_positive_rate': (rolling_ic > 0).mean(),
            'ic_abs_mean': rolling_ic.abs().mean(),
        }
        
        # Quantile analysis
        aligned['quantile'] = pd.qcut(aligned['factor'], 5, labels=False, duplicates='drop')
        quantile_returns = aligned.groupby('quantile')['return'].mean()
        
        ic_stats['quantile_returns'] = quantile_returns.to_dict()
        ic_stats['monotonicity'] = self._check_monotonicity(quantile_returns)
        
        return ic_stats
        
    def _check_monotonicity(self, quantile_returns: pd.Series) -> float:
        """Check if quantile returns are monotonic."""
        diffs = quantile_returns.diff().dropna()
        if len(diffs) == 0:
            return 0
        return (diffs > 0).mean()
        
    def run_factor_research(self, df: pd.DataFrame, factor_name: str,
                           forward_period: int = 5) -> Dict:
        """
        Run complete factor research.
        
        Args:
            df: Stock data
            factor_name: Factor to research
            forward_period: Forward return period
            
        Returns:
            Research results
        """
        # Calculate factor
        factor_values = self.calculate_factor(df, factor_name)
        
        # Calculate forward returns
        forward_returns = df['close'].shift(-forward_period) / df['close'] - 1
        
        # IC analysis
        ic_results = self.factor_ic_analysis(factor_values, forward_returns)
        
        # Log research
        research_log = {
            'factor': factor_name,
            'timestamp': datetime.now().isoformat(),
            'forward_period': forward_period,
            'data_points': len(df),
            'results': ic_results
        }
        self.research_log.append(research_log)
        
        return research_log
        
    def generate_factor_report(self, research_result: Dict) -> str:
        """Generate factor research report."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"🔬 因子研究报告 - {research_result['factor']}")
        lines.append("=" * 60)
        
        results = research_result['results']
        if 'error' in results:
            lines.append(f"\n⚠️ {results['error']}")
            return "\n".join(lines)
            
        lines.append(f"\n📊 IC 分析")
        lines.append(f"  IC: {results.get('ic', 0):.4f}")
        lines.append(f"  IC 均值: {results.get('ic_mean', 0):.4f}")
        lines.append(f"  IC 标准差: {results.get('ic_std', 0):.4f}")
        lines.append(f"  ICIR: {results.get('icir', 0):.4f}")
        lines.append(f"  IC 正率: {results.get('ic_positive_rate', 0):.1%}")
        
        qr = results.get('quantile_returns', {})
        if qr:
            lines.append(f"\n📈 分组收益")
            for q, ret in sorted(qr.items()):
                lines.append(f"  Q{int(q)+1}: {ret:+.4f}")
            lines.append(f"  单调性: {results.get('monotonicity', 0):.1%}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    # Test factor research
    np.random.seed(42)
    dates = pd.bdate_range('2024-01-01', periods=200)
    df = pd.DataFrame({
        'date': dates,
        'close': np.cumprod(1 + np.random.normal(0.0005, 0.015, 200)) * 100,
        'volume': np.random.uniform(1e6, 1e8, 200)
    })
    
    researcher = FactorResearcher()
    result = researcher.run_factor_research(df, 'momentum_20d', forward_period=5)
    print(researcher.generate_factor_report(result))
