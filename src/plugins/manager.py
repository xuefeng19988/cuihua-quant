"""
Phase 15: Plugin System
Allows third-party data sources and strategies to be plugged in.
"""

import os
import sys
import importlib
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class DataSourcePlugin(ABC):
    """Base class for data source plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name."""
        pass
        
    @abstractmethod
    def fetch_data(self, code: str, **kwargs) -> Any:
        """Fetch data for a stock."""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if data source is available."""
        pass

class StrategyPlugin(ABC):
    """Base class for strategy plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return strategy name."""
        pass
        
    @abstractmethod
    def generate_signals(self, data: Any) -> Any:
        """Generate trading signals."""
        pass
        
    @abstractmethod
    def get_parameters(self) -> Dict:
        """Return strategy parameters."""
        pass

class PluginManager:
    """
    Manages plugin loading, registration, and execution.
    Supports hot-reloading of plugins.
    """
    
    def __init__(self, plugin_dir: str = None):
        if plugin_dir is None:
            plugin_dir = os.path.join(project_root, 'plugins')
        self.plugin_dir = plugin_dir
        os.makedirs(plugin_dir, exist_ok=True)
        
        self.data_sources: Dict[str, DataSourcePlugin] = {}
        self.strategies: Dict[str, StrategyPlugin] = {}
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load plugin configuration."""
        config_path = os.path.join(self.plugin_dir, 'plugins.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
        
    def register_data_source(self, plugin: DataSourcePlugin):
        """Register a data source plugin."""
        name = plugin.get_name()
        self.data_sources[name] = plugin
        print(f"✅ Registered data source: {name}")
        
    def register_strategy(self, plugin: StrategyPlugin):
        """Register a strategy plugin."""
        name = plugin.get_name()
        self.strategies[name] = plugin
        print(f"✅ Registered strategy: {name}")
        
    def load_plugins(self):
        """Load all plugins from plugin directory."""
        if not os.path.exists(self.plugin_dir):
            return
            
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(
                        module_name,
                        os.path.join(self.plugin_dir, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check for plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type):
                            if issubclass(attr, DataSourcePlugin) and attr != DataSourcePlugin:
                                self.register_data_source(attr())
                            elif issubclass(attr, StrategyPlugin) and attr != StrategyPlugin:
                                self.register_strategy(attr())
                                
                except Exception as e:
                    print(f"⚠️ Failed to load plugin {filename}: {e}")
                    
    def get_available_data_sources(self) -> List[str]:
        """Get list of available data sources."""
        return list(self.data_sources.keys())
        
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategies."""
        return list(self.strategies.keys())
        
    def generate_plugin_report(self) -> str:
        """Generate plugin status report."""
        lines = []
        lines.append("=" * 50)
        lines.append("🔌 插件系统报告")
        lines.append("=" * 50)
        
        lines.append(f"\n📊 数据源插件 ({len(self.data_sources)})")
        for name, plugin in self.data_sources.items():
            status = "✅" if plugin.is_available() else "❌"
            lines.append(f"  {status} {name}")
            
        lines.append(f"\n🧠 策略插件 ({len(self.strategies)})")
        for name, plugin in self.strategies.items():
            params = plugin.get_parameters()
            lines.append(f"  ✅ {name} ({len(params)} 参数)")
            
        if not self.data_sources and not self.strategies:
            lines.append("\n⚠️ 无插件加载")
            lines.append(f"  插件目录: {self.plugin_dir}")
            lines.append("  将 .py 文件放入插件目录即可自动加载")
            
        return "\n".join(lines)


if __name__ == "__main__":
    manager = PluginManager()
    manager.load_plugins()
    print(manager.generate_plugin_report())
