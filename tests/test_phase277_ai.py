"""
Phase 277: AI 大模型模块测试
"""

import os
import sys
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)


class TestAIEndpoints(unittest.TestCase):
    """测试 AI API 端点"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        from src.web.modules.ai_service import ai_bp
        self.app.register_blueprint(ai_bp)
        self.client = self.app.test_client()

    def test_status_endpoint(self):
        """GET /api/ai/status"""
        resp = self.client.get('/api/ai/status')
        data = resp.get_json()
        self.assertEqual(data['code'], 200)
        self.assertIn('available', data['data'])

    def test_chat_no_api_key(self):
        """未配置 API Key 时问答返回错误"""
        resp = self.client.post('/api/ai/chat', json={'question': 'test'})
        data = resp.get_json()
        self.assertIn(data['code'], [400, 500])

    def test_analyze_stock_missing_code(self):
        """分析股票缺少代码"""
        resp = self.client.post('/api/ai/analyze-stock', json={'name': 'test'})
        data = resp.get_json()
        self.assertIn(data['code'], [400, 500])

    def test_generate_report_missing_context(self):
        """生成研报缺少上下文"""
        resp = self.client.post('/api/ai/generate-report', json={})
        data = resp.get_json()
        self.assertIn(data['code'], [400, 500])

    def test_market_summary_missing_context(self):
        """市场总结缺少数据"""
        resp = self.client.post('/api/ai/market-summary', json={})
        data = resp.get_json()
        self.assertIn(data['code'], [400, 500])

    def test_history_endpoint(self):
        """GET /api/ai/history"""
        resp = self.client.get('/api/ai/history')
        data = resp.get_json()
        self.assertEqual(data['code'], 200)
        self.assertIn('history', data['data'])

    def test_clear_history(self):
        """POST /api/ai/history/clear"""
        resp = self.client.post('/api/ai/history/clear')
        data = resp.get_json()
        self.assertEqual(data['code'], 200)


class TestLLMEngine(unittest.TestCase):
    """测试 LLM 引擎核心"""

    def test_engine_import(self):
        from src.ai.llm_engine import LLMEngine, LLMProvider
        self.assertIsNotNone(LLMEngine)
        self.assertIsNotNone(LLMProvider)

    def test_engine_no_api_key(self):
        from src.ai.llm_engine import LLMEngine
        engine = LLMEngine()
        self.assertFalse(engine.is_available())

    def test_engine_config(self):
        from src.ai.llm_engine import LLMEngine
        engine = LLMEngine()
        config = engine.get_config()
        self.assertFalse(config['available'])
        self.assertEqual(config['model'], 'none')

    def test_engine_get_singleton(self):
        from src.ai.llm_engine import get_llm_engine
        engine = get_llm_engine()
        self.assertIsNotNone(engine)
        self.assertIsInstance(engine, type(get_llm_engine()))

    def test_engine_history(self):
        from src.ai.llm_engine import LLMEngine
        engine = LLMEngine()
        self.assertEqual(len(engine.history), 0)
        engine.clear_history()
        self.assertEqual(len(engine.history), 0)

    def test_prompt_templates(self):
        from src.ai.llm_engine import LLMEngine
        self.assertIn('{code}', LLMEngine.PROMPT_STOCK_ANALYSIS)
        self.assertIn('{context}', LLMEngine.PROMPT_REPORT_GENERATE)
        self.assertIn('{context}', LLMEngine.PROMPT_MARKET_SUMMARY)


if __name__ == '__main__':
    unittest.main(verbosity=2)
