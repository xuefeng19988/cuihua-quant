"""
Phase 12: Real Trading Environment Manager
Manages real trading environment configuration and safety checks.
(Development mode - no actual trading)
"""

import os
import sys
import yaml
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

@dataclass
class TradingEnvironment:
    """Trading environment configuration."""
    name: str
    mode: str  # 'simulation' or 'real'
    api_host: str
    api_port: int
    api_key: str
    initial_capital: float
    max_single_position_pct: float
    stop_loss_pct: float
    take_profit_pct: float
    max_daily_loss_pct: float
    max_drawdown_pct: float
    emergency_contact: str
    auto_halt_enabled: bool
    log_level: str = 'INFO'

class RealTradingManager:
    """
    Manages real trading environment setup and safety.
    Development mode - simulates real trading setup without actual orders.
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(project_root, 'config', 'real_trading.yaml')
        self.config_path = config_path
        self.environment: Optional[TradingEnvironment] = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup trading logger."""
        logger = logging.getLogger('real_trading')
        logger.setLevel(logging.INFO)
        
        log_dir = os.path.join(project_root, 'data', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        handler = logging.FileHandler(os.path.join(log_dir, 'real_trading.log'))
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        logger.addHandler(handler)
        
        return logger
        
    def load_config(self) -> bool:
        """Load trading environment configuration."""
        if not os.path.exists(self.config_path):
            self.logger.warning(f"Config not found: {self.config_path}")
            return False
            
        with open(self.config_path, 'r') as f:
            cfg = yaml.safe_load(f)
            
        self.environment = TradingEnvironment(**cfg)
        self.logger.info(f"Loaded environment: {self.environment.name} ({self.environment.mode})")
        return True
        
    def validate_environment(self) -> Dict:
        """Validate trading environment configuration."""
        if not self.environment:
            return {'status': 'ERROR', 'message': 'No environment loaded'}
            
        checks = {}
        
        # Check API connectivity (simulated)
        checks['api_config'] = {
            'host': self.environment.api_host,
            'port': self.environment.api_port,
            'status': 'CONFIGURED' if self.environment.api_host else 'MISSING'
        }
        
        # Check risk parameters
        checks['risk_params'] = {
            'max_single_position': f"{self.environment.max_single_position_pct:.0%}",
            'stop_loss': f"{self.environment.stop_loss_pct:.0%}",
            'take_profit': f"{self.environment.take_profit_pct:.0%}",
            'max_daily_loss': f"{self.environment.max_daily_loss_pct:.0%}",
            'max_drawdown': f"{self.environment.max_drawdown_pct:.0%}"
        }
        
        # Validate risk limits are reasonable for real trading
        if self.environment.mode == 'real':
            if self.environment.max_single_position_pct > 0.10:
                checks['risk_warning'] = 'Single position limit >10% is risky for real trading'
            if self.environment.stop_loss_pct > 0.08:
                checks['risk_warning'] = 'Stop loss >8% may be too wide for real trading'
                
        return {
            'status': 'OK',
            'environment': self.environment.name,
            'mode': self.environment.mode,
            'checks': checks
        }
        
    def check_safety(self) -> Dict:
        """Perform pre-trading safety checks."""
        safety_checks = {
            'environment_loaded': self.environment is not None,
            'api_configured': self.environment.api_host != '' if self.environment else False,
            'risk_limits_set': self.environment.max_daily_loss_pct > 0 if self.environment else False,
            'emergency_contact_set': self.environment.emergency_contact != '' if self.environment else False,
            'auto_halt_enabled': self.environment.auto_halt_enabled if self.environment else False,
            'log_configured': True
        }
        
        all_pass = all(safety_checks.values())
        
        return {
            'status': 'PASS' if all_pass else 'FAIL',
            'checks': safety_checks,
            'ready_for_trading': all_pass
        }
        
    def emergency_halt(self, reason: str) -> Dict:
        """Emergency halt all trading."""
        self.logger.critical(f"EMERGENCY HALT: {reason}")
        
        # In real implementation, this would:
        # 1. Cancel all pending orders
        # 2. Close all positions
        # 3. Send alert to emergency contact
        # 4. Log the incident
        
        return {
            'status': 'HALTED',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
    def generate_setup_report(self) -> str:
        """Generate real trading setup report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🔐 实盘交易环境配置报告")
        lines.append("=" * 60)
        
        if not self.environment:
            lines.append("\n⚠️ 环境未加载")
            return "\n".join(lines)
            
        lines.append(f"\n📊 环境信息")
        lines.append(f"  名称: {self.environment.name}")
        lines.append(f"  模式: {self.environment.mode}")
        lines.append(f"  API: {self.environment.api_host}:{self.environment.api_port}")
        
        lines.append(f"\n🛡️  风控参数")
        lines.append(f"  单只仓位: {self.environment.max_single_position_pct:.0%}")
        lines.append(f"  止损线: {self.environment.stop_loss_pct:.0%}")
        lines.append(f"  止盈线: {self.environment.take_profit_pct:.0%}")
        lines.append(f"  日亏损限制: {self.environment.max_daily_loss_pct:.0%}")
        lines.append(f"  最大回撤: {self.environment.max_drawdown_pct:.0%}")
        
        lines.append(f"\n🔔 安全设置")
        lines.append(f"  紧急联系人: {self.environment.emergency_contact}")
        lines.append(f"  自动暂停: {'✅ 启用' if self.environment.auto_halt_enabled else '❌ 禁用'}")
        
        # Safety checks
        safety = self.check_safety()
        lines.append(f"\n✅ 安全检查")
        for check, passed in safety['checks'].items():
            icon = "✅" if passed else "❌"
            lines.append(f"  {icon} {check}")
            
        lines.append(f"\n{'🟢 环境就绪' if safety['ready_for_trading'] else '🔴 环境未就绪'}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


if __name__ == "__main__":
    manager = RealTradingManager()
    # Create default config if not exists
    config_path = os.path.join(project_root, 'config', 'real_trading.yaml')
    if not os.path.exists(config_path):
        default_config = {
            'name': 'test_environment',
            'mode': 'simulation',
            'api_host': '127.0.0.1',
            'api_port': 11112,
            'api_key': '',
            'initial_capital': 10000,
            'max_single_position_pct': 0.05,
            'stop_loss_pct': 0.05,
            'take_profit_pct': 0.15,
            'max_daily_loss_pct': 0.02,
            'max_drawdown_pct': 0.10,
            'emergency_contact': 'admin@example.com',
            'auto_halt_enabled': True
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        print(f"Created default config: {config_path}")
        
    manager.load_config()
    print(manager.generate_setup_report())
