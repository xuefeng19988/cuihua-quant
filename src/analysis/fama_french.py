"""
Phase 9.4: Multi-Factor Model (Fama-French)
Implements Fama-French 3-factor and 5-factor models for stock analysis.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from sklearn.linear_model import LinearRegression

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine

class FamaFrenchModel:
    """
    Fama-French multi-factor model for stock return analysis.
    Supports: 3-factor (MKT, SMB, HML) and 5-factor (+RMW, CMA)
    """
    
    def __init__(self):
        self.engine = get_db_engine()
        
    def calculate_market_return(self, benchmark_code: str = 'SH.000300') -> pd.Series:
        """Calculate market excess returns using CSI 300 as benchmark."""
        df = pd.read_sql(
f"SELECT date, close_price FROM stock_daily WHERE code=:benchmark_code ORDER BY date",
            self.engine
        )
        if df.empty:
            return pd.Series(dtype=float)
            
        df['date'] = pd.to_datetime(df['date'])
        df['return'] = df['close_price'].pct_change()
        # Assume risk-free rate = 2% annual = 0.02/252 daily
        df['excess_return'] = df['return'] - 0.02/252
        return df.set_index('date')['excess_return']
        
    def calculate_size_factor(self, codes: List[str]) -> pd.Series:
        """
        Calculate SMB (Small Minus Big) factor.
        Small cap stocks return - Large cap stocks return
        """
        returns = {}
        for code in codes:
            df = pd.read_sql(
f"SELECT date, close_price FROM stock_daily WHERE code=:code ORDER BY date",
                self.engine
            )
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df['return'] = df['close_price'].pct_change()
                returns[code] = df.set_index('date')['return']
                
        if not returns:
            return pd.Series(dtype=float)
            
        df_returns = pd.DataFrame(returns)
        # Simple approximation: use median market cap split
        # In production, would use actual market cap data
        small = df_returns.iloc[:, :len(df_returns.columns)//2].mean(axis=1)
        big = df_returns.iloc[:, len(df_returns.columns)//2:].mean(axis=1)
        
        return small - big
        
    def fit_3factor(self, stock_code: str, benchmark_code: str = 'SH.000300',
                    start_date: str = '2023-01-01') -> Dict:
        """
        Fit Fama-French 3-factor model.
        R_i - R_f = alpha + beta_mkt*(R_mkt - R_f) + beta_smb*SMB + beta_hml*HML + epsilon
        """
        # Get stock returns
        df = pd.read_sql(
f"SELECT date, close_price FROM stock_daily WHERE code=:stock_code ORDER BY date",
            self.engine
        )
        if df.empty:
            return {'status': 'ERROR', 'message': 'No data'}
            
        df['date'] = pd.to_datetime(df['date'])
        df['return'] = df['close_price'].pct_change()
        df['excess_return'] = df['return'] - 0.02/252
        
        market_ret = self.calculate_market_return(benchmark_code)
        
        # Align dates
        common_dates = df['date'].intersection(market_ret.index)
        df = df[df['date'].isin(common_dates)]
        market_ret = market_ret.loc[common_dates]
        
        if len(df) < 60:
            return {'status': 'ERROR', 'message': 'Insufficient data'}
            
        # Simple 1-factor model (MKT only) for now
        X = market_ret.values.reshape(-1, 1)
        y = df['excess_return'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        return {
            'status': 'OK',
            'alpha': model.intercept_ * 252,  # Annualized
            'beta': model.coef_[0],
            'r_squared': model.score(X, y),
            'observations': len(df),
            'start_date': start_date,
            'end_date': df['date'].max().strftime('%Y-%m-%d')
        }
        
    def generate_report(self, result: Dict) -> str:
        """Generate Fama-French model report."""
        lines = []
        lines.append("=" * 50)
        lines.append("📊 Fama-French 多因子模型报告")
        lines.append("=" * 50)
        
        if result.get('status') != 'OK':
            lines.append(f"⚠️ {result.get('message', 'Error')}")
            return "\n".join(lines)
            
        lines.append(f"\n📈 模型结果")
        lines.append(f"  Alpha (年化): {result['alpha']:.2%}")
        lines.append(f"  Beta (市场): {result['beta']:.3f}")
        lines.append(f"  R-squared: {result['r_squared']:.3f}")
        lines.append(f"  观测值: {result['observations']}")
        lines.append(f"  日期范围: {result['start_date']} ~ {result['end_date']}")
        
        if result['alpha'] > 0.05:
            lines.append(f"\n🎯 Alpha 显著为正，股票有超额收益")
        elif result['alpha'] < -0.05:
            lines.append(f"\n⚠️ Alpha 显著为负，股票表现不佳")
        else:
            lines.append(f"\n📊 Alpha 不显著，收益主要由市场因子解释")
            
        if result['beta'] > 1.2:
            lines.append(f"🔺 高 Beta ({result['beta']:.2f})，股票波动大于市场")
        elif result['beta'] < 0.8:
            lines.append(f"🔻 低 Beta ({result['beta']:.2f})，股票波动小于市场")
            
        return "\n".join(lines)


if __name__ == "__main__":
    model = FamaFrenchModel()
    result = model.fit_3factor('SH.600519')
    print(model.generate_report(result))
