"""
Phase 275: 核心模块单元测试
测试 response_helpers, stock_scorer, advanced_cache, batch_scorer
"""

import os
import sys
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)


class TestResponseHelpers(unittest.TestCase):
    """测试统一响应辅助函数"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_ok_basic(self):
        from src.web.response_helpers import ok
        resp = ok()
        data = resp.get_json()
        self.assertEqual(data['code'], 200)

    def test_ok_with_data(self):
        from src.web.response_helpers import ok
        resp = ok(data={'key': 'value'})
        data = resp.get_json()
        self.assertEqual(data['data']['key'], 'value')

    def test_error_basic(self):
        from src.web.response_helpers import error
        resp = error(message='test', code=500)
        data = resp.get_json()
        self.assertEqual(data['code'], 500)

    def test_not_found(self):
        from src.web.response_helpers import not_found
        resp = not_found()
        data = resp.get_json()
        self.assertEqual(data['code'], 404)

    def test_bad_request(self):
        from src.web.response_helpers import bad_request
        resp = bad_request()
        data = resp.get_json()
        self.assertEqual(data['code'], 400)


class TestStockScorer(unittest.TestCase):
    """测试股票评分器"""

    def test_scorer_exists(self):
        from src.web.modules.stock_scorer import StockScorer
        scorer = StockScorer()
        self.assertIsNotNone(scorer)

    def test_calculate_score(self):
        from src.web.modules.stock_scorer import StockScorer
        scorer = StockScorer()
        data = {
            'price': 100.0, 'ma5': 105.0, 'ma20': 95.0, 'ma60': 90.0,
            'volume_ratio': 1.5, 'turnover_rate': 3.0, 'change_pct': 2.0,
            'week52_high': 120.0, 'week52_low': 80.0,
            'pe_ratio': 15.0, 'pb_ratio': 2.0, 'roe': 15.0,
            'revenue_growth': 20.0, 'profit_growth': 25.0, 'debt_ratio': 40.0,
        }
        result = scorer.calculate_score(data)
        self.assertIsNotNone(result)

    def test_score_range(self):
        from src.web.modules.stock_scorer import StockScorer
        scorer = StockScorer()
        data = {
            'price': 100.0, 'ma5': 105.0, 'ma20': 95.0, 'ma60': 90.0,
            'volume_ratio': 1.5, 'turnover_rate': 3.0, 'change_pct': 2.0,
            'week52_high': 120.0, 'week52_low': 80.0,
            'pe_ratio': 15.0, 'pb_ratio': 2.0, 'roe': 15.0,
            'revenue_growth': 20.0, 'profit_growth': 25.0, 'debt_ratio': 40.0,
        }
        score = scorer.calculate_score(data)
        total = score.get('total', score.get('score', 50))
        self.assertGreaterEqual(total, 0)
        self.assertLessEqual(total, 100)

    def test_grade(self):
        from src.web.modules.stock_scorer import StockScorer
        grade = StockScorer.get_grade(90)
        self.assertIsNotNone(grade)


class TestAdvancedCache(unittest.TestCase):
    """测试高级缓存"""

    def test_cache_create(self):
        from src.web.modules.cache_manager import AdvancedCache
        cache = AdvancedCache(max_items=100, max_memory_mb=64)
        self.assertIsNotNone(cache)

    def test_basic_set_get(self):
        from src.web.modules.cache_manager import AdvancedCache
        cache = AdvancedCache(max_items=10, max_memory_mb=16)
        cache.set('key1', 'value1')
        val = cache.get('key1')
        self.assertEqual(val, 'value1')

    def test_cache_miss(self):
        from src.web.modules.cache_manager import AdvancedCache
        cache = AdvancedCache(max_items=10, max_memory_mb=16)
        self.assertIsNone(cache.get('no_such_key'))

    def test_clear(self):
        from src.web.modules.cache_manager import AdvancedCache
        cache = AdvancedCache(max_items=10, max_memory_mb=16)
        cache.set('x', 1)
        cache.set('y', 2)
        cache.clear()
        self.assertIsNone(cache.get('x'))

    def test_stats(self):
        from src.web.modules.cache_manager import AdvancedCache
        cache = AdvancedCache(max_items=100, max_memory_mb=64)
        cache.set('k1', 'v1')
        cache.get('k1')
        cache.get('missing')
        s = cache.stats
        self.assertGreaterEqual(s.hits, 1)
        self.assertGreaterEqual(s.misses, 1)

    def test_to_dict(self):
        from src.web.modules.cache_manager import AdvancedCache
        cache = AdvancedCache(max_items=50, max_memory_mb=32)
        cache.set('a', 1)
        result = cache.to_dict()
        self.assertIsInstance(result, dict)


class TestBatchScorer(unittest.TestCase):
    """测试批量评分函数"""

    def test_batch_function_exists(self):
        from src.web.modules.batch_scorer import batch_build_score_data
        self.assertIsNotNone(batch_build_score_data)

    def test_compute_indicators(self):
        from src.web.modules.batch_scorer import _compute_indicators
        closes = [100, 102, 104, 103, 105, 107, 106, 108, 110, 109]
        result = _compute_indicators(closes)
        self.assertIsNotNone(result)

    def test_build_score(self):
        from src.web.modules.batch_scorer import _build_score_from_indicators
        indicators = {
            'price': 100.0, 'change': 2.0, 'volume': 1000000,
            'ma5': 105.0, 'ma20': 95.0, 'ma60': 90.0,
            'volume_ratio': 1.5, 'turnover_rate': 3.0,
            'pe': 15.0, 'pb': 2.0, 'roe': 15.0,
            'rsi': 50.0, 'macd': 0.5,
            'week52_high': 120.0, 'week52_low': 80.0,
        }
        result = _build_score_from_indicators(indicators)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
