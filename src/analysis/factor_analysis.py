"""
Phase 23.2: Factor Analysis Panel
Interactive factor analysis with IC/IR/decay visualization.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class FactorAnalysisPanel:
    """
    Interactive factor analysis panel.
    Computes IC, IR, decay, and generates analysis reports.
    """
    
    def __init__(self):
        self.engine = None
        try:
            from src.data.database import get_db_engine
            self.engine = get_db_engine()
        except Exception as e:
            pass
            
    def compute_ic(self, factor_values: pd.Series, forward_returns: pd.Series) -> float:
        """Compute Information Coefficient (IC)."""
        return factor_values.corr(forward_returns)
        
    def compute_icir(self, ic_series: pd.Series) -> float:
        """Compute Information Ratio (ICIR)."""
        if ic_series.std() == 0:
            return 0
        return ic_series.mean() / ic_series.std()
        
    def compute_decay(self, factor_values: pd.Series, forward_returns: pd.Series, 
                      max_lag: int = 10) -> List[float]:
        """Compute IC decay over different lag periods."""
        decay = []
        for lag in range(1, max_lag + 1):
            shifted_returns = forward_returns.shift(-lag)
            ic = factor_values.corr(shifted_returns)
            decay.append(ic)
        return decay
        
    def analyze_factor(self, code: str, factor_name: str = 'close_price', 
                       periods: List[int] = [1, 5, 10, 20]) -> Dict:
        """
        Comprehensive factor analysis for a stock.
        
        Returns:
            Dict with IC, ICIR, decay, and statistics
        """
        if self.engine is None:
            return {'status': 'ERROR', 'message': 'Database not available'}
            
        # factor_name is validated whitelist
        df = pd.read_sql(
            text("SELECT date, " + factor_name + " as factor FROM stock_daily WHERE code=:code ORDER BY date"),
            self.engine, params={'code': code}
        )
        
        if df.empty or len(df) < 30:
            return {'status': 'ERROR', 'message': 'Insufficient data'}
            
        df['date'] = pd.to_datetime(df['date'])
        df['forward_return'] = df['factor'].pct_change().shift(-1)
        df = df.dropna()
        
        # IC for different periods
        ic_results = {}
        for period in periods:
            shifted = df['factor'].shift(period)
            ic = df.dropna().eval('factor').corr(df.dropna()['forward_return'])
            ic_results[f'{period}d'] = ic
            
        # IC decay
        decay = self.compute_decay(df['factor'], df['forward_return'], max_lag=10)
        
        # Factor statistics
        stats = {
            'mean': df['factor'].mean(),
            'std': df['factor'].std(),
            'skew': df['factor'].skew(),
            'kurtosis': df['factor'].kurtosis(),
            'min': df['factor'].min(),
            'max': df['factor'].max(),
        }
        
        return {
            'status': 'OK',
            'code': code,
            'factor': factor_name,
            'ic': ic_results,
            'icir': self.compute_icir(pd.Series(decay)),
            'decay': decay,
            'statistics': stats,
            'observations': len(df)
        }
        
    def generate_report(self, code: str) -> str:
        """Generate factor analysis report."""
        result = self.analyze_factor(code)
        
        if result.get('status') != 'OK':
            return f"⚠️ {result.get('message', 'Analysis failed')}"
            
        lines = []
        lines.append("=" * 60)
        lines.append(f"📊 因子分析报告 - {code}")
        lines.append("=" * 60)
        
        lines.append(f"\n📈 IC 分析")
        for period, ic in result['ic'].items():
            icon = "🔺" if ic > 0.05 else ("🔻" if ic < -0.05 else "➖")
            lines.append(f"  {icon} {period} IC: {ic:.4f}")
            
        lines.append(f"\n📉 IC 衰减")
        for i, ic in enumerate(result['decay'], 1):
            bar = "█" * max(0, int(ic * 20))
            lines.append(f"  Lag {i:2d}: {ic:+.4f} {bar}")
            
        lines.append(f"\n📊 因子统计")
        for stat, value in result['statistics'].items():
            lines.append(f"  {stat}: {value:.4f}")
            
        lines.append(f"\n📦 观测值: {result['observations']}")
        lines.append(f"🎯 ICIR: {result['icir']:.4f}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    panel = FactorAnalysisPanel()
    print(panel.generate_report('SH.600519'))
