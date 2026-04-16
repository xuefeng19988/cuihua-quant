"""
Strategy Runner
Manages multiple strategies and runs them on historical data.
"""

import os
import sys
import yaml
import pandas as pd
from typing import List, Dict
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.strategy.base import BaseStrategy, Signal
from src.strategy.multi_factor import MultiFactorStrategy
from src.strategy.momentum import MomentumStrategy
from src.strategy.mean_reversion import MeanReversionStrategy

class StrategyRunner:
    """
    Runs multiple strategies on historical data and aggregates signals.
    """
    
    def __init__(self, config_path: str = None):
        self.engine = get_db_engine()
        self.strategies: Dict[str, BaseStrategy] = {}
        
        # Load config
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
            strategy_cfg = cfg.get('strategies', {})
        else:
            strategy_cfg = {}
            
        # Initialize default strategies
        self._init_strategies(strategy_cfg)
        
    def _init_strategies(self, config: Dict):
        """Initialize strategies from config."""
        # Multi-Factor Strategy
        mf_params = config.get('multi_factor', {})
        if mf_params.get('enabled', True):
            self.strategies['multi_factor'] = MultiFactorStrategy(mf_params)
            
        # Momentum Strategy
        mom_params = config.get('momentum', {})
        if mom_params.get('enabled', True):
            self.strategies['momentum'] = MomentumStrategy(mom_params)
            
        # Mean Reversion Strategy
        mr_params = config.get('mean_reversion', {})
        if mr_params.get('enabled', True):
            self.strategies['mean_reversion'] = MeanReversionStrategy(mr_params)
            
    def load_stock_data(self, codes: List[str], days: int = 60) -> Dict[str, pd.DataFrame]:
        """Load historical data for given stocks."""
        data = {}
        
        for code in codes:
            query = f"""
                SELECT date, open_price as open, high_price as high, 
                       low_price as low, close_price as close, volume,
                       pe_ratio, turnover_rate
                FROM stock_daily 
                WHERE code = '{code}' 
                ORDER BY date DESC
                LIMIT {days}
            """
            
            try:
                df = pd.read_sql(query, self.engine)
                if not df.empty:
                    df = df.sort_values('date').reset_index(drop=True)
                    data[code] = df
            except Exception as e:
                print(f"⚠️ Error loading {code}: {e}")
                
        return data
        
    def run_all_strategies(self, codes: List[str]) -> Dict[str, List[Signal]]:
        """
        Run all enabled strategies on given stocks.
        
        Returns:
            Dict mapping strategy name to list of signals
        """
        # Load data
        data = self.load_stock_data(codes)
        if not data:
            print("⚠️ No data loaded.")
            return {}
            
        results = {}
        
        for name, strategy in self.strategies.items():
            print(f"🧠 Running {name}...")
            try:
                signals = strategy.generate_signals(data)
                results[name] = signals
                print(f"  ✅ {len(signals)} signals generated")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results[name] = []
                
        return results
        
    def aggregate_signals(self, results: Dict[str, List[Signal]]) -> pd.DataFrame:
        """
        Aggregate signals from multiple strategies.
        Uses voting mechanism: BUY = +1, SELL = -1, HOLD = 0
        """
        # Collect all codes
        all_codes = set()
        for signals in results.values():
            for sig in signals:
                all_codes.add(sig.code)
                
        # Aggregate
        rows = []
        for code in all_codes:
            buy_votes = 0
            sell_votes = 0
            total_strength = 0.0
            reasons = []
            
            for strategy_name, signals in results.items():
                for sig in signals:
                    if sig.code == code:
                        if sig.direction == 'BUY':
                            buy_votes += 1
                            total_strength += sig.strength
                            reasons.append(f"{strategy_name}: BUY")
                        elif sig.direction == 'SELL':
                            sell_votes += 1
                            total_strength -= sig.strength
                            reasons.append(f"{strategy_name}: SELL")
                            
            # Calculate consensus
            net_votes = buy_votes - sell_votes
            num_strategies = len(results)
            consensus = net_votes / num_strategies if num_strategies > 0 else 0
            
            # Determine action
            if consensus > 0.3:
                action = 'BUY'
            elif consensus < -0.3:
                action = 'SELL'
            else:
                action = 'HOLD'
                
            rows.append({
                'code': code,
                'buy_votes': buy_votes,
                'sell_votes': sell_votes,
                'consensus': consensus,
                'avg_strength': total_strength / num_strategies if num_strategies > 0 else 0,
                'action': action,
                'reasons': ', '.join(reasons),
                'date': datetime.now().strftime('%Y-%m-%d')
            })
            
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values('consensus', ascending=False).reset_index(drop=True)
            df['rank'] = df.index + 1
            
        return df
        
    def run_and_aggregate(self, codes: List[str]) -> pd.DataFrame:
        """Run all strategies and return aggregated signals."""
        results = self.run_all_strategies(codes)
        return self.aggregate_signals(results)
