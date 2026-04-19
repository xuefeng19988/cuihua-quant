"""
Portfolio Rebalancer
Implements portfolio allocation strategies.
"""

import os
import sys
import yaml
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine

class PortfolioRebalancer:
    """
    Portfolio rebalancing strategies:
    1. Equal Weight
    2. Risk Parity (inverse volatility)
    3. Score-based (from signal engine)
    """
    
    def __init__(self, config_path: str = None):
        self.engine = get_db_engine()
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
            self.risk_cfg = cfg.get('risk', {})
        else:
            self.risk_cfg = {}
        self.max_single_pct = self.risk_cfg.get('max_single_position_pct', 0.10)
        
    def equal_weight(self, codes: List[str]) -> Dict[str, float]:
        """Equal weight allocation."""
        if not codes:
            return {}
        w = 1.0 / len(codes)
        return {code: w for code in codes}
        
    def risk_parity(self, codes: List[str], lookback: int = 60) -> Dict[str, float]:
        """
        Risk parity: inverse volatility weighting.
        Lower vol → higher weight.
        """
        vols = {}
        for code in codes:
            try:
                df = pd.read_sql(
                    f"SELECT close_price FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT {lookback}",
                    self.engine
                )
                if len(df) >= 20:
                    ret = df['close_price'].pct_change().dropna()
                    vols[code] = max(ret.std() * np.sqrt(252), 0.1)
            except Exception as e:
                vols[code] = 0.2
                
        if not vols:
            return self.equal_weight(codes)
            
        inv = {c: 1.0/v for c,v in vols.items()}
        total = sum(inv.values())
        return {c: w/total for c,w in inv.items()}
        
    def score_based(self, signals_df: pd.DataFrame) -> Dict[str, float]:
        """Score-based allocation from signal engine."""
        if signals_df is None or signals_df.empty:
            return {}
        pos = signals_df[signals_df['combined_score'] > 0].copy()
        if pos.empty:
            return {}
        total = pos['combined_score'].sum()
        if total <= 0:
            return self.equal_weight(pos['code'].tolist())
        return {r['code']: r['combined_score']/total for _,r in pos.iterrows()}
        
    def generate_orders(self, target_weights: Dict[str, float],
                         current_positions: Dict[str, int],
                         current_prices: Dict[str, float],
                         total_value: float) -> List[Dict]:
        """Generate rebalancing orders."""
        orders = []
        all_codes = set(list(target_weights.keys()) + list(current_positions.keys()))
        
        for code in all_codes:
            tw = target_weights.get(code, 0)
            cs = current_positions.get(code, 0)
            price = current_prices.get(code, 0)
            if price <= 0:
                continue
                
            target_shares = int(total_value * tw / price / 100) * 100
            diff = target_shares - cs
            
            if abs(diff) >= 100:
                orders.append({
                    'code': code,
                    'action': 'BUY' if diff > 0 else 'SELL',
                    'shares': abs(diff),
                    'price': price,
                    'est_value': abs(diff) * price,
                    'target_weight': tw
                })
        return orders
