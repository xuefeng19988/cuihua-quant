"""
Trading Pipeline v2
Full pipeline with logging, risk control, and ML integration.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from typing import List, Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.futu_sync import FutuSync
from src.data.akshare_sync import AKShareSync
from src.data.trade_logger import TradeLogger
from src.analysis.signal_gen import SignalGenerator
from src.analysis.news_sentiment import NewsSentimentFetcher
from src.analysis.ml_adapter import MLModelAdapter
from src.execution.risk_control import RiskManager
from src.execution.futu_trader import FutuTrader
from src.execution.position_manager import PositionManager
from src.monitor.reporter import DailyReporter
from src.monitor.report_generator import AutomatedReportGenerator
from src.monitor.intraday_monitor import IntradayMonitor

class TradingPipelineV2:
    """
    Full trading pipeline v2 with:
    - Data sync (Futu → AKShare fallback)
    - Signal generation (Technical + Sentiment + ML)
    - Risk management
    - Position management
    - Trade logging
    - Intraday monitoring
    - Reporting
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
        self.trade_logger = TradeLogger()
        self.signal_gen = SignalGenerator()
        self.sentiment_fetcher = NewsSentimentFetcher()
        self.ml_adapter = MLModelAdapter()
        self.risk_mgr = RiskManager(self.configs.get('risk', {}))
        self.trader = FutuTrader(paper_trading=True)
        self.position_mgr = PositionManager()
        self.reporter = DailyReporter()
        self.report_generator = AutomatedReportGenerator()
        self.intraday_monitor = IntradayMonitor()
        
        # Pipeline state
        self.signals_df = None
        self.orders = []
        
    def run_full_pipeline(self, execute_trades: bool = False, include_ml: bool = False):
        """Run the complete trading pipeline."""
        print("=" * 60)
        print(f"🚀 Cuihua Quant Pipeline v2 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        
        # Step 1: Sync Data
        print("\n📥 Step 1: Syncing Data...")
        self._sync_data()
        
        # Step 2: Fetch News Sentiment
        print("\n📰 Step 2: Fetching News Sentiment...")
        news_scores = self._fetch_sentiment()
        
        # Step 3: Generate Signals
        print("\n🧠 Step 3: Generating Signals...")
        self._generate_signals(news_scores)
        
        # Step 4: ML Predictions (Optional)
        if include_ml:
            print("\n🤖 Step 4: ML Predictions...")
            self._run_ml_predictions()
            
        # Step 5: Risk Validation
        print("\n🛡️ Step 5: Risk Validation...")
        validated = self._apply_risk_checks()
        
        # Step 6: Log Signals
        print("\n📝 Step 6: Logging Signals...")
        self._log_signals()
        
        # Step 7: Execute Trades (Optional)
        if execute_trades:
            print("\n💰 Step 7: Executing Trades...")
            self._execute_trades()
        else:
            print("\n⏭️ Step 7: Paper Mode")
            
        # Step 8: Update Monitor
        print("\n📊 Step 8: Updating Monitor...")
        self._update_monitor()
        
        # Step 9: Generate Reports
        print("\n📈 Step 9: Generating Reports...")
        self._generate_reports()
        
        print("\n✅ Pipeline v2 Completed.")
        return self.signals_df
        
    def _sync_data(self):
        """Sync market data."""
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return
            
        syncer = FutuSync()
        if syncer.connect():
            syncer.run(pool_name='watchlist', days_back=5)
            syncer.close()
        else:
            ak_syncer = AKShareSync()
            ak_syncer.run(pool_name='watchlist', days_back=5)
            
    def _fetch_sentiment(self) -> Dict:
        """Fetch news sentiment scores."""
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return {}
        return self.sentiment_fetcher.analyze_and_score(stocks)
        
    def _generate_signals(self, news_scores: Dict):
        """Generate trading signals."""
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return
            
        self.signals_df = self.signal_gen.generate_combined_signal(stocks)
        if self.signals_df is not None and not self.signals_df.empty:
            print(f"  ✅ {len(self.signals_df)} signals generated")
            
    def _run_ml_predictions(self):
        """Run ML model predictions."""
        # Load models
        self.ml_adapter.load_model('lightgbm', 'lgb_model.pkl')
        
    def _apply_risk_checks(self) -> pd.DataFrame:
        """Apply risk filters."""
        if self.signals_df is None or self.signals_df.empty:
            return pd.DataFrame()
            
        valid = self.signals_df[self.signals_df['combined_score'] > 0].copy()
        max_pos = self.risk_mgr.max_position_count
        if len(valid) > max_pos:
            valid = valid.head(max_pos)
            
        return valid
        
    def _log_signals(self):
        """Log all generated signals."""
        if self.signals_df is None or self.signals_df.empty:
            return
            
        for _, row in self.signals_df.iterrows():
            self.trade_logger.log_signal(
                code=row['code'],
                strategy='combined',
                direction='BUY' if row['combined_score'] > 0 else 'SELL',
                score=row['combined_score'],
                strength=abs(row['combined_score']),
                reason=', '.join(row.get('signals', [])),
                price=row.get('close', 0)
            )
        print(f"  ✅ Logged {len(self.signals_df)} signals")
        
    def _execute_trades(self):
        """Execute trades."""
        if self.signals_df is None or self.signals_df.empty:
            return
            
        if not self.trader.connect():
            return
            
        for _, row in self.signals_df.head(5).iterrows():
            code = row['code']
            price = row['close']
            score = row['combined_score']
            
            order = self.risk_mgr.generate_order(code, price, score)
            if not order.get('rejected'):
                result = self.trader.execute_signal({
                    'code': code,
                    'action': 'BUY',
                    'shares': order['shares'],
                    'price': price
                })
                self.orders.append(result)
                self.trade_logger.log_order(
                    code=code,
                    action='BUY',
                    shares=order.get('shares', 0),
                    price=price,
                    estimated_value=order.get('value', 0),
                    status='SUBMITTED' if result.get('success') else 'REJECTED',
                    order_id=result.get('order_id', ''),
                    notes=result.get('error', '')
                )
                
        self.trader.disconnect()
        
    def _update_monitor(self):
        """Update intraday monitor."""
        if self.signals_df is not None and not self.signals_df.empty:
            for _, row in self.signals_df.iterrows():
                self.intraday_monitor.positions[row['code']] = {
                    'avg_cost': row.get('close', 0),
                    'stop_loss': row.get('close', 0) * 0.92,
                    'take_profit': row.get('close', 0) * 1.20
                }
                
    def _generate_reports(self):
        """Generate and send reports."""
        # Daily report
        daily_report = self.report_generator.generate_daily_report()
        print("\n" + daily_report)
        self.reporter.send_wecom(daily_report)
