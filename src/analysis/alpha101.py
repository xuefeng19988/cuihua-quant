"""
Phase 14.1: Alpha101 Factor Library
Implements WorldQuant Alpha101 factors for stock analysis.
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

from src.data.database import get_db_engine

class Alpha101Factors:
    """
    Implementation of WorldQuant Alpha101 factors.
    Reference: https://arxiv.org/pdf/1601.00991
    """
    
    def __init__(self):
        self.engine = get_db_engine()
        
    def load_stock_data(self, code: str, days: int = 252) -> pd.DataFrame:
        """Load stock data for factor calculation."""
        df = pd.read_sql(
            f"SELECT date, open_price as open, high_price as high, low_price as low, "
            f"close_price as close, volume, turnover_rate FROM stock_daily "
            f"WHERE code='{code}' ORDER BY date DESC LIMIT {days}",
            self.engine
        )
        if df.empty:
            return df
        return df.iloc[::-1].reset_index(drop=True)
        
    # Helper functions
    @staticmethod
    def ts_rank(series: pd.Series, window: int) -> pd.Series:
        """Time series rank."""
        return series.rolling(window).apply(lambda x: pd.Series(x).rank().iloc[-1])
        
    @staticmethod
    def delta(series: pd.Series, period: int = 1) -> pd.Series:
        """Difference."""
        return series.diff(period)
        
    @staticmethod
    def delay(series: pd.Series, period: int = 1) -> pd.Series:
        """Lag."""
        return series.shift(period)
        
    @staticmethod
    def correlation(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
        """Rolling correlation."""
        return x.rolling(window).corr(y)
        
    @staticmethod
    def covariance(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
        """Rolling covariance."""
        return x.rolling(window).cov(y)
        
    @staticmethod
    def scale(series: pd.Series) -> pd.Series:
        """Scale to unit sum."""
        return series / series.abs().sum()
        
    # Alpha factors
    def alpha001(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#1: (-1 * CORR(RANK(DELTA(LOG(VOLUME), 1)), RANK(((CLOSE - OPEN) / OPEN)), 6))"""
        vol_rank = self.ts_rank(np.log(df['volume']).diff(1), 6)
        price_rank = self.ts_rank((df['close'] - df['open']) / df['open'], 6)
        return -1 * self.correlation(vol_rank, price_rank, 6)
        
    def alpha002(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#2: (-1 * DELTA((((CLOSE - LOW) - (HIGH - CLOSE)) / (HIGH - LOW)), 1))"""
        return -1 * ((df['close'] - df['low']) - (df['high'] - df['close'])).diff(1) / (df['high'] - df['low'])
        
    def alpha003(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#3: SUM((CLOSE=DELAY(CLOSE,1)?0:CLOSE-(CLOSE>DELAY(CLOSE,1)?MIN(LOW,DELAY(CLOSE,1)):MAX(HIGH,DELAY(CLOSE,1)))),6)"""
        cond = df['close'] == df['close'].shift(1)
        term = np.where(
            cond, 0,
            np.where(df['close'] > df['close'].shift(1),
                     np.minimum(df['low'], df['close'].shift(1)),
                     np.maximum(df['high'], df['close'].shift(1)))
        )
        return pd.Series(term, index=df.index).rolling(6).sum()
        
    def alpha004(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#4: ((((SUM(CLOSE, 8) / 8) + STD(CLOSE, 8)) < (SUM(CLOSE, 2) / 2)) ? (-1 * 1) : (((SUM(CLOSE, 2) / 2) < ((SUM(CLOSE, 8) / 8) - STD(CLOSE, 8))) ? 1 : (((1 < (VOLUME / DELAY(VOLUME, 1))) ? 1 : -1))))"""
        sum8 = df['close'].rolling(8).mean()
        std8 = df['close'].rolling(8).std()
        sum2 = df['close'].rolling(2).mean()
        
        result = pd.Series(0.0, index=df.index)
        mask1 = (sum8 + std8) < sum2
        mask2 = sum2 < (sum8 - std8)
        mask3 = df['volume'] > df['volume'].shift(1)
        
        result[mask1] = -1
        result[mask2] = 1
        result[~mask1 & ~mask2 & mask3] = 1
        result[~mask1 & ~mask2 & ~mask3] = -1
        
        return result
        
    def alpha005(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#5: (-1 * TSMAX(CORR(TSRANK(VOLUME, 5), TSRANK(HIGH, 5), 5), 3))"""
        vol_rank = self.ts_rank(df['volume'], 5)
        high_rank = self.ts_rank(df['high'], 5)
        corr = self.correlation(vol_rank, high_rank, 5)
        return -1 * corr.rolling(3).max()
        
    def alpha006(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#6: (-1 * RANK(DELTA((((OPEN * 0.85) + (HIGH * 0.15))), 4)))"""
        return -1 * ((df['open'] * 0.85 + df['high'] * 0.15).diff(4)).rank()
        
    def alpha007(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#7: ((RANK(MAX((VWAP - CLOSE), 3)) + RANK(MIN((VWAP - CLOSE), 3))) * RANK(DELTA(VOLUME, 3)))"""
        # VWAP approximation
        vwap = (df['close'] * df['volume']).rolling(3).sum() / df['volume'].rolling(3).sum()
        diff = vwap - df['close']
        return ((diff.rolling(3).max().rank() + diff.rolling(3).min().rank()) * df['volume'].diff(3).rank())
        
    def alpha008(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#8: RANK(DELTA(((((HIGH + LOW) / 2) * 0.2) + (VWAP * 0.8)), 4) * -1)"""
        vwap = (df['close'] * df['volume']).rolling(3).sum() / df['volume'].rolling(3).sum()
        term = ((df['high'] + df['low']) / 2 * 0.2) + (vwap * 0.8)
        return (term.diff(4) * -1).rank()
        
    def alpha009(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#9: SMA(((HIGH+LOW)/2-(DELAY(HIGH,1)+DELAY(LOW,1))/2)*(HIGH-LOW)/VOLUME,7,2)"""
        term = ((df['high'] + df['low']) / 2 - (df['high'].shift(1) + df['low'].shift(1)) / 2) * (df['high'] - df['low']) / df['volume']
        return term.ewm(span=7, min_periods=2).mean()
        
    def alpha010(self, df: pd.DataFrame) -> pd.Series:
        """Alpha#10: RANK(MAX(((RET < 0) ? STD(RET, 20) : CLOSE)^2),5)"""
        ret = df['close'].pct_change()
        std_ret = ret.rolling(20).std()
        term = np.where(ret < 0, std_ret, df['close']) ** 2
        return pd.Series(term, index=df.index).rolling(5).max().rank()
        
    def calculate_all(self, code: str) -> pd.DataFrame:
        """Calculate all available alpha factors for a stock."""
        df = self.load_stock_data(code)
        if df.empty:
            return pd.DataFrame()
            
        factors = pd.DataFrame({'date': df['date']})
        
        # Calculate factors
        factor_methods = [m for m in dir(self) if m.startswith('alpha') and callable(getattr(self, m))]
        
        for method_name in factor_methods:
            try:
                factor = getattr(self, method_name)(df)
                factors[method_name] = factor.values
            except Exception as e:
                print(f"⚠️ {method_name} failed: {e}")
                
        return factors.dropna()
        
    def generate_factor_report(self, code: str) -> str:
        """Generate factor calculation report."""
        factors = self.calculate_all(code)
        if factors.empty:
            return f"⚠️ No factors calculated for {code}"
            
        lines = []
        lines.append("=" * 50)
        lines.append(f"📊 Alpha101 因子报告 - {code}")
        lines.append("=" * 50)
        
        lines.append(f"\n📈 可用因子: {len([c for c in factors.columns if c.startswith('alpha')])}")
        
        for col in factors.columns:
            if col.startswith('alpha'):
                lines.append(f"  {col}: mean={factors[col].mean():.4f}, std={factors[col].std():.4f}")
                
        return "\n".join(lines)


if __name__ == "__main__":
    factors = Alpha101Factors()
    # Test with a stock
    print(factors.generate_factor_report('SH.600519'))
