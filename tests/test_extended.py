"""
Extended Unit Tests for Cuihua Quant System
Tests for Phase 4-7 modules.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

class TestPipelineValidator(unittest.TestCase):
    """Test pipeline validation module."""
    
    def test_validator_initialization(self):
        """Test validator can be initialized."""
        from src.execution.pipeline import PipelineValidator
        validator = PipelineValidator()
        self.assertIsNotNone(validator)
        self.assertIsNotNone(validator.engine)
        
    def test_data_check(self):
        """Test data availability check."""
        from src.execution.pipeline import PipelineValidator
        validator = PipelineValidator()
        result = validator._check_data()
        self.assertIn('status', result)
        
class TestPerformanceDashboard(unittest.TestCase):
    """Test performance dashboard."""
    
    def test_dashboard_generation(self):
        """Test dashboard can be generated."""
        from src.monitor.performance import PerformanceDashboard
        dashboard = PerformanceDashboard()
        report = dashboard.generate_dashboard()
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 50)
        
class TestPaperTrading(unittest.TestCase):
    """Test paper trading module."""
    
    def test_paper_trader_initialization(self):
        """Test paper trader can be initialized."""
        from src.execution.paper_trading import PaperTrader
        trader = PaperTrader(initial_capital=500000)
        self.assertEqual(trader.initial_capital, 500000)
        self.assertEqual(trader.cash, 500000)
        
class TestRiskAlert(unittest.TestCase):
    """Test risk alert module."""
    
    def setUp(self):
        from src.monitor.risk_alert import RiskAlertMonitor
        self.monitor = RiskAlertMonitor()
        
    def test_stop_loss_detection(self):
        """Test stop-loss trigger detection."""
        self.monitor.set_positions({
            'TEST.001': {'avg_cost': 100.0, 'shares': 100}
        })
        alerts = self.monitor.check_positions({'TEST.001': 90.0})  # -10%
        self.assertTrue(len(alerts) > 0)
        self.assertEqual(alerts[0]['type'], 'STOP_LOSS')
        
    def test_take_profit_detection(self):
        """Test take-profit trigger detection."""
        self.monitor.set_positions({
            'TEST.001': {'avg_cost': 100.0, 'shares': 100}
        })
        alerts = self.monitor.check_positions({'TEST.001': 125.0})  # +25%
        self.assertTrue(len(alerts) > 0)
        self.assertEqual(alerts[0]['type'], 'TAKE_PROFIT')
        
class TestExtendedSentiment(unittest.TestCase):
    """Test extended sentiment analysis."""
    
    def test_analyzer_initialization(self):
        """Test extended sentiment analyzer."""
        from src.analysis.extended_sentiment import ExtendedSentimentAnalyzer
        analyzer = ExtendedSentimentAnalyzer()
        self.assertIsNotNone(analyzer)
        self.assertGreater(len(analyzer.stock_keywords), 20)
        
class TestFeatureEngineering(unittest.TestCase):
    """Test feature engineering."""
    
    def test_feature_names(self):
        """Test feature names list."""
        from src.analysis.feature_engineering import FeatureEngineer
        fe = FeatureEngineer()
        names = fe.get_feature_names()
        self.assertIsInstance(names, list)
        self.assertGreater(len(names), 10)
        
class TestParamOptimizer(unittest.TestCase):
    """Test parameter optimizer."""
    
    def test_multi_factor_optimization(self):
        """Test multi-factor weight optimization."""
        from src.strategy.param_optimizer import ParameterOptimizer
        optimizer = ParameterOptimizer()
        result = optimizer.optimize_multi_factor()
        self.assertIn('weights', result)
        weights = result['weights']
        total = sum(weights.values())
        self.assertAlmostEqual(total, 1.0, places=2)
        
class TestAutoTuner(unittest.TestCase):
    """Test auto parameter tuner."""
    
    def test_recommendations(self):
        """Test recommendation generation."""
        from src.strategy.auto_tuner import AutoParamTuner
        tuner = AutoParamTuner()
        import pandas as pd
        df = pd.DataFrame({
            'code': ['TEST'], 'fast': [5], 'slow': [20],
            'return_pct': [0.1], 'sharpe': [1.5],
            'max_drawdown': [0.05], 'total_trades': [10], 'win_rate': [0.6]
        })
        recs = tuner.generate_recommendations(df)
        self.assertIn('best_return', recs)
        self.assertIn('best_sharpe', recs)
        
class TestConfigManager(unittest.TestCase):
    """Test configuration manager."""
    
    def test_config_loading(self):
        """Test config manager loads configs."""
        from src.config.manager import ConfigManager
        config = ConfigManager()
        self.assertTrue(config.configs)
        
    def test_config_get(self):
        """Test config value retrieval."""
        from src.config.manager import ConfigManager
        config = ConfigManager()
        # Should not raise
        _ = config.get('app', {})
        
    def test_config_validation(self):
        """Test config validation."""
        from src.config.manager import ConfigManager
        config = ConfigManager()
        errors = config.validate()
        self.assertIsInstance(errors, dict)
        
class TestSystemMonitor(unittest.TestCase):
    """Test system monitor."""
    
    def test_health_report(self):
        """Test health report generation."""
        from src.monitor.system_monitor import SystemMonitor
        monitor = SystemMonitor()
        report = monitor.generate_health_report()
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 50)
        
class TestUSStocks(unittest.TestCase):
    """Test US stock fetcher."""
    
    def test_fetcher_initialization(self):
        """Test US stock fetcher can be initialized."""
        from src.data.us_stocks import USStockFetcher
        fetcher = USStockFetcher()
        self.assertIsNotNone(fetcher)
        
class TestCache(unittest.TestCase):
    """Test cache manager."""
    
    def test_memory_cache(self):
        """Test memory cache operations."""
        from src.data.cache import CacheManager
        cache = CacheManager(use_redis=False)
        
        cache.set('test_key', {'value': 123}, ttl_seconds=60)
        result = cache.get('test_key')
        self.assertEqual(result['value'], 123)
        
        cache.delete('test_key')
        result = cache.get('test_key')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
