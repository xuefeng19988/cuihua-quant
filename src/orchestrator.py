"""
Orchestrator Module
Coordinates all system components: data → analysis → strategy → execution → monitor.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from typing import List, Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.data.futu_sync import FutuSync
from src.data.akshare_sync import AKShareSync
from src.analysis.signal_gen import SignalGenerator
from src.execution.risk_control import RiskManager
from src.execution.futu_trader import FutuTrader
from src.monitor.reporter import DailyReporter

class Orchestrator:
    """
    Main orchestrator that runs the full trading pipeline:
    1. Sync Data (Futu → fallback to AKShare)
    2. Generate Signals (Technical + Sentiment)
    3. Apply Risk Controls
    4. Execute Orders (if enabled)
    5. Send Report
    """
    
    def __init__(self, config_dir: str = None):
        if not config_dir:
            config_dir = os.path.join(project_root, 'config')
            
        # Load configs
        self.configs = {}
        for fname in ['app.yaml', 'stocks.yaml', 'strategies.yaml', 'risk.yaml']:
            fpath = os.path.join(config_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    self.configs[fname.replace('.yaml', '')] = yaml.safe_load(f) or {}
                    
        # Components
        self.signal_gen = SignalGenerator()
        self.risk_mgr = RiskManager(self.configs.get('risk', {}))
        self.trader = FutuTrader(paper_trading=True)  # Default to paper trading
        self.reporter = DailyReporter()
        
    def run_pipeline(self, execute_trades: bool = False):
        """Run the full daily trading pipeline."""
        print("=" * 60)
        print(f"🚀 Cuihua Quant Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        
        # Step 1: Sync Data
        print("\n📥 Step 1: Syncing Data...")
        self._sync_data()
        
        # Step 2: Generate Signals
        print("\n🧠 Step 2: Generating Signals...")
        signals = self._generate_signals()
        
        if signals.empty:
            print("⚠️ No signals generated. Pipeline stopped.")
            return
            
        # Step 3: Risk Check
        print("\n🛡️ Step 3: Risk Checks...")
        validated = self._apply_risk_checks(signals)
        
        # Step 4: Execute (Optional)
        if execute_trades:
            print("\n💰 Step 4: Executing Trades...")
            self._execute_trades(validated)
        else:
            print("\n⏭️ Step 4: Trading Skipped (Paper Mode)")
            
        # Step 5: Report
        print("\n📊 Step 5: Generating Report...")
        self._send_report(validated)
        
        print("\n✅ Pipeline Completed.")
        
    def _sync_data(self):
        """Sync market data from Futu, fallback to AKShare."""
        # Try Futu first
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            print("⚠️ No stocks configured.")
            return
            
        syncer = FutuSync()
        if syncer.connect():
            syncer.run(pool_name='watchlist', days_back=5)
            syncer.close()
        else:
            print("🔄 Falling back to AKShare...")
            ak_syncer = AKShareSync()
            ak_syncer.run(pool_name='watchlist', days_back=5)
            
    def _generate_signals(self) -> pd.DataFrame:
        """Generate trading signals."""
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        signals = self.signal_gen.generate_combined_signal(stocks)
        
        if not signals.empty:
            print(f"✅ Generated signals for {len(signals)} stocks.")
            print("\n📈 Top 5 Signals:")
            for _, row in signals.head(5).iterrows():
                print(f"  #{row['rank']} {row['code']}: Score {row['combined_score']:.3f} | Close {row['close']:.2f}")
                
        return signals
        
    def _apply_risk_checks(self, signals: pd.DataFrame) -> pd.DataFrame:
        """Apply risk filters to signals."""
        # Filter out signals with negative scores
        valid = signals[signals['combined_score'] > 0].copy()
        
        # Apply max position count limit
        max_positions = self.risk_mgr.max_position_count
        if len(valid) > max_positions:
            valid = valid.head(max_positions)
            print(f"⚠️ Limited to top {max_positions} signals.")
            
        print(f"✅ {len(valid)} signals passed risk checks.")
        return valid
        
    def _execute_trades(self, signals: pd.DataFrame):
        """Execute trades based on signals."""
        if not self.trader.connect():
            print("❌ Trading connection failed.")
            return
            
        for _, row in signals.iterrows():
            code = row['code']
            price = row['close']
            score = row['combined_score']
            
            # Generate order via risk manager
            order = self.risk_mgr.generate_order(code, price, score)
            
            if order.get('action') == 'BUY':
                result = self.trader.place_order(
                    code=code,
                    side='BUY',
                    qty=order['shares'],
                    price=price
                )
                print(f"  📤 Order: {result}")
                
        self.trader.disconnect()
        
    def _send_report(self, signals: pd.DataFrame):
        """Generate and send daily report."""
        content = self.reporter.generate_content(signals)
        self.reporter.send_wecom(content)

if __name__ == "__main__":
    # Run pipeline (paper trading mode)
    orch = Orchestrator()
    orch.run_pipeline(execute_trades=False)
