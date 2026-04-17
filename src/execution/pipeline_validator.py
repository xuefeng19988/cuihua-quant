"""
Pipeline Validator
Runs full pipeline validation with real data.
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
from src.data.futu_sync import FutuSync
from src.data.akshare_sync import AKShareSync
from src.data.trade_logger import TradeLogger
from src.analysis.signal_gen import SignalGenerator
from src.analysis.sentiment import StockSentimentAnalyzer
from src.execution.risk_control import RiskManager
from src.monitor.performance import PerformanceAnalyzer
from src.monitor.report_generator import PerformanceReporter

class PipelineValidator:
    """
    Validates the full trading pipeline with real data.
    Checks:
    1. Data availability
    2. Signal generation
    3. Risk control
    4. Trade logging
    5. Report generation
    """
    
    def __init__(self, config_dir: str = None):
        if not config_dir:
            config_dir = os.path.join(project_root, 'config')
        self.config_dir = config_dir
        self.engine = get_db_engine()
        self.trade_logger = TradeLogger()
        
        # Load configs
        self.configs = {}
        for fname in ['stocks.yaml', 'strategies.yaml', 'risk.yaml']:
            fpath = os.path.join(config_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    self.configs[fname.replace('.yaml', '')] = yaml.safe_load(f) or {}
    
    def run_validation(self) -> Dict:
        """Run full pipeline validation."""
        results = {}
        
        print("=" * 60)
        print(f"🔍 Pipeline Validation - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        
        # 1. Check Data
        print("\n📥 Step 1: Checking Data...")
        results['data'] = self._check_data()
        
        # 2. Generate Signals
        print("\n🧠 Step 2: Generating Signals...")
        results['signals'] = self._check_signals()
        
        # 3. Risk Control
        print("\n🛡️ Step 3: Testing Risk Control...")
        results['risk'] = self._check_risk()
        
        # 4. Trade Logging
        print("\n📝 Step 4: Testing Trade Logger...")
        results['logger'] = self._check_logger()
        
        # 5. Report Generation
        print("\n📊 Step 5: Testing Report Generator...")
        results['report'] = self._check_report()
        
        # Summary
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
        """Check data availability."""
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        if not stocks:
            return {'status': 'FAIL', 'message': 'No stocks configured'}
            
        # Check how many stocks have data
        codes_str = ','.join([f"'{c}'" for c in stocks])
        query = f"SELECT code, COUNT(*) as cnt FROM stock_daily WHERE code IN ({codes_str}) GROUP BY code"
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
                'stocks_with_data': total_stocks,
                'total_records': int(total_records),
                'min_records': int(min_records),
                'max_records': int(max_records)
            }
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}
    
    def _check_signals(self) -> Dict:
        """Check signal generation."""
        stocks = self.configs.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
        try:
            gen = SignalGenerator()
            df = gen.generate_combined_signal(stocks[:10])  # Test with first 10
            if df is not None and not df.empty:
                return {
                    'status': 'PASS',
                    'message': f'{len(df)} signals generated',
                    'signal_count': len(df),
                    'avg_score': float(df['combined_score'].mean()),
                    'max_score': float(df['combined_score'].max())
                }
            return {'status': 'WARN', 'message': 'No signals generated'}
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}
    
    def _check_risk(self) -> Dict:
        """Check risk control."""
        try:
            risk = RiskManager(self.configs.get('risk', {}))
            # Test position sizing
            shares = risk.calculate_position_size(100.0, 0.5)
            # Test stop loss
            sl = risk.check_stop_loss(100.0, 90.0)
            # Test take profit
            tp = risk.check_take_profit(100.0, 125.0)
            
            if shares > 0 and sl and tp:
                return {'status': 'PASS', 'message': f'Position size: {shares}, SL/TP working'}
            return {'status': 'FAIL', 'message': 'Risk control not working'}
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}
    
    def _check_logger(self) -> Dict:
        """Check trade logging."""
        try:
            # Log a test signal
            self.trade_logger.log_signal(
                code='TEST.001', strategy='test', direction='BUY',
                score=0.5, strength=0.3, reason='Test', price=100.0
            )
            # Log a test order
            self.trade_logger.log_order(
                code='TEST.001', action='BUY', shares=100, price=100.0,
                estimated_value=10000.0, status='TEST'
            )
            # Get summary
            summary = self.trade_logger.get_summary()
            return {
                'status': 'PASS',
                'message': f'Signals: {summary["total_signals"]}, Orders: {summary["total_orders"]}'
            }
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}
    
    def _check_report(self) -> Dict:
        """Check report generation."""
        try:
            reporter = PerformanceReporter()
            daily = reporter.daily_report()
            if daily and len(daily) > 50:
                return {'status': 'PASS', 'message': f'Report generated ({len(daily)} chars)'}
            return {'status': 'WARN', 'message': 'Report empty or too short'}
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}


if __name__ == "__main__":
    validator = PipelineValidator()
    results = validator.run_validation()
