"""
Extended unit tests for Phase 16-21 modules.
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

class TestCoreExceptions(unittest.TestCase):
    """Test core exception classes."""
    
    def test_cuihua_quant_error(self):
        from src.core.exceptions import CuihuaQuantError
        err = CuihuaQuantError("Test error", code="TEST")
        self.assertEqual(err.message, "Test error")
        self.assertEqual(err.code, "TEST")
        
    def test_data_error(self):
        from src.core.exceptions import DataError
        err = DataError("Fetch failed", source="futu")
        self.assertEqual(err.code, "DATA_ERROR")
        self.assertEqual(err.details["source"], "futu")
        
    def test_config_error(self):
        from src.core.exceptions import ConfigError
        err = ConfigError("Invalid value", key="risk.stop_loss")
        self.assertEqual(err.code, "CONFIG_ERROR")
        
    def test_trading_error(self):
        from src.core.exceptions import TradingError
        err = TradingError("Order failed", order_id="123")
        self.assertEqual(err.code, "TRADING_ERROR")

class TestCoreTypes(unittest.TestCase):
    """Test core type definitions."""
    
    def test_market_type(self):
        from src.core.types import MarketType
        self.assertEqual(MarketType.A_SHARE.value, "A_SHARE")
        self.assertEqual(MarketType.HK_SHARE.value, "HK_SHARE")
        
    def test_signal_direction(self):
        from src.core.types import SignalDirection
        self.assertEqual(SignalDirection.BUY.value, "BUY")
        
    def test_order_status(self):
        from src.core.types import OrderStatus
        self.assertEqual(OrderStatus.FILLED.value, "FILLED")
        
    def test_ohlcv_dataclass(self):
        from src.core.types import OHLCV
        ohlcv = OHLCV(date=datetime.now(), open=100, high=105, low=95, close=102, volume=1e6)
        self.assertEqual(ohlcv.close, 102)

class TestConfigValidator(unittest.TestCase):
    """Test configuration validator."""
    
    def test_risk_schema(self):
        from src.core.config_validator import ConfigValidator
        validator = ConfigValidator()
        errors = validator.validate("risk", {
            "total_capital": 1000000,
            "max_single_position_pct": 0.10,
            "stop_loss_pct": 0.08,
            "take_profit_pct": 0.20,
            "max_daily_loss_pct": 0.03,
            "max_drawdown_pct": 0.15,
            "max_position_count": 10,
        })
        self.assertEqual(errors, [])
        
    def test_invalid_config(self):
        from src.core.config_validator import ConfigValidator
        validator = ConfigValidator()
        errors = validator.validate("risk", {
            "total_capital": -100,  # Invalid
        })
        self.assertTrue(len(errors) > 0)

class TestDIContainer(unittest.TestCase):
    """Test dependency injection container."""
    
    def test_singleton_registration(self):
        from src.core.di_container import DIContainer
        container = DIContainer()
        container.register_singleton("test_service", {"key": "value"})
        result = container.resolve("test_service")
        self.assertEqual(result, {"key": "value"})
        
    def test_transient_registration(self):
        from src.core.di_container import DIContainer
        container = DIContainer()
        container.register_transient("counter", lambda c: {"count": 0})
        r1 = container.resolve("counter")
        r2 = container.resolve("counter")
        self.assertIsNot(r1, r2)
        
    def test_has_service(self):
        from src.core.di_container import DIContainer
        container = DIContainer()
        self.assertFalse(container.has("nonexistent"))

class TestAsyncUtils(unittest.TestCase):
    """Test async processing utilities."""
    
    def test_run_parallel(self):
        from src.core.async_utils import AsyncProcessor
        processor = AsyncProcessor(max_workers=2)
        
        def square(x):
            return x * x
            
        results = processor.run_parallel(square, [1, 2, 3, 4, 5])
        self.assertEqual(results[1], 1)
        self.assertEqual(results[5], 25)
        
    def test_run_batch(self):
        from src.core.async_utils import AsyncProcessor
        processor = AsyncProcessor(max_workers=2)
        
        results = processor.run_batch([lambda: 1, lambda: 2, lambda: 3])
        self.assertEqual(results, [1, 2, 3])

class TestMockDataGenerator(unittest.TestCase):
    """Test mock data generator."""
    
    def test_generate_ohlcv(self):
        from tests.mock_data import MockDataGenerator
        df = MockDataGenerator.generate_ohlcv("SH.600519", days=100)
        self.assertEqual(len(df), 100)
        self.assertIn("close_price", df.columns)
        self.assertIn("volume", df.columns)
        
    def test_generate_portfolio(self):
        from tests.mock_data import MockDataGenerator
        df = MockDataGenerator.generate_portfolio(1000000, days=30)
        self.assertEqual(len(df), 30)
        self.assertIn("portfolio_value", df.columns)
        
    def test_generate_trades(self):
        from tests.mock_data import MockDataGenerator
        df = MockDataGenerator.generate_trades(count=50)
        self.assertEqual(len(df), 50)
        self.assertIn("pnl", df.columns)
        
    def test_generate_signals(self):
        from tests.mock_data import MockDataGenerator
        df = MockDataGenerator.generate_signals(["SH.600519", "SZ.002594"], count=5)
        self.assertFalse(df.empty)
        self.assertIn("combined_score", df.columns)

class TestAuditLogger(unittest.TestCase):
    """Test audit logger."""
    
    def test_log_entry(self):
        from src.core.audit_logger import AuditLogger
        logger = AuditLogger()
        logger.log("TEST_ACTION", "test_resource", {"key": "value"})
        self.assertEqual(len(logger.entries), 1)
        self.assertEqual(logger.entries[0].action, "TEST_ACTION")
        
    def test_query(self):
        from src.core.audit_logger import AuditLogger
        logger = AuditLogger()
        logger.log("ACTION_1", "resource_1", {})
        logger.log("ACTION_2", "resource_2", {})
        results = logger.query(action="ACTION_1")
        self.assertEqual(len(results), 1)

class TestCLIUtils(unittest.TestCase):
    """Test CLI utilities."""
    
    def test_progress_bar(self):
        from src.core.cli_utils import ProgressBar
        bar = ProgressBar(10, "Test")
        bar.update(5)
        self.assertEqual(bar.current, 5)
        bar.complete()
        
    def test_colors(self):
        from src.core.cli_utils import Colors
        self.assertIn("RESET", dir(Colors))

class TestPerformanceDashboard(unittest.TestCase):
    """Test performance dashboard."""
    
    def test_dashboard_generation(self):
        from src.monitor.performance import PerformanceDashboard
        dashboard = PerformanceDashboard()
        report = dashboard.generate_dashboard()
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 50)

class TestRiskAlert(unittest.TestCase):
    """Test risk alert module."""
    
    def setUp(self):
        from src.monitor.risk_alert import RiskAlertMonitor
        self.monitor = RiskAlertMonitor()
        
    def test_stop_loss_detection(self):
        self.monitor.set_positions({
            "TEST.001": {"avg_cost": 100.0, "shares": 100}
        })
        alerts = self.monitor.check_positions({"TEST.001": 90.0})
        self.assertTrue(len(alerts) > 0)

class TestMetricsCollector(unittest.TestCase):
    """Test metrics collector."""
    
    def test_collect_system_metrics(self):
        from src.monitor.metrics import MetricsCollector
        collector = MetricsCollector()
        metrics = collector.collect_system_metrics()
        self.assertIn("cpu_percent", metrics)
        self.assertIn("memory_percent", metrics)

class TestOptionsAnalyzer(unittest.TestCase):
    """Test options analyzer."""
    
    def test_black_scholes(self):
        from src.strategy.options_strategy import OptionsAnalyzer
        analyzer = OptionsAnalyzer()
        result = analyzer.black_scholes(S=100, K=100, T=30/365, r=0.03, sigma=0.2)
        self.assertIn("price", result)
        self.assertIn("delta", result)
        self.assertGreater(result["price"], 0)

class TestAlpha101(unittest.TestCase):
    """Test Alpha101 factors."""
    
    def test_helper_functions(self):
        from src.analysis.alpha101 import Alpha101Factors
        factors = Alpha101Factors()
        
        import pandas as pd
        series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        ranked = factors.ts_rank(series, 5)
        self.assertEqual(len(ranked), 10)

class TestFamaFrench(unittest.TestCase):
    """Test Fama-French model."""
    
    def test_model_initialization(self):
        from src.analysis.fama_french import FamaFrenchModel
        model = FamaFrenchModel()
        self.assertIsNotNone(model)

class TestPluginManager(unittest.TestCase):
    """Test plugin manager."""
    
    def test_plugin_initialization(self):
        from src.plugins.manager import PluginManager
        manager = PluginManager()
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.data_sources), 0)
        self.assertEqual(len(manager.strategies), 0)

if __name__ == "__main__":
    unittest.main()
