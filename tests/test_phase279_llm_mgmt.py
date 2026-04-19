"""
Phase 279: LLM 管理模块测试
"""

import os
import sys
import unittest
import tempfile

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)


class TestLLMManager(unittest.TestCase):
    """测试 LLM 管理器"""

    def setUp(self):
        from src.ai.llm_manager import LLMManager
        self.tmp = tempfile.mktemp(suffix='.json')
        self.mgr = LLMManager(config_path=self.tmp)

    def tearDown(self):
        if os.path.exists(self.tmp):
            os.unlink(self.tmp)

    def test_init_presets(self):
        """初始化后应有预设配置"""
        self.assertGreater(len(self.mgr.configs), 0)
        self.assertIn('bailian', self.mgr.configs)

    def test_add_config(self):
        """添加配置"""
        result = self.mgr.add_config('my_qwen', 'bailian', 'sk-test123', 'qwen-max')
        self.assertTrue(result['success'])
        self.assertIn('my_qwen', self.mgr.configs)

    def test_add_duplicate(self):
        """重复添加应失败"""
        self.mgr.add_config('dup', 'openai', 'sk-test', 'gpt-3.5-turbo')
        result = self.mgr.add_config('dup', 'openai', 'sk-test2', 'gpt-4')
        self.assertFalse(result['success'])

    def test_list_configs(self):
        """列出配置"""
        configs = self.mgr.list_configs()
        self.assertIsInstance(configs, list)
        self.assertGreater(len(configs), 0)

    def test_update_config(self):
        """更新配置"""
        self.mgr.add_config('upd', 'bailian', 'sk-old', 'qwen-turbo')
        result = self.mgr.update_config('upd', api_key='sk-new', model='qwen-plus')
        self.assertTrue(result['success'])
        cfg = self.mgr.get_config('upd')
        self.assertEqual(cfg['model'], 'qwen-plus')

    def test_switch_config(self):
        """切换配置"""
        self.mgr.add_config('a', 'openai', 'sk-a', 'gpt-3.5-turbo')
        self.mgr.add_config('b', 'bailian', 'sk-b', 'qwen-plus')
        result = self.mgr.switch_config('b')
        self.assertTrue(result['success'])
        self.assertEqual(result['new'], 'b')
        self.assertEqual(self.mgr.active_config, 'b')

    def test_switch_nonexistent(self):
        """切换不存在的配置"""
        result = self.mgr.switch_config('no_such')
        self.assertFalse(result['success'])

    def test_delete_config(self):
        """删除配置"""
        self.mgr.add_config('del', 'openai', 'sk-del', 'gpt-3.5-turbo')
        result = self.mgr.delete_config('del')
        self.assertTrue(result['success'])
        self.assertNotIn('del', self.mgr.configs)

    def test_get_active(self):
        """获取活动配置"""
        active = self.mgr.get_active_config()
        self.assertIsNotNone(active)

    def test_record_usage(self):
        """记录使用量"""
        self.mgr.add_config('usage', 'bailian', 'sk-u', 'qwen-plus')
        self.mgr.record_usage('usage', 1000)
        cfg = self.mgr.get_config('usage')
        self.assertEqual(cfg['usage_count'], 1)
        self.assertEqual(cfg['total_tokens'], 1000)

    def test_stats(self):
        """统计信息"""
        stats = self.mgr.get_stats()
        self.assertIn('total_configs', stats)
        self.assertIn('active_config', stats)
        self.assertGreater(stats['total_configs'], 0)


class TestLLMManagementAPI(unittest.TestCase):
    """测试 LLM 管理 API 端点"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        from src.web.modules.llm_mgmt import llm_mgmt_bp
        self.app.register_blueprint(llm_mgmt_bp)
        self.client = self.app.test_client()

    def test_list_configs(self):
        """GET /api/llm/configs"""
        resp = self.client.get('/api/llm/configs')
        data = resp.get_json()
        self.assertEqual(data['code'], 200)
        self.assertIn('configs', data['data'])

    def test_providers(self):
        """GET /api/llm/providers"""
        resp = self.client.get('/api/llm/providers')
        data = resp.get_json()
        self.assertEqual(data['code'], 200)
        self.assertIn('bailian', data['data']['providers'])

    def test_stats(self):
        """GET /api/llm/stats"""
        resp = self.client.get('/api/llm/stats')
        data = resp.get_json()
        self.assertEqual(data['code'], 200)

    def test_add_missing_name(self):
        """添加配置缺少名称"""
        resp = self.client.post('/api/llm/configs', json={'provider': 'bailian'})
        data = resp.get_json()
        self.assertEqual(data['code'], 400)

    def test_add_missing_api_key(self):
        """添加配置缺少 API Key"""
        resp = self.client.post('/api/llm/configs', json={'name': 'test', 'provider': 'bailian'})
        data = resp.get_json()
        self.assertEqual(data['code'], 400)

    def test_delete_nonexistent(self):
        """删除不存在的配置"""
        resp = self.client.delete('/api/llm/configs/no_such')
        data = resp.get_json()
        self.assertEqual(data['code'], 500)

    def test_switch_nonexistent(self):
        """切换不存在的配置"""
        resp = self.client.post('/api/llm/switch/no_such')
        data = resp.get_json()
        self.assertEqual(data['code'], 500)


if __name__ == '__main__':
    unittest.main(verbosity=2)
