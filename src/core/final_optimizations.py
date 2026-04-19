"""
Phase 74-76: Final System Optimizations
Phase 74: Error Handling Enhancement
Phase 75: Logging System Upgrade
Phase 76: Configuration Management v2
"""

import os
import sys
import json
import logging
import yaml
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from pathlib import Path

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# ==================== Phase 74: Error Handling Enhancement ====================

class EnhancedErrorHandler:
    """
    Enhanced error handling with context and recovery.
    """
    
    def __init__(self, log_file: str = None):
        if log_file is None:
            log_file = os.path.join(project_root, 'data', 'logs', 'errors.log')
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self.error_history: List[Dict] = []
        
    def handle_error(self, error: Exception, context: Dict = None,
                    recovery_func: Callable = None) -> Dict:
        """
        Handle error with context and optional recovery.
        """
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'timestamp': datetime.now().isoformat(),
            'recovered': False
        }
        
        # Try recovery
        if recovery_func:
            try:
                result = recovery_func()
                error_info['recovered'] = True
                error_info['recovery_result'] = str(result)
            except Exception as recovery_error:
                error_info['recovery_error'] = str(recovery_error)
                
        # Log error
        self.error_history.append(error_info)
        self._log_error(error_info)
        
        return error_info
        
    def _log_error(self, error_info: Dict):
        """Log error to file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_info, ensure_ascii=False) + '\n')
        except Exception as e:
            pass
            
    def get_error_summary(self) -> Dict:
        """Get error summary."""
        if not self.error_history:
            return {'total_errors': 0}
            
        error_types = {}
        for error in self.error_history:
            error_type = error['type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
        return {
            'total_errors': len(self.error_history),
            'error_types': error_types,
            'recovery_rate': sum(1 for e in self.error_history if e.get('recovered')) / len(self.error_history),
            'latest_error': self.error_history[-1] if self.error_history else None
        }


def safe_execute(default_value: Any = None, error_handler: EnhancedErrorHandler = None):
    """
    Decorator for safe function execution.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_handler:
                    error_handler.handle_error(e, {
                        'function': func.__name__,
                        'args': str(args)[:100],
                        'kwargs': str(kwargs)[:100]
                    })
                return default_value
        return wrapper
    return decorator


# ==================== Phase 75: Logging System Upgrade ====================

class AdvancedLogger:
    """
    Advanced logging system with multiple outputs and formatting.
    """
    
    def __init__(self, name: str = 'cuihua_quant', 
                 log_dir: str = None,
                 level: str = 'INFO'):
        self.name = name
        if log_dir is None:
            log_dir = os.path.join(project_root, 'data', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_formatter(False))
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'{name}.log'),
            encoding='utf-8'
        )
        file_handler.setFormatter(self._get_formatter(True))
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(
            os.path.join(log_dir, f'{name}_error.log'),
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self._get_formatter(True))
        self.logger.addHandler(error_handler)
        
    def _get_formatter(self, detailed: bool = False) -> logging.Formatter:
        """Get log formatter."""
        if detailed:
            return logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s'
            )
        return logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
        
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
        
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
        
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)
        
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, extra=kwargs)


# ==================== Phase 76: Configuration Management v2 ====================

class ConfigManagerV2:
    """
    Enhanced configuration management with validation and hot-reload.
    """
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(project_root, 'config')
        self.config_dir = config_dir
        self._configs: Dict[str, Dict] = {}
        self._validators: Dict[str, Callable] = {}
        self._load_all_configs()
        
    def _load_all_configs(self):
        """Load all configuration files."""
        config_files = [
            'app.yaml', 'stocks.yaml', 'strategies.yaml',
            'risk.yaml', 'schedule.yaml', 'logging.yaml'
        ]
        
        for filename in config_files:
            filepath = os.path.join(self.config_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    config_name = filename.replace('.yaml', '')
                    self._configs[config_name] = yaml.safe_load(f) or {}
                    
    def get(self, config_name: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value."""
        config = self._configs.get(config_name, {})
        if key is None:
            return config
            
        # Support nested keys
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
        
    def set(self, config_name: str, key: str, value: Any):
        """Set configuration value."""
        if config_name not in self._configs:
            self._configs[config_name] = {}
            
        keys = key.split('.')
        config = self._configs[config_name]
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        
    def save(self, config_name: str):
        """Save configuration to file."""
        if config_name not in self._configs:
            return False
            
        filepath = os.path.join(self.config_dir, f'{config_name}.yaml')
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(self._configs[config_name], f, 
                         default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            return False
            
    def reload(self, config_name: str = None):
        """Reload configuration from files."""
        if config_name:
            filepath = os.path.join(self.config_dir, f'{config_name}.yaml')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self._configs[config_name] = yaml.safe_load(f) or {}
        else:
            self._load_all_configs()
            
    def validate(self, config_name: str) -> List[str]:
        """Validate configuration."""
        if config_name not in self._validators:
            return []
            
        validator = self._validators[config_name]
        return validator(self._configs.get(config_name, {}))
        
    def register_validator(self, config_name: str, validator: Callable):
        """Register configuration validator."""
        self._validators[config_name] = validator
        
    def get_all_configs(self) -> Dict:
        """Get all configurations."""
        return self._configs.copy()
        
    def generate_report(self) -> str:
        """Generate configuration report."""
        lines = []
        lines.append("=" * 60)
        lines.append("⚙️  配置管理报告")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 已加载配置: {len(self._configs)}")
        for name, config in self._configs.items():
            lines.append(f"  ✅ {name}.yaml ({len(config)} 项)")
            
        return "\n".join(lines)


if __name__ == "__main__":
    print("✅ Phase 74-76 modules loaded successfully")
    
    # Test error handler
    error_handler = EnhancedErrorHandler()
    
    @safe_execute(default_value="error", error_handler=error_handler)
    def risky_function():
        raise ValueError("Test error")
        
    result = risky_function()
    print(f"\n🔧 Error Handler Test:")
    print(f"  Result: {result}")
    print(f"  Errors: {error_handler.get_error_summary()['total_errors']}")
    
    # Test config manager
    config_mgr = ConfigManagerV2()
    print(f"\n⚙️ Config Manager Test:")
    print(config_mgr.generate_report())
