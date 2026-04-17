"""
Phase 48: Complete Trading System Integration
Full integration of all modules into a cohesive trading system.
"""

import os
import sys
import yaml
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class CompleteTradingSystem:
    """
    Complete integrated trading system.
    Combines all modules into a cohesive system.
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = self._load_config()
        self._initialize_modules()
        
    def _load_config(self) -> Dict:
        """Load system configuration."""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
        
    def _initialize_modules(self):
        """Initialize all system modules."""
        # Data layer
        from src.data.futu_sync import FutuSync
        from src.data.akshare_sync import AKShareSync
        from src.data.data_access import DataAccessLayer
        from src.data.quality_checker import DataQualityChecker
        
        self.futu_sync = FutuSync()
        self.akshare_sync = AKShareSync()
        self.data_access = DataAccessLayer()
        self.quality_checker = DataQualityChecker()
        
        # Analysis layer
        from src.analysis.signal_gen import SignalGenerator
        from src.analysis.feature_engineering import FeatureEngineer
        from src.analysis.factor_research import FactorResearcher
        from src.analysis.regime_detector import MarketRegimeDetector
        
        self.signal_gen = SignalGenerator()
        self.feature_engineer = FeatureEngineer()
        self.factor_researcher = FactorResearcher()
        self.regime_detector = MarketRegimeDetector()
        
        # Strategy layer
        from src.strategy.ensemble_manager import StrategyEnsembleManager
        from src.strategy.optimizer import GeneticOptimizer
        
        self.strategy_ensemble = StrategyEnsembleManager(['momentum', 'mean_reversion'])
        self.strategy_optimizer = GeneticOptimizer()
        
        # Execution layer
        from src.execution.risk_control import RiskManager
        from src.execution.advanced_risk import AdvancedRiskManager
        from src.execution.portfolio_optimizer import PortfolioOptimizer
        from src.execution.paper_trading_v2 import PaperTradingSimulator
        
        self.risk_mgr = RiskManager(self.config.get('risk', {}))
        self.advanced_risk = AdvancedRiskManager()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.paper_trader = PaperTradingSimulator()
        
        # Monitoring layer
        from src.monitor.performance_analyzer import StrategyPerformanceAnalyzer
        from src.monitor.live_monitor import LiveTradingMonitor
        from src.monitor.report_generator import PerformanceReporter
        
        self.performance_analyzer = StrategyPerformanceAnalyzer()
        self.live_monitor = LiveTradingMonitor()
        self.reporter = PerformanceReporter()
        
        logger.info("All modules initialized successfully")
        
    def run_daily_routine(self, date: str = None) -> Dict:
        """
        Run complete daily trading routine.
        
        Args:
            date: Trading date (YYYY-MM-DD)
            
        Returns:
            Daily routine results
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"Starting daily routine for {date}")
        results = {'date': date, 'steps': {}}
        
        try:
            # Step 1: Sync data
            logger.info("Step 1: Syncing market data...")
            self.futu_sync.connect()
            self.futu_sync.run(pool_name='watchlist', days_back=5)
            self.futu_sync.close()
            results['steps']['data_sync'] = 'success'
            
            # Step 2: Check data quality
            logger.info("Step 2: Checking data quality...")
            stocks = self.config.get('stocks', {}).get('pools', {}).get('watchlist', {}).get('stocks', [])
            for code in stocks[:5]:
                df = self.data_access.get_stock_data(code, limit=100)
                if not df.empty:
                    quality_report = self.quality_checker.run_full_check(df)
                    results['steps'][f'quality_{code}'] = quality_report['overall_score']
                    
            # Step 3: Detect market regime
            logger.info("Step 3: Detecting market regime...")
            market_df = self.data_access.get_stock_data('SH.000300', limit=200)
            if not market_df.empty:
                returns = market_df['close_price'].pct_change()
                features = self.regime_detector.prepare_features(returns)
                regime_results = self.regime_detector.fit(features)
                current_regime = regime_results['current_regime']
                regime_strategy = self.regime_detector.get_regime_strategy(current_regime)
                results['steps']['regime'] = {
                    'current_regime': current_regime,
                    'strategy': regime_strategy
                }
                
            # Step 4: Generate signals
            logger.info("Step 4: Generating trading signals...")
            signals_df = self.signal_gen.generate_combined_signal(stocks)
            if signals_df is not None and not signals_df.empty:
                results['steps']['signals'] = len(signals_df)
                
            # Step 5: Risk check
            logger.info("Step 5: Running risk checks...")
            portfolio_value = self.paper_trader.get_portfolio_value()
            risk_status = self.risk_mgr.check_portfolio_risk(portfolio_value)
            results['steps']['risk_check'] = risk_status
            
            # Step 6: Generate report
            logger.info("Step 6: Generating daily report...")
            report = self.reporter.daily_report(date)
            results['steps']['report'] = 'generated'
            
            results['status'] = 'success'
            logger.info(f"Daily routine completed successfully for {date}")
            
        except Exception as e:
            logger.error(f"Daily routine failed: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
        return results
        
    def get_system_status(self) -> Dict:
        """Get complete system status."""
        return {
            'timestamp': datetime.now().isoformat(),
            'modules': {
                'data_sync': 'initialized',
                'analysis': 'initialized',
                'strategy': 'initialized',
                'execution': 'initialized',
                'monitoring': 'initialized'
            },
            'config': self.config.get('name', 'Cuihua Quant System'),
            'version': self.config.get('version', '1.5.0')
        }
        
    def generate_full_report(self) -> str:
        """Generate complete system report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🦜 翠花量化系统 - 完整报告")
        lines.append("=" * 60)
        lines.append(f"\n📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"📊 系统版本: {self.config.get('version', '1.5.0')}")
        
        # Module status
        status = self.get_system_status()
        lines.append(f"\n🔧 模块状态")
        for module, state in status['modules'].items():
            icon = "✅" if state == 'initialized' else "❌"
            lines.append(f"  {icon} {module}: {state}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    # Initialize complete trading system
    system = CompleteTradingSystem()
    print(system.generate_full_report())
