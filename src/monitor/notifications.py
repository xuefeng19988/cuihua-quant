"""
Phase 10.4: Notification System
Customizable notification rules and templates for trading alerts.
"""

import os
import sys
import yaml
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

class NotificationTemplate:
    """Notification template for different alert types."""
    
    def __init__(self, name: str, pattern: str, channels: List[str] = None):
        self.name = name
        self.pattern = pattern  # Template pattern with {variables}
        self.channels = channels or ['wecom']
        
    def render(self, **kwargs) -> str:
        """Render template with variables."""
        try:
            return self.pattern.format(**kwargs)
        except KeyError as e:
            return f"⚠️ Template error: missing {e}"

class NotificationSystem:
    """
    Manages customizable notifications for trading alerts.
    Supports multiple channels and templates.
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(project_root, 'config', 'notifications.yaml')
        self.config_path = config_path
        self.templates: Dict[str, NotificationTemplate] = {}
        self.rules: List[Dict] = []
        self._load_config()
        
    def _load_config(self):
        """Load notification configuration."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                cfg = yaml.safe_load(f)
                
            # Load templates
            for name, tmpl in cfg.get('templates', {}).items():
                self.templates[name] = NotificationTemplate(
                    name=name,
                    pattern=tmpl['pattern'],
                    channels=tmpl.get('channels', ['wecom'])
                )
                
            # Load rules
            self.rules = cfg.get('rules', [])
            
    def add_rule(self, rule: Dict):
        """Add notification rule."""
        self.rules.append(rule)
        
    def check_rules(self, context: Dict) -> List[Dict]:
        """Check rules against current context."""
        triggered = []
        for rule in self.rules:
            condition = rule.get('condition', '')
            # Simple condition evaluation (would be more sophisticated in production)
            if self._evaluate_condition(condition, context):
                triggered.append(rule)
        return triggered
        
    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """Evaluate a simple condition."""
        # In production, would use a proper expression evaluator
        # For now, simple keyword matching
        for key, value in context.items():
            if key in condition:
                return True
        return False
        
    def send_notification(self, template_name: str, channels: List[str] = None, **kwargs):
        """Send notification using template."""
        if template_name not in self.templates:
            print(f"⚠️ Template not found: {template_name}")
            return False
            
        template = self.templates[template_name]
        message = template.render(**kwargs)
        
        if channels is None:
            channels = template.channels
            
        for channel in channels:
            self._send_to_channel(channel, message)
            
        return True
        
    def _send_to_channel(self, channel: str, message: str) -> bool:
        """Send message to specified channel."""
        try:
            if channel == 'wecom':
                cmd = [
                    'openclaw', 'message', 'send',
                    '--channel', 'wecom',
                    '--target', 'xuefeng',
                    '--message', message
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                return result.returncode == 0
            elif channel == 'console':
                print(f"[{channel}] {message}")
                return True
        except Exception as e:
            print(f"⚠️ Failed to send to {channel}: {e}")
        return False
        
    def generate_report(self) -> str:
        """Generate notification system report."""
        lines = []
        lines.append("=" * 50)
        lines.append("🔔 通知系统报告")
        lines.append("=" * 50)
        
        lines.append(f"\n📝 模板 ({len(self.templates)})")
        for name, tmpl in self.templates.items():
            lines.append(f"  ✅ {name} -> {tmpl.channels}")
            
        lines.append(f"\n📋 规则 ({len(self.rules)})")
        for rule in self.rules:
            lines.append(f"  ✅ {rule.get('name', 'Unnamed')}: {rule.get('condition', '')}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    notif = NotificationSystem()
    print(notif.generate_report())
