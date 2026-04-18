"""
API 端点基础测试
"""
import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestAPIHealth:
    """健康检查API测试"""
    
    def test_health_endpoint_structure(self):
        """测试健康检查接口结构"""
        # 验证API路由定义存在
        from src.web.api_server import app
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/api/health' in rules, "健康检查端点不存在"
    
    def test_api_routes_count(self):
        """测试API路由数量"""
        from src.web.api_server import app
        api_rules = [r for r in app.url_map.iter_rules() if '/api/' in r.rule]
        assert len(api_rules) >= 100, f"API路由数量不足: {len(api_rules)}"


class TestConfig:
    """配置测试"""
    
    def test_stocks_yaml_exists(self):
        """测试股票配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'stocks.yaml')
        assert os.path.exists(config_path), "stocks.yaml 不存在"
    
    def test_auth_yaml_exists(self):
        """测试认证配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'auth.yaml')
        assert os.path.exists(config_path), "auth.yaml 不存在"
    
    def test_env_file_exists(self):
        """测试环境变量文件"""
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        assert os.path.exists(env_path), ".env 不存在"
