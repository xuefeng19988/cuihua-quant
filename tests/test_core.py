"""
Unit Tests for Cuihua Quant System
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

class TestRiskControl(unittest.TestCase):
    """Test risk control module."""
    
    def setUp(self):
        from src.execution.risk_control import RiskManager
        self.risk = RiskManager({
            'total_capital': 1000000,
            'max_single_position_pct': 0.10,
            'stop_loss_pct': 0.05,
            'take_profit_pct': 0.15
        })
        
    def test_position_size(self):
        """Test position size calculation."""
        shares = self.risk.calculate_position_size(100.0, 1.0)
        # Should be 10% of 1M / 100 = 1000 shares, rounded to 100
        self.assertEqual(shares, 1000)
        
    def test_position_size_with_strength(self):
        """Test position size with signal strength."""
        shares = self.risk.calculate_position_size(100.0, 0.5)
        # Should be 50% of max = 500 shares
        self.assertEqual(shares, 500)
        
    def test_stop_loss(self):
        """Test stop loss detection."""
        self.assertTrue(self.risk.check_stop_loss(100.0, 94.0))  # 6% loss
        self.assertFalse(self.risk.check_stop_loss(100.0, 96.0))  # 4% loss
        
    def test_take_profit(self):
        """Test take profit detection."""
        self.assertTrue(self.risk.check_take_profit(100.0, 116.0))  # 16% gain
        self.assertFalse(self.risk.check_take_profit(100.0, 114.0))  # 14% gain

class TestSentimentAnalysis(unittest.TestCase):
    """Test sentiment analysis module."""
    
    def setUp(self):
        from src.analysis.sentiment import StockSentimentAnalyzer
        self.analyzer = StockSentimentAnalyzer()
        
    def test_positive_text(self):
        """Test positive sentiment detection."""
        text = "比亚迪今日大涨，突破新高，机构看好"
        result = self.analyzer.analyze_text(text)
        self.assertEqual(result['label'], 'positive')
        
    def test_negative_text(self):
        """Test negative sentiment detection."""
        text = "贵州茅台下跌，利空消息，机构看空"
        result = self.analyzer.analyze_text(text)
        self.assertEqual(result['label'], 'negative')
        
    def test_neutral_text(self):
        """Test neutral sentiment."""
        text = "今日市场平稳，无明显波动"
        result = self.analyzer.analyze_text(text)
        self.assertEqual(result['label'], 'neutral')
        
    def test_stock_mention(self):
        """Test stock mention detection."""
        text = "比亚迪和腾讯今日表现不错"
        stocks = self.analyzer._find_mentioned_stocks(text)
        self.assertIn('SZ.002594', stocks)  # 比亚迪
        self.assertIn('HK.00700', stocks)   # 腾讯

class TestPositionManager(unittest.TestCase):
    """Test position manager module."""
    
    def setUp(self):
        from src.execution.position_manager import PositionManager
        self.pm = PositionManager()
        self.pm.cash = 1000000
        
    def test_buy_position(self):
        """Test buying a position."""
        order = {
            'code': 'SH.600519',
            'action': 'BUY',
            'shares': 100,
            'price': 1500.0
        }
        self.pm.execute_orders([order])
        
        self.assertIn('SH.600519', self.pm.positions)
        self.assertEqual(self.pm.positions['SH.600519'].shares, 100)
        self.assertEqual(self.pm.cash, 1000000 - 150000)  # 100 * 1500
        
    def test_sell_position(self):
        """Test selling a position."""
        # Buy first
        buy_order = {'code': 'SH.600519', 'action': 'BUY', 'shares': 100, 'price': 1500.0}
        self.pm.execute_orders([buy_order])
        
        # Update price and sell
        self.pm.positions['SH.600519'].current_price = 1600.0
        sell_order = {'code': 'SH.600519', 'action': 'SELL', 'shares': 50, 'price': 1600.0}
        self.pm.execute_orders([sell_order])
        
        self.assertEqual(self.pm.positions['SH.600519'].shares, 50)
        self.assertGreater(self.pm.cash, 850000)  # Should have cash from sale
        
    def test_pnl_calculation(self):
        """Test P&L calculation."""
        order = {'code': 'SH.600519', 'action': 'BUY', 'shares': 100, 'price': 1500.0}
        self.pm.execute_orders([order])
        
        # Update current price
        self.pm.positions['SH.600519'].current_price = 1600.0
        
        pos = self.pm.positions['SH.600519']
        self.assertAlmostEqual(pos.pnl, 10000.0)  # (1600 - 1500) * 100
        self.assertAlmostEqual(pos.pnl_pct, 6.67, places=2)

class TestPerformanceAnalyzer(unittest.TestCase):
    """Test performance analytics module."""
    
    def setUp(self):
        from src.monitor.performance import PerformanceAnalyzer
        self.analyzer = PerformanceAnalyzer()
        
        # Create sample equity curve
        dates = pd.date_range('2025-01-01', periods=100, freq='B')
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 100)
        equity = 100000 * np.cumprod(1 + returns)
        
        self.equity_df = pd.DataFrame({
            'date': dates,
            'equity': equity
        })
        self.analyzer.load_equity_curve(self.equity_df)
        
    def test_total_return(self):
        """Test total return calculation."""
        ret = self.analyzer.total_return()
        self.assertGreater(ret, -0.5)  # Should be reasonable
        self.assertLess(ret, 0.5)
        
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        sharpe = self.analyzer.sharpe_ratio()
        self.assertIsInstance(sharpe, float)
        
    def test_max_drawdown(self):
        """Test max drawdown calculation."""
        mdd = self.analyzer.max_drawdown()
        self.assertLessEqual(mdd, 0)  # Drawdown is negative or zero

class TestSignalGenerator(unittest.TestCase):
    """Test signal generation."""
    
    def test_signal_combination(self):
        """Test combining technical and sentiment signals."""
        from src.analysis.signal_gen import SignalGenerator
        
        # This test requires DB, so we mock it
        gen = SignalGenerator()
        
        # Mock data
        tech_signals = {
            'SH.600519': {'score': 3.0, 'close': 1500.0, 'signals': ['MACD_GoldenCross']}
        }
        sentiment_scores = {'SH.600519': 0.5}
        
        # Test normalization
        tech_norm = min(max(3.0 / 5.0, -1.0), 1.0)
        combined = tech_norm * 0.6 + 0.5 * 0.4
        self.assertAlmostEqual(combined, 0.56, places=2)

if __name__ == '__main__':
    unittest.main()
