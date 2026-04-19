"""
Phase 276: 实盘交易模块测试
"""

import os
import sys
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)


class TestLiveTradingModule(unittest.TestCase):
    """测试实盘交易模块"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        from src.web.modules.live_trading import live_trading_bp
        self.app.register_blueprint(live_trading_bp)
        self.client = self.app.test_client()

    def test_status_endpoint(self):
        """GET /api/trading/status"""
        resp = self.client.get('/api/trading/status')
        data = resp.get_json()
        self.assertEqual(data['code'], 200)
        self.assertIn('connected', data['data'])

    def test_status_not_connected(self):
        """未连接时下单返回错误"""
        resp = self.client.post('/api/trading/order', json={'code': 'SH.600519', 'side': 'BUY', 'qty': 100})
        data = resp.get_json()
        self.assertEqual(data['code'], 400)
        self.assertIn('未连接', data['message'])

    def test_place_order_missing_code(self):
        """下单缺少股票代码"""
        # 先模拟已连接状态
        import src.web.modules.live_trading as lt
        lt._trader_state['connected'] = True
        resp = self.client.post('/api/trading/order', json={'side': 'BUY', 'qty': 100})
        data = resp.get_json()
        self.assertEqual(data['code'], 400)
        lt._trader_state['connected'] = False

    def test_place_order_invalid_qty(self):
        """下单数量无效"""
        import src.web.modules.live_trading as lt
        lt._trader_state['connected'] = True
        resp = self.client.post('/api/trading/order', json={'code': 'SH.600519', 'side': 'BUY', 'qty': 0})
        data = resp.get_json()
        self.assertEqual(data['code'], 400)
        lt._trader_state['connected'] = False

    def test_place_order_invalid_side(self):
        """下单方向无效"""
        import src.web.modules.live_trading as lt
        lt._trader_state['connected'] = True
        resp = self.client.post('/api/trading/order', json={'code': 'SH.600519', 'side': 'HOLD', 'qty': 100})
        data = resp.get_json()
        self.assertEqual(data['code'], 400)
        lt._trader_state['connected'] = False

    def test_positions_not_connected(self):
        """未连接时查询持仓"""
        resp = self.client.get('/api/trading/positions')
        data = resp.get_json()
        self.assertEqual(data['code'], 400)

    def test_account_not_connected(self):
        """未连接时查询账户"""
        resp = self.client.get('/api/trading/account')
        data = resp.get_json()
        self.assertEqual(data['code'], 400)

    def test_order_status_not_connected(self):
        """未连接时查询订单"""
        resp = self.client.get('/api/trading/orders/123')
        data = resp.get_json()
        self.assertEqual(data['code'], 400)

    def test_signal_not_connected(self):
        """未连接时执行信号"""
        resp = self.client.post('/api/trading/signal', json={'code': 'SH.600519', 'action': 'BUY', 'shares': 100})
        data = resp.get_json()
        self.assertEqual(data['code'], 400)


class TestFutuTraderModule(unittest.TestCase):
    """测试 FutuTrader 模块 (仅验证模块可导入和结构)"""

    def test_module_import(self):
        from src.execution.futu_trader import FutuTrader
        self.assertIsNotNone(FutuTrader)

    def test_trader_instance(self):
        from src.execution.futu_trader import FutuTrader
        trader = FutuTrader(paper_trading=True)
        self.assertFalse(trader.paper_trading is None)
        self.assertEqual(trader.host, '127.0.0.1')
        self.assertEqual(trader.quote_port, 11112)
        self.assertEqual(trader.trd_port, 11113)

    def test_trader_methods(self):
        from src.execution.futu_trader import FutuTrader
        trader = FutuTrader(paper_trading=True)
        self.assertTrue(hasattr(trader, 'connect'))
        self.assertTrue(hasattr(trader, 'disconnect'))
        self.assertTrue(hasattr(trader, 'place_order'))
        self.assertTrue(hasattr(trader, 'get_positions'))
        self.assertTrue(hasattr(trader, 'get_account_info'))
        self.assertTrue(hasattr(trader, 'execute_signal'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
