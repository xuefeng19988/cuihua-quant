"""
Phase 279: LLM 管理模块
支持多模型配置管理、连接测试、用量统计、模型切换
"""

import os
import json
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime


class LLMConfig:
    """单个 LLM 配置"""
    
    def __init__(self, name: str, provider: str, api_key: str, model: str, base_url: str = '', enabled: bool = True):
        self.name = name
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.enabled = enabled
        self.created_at = datetime.now().isoformat()
        self.last_used: Optional[str] = None
        self.usage_count = 0
        self.total_tokens = 0
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'provider': self.provider,
            'api_key': self.api_key[:8] + '***' if len(self.api_key) > 8 else '***',
            'api_key_full': self.api_key,  # 内部使用
            'model': self.model,
            'base_url': self.base_url,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'usage_count': self.usage_count,
            'total_tokens': self.total_tokens,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LLMConfig':
        cfg = cls(
            name=data['name'],
            provider=data['provider'],
            api_key=data.get('api_key_full', data.get('api_key', '')),
            model=data['model'],
            base_url=data.get('base_url', ''),
            enabled=data.get('enabled', True),
        )
        cfg.created_at = data.get('created_at', cfg.created_at)
        cfg.last_used = data.get('last_used')
        cfg.usage_count = data.get('usage_count', 0)
        cfg.total_tokens = data.get('total_tokens', 0)
        return cfg


class LLMManager:
    """
    LLM 管理器
    维护多个 LLM 配置，支持切换、测试、统计
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data', 'llm_configs.json'
        )
        self._lock = threading.Lock()
        self.configs: Dict[str, LLMConfig] = {}
        self.active_config: Optional[str] = None
        self._load_configs()
        
        # 如果没有配置，添加预设
        if not self.configs:
            self._init_presets()
    
    def _init_presets(self):
        """初始化预设配置"""
        from src.ai.llm_engine import PROVIDER_PRESETS
        
        for name, info in PROVIDER_PRESETS.items():
            self.configs[name] = LLMConfig(
                name=name,
                provider=name,
                api_key='',
                model=info['default_model'],
                base_url=info['base_url'],
                enabled=False,
            )
        # 默认激活 bailian
        if 'bailian' in self.configs:
            self.configs['bailian'].enabled = True
            self.active_config = 'bailian'
        self._save_configs()
    
    def _load_configs(self):
        """从文件加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for name, cfg_data in data.get('configs', {}).items():
                    self.configs[name] = LLMConfig.from_dict(cfg_data)
                self.active_config = data.get('active_config')
            except Exception:
                pass
    
    def _save_configs(self):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        data = {
            'configs': {name: cfg.to_dict() for name, cfg in self.configs.items()},
            'active_config': self.active_config,
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def list_configs(self) -> List[Dict]:
        """列出所有配置"""
        result = []
        for name, cfg in self.configs.items():
            d = cfg.to_dict()
            d['is_active'] = (name == self.active_config)
            result.append(d)
        return result
    
    def get_config(self, name: str) -> Optional[Dict]:
        """获取单个配置"""
        cfg = self.configs.get(name)
        if cfg:
            d = cfg.to_dict()
            d['is_active'] = (name == self.active_config)
            return d
        return None
    
    def add_config(self, name: str, provider: str, api_key: str, model: str, base_url: str = '') -> Dict:
        """添加新配置"""
        with self._lock:
            if name in self.configs:
                return {'success': False, 'error': f'配置 {name} 已存在'}
            
            from src.ai.llm_engine import PROVIDER_PRESETS
            preset = PROVIDER_PRESETS.get(provider)
            if preset and not base_url:
                base_url = preset['base_url']
            
            self.configs[name] = LLMConfig(name, provider, api_key, model, base_url)
            if len(self.configs) == 1:
                self.active_config = name
            self._save_configs()
            return {'success': True, 'name': name}
    
    def update_config(self, name: str, **kwargs) -> Dict:
        """更新配置"""
        with self._lock:
            cfg = self.configs.get(name)
            if not cfg:
                return {'success': False, 'error': f'配置 {name} 不存在'}
            
            if 'api_key' in kwargs:
                cfg.api_key = kwargs.pop('api_key')
            if 'model' in kwargs:
                cfg.model = kwargs.pop('model')
            if 'base_url' in kwargs:
                cfg.base_url = kwargs.pop('base_url')
            if 'enabled' in kwargs:
                cfg.enabled = kwargs.pop('enabled')
            
            self._save_configs()
            return {'success': True}
    
    def delete_config(self, name: str) -> Dict:
        """删除配置"""
        with self._lock:
            if name not in self.configs:
                return {'success': False, 'error': f'配置 {name} 不存在'}
            
            del self.configs[name]
            if self.active_config == name:
                # 激活第一个可用的
                self.active_config = next(iter(self.configs), None)
            self._save_configs()
            return {'success': True}
    
    def switch_config(self, name: str) -> Dict:
        """切换活动配置"""
        with self._lock:
            if name not in self.configs:
                return {'success': False, 'error': f'配置 {name} 不存在'}
            
            old = self.active_config
            self.active_config = name
            self._save_configs()
            return {'success': True, 'old': old, 'new': name}
    
    def record_usage(self, name: str, tokens: int = 0):
        """记录使用量"""
        with self._lock:
            cfg = self.configs.get(name)
            if cfg:
                cfg.usage_count += 1
                cfg.total_tokens += tokens
                cfg.last_used = datetime.now().isoformat()
                self._save_configs()
    
    def get_active_config(self) -> Optional[Dict]:
        """获取当前活动配置"""
        if self.active_config and self.active_config in self.configs:
            return self.get_config(self.active_config)
        return None
    
    def get_stats(self) -> Dict:
        """获取全局统计"""
        total_usage = sum(c.usage_count for c in self.configs.values())
        total_tokens = sum(c.total_tokens for c in self.configs.values())
        return {
            'total_configs': len(self.configs),
            'enabled_configs': sum(1 for c in self.configs.values() if c.enabled),
            'active_config': self.active_config,
            'total_usage': total_usage,
            'total_tokens': total_tokens,
        }


# 全局实例
_llm_manager = None

def get_llm_manager() -> LLMManager:
    """获取全局 LLM 管理器实例"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager
