"""
Trading Pipeline
Orchestrates data → signals → risk → execution → reporting.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.analysis.signal_gen import SignalGenerator
from src.execution.risk_control import RiskManager
from src.execution.futu_trader import FutuTrader
from src.monitor.reporter import DailyReporter

class TradingPipeline:
    """
    Main trading pipeline that runs end-to-end:
    1. Load market data
    2. Generate combined signals (technical + sentiment)
    3. Apply risk filters
    4. Execute orders (optional)
    5. Generate report
    """
    
    def __init__(self, config_path: str = None):
        # Load config
        if config_path is None:
            config_path = os.path.join(project_root, 'config', 'app.yaml')
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        # Initialize components
        self.signal_gen = SignalGenerator()
        self.risk_mgr = RiskManager()
        self.trader = FutuTrader(paper_trading=True)  # Default to paper trading
        self.reporter = DailyReporter()
        
        # Pipeline state
        self.signals_df = None
        self.orders = []
        self.report_content = ""
        
    def run(self, codes: List[str] = None, news_items: List[Dict] = None, execute: bool = False):
        """
        Run the full trading pipeline.
        
        Args:
            codes: List of stock codes to analyze (uses watchlist if None)
            news_items: Optional news for sentiment analysis
            execute: If True, execute trades via Futu (paper trading by default)
        """
        print("=" * 60)
        print(f"🚀 Cuihua Quant Trading Pipeline")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        
        # Step 1: Generate Signals
        print("\n🧠 Step 1: Generating Signals...")
        self._step_generate_signals(codes, news_items)
        
        # Step 2: Risk Validation
        print("\n🛡️ Step 2: Applying Risk Filters...")
        self._step_risk_validation()
        
        # Step 3: Execute Orders (Optional)
        if execute:
            print("\n💰 Step 3: Executing Trades...")
            self._step_execute_orders()
        else:
            print("\n⏭️ Step 3: Skipped (Paper Mode)")
            
        # Step 4: Generate Report
        print("\n📊 Step 4: Generating Report...")
        self._step_generate_report()
        
        print("\n✅ Pipeline Completed.")
        return self.signals_df
        
    def _step_generate_signals(self, codes, news_items):
        """Generate combined signals."""
        if codes is None:
            # Load from config
            stocks_cfg = os.path.join(project_root, 'config', 'stocks.yaml')
            if os.path.exists(stocks_cfg):
                with open(stocks_cfg, 'r') as f:
                    cfg = yaml.safe_load(f)
                codes = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
                
        if not codes:
            print("⚠️ No stock codes provided.")
            return
            
        self.signals_df = self.signal_gen.generate_combined_signal(codes, news_items)
        
        if self.signals_df is not None and not self.signals_df.empty:
            print(f"✅ Generated signals for {len(self.signals_df)} stocks.")
            print("\n📈 Top 5 Signals:")
            for _, row in self.signals_df.head(5).iterrows():
                print(f"  #{row['rank']} {row['code']}: Score {row['combined_score']:.3f}")
        else:
            print("⚠️ No signals generated.")
            
    def _step_risk_validation(self):
        """Apply risk filters to signals."""
        if self.signals_df is None or self.signals_df.empty:
            return
            
        # Filter out negative scores
        before = len(self.signals_df)
        self.signals_df = self.signals_df[self.signals_df['combined_score'] > 0].copy()
        after = len(self.signals_df)
        
        print(f"  Filtered: {before} → {after} signals (removed negative scores)")
        
        # Check portfolio drawdown
        risk_status = self.risk_mgr.get_risk_status()
        if risk_status['trading_halted']:
            print(f"🚨 Trading HALTED: {risk_status['drawdown_pct']:.1f}% drawdown")
            self.signals_df = pd.DataFrame()  # Clear signals
            return
            
        # Limit max positions
        max_pos = self.risk_mgr.max_position_count
        if len(self.signals_df) > max_pos:
            self.signals_df = self.signals_df.head(max_pos)
            print(f"  Limited to top {max_pos} positions")
            
        print(f"✅ {len(self.signals_df)} signals passed risk checks.")
        
    def _step_execute_orders(self):
        """Execute trades for top signals."""
        if self.signals_df is None or self.signals_df.empty:
            print("  No signals to execute.")
            return
            
        if not self.trader.connect():
            print("❌ Failed to connect to Futu.")
            return
            
        for _, row in self.signals_df.head(5).iterrows():
            code = row['code']
            price = row['close']
            score = row['combined_score']
            
            # Generate order via risk manager
            order = self.risk_mgr.generate_order(code, price, score)
            
            if not order.get('rejected'):
                result = self.trader.execute_signal({
                    'code': code,
                    'action': 'BUY',
                    'shares': order['shares'],
                    'price': price
                })
                self.orders.append(result)
                print(f"  📤 Order: {result.get('success', False)} - {code}")
            else:
                print(f"  ⛔ Rejected: {code} - {order.get('reason')}")
                
        self.trader.disconnect()
        print(f"✅ Executed {len(self.orders)} orders.")
        
    def _step_generate_report(self):
        """Generate and send daily report."""
        if self.signals_df is None or self.signals_df.empty:
            self.report_content = "⚠️ No trading signals generated today."
        else:
            self.report_content = self.reporter.generate_content(self.signals_df)
            
        # Print report summary
        print("\n" + self.report_content[:500] + "...")
        
        # Send to WeCom
        self.reporter.send_wecom(self.report_content)

if __name__ == "__main__":
    # Run pipeline
    pipeline = TradingPipeline()
    pipeline.run(execute=False)  # Paper mode
