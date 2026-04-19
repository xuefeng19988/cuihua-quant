"""
Phase 77: 实时告警系统 (Real-time Alert System)

多渠道告警通知：
- 邮件告警
- Webhook 告警
- 控制台告警
- 自定义告警规则
"""


import time
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertChannel(Enum):
    """告警渠道"""
    CONSOLE = "console"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CUSTOM = "custom"


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: Callable[[Dict], bool]
    level: AlertLevel
    channels: List[AlertChannel]
    cooldown_seconds: int = 300  # 冷却时间
    last_triggered: float = 0.0
    enabled: bool = True


@dataclass
class AlertMessage:
    """告警消息"""
    title: str
    message: str
    level: AlertLevel
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "message": self.message,
            "level": self.level.value,
            "timestamp": self.timestamp,
            "time_str": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "metadata": self.metadata,
        }


class AlertSystem:
    """实时告警系统"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.rules: List[AlertRule] = []
        self.history: List[AlertMessage] = []
        self.handlers: Dict[AlertChannel, Callable] = {
            AlertChannel.CONSOLE: self._handle_console,
            AlertChannel.EMAIL: self._handle_email,
            AlertChannel.WEBHOOK: self._handle_webhook,
            AlertChannel.CUSTOM: self._handle_custom,
        }
        self._custom_handler: Optional[Callable] = None

    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules.append(rule)

    def set_custom_handler(self, handler: Callable):
        """设置自定义告警处理器"""
        self._custom_handler = handler
        self.handlers[AlertChannel.CUSTOM] = handler

    def check_rules(self, data: Dict) -> List[AlertMessage]:
        """检查所有规则，触发符合条件的告警"""
        triggered = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            # 检查冷却时间
            now = time.time()
            if now - rule.last_triggered < rule.cooldown_seconds:
                continue

            # 检查条件
            if rule.condition(data):
                alert = AlertMessage(
                    title=f"告警: {rule.name}",
                    message=f"规则 '{rule.name}' 被触发",
                    level=rule.level,
                    metadata={"rule_name": rule.name, "data": data},
                )

                # 更新冷却时间
                rule.last_triggered = now

                # 发送告警
                self._send_alert(alert, rule.channels)

                triggered.append(alert)

        return triggered

    def send_alert(self, alert: AlertMessage, channels: List[AlertChannel]):
        """直接发送告警"""
        self.history.append(alert)
        self._send_alert(alert, channels)

    def _send_alert(self, alert: AlertMessage, channels: List[AlertChannel]):
        """通过指定渠道发送告警"""
        for channel in channels:
            handler = self.handlers.get(channel)
            if handler:
                try:
                    handler(alert)
                except Exception as e:
                    print(f"[告警系统] 渠道 {channel.value} 发送失败: {e}")

    def _handle_console(self, alert: AlertMessage):
        """控制台告警"""
        level_colors = {
            AlertLevel.INFO: "\033[94m",
            AlertLevel.WARNING: "\033[93m",
            AlertLevel.CRITICAL: "\033[91m",
            AlertLevel.EMERGENCY: "\033[95m",
        }
        reset = "\033[0m"
        color = level_colors.get(alert.level, "")

        print(f"{color}[{alert.level.value.upper()}] {alert.title}: {alert.message}{reset}")

    def _handle_email(self, alert: AlertMessage):
        """邮件告警"""
        smtp_config = self.config.get("smtp", {})
        if not smtp_config:
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_config.get("from", "")
            msg["To"] = ", ".join(smtp_config.get("to", []))
            msg["Subject"] = f"[翠花量化] {alert.title}"

            body = f"""
告警级别: {alert.level.value}
告警时间: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}
告警内容: {alert.message}

元数据:
{alert.metadata}
            """
            msg.attach(MIMEText(body, "plain", "utf-8"))

            server = smtplib.SMTP(smtp_config.get("server", "localhost"), smtp_config.get("port", 587))
            if smtp_config.get("use_tls", False):
                server.starttls()
            if "username" in smtp_config and "password" in smtp_config:
                server.login(smtp_config["username"], smtp_config["password"])

            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"[邮件告警] 发送失败: {e}")

    def _handle_webhook(self, alert: AlertMessage):
        """Webhook 告警"""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return

        try:
            payload = {
                "title": alert.title,
                "message": alert.message,
                "level": alert.level.value,
                "timestamp": alert.timestamp,
                "metadata": alert.metadata,
            }
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"[Webhook 告警] 发送失败: {e}")

    def get_history(self, limit: int = 50) -> List[Dict]:
        """获取告警历史"""
        return [alert.to_dict() for alert in self.history[-limit:]]

    def get_stats(self) -> Dict:
        """获取告警统计"""
        stats = {
            "total_alerts": len(self.history),
            "by_level": {},
            "by_channel": {},
        }

        for alert in self.history:
            level = alert.level.value
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1

        return stats


# 预定义告警规则
def create_portfolio_drop_rule(threshold: float = -0.05) -> AlertRule:
    """组合下跌告警"""
    return AlertRule(
        name="组合下跌告警",
        condition=lambda data: data.get("portfolio_return", 0) < threshold,
        level=AlertLevel.CRITICAL,
        channels=[AlertChannel.CONSOLE, AlertChannel.EMAIL],
        cooldown_seconds=3600,
    )


def create_position_limit_rule(max_position: float = 0.3) -> AlertRule:
    """仓位超限告警"""
    return AlertRule(
        name="仓位超限告警",
        condition=lambda data: data.get("max_position_pct", 0) > max_position,
        level=AlertLevel.WARNING,
        channels=[AlertChannel.CONSOLE],
        cooldown_seconds=1800,
    )


def create_drawdown_rule(max_drawdown: float = -0.1) -> AlertRule:
    """最大回撤告警"""
    return AlertRule(
        name="最大回撤告警",
        condition=lambda data: data.get("max_drawdown", 0) < max_drawdown,
        level=AlertLevel.EMERGENCY,
        channels=[AlertChannel.CONSOLE, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
        cooldown_seconds=7200,
    )
