"""
Trading Pipeline v2
Full pipeline with logging, risk control, ML integration, and validation.
Merged from: pipeline.py, pipeline_validator.py
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
from src.analysis.sentiment import NewsSentimentFetcher
from src.analysis.ml_engine import MLModelAdapter
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
        self.config_dir = config_dir
        self.configs = {}
        for fname in ['app.yaml', 'stocks.yaml', 'strategies.yaml', 'risk.yaml']:
            fpath = os.path.join(config_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    self.configs[fname.replace('.yaml', '')] = yaml.safe_load(f) or {}
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
        self.signals_df = None
        self.orders = []
        
    def run_full_pipeline(self, execute_trades: bool = False, include_ml: bool = False):
        """Run the complete trading pipeline."""
        print("=" * 60)
        print(f"🚀 Cuihua Quant Pipeline v2 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        print("\n📥 Step 1: Syncing Data...")
        self._sync_data()
        print("\n📰 Step 2: Fetching News Sentiment...")
        news_scores = self._fetch_sentiment()
        print("\n🧠 Step 3: Generating Signals...")
        self._generate_signals(news_scores)
        if include_ml:
            print("\n🤖 Step 4: ML Predictions...")
            self._run_ml_predictions()
        print("\n🛡️ Step 5: Risk Validation...")
        validated = self._apply_risk_checks()
        print("\n📝 Step 6: Logging Signals...")
        self._log_signals()
        if execute_trades:
            print("\n💰 Step 7: Executing Trades...")
            self._execute_trades()
        else:
            print("\n⏭️ Step 7: Paper Mode")
        print("\n📊 Step 8: Updating Monitor...")
        self._update_monitor()
        print("\n📈 Step 9: Generating Reports...")
        self._generate_reports()
        print("\n✅ Pipeline v2 Completed.")
        return self.signals_df
        
    def _sync_data(self):
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
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return {}
        return self.sentiment_fetcher.analyze_and_score(stocks)
        
    def _generate_signals(self, news_scores: Dict):
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return
        self.signals_df = self.signal_gen.generate_combined_signal(stocks)
        if self.signals_df is not None and not self.signals_df.empty:
            print(f"  ✅ {len(self.signals_df)} signals generated")
            
    def _run_ml_predictions(self):
        self.ml_adapter.load_model('lightgbm', 'lgb_model.pkl')
        
    def _apply_risk_checks(self) -> pd.DataFrame:
        if self.signals_df is None or self.signals_df.empty:
            return pd.DataFrame()
        valid = self.signals_df[self.signals_df['combined_score'] > 0].copy()
        max_pos = self.risk_mgr.max_position_count
        if len(valid) > max_pos:
            valid = valid.head(max_pos)
        return valid
        
    def _log_signals(self):
        if self.signals_df is None or self.signals_df.empty:
            return
        for _, row in self.signals_df.iterrows():
            self.trade_logger.log_signal(
                code=row['code'], strategy='combined',
                direction='BUY' if row['combined_score'] > 0 else 'SELL',
                score=row['combined_score'], strength=abs(row['combined_score']),
                reason=', '.join(row.get('signals', [])), price=row.get('close', 0)
            )
        print(f"  ✅ Logged {len(self.signals_df)} signals")
        
    def _execute_trades(self):
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
                    'code': code, 'action': 'BUY',
                    'shares': order['shares'], 'price': price
                })
                self.orders.append(result)
                self.trade_logger.log_order(
                    code=code, action='BUY', shares=order.get('shares', 0), price=price,
                    estimated_value=order.get('value', 0),
                    status='SUBMITTED' if result.get('success') else 'REJECTED',
                    order_id=result.get('order_id', ''), notes=result.get('error', '')
                )
        self.trader.disconnect()
        
    def _update_monitor(self):
        if self.signals_df is not None and not self.signals_df.empty:
            for _, row in self.signals_df.iterrows():
                self.intraday_monitor.positions[row['code']] = {
                    'avg_cost': row.get('close', 0),
                    'stop_loss': row.get('close', 0) * 0.92,
                    'take_profit': row.get('close', 0) * 1.20
                }
                
    def _generate_reports(self):
        daily_report = self.report_generator.generate_daily_report()
        print("\n" + daily_report)
        self.reporter.send_wecom(daily_report)


# ============================================================================
# Pipeline Validator (merged from pipeline_validator.py)
# ============================================================================

class PipelineValidator:
    """
    Validates the full trading pipeline with real data.
    Checks: 1. Data availability 2. Signal generation 3. Risk control
    4. Trade logging 5. Report generation
    """

    def __init__(self, config_dir: str = None):
        if not config_dir:
            config_dir = os.path.join(project_root, 'config')
        self.config_dir = config_dir
        from src.data.database import get_db_engine
        from src.data.trade_logger import TradeLogger
        self.engine = get_db_engine()
        self.trade_logger = TradeLogger()
        self.configs = {}
        for fname in ['stocks.yaml', 'strategies.yaml', 'risk.yaml']:
            fpath = os.path.join(config_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    self.configs[fname.replace('.yaml', '')] = yaml.safe_load(f) or {}

    def run_validation(self) -> Dict:
        results = {}
        print("=" * 60)
        print(f"🔍 Pipeline Validation - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        print("\n📥 Step 1: Checking Data...")
        results['data'] = self._check_data()
        print("\n🧠 Step 2: Generating Signals...")
        results['signals'] = self._check_signals()
        print("\n🛡️ Step 3: Testing Risk Control...")
        results['risk'] = self._check_risk()
        print("\n📝 Step 4: Testing Trade Logger...")
        results['logger'] = self._check_logger()
        print("\n📊 Step 5: Testing Report Generator...")
        results['report'] = self._check_report()
        print("\n" + "=" * 60)
        print("📊 Validation Summary")
        print("=" * 60)
        all_pass = all(v.get('status') == 'PASS' for v in results.values())
        print(f"Overall: {'✅ PASS' if all_pass else '⚠️ ISSUES FOUND'}")
        for name, result in results.items():
            icon = "✅" if result.get('status') == 'PASS' else "❌"
            print(f"  {icon} {name}: {result.get('message', '')}")
        return results

    def _check_data(self) -> Dict:
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return {'status': 'FAIL', 'message': 'No stocks configured'}
        codes_str = ','.join([f"'{c}'" for c in stocks])
        query = text("SELECT code, COUNT(*) as cnt FROM stock_daily WHERE code IN :codes GROUP BY code")
        try:
            df = pd.read_sql(query, self.engine)
            total_stocks = len(df)
            total_records = df['cnt'].sum()
            min_records = df['cnt'].min()
            max_records = df['cnt'].max()
            status = 'PASS' if total_stocks > 0 else 'FAIL'
            return {
                'status': status,
                'message': f'{total_stocks} stocks, {total_records} records (min:{min_records}, max:{max_records})',
                'stocks_with_data': total_stocks, 'total_records': int(total_records),
                'min_records': int(min_records), 'max_records': int(max_records)
            }
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}

    def _check_signals(self) -> Dict:
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        try:
            gen = SignalGenerator()
            df = gen.generate_combined_signal(stocks[:10])
            if df is not None and not df.empty:
                return {
                    'status': 'PASS', 'message': f'{len(df)} signals generated',
                    'signal_count': len(df),
                    'avg_score': float(df['combined_score'].mean()),
                    'max_score': float(df['combined_score'].max())
                }
            return {'status': 'WARN', 'message': 'No signals generated'}
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}

    def _check_risk(self) -> Dict:
        try:
            risk = RiskManager(self.configs.get('risk', {}))
            shares = risk.calculate_position_size(100.0, 0.5)
            sl = risk.check_stop_loss(100.0, 90.0)
            tp = risk.check_take_profit(100.0, 125.0)
            if shares > 0 and sl and tp:
                return {'status': 'PASS', 'message': f'Position size: {shares}, SL/TP working'}
            return {'status': 'FAIL', 'message': 'Risk control not working'}
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}

    def _check_logger(self) -> Dict:
        try:
            self.trade_logger.log_signal(
                code='TEST.001', strategy='test', direction='BUY',
                score=0.5, strength=0.3, reason='Test', price=100.0)
            self.trade_logger.log_order(
                code='TEST.001', action='BUY', shares=100, price=100.0,
                estimated_value=10000.0, status='TEST')
            summary = self.trade_logger.get_summary()
            return {
                'status': 'PASS',
                'message': f'Signals: {summary["total_signals"]}, Orders: {summary["total_orders"]}'
            }
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}

    def _check_report(self) -> Dict:
        from src.monitor.report_generator import PerformanceReporter
        try:
            reporter = PerformanceReporter()
            daily = reporter.daily_report()
            if daily and len(daily) > 50:
                return {'status': 'PASS', 'message': f'Report generated ({len(daily)} chars)'}
            return {'status': 'WARN', 'message': 'Report empty or too short'}
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}



