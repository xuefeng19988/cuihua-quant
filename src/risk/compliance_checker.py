"""
Phase 100: 交易合规检查系统 (Trade Compliance Checker)

交易合规性验证与审计
"""


from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ComplianceRuleType(Enum):
    """合规规则类型"""
    POSITION_LIMIT = "仓位限制"
    SECTOR_LIMIT = "板块限制"
    CONCENTRATION_LIMIT = "集中度限制"
    LEVERAGE_LIMIT = "杠杆限制"
    LIQUIDITY_REQUIREMENT = "流动性要求"
    RISK_BUDGET = "风险预算"
    BLACKLIST = "黑名单"
    WHITELIST = "白名单"
    TRADE_SIZE_LIMIT = "交易规模限制"
    FREQUENCY_LIMIT = "交易频率限制"


class ComplianceStatus(Enum):
    """合规状态"""
    PASS = "通过"
    WARNING = "警告"
    VIOLATION = "违规"
    BLOCKED = "拦截"


@dataclass
class ComplianceRule:
    """合规规则"""
    rule_id: str
    name: str
    rule_type: ComplianceRuleType
    threshold: float
    enabled: bool = True
    description: str = ""

    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "type": self.rule_type.value,
            "threshold": self.threshold,
            "enabled": self.enabled,
            "description": self.description,
        }


@dataclass
class ComplianceCheck:
    """合规检查"""
    rule_id: str
    rule_name: str
    status: ComplianceStatus
    actual_value: float
    threshold: float
    message: str

    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": self.status.value,
            "actual_value": self.actual_value,
            "threshold": self.threshold,
            "message": self.message,
        }


@dataclass
class ComplianceReport:
    """合规报告"""
    trade_id: str
    timestamp: float
    overall_status: ComplianceStatus
    checks: List[ComplianceCheck]
    violations: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            "trade_id": self.trade_id,
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": self.overall_status.value,
            "checks": [c.to_dict() for c in self.checks],
            "violations": self.violations,
            "recommendations": self.recommendations,
        }


class TradeComplianceChecker:
    """交易合规检查器"""

    def __init__(self):
        self.rules: List[ComplianceRule] = []
        self.blacklist = set()
        self.whitelist = set()
        self.audit_log = []

        self._setup_default_rules()

    def _setup_default_rules(self):
        """设置默认合规规则"""
        self.rules = [
            ComplianceRule(
                rule_id="POS001",
                name="单票仓位限制",
                rule_type=ComplianceRuleType.POSITION_LIMIT,
                threshold=0.20,  # 20%
                description="单一股票仓位不超过 20%",
            ),
            ComplianceRule(
                rule_id="SEC001",
                name="板块仓位限制",
                rule_type=ComplianceRuleType.SECTOR_LIMIT,
                threshold=0.40,  # 40%
                description="单一板块仓位不超过 40%",
            ),
            ComplianceRule(
                rule_id="CON001",
                name="集中度限制",
                rule_type=ComplianceRuleType.CONCENTRATION_LIMIT,
                threshold=0.50,  # 50%
                description="前 5 大持仓不超过 50%",
            ),
            ComplianceRule(
                rule_id="LEV001",
                name="杠杆限制",
                rule_type=ComplianceRuleType.LEVERAGE_LIMIT,
                threshold=2.0,  # 2x
                description="总杠杆不超过 2 倍",
            ),
            ComplianceRule(
                rule_id="LIQ001",
                name="流动性要求",
                rule_type=ComplianceRuleType.LIQUIDITY_REQUIREMENT,
                threshold=0.10,  # 10%
                description="现金比例不低于 10%",
            ),
        ]

    def add_rule(self, rule: ComplianceRule):
        """添加合规规则"""
        self.rules.append(rule)

    def add_to_blacklist(self, symbol: str):
        """添加黑名单"""
        self.blacklist.add(symbol)

    def add_to_whitelist(self, symbol: str):
        """添加白名单"""
        self.whitelist.add(symbol)

    def check_trade(
        self,
        trade: Dict,
        portfolio_state: Dict,
    ) -> ComplianceReport:
        """
        检查交易合规性

        Args:
            trade: 交易信息
            portfolio_state: 组合状态

        Returns:
            合规报告
        """
        checks = []
        violations = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            check = self._check_rule(rule, trade, portfolio_state)
            checks.append(check)

            if check.status in [ComplianceStatus.VIOLATION, ComplianceStatus.BLOCKED]:
                violations.append(f"{rule.name}: {check.message}")

        # 黑名单检查
        if trade.get("symbol") in self.blacklist:
            violations.append(f"股票 {trade['symbol']} 在黑名单中")

        # 白名单检查（如果有白名单）
        if self.whitelist and trade.get("symbol") not in self.whitelist:
            violations.append(f"股票 {trade['symbol']} 不在白名单中")

        # 确定整体状态
        if any(c.status == ComplianceStatus.BLOCKED for c in checks):
            overall_status = ComplianceStatus.BLOCKED
        elif violations:
            overall_status = ComplianceStatus.VIOLATION
        elif any(c.status == ComplianceStatus.WARNING for c in checks):
            overall_status = ComplianceStatus.WARNING
        else:
            overall_status = ComplianceStatus.PASS

        # 生成建议
        recommendations = self._generate_recommendations(violations)

        report = ComplianceReport(
            trade_id=trade.get("trade_id", "unknown"),
            timestamp=datetime.now().timestamp(),
            overall_status=overall_status,
            checks=checks,
            violations=violations,
            recommendations=recommendations,
        )

        # 记录审计日志
        self.audit_log.append(report)

        return report

    def _check_rule(
        self,
        rule: ComplianceRule,
        trade: Dict,
        portfolio_state: Dict,
    ) -> ComplianceCheck:
        """检查单个规则"""
        if rule.rule_type == ComplianceRuleType.POSITION_LIMIT:
            return self._check_position_limit(rule, trade, portfolio_state)
        elif rule.rule_type == ComplianceRuleType.SECTOR_LIMIT:
            return self._check_sector_limit(rule, trade, portfolio_state)
        elif rule.rule_type == ComplianceRuleType.LEVERAGE_LIMIT:
            return self._check_leverage_limit(rule, portfolio_state)
        elif rule.rule_type == ComplianceRuleType.LIQUIDITY_REQUIREMENT:
            return self._check_liquidity(rule, portfolio_state)
        else:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.PASS,
                actual_value=0,
                threshold=rule.threshold,
                message="检查通过",
            )

    def _check_position_limit(
        self,
        rule: ComplianceRule,
        trade: Dict,
        portfolio_state: Dict,
    ) -> ComplianceCheck:
        """检查仓位限制"""
        symbol = trade.get("symbol", "")
        positions = portfolio_state.get("positions", {})
        portfolio_value = portfolio_state.get("total_value", 1)

        current_position = positions.get(symbol, {}).get("value", 0)
        trade_value = trade.get("quantity", 0) * trade.get("price", 0)

        if trade.get("side") == "buy":
            new_position = current_position + trade_value
        else:
            new_position = current_position - trade_value

        position_pct = new_position / portfolio_value if portfolio_value > 0 else 0

        if position_pct > rule.threshold:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.VIOLATION,
                actual_value=position_pct,
                threshold=rule.threshold,
                message=f"仓位 {position_pct:.2%} 超过限制 {rule.threshold:.2%}",
            )
        elif position_pct > rule.threshold * 0.9:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.WARNING,
                actual_value=position_pct,
                threshold=rule.threshold,
                message=f"仓位 {position_pct:.2%} 接近限制",
            )

        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.PASS,
            actual_value=position_pct,
            threshold=rule.threshold,
            message="检查通过",
        )

    def _check_sector_limit(
        self,
        rule: ComplianceRule,
        trade: Dict,
        portfolio_state: Dict,
    ) -> ComplianceCheck:
        """检查板块限制"""
        sector = trade.get("sector", "")
        sector_allocation = portfolio_state.get("sector_allocation", {})
        portfolio_value = portfolio_state.get("total_value", 1)

        current_sector_value = sector_allocation.get(sector, 0)
        trade_value = trade.get("quantity", 0) * trade.get("price", 0)

        if trade.get("side") == "buy":
            new_sector_value = current_sector_value + trade_value
        else:
            new_sector_value = current_sector_value - trade_value

        sector_pct = new_sector_value / portfolio_value if portfolio_value > 0 else 0

        if sector_pct > rule.threshold:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.VIOLATION,
                actual_value=sector_pct,
                threshold=rule.threshold,
                message=f"板块 {sector} 仓位 {sector_pct:.2%} 超过限制",
            )

        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.PASS,
            actual_value=sector_pct,
            threshold=rule.threshold,
            message="检查通过",
        )

    def _check_leverage_limit(
        self,
        rule: ComplianceRule,
        portfolio_state: Dict,
    ) -> ComplianceCheck:
        """检查杠杆限制"""
        total_value = portfolio_state.get("total_value", 1)
        cash = portfolio_state.get("cash", 0)
        leverage = (total_value - cash) / cash if cash > 0 else 0

        if leverage > rule.threshold:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.VIOLATION,
                actual_value=leverage,
                threshold=rule.threshold,
                message=f"杠杆 {leverage:.2f}x 超过限制 {rule.threshold:.1f}x",
            )

        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.PASS,
            actual_value=leverage,
            threshold=rule.threshold,
            message="检查通过",
        )

    def _check_liquidity(
        self,
        rule: ComplianceRule,
        portfolio_state: Dict,
    ) -> ComplianceCheck:
        """检查流动性"""
        total_value = portfolio_state.get("total_value", 1)
        cash = portfolio_state.get("cash", 0)
        cash_ratio = cash / total_value if total_value > 0 else 0

        if cash_ratio < rule.threshold:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.WARNING,
                actual_value=cash_ratio,
                threshold=rule.threshold,
                message=f"现金比例 {cash_ratio:.2%} 低于要求 {rule.threshold:.2%}",
            )

        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.PASS,
            actual_value=cash_ratio,
            threshold=rule.threshold,
            message="检查通过",
        )

    def _generate_recommendations(self, violations: List[str]) -> List[str]:
        """生成合规建议"""
        recommendations = []

        if violations:
            recommendations.append("🚨 交易存在合规问题，建议调整后再执行")
            for v in violations:
                recommendations.append(f"  - {v}")

        if not recommendations:
            recommendations.append("✅ 交易合规，可以执行")

        return recommendations

    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """获取审计日志"""
        return [r.to_dict() for r in self.audit_log[-limit:]]

    def get_compliance_summary(self) -> Dict:
        """获取合规总结"""
        total_checks = len(self.audit_log)
        passed = sum(1 for r in self.audit_log if r.overall_status == ComplianceStatus.PASS)
        violations = sum(1 for r in self.audit_log if r.overall_status in [
            ComplianceStatus.VIOLATION,
            ComplianceStatus.BLOCKED,
        ])

        return {
            "total_checks": total_checks,
            "passed": passed,
            "violations": violations,
            "pass_rate": f"{passed / total_checks:.1%}" if total_checks > 0 else "100%",
            "active_rules": sum(1 for r in self.rules if r.enabled),
            "blacklist_count": len(self.blacklist),
            "whitelist_count": len(self.whitelist),
        }
