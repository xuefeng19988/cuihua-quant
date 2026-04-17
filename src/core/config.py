"""
翠花量化系统 - 统一配置管理器
Centralized configuration manager with validation, defaults, and hot-reload.
"""

import os
import sys
import yaml
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = f"sqlite:///{os.path.join(project_root, 'data', 'cuihua_quant.db')}"
    echo_sql: bool = False
    pool_size: int = 5
    max_overflow: int = 10

@dataclass
class FutuConfig:
    """Futu OpenD configuration."""
    host: str = "127.0.0.1"
    quote_port: int = 11112
    trd_port: int = 11113
    rsa_key_path: str = ""
    paper_trading: bool = True

@dataclass
class RiskConfig:
    """Risk management configuration."""
    total_capital: float = 1_000_000
    max_single_position_pct: float = 0.10
    max_total_exposure_pct: float = 0.90
    max_position_count: int = 10
    stop_loss_pct: float = 0.08
    take_profit_pct: float = 0.20
    max_daily_loss_pct: float = 0.03
    max_drawdown_pct: float = 0.15
    rebalance_threshold: float = 0.05

@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    memory_max_items: int = 1000
    file_cache_dir: str = os.path.join(project_root, 'data', 'cache')
    default_ttl: int = 300  # 5 minutes

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    file: str = os.path.join(project_root, 'data', 'logs', 'cuihua_quant.log')
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_json: bool = False

@dataclass
class WebConfig:
    """Web dashboard configuration."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: str = "change-me-in-production"

@dataclass 
class AppConfig:
    """Main application configuration."""
    name: str = "翠花量化系统"
    version: str = "1.5.0"
    environment: str = "development"  # development, staging, production
    
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    futu: FutuConfig = field(default_factory=FutuConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    web: WebConfig = field(default_factory=WebConfig)

class ConfigManager:
    """
    Centralized configuration manager.
    Loads from YAML files, environment variables, and provides defaults.
    """
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(project_root, 'config')
        self.config_dir = config_dir
        self._config: Optional[AppConfig] = None
        self._load_time: Optional[str] = None
        
    def load(self) -> AppConfig:
        """Load configuration from files and environment."""
        config = AppConfig()
        
        # Load from YAML files
        config = self._load_yaml_config(config)
        
        # Override with environment variables
        config = self._load_env_config(config)
        
        self._config = config
        self._load_time = datetime.now().isoformat()
        
        return config
        
    def _load_yaml_config(self, config: AppConfig) -> AppConfig:
        """Load configuration from YAML files."""
        # Load risk config
        risk_path = os.path.join(self.config_dir, 'risk.yaml')
        if os.path.exists(risk_path):
            with open(risk_path, 'r') as f:
                risk_data = yaml.safe_load(f) or {}
            for key, value in risk_data.items():
                if hasattr(config.risk, key):
                    setattr(config.risk, key, value)
                    
        # Load app config
        app_path = os.path.join(self.config_dir, 'app.yaml')
        if os.path.exists(app_path):
            with open(app_path, 'r') as f:
                app_data = yaml.safe_load(f) or {}
            if 'logging' in app_data:
                for key, value in app_data['logging'].items():
                    if hasattr(config.logging, key):
                        setattr(config.logging, key, value)
                        
        return config
        
    def _load_env_config(self, config: AppConfig) -> AppConfig:
        """Override configuration with environment variables."""
        # Database
        if db_url := os.getenv('DB_URL'):
            config.database.url = db_url
            
        # Futu
        if futu_host := os.getenv('FUTU_HOST'):
            config.futu.host = futu_host
        if futu_port := os.getenv('FUTU_QUOTE_PORT'):
            config.futu.quote_port = int(futu_port)
            
        # Web
        if web_port := os.getenv('WEB_PORT'):
            config.web.port = int(web_port)
        if os.getenv('FLASK_DEBUG'):
            config.web.debug = True
            
        # Environment
        if env := os.getenv('APP_ENV'):
            config.environment = env
            
        return config
        
    @property
    def config(self) -> AppConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            self.load()
        return self._config
        
    def reload(self) -> AppConfig:
        """Reload configuration from files."""
        self._config = None
        return self.load()
        
    def get_status(self) -> Dict:
        """Get configuration status."""
        if self._config is None:
            return {'status': 'not_loaded'}
            
        return {
            'status': 'loaded',
            'load_time': self._load_time,
            'environment': self._config.environment,
            'version': self._config.version,
            'database': self._config.database.url.split('://')[0],
            'web_port': self._config.web.port,
            'futu_host': f"{self._config.futu.host}:{self._config.futu.quote_port}"
        }
        
    def generate_report(self) -> str:
        """Generate configuration report."""
        if self._config is None:
            return "⚠️ 配置未加载"
            
        cfg = self._config
        lines = []
        lines.append("=" * 60)
        lines.append(f"⚙️  系统配置报告 - {cfg.name} v{cfg.version}")
        lines.append("=" * 60)
        lines.append(f"\n📊 环境: {cfg.environment}")
        lines.append(f"📅 加载时间: {self._load_time}")
        
        lines.append(f"\n🗄️  数据库")
        lines.append(f"  类型: {cfg.database.url.split('://')[0]}")
        lines.append(f"  路径: {cfg.database.url}")
        
        lines.append(f"\n📡 Futu OpenD")
        lines.append(f"  地址: {cfg.futu.host}:{cfg.futu.quote_port}")
        lines.append(f"  模拟盘: {'✅' if cfg.futu.paper_trading else '❌'}")
        
        lines.append(f"\n🛡️  风控参数")
        lines.append(f"  总资金: ¥{cfg.risk.total_capital:,.0f}")
        lines.append(f"  单只仓位: {cfg.risk.max_single_position_pct:.0%}")
        lines.append(f"  止损: {cfg.risk.stop_loss_pct:.0%}")
        lines.append(f"  止盈: {cfg.risk.take_profit_pct:.0%}")
        
        lines.append(f"\n💾 缓存")
        lines.append(f"  启用: {'✅' if cfg.cache.enabled else '❌'}")
        lines.append(f"  内存最大项: {cfg.cache.memory_max_items}")
        lines.append(f"  默认 TTL: {cfg.cache.default_ttl}秒")
        
        lines.append(f"\n🌐 Web 服务")
        lines.append(f"  地址: {cfg.web.host}:{cfg.web.port}")
        lines.append(f"  调试模式: {'✅' if cfg.web.debug else '❌'}")
        
        return "\n".join(lines)


# Global config manager instance
config_manager = ConfigManager()
