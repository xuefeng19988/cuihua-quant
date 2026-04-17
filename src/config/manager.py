"""
Configuration Manager
Manages all YAML configurations with validation and hot-reload.
"""

import os
import sys
import yaml
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
config_dir = os.path.join(project_root, 'config')

class ConfigManager:
    """
    Centralized configuration manager.
    - Load configs from YAML files
    - Validate configurations
    - Hot-reload support
    - Get/set individual values
    """
    
    def __init__(self):
        self.configs: Dict[str, Dict] = {}
        self._load_time: Optional[str] = None
        self.reload()
        
    def reload(self):
        """Reload all configuration files."""
        self.configs = {}
        for fname in ['app.yaml', 'stocks.yaml', 'strategies.yaml', 'risk.yaml', 'schedule.yaml']:
            fpath = os.path.join(config_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    self.configs[fname.replace('.yaml', '')] = yaml.safe_load(f) or {}
        self._load_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get config value by dot-separated path.
        Example: config.get('stocks.pools.watchlist.stocks')
        """
        parts = path.split('.')
        value = self.configs
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
                
        return value
        
    def set(self, path: str, value: Any) -> bool:
        """
        Set config value by dot-separated path.
        Note: Changes are in-memory only. Use save() to persist.
        """
        parts = path.split('.')
        current = self.configs
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
            
        current[parts[-1]] = value
        return True
        
    def validate(self) -> Dict[str, str]:
        """Validate all configurations."""
        errors = {}
        
        # Check stocks.yaml
        stocks = self.get('stocks.pools')
        if not stocks:
            errors['stocks'] = 'No stock pools defined'
        else:
            for pool_name, pool in stocks.items():
                if not pool.get('stocks'):
                    errors[f'stocks.{pool_name}'] = f'Pool {pool_name} has no stocks'
                    
        # Check risk.yaml
        risk = self.get('risk')
        if risk:
            if risk.get('stop_loss_pct', 0) <= 0:
                errors['risk.stop_loss_pct'] = 'Stop loss must be positive'
            if risk.get('total_capital', 0) <= 0:
                errors['risk.total_capital'] = 'Total capital must be positive'
                
        # Check strategies.yaml
        strategies = self.get('strategies')
        if strategies:
            for name, cfg in strategies.items():
                if isinstance(cfg, dict) and cfg.get('enabled', True):
                    if 'weights' in cfg:
                        total = sum(cfg['weights'].values())
                        if abs(total - 1.0) > 0.01:
                            errors[f'strategies.{name}.weights'] = f'Weights sum to {total}, expected 1.0'
                            
        return errors
        
    def get_status(self) -> Dict:
        """Get configuration status."""
        return {
            'loaded': bool(self.configs),
            'load_time': self._load_time,
            'config_files': list(self.configs.keys()),
            'validation_errors': self.validate()
        }
        
    def export_json(self) -> str:
        """Export all configs as JSON string."""
        return json.dumps(self.configs, indent=2, ensure_ascii=False)
        
    def generate_report(self) -> str:
        """Generate configuration report."""
        lines = []
        lines.append("=" * 50)
        lines.append("⚙️  配置状态报告")
        lines.append("=" * 50)
        
        status = self.get_status()
        lines.append(f"\n📅 加载时间: {status['load_time']}")
        lines.append(f"📁 配置文件: {', '.join(status['config_files'])}")
        
        # Stocks
        stocks = self.get('stocks.pools', {})
        lines.append(f"\n📊 股票池")
        for name, pool in stocks.items():
            stock_list = pool.get('stocks', [])
            lines.append(f"  - {name}: {len(stock_list)} 只股票")
            
        # Risk
        risk = self.get('risk', {})
        if risk:
            lines.append(f"\n🛡️  风控参数")
            lines.append(f"  总资金: ¥{risk.get('total_capital', 0):,.0f}")
            lines.append(f"  止损: {risk.get('stop_loss_pct', 0):.0%}")
            lines.append(f"  止盈: {risk.get('take_profit_pct', 0):.0%}")
            lines.append(f"  最大回撤: {risk.get('max_drawdown_pct', 0):.0%}")
            
        # Validation
        errors = status['validation_errors']
        if errors:
            lines.append(f"\n⚠️  配置错误")
            for key, msg in errors.items():
                lines.append(f"  ❌ {key}: {msg}")
        else:
            lines.append(f"\n✅ 配置验证通过")
            
        return "\n".join(lines)


if __name__ == "__main__":
    config = ConfigManager()
    print(config.generate_report())
