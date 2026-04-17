"""
Phase 97: 自动报告生成器 (Automated Report Generator)

日报/周报/月报自动生成与分发
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class ReportType(Enum):
    """报告类型"""
    DAILY = "日报"
    WEEKLY = "周报"
    MONTHLY = "月报"
    QUARTERLY = "季报"
    ANNUAL = "年报"
    CUSTOM = "自定义"


@dataclass
class ReportConfig:
    """报告配置"""
    report_type: ReportType
    title: str
    include_sections: List[str]
    recipients: List[str]
    delivery_method: str  # email/file/console
    schedule: Optional[str] = None  # cron 表达式


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    metrics: Optional[Dict] = None
    charts: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "content": self.content,
            "metrics": self.metrics,
            "charts": self.charts,
        }


@dataclass
class GeneratedReport:
    """生成的报告"""
    report_id: str
    report_type: ReportType
    period: str
    generated_at: float
    sections: List[ReportSection]
    summary: str
    file_path: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "report_id": self.report_id,
            "type": self.report_type.value,
            "period": self.period,
            "generated_at": datetime.fromtimestamp(self.generated_at).strftime("%Y-%m-%d %H:%M:%S"),
            "sections": [s.to_dict() for s in self.sections],
            "summary": self.summary,
            "file_path": self.file_path,
        }


class AutomatedReportGenerator:
    """自动报告生成器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.templates = self._load_templates()
        self.history = []

    def _load_templates(self) -> Dict:
        """加载报告模板"""
        return {
            ReportType.DAILY: {
                "title": "翠花量化 - 每日交易报告",
                "sections": ["市场概览", "组合表现", "交易记录", "风险提示"],
            },
            ReportType.WEEKLY: {
                "title": "翠花量化 - 每周交易报告",
                "sections": ["市场回顾", "周度绩效", "策略表现", "下周展望"],
            },
            ReportType.MONTHLY: {
                "title": "翠花量化 - 月度投资报告",
                "sections": ["市场总结", "月度绩效", "因子分析", "风险评估", "下月计划"],
            },
        }

    def generate_report(
        self,
        report_type: ReportType,
        portfolio_data: Dict,
        market_data: Optional[Dict] = None,
        period: Optional[str] = None,
    ) -> GeneratedReport:
        """
        生成报告

        Args:
            report_type: 报告类型
            portfolio_data: 组合数据
            market_data: 市场数据
            period: 时间段

        Returns:
            生成的报告
        """
        if period is None:
            period = self._get_default_period(report_type)

        report_id = f"report_{report_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        template = self.templates.get(report_type, {})

        sections = []

        # 生成各章节
        for section_name in template.get("sections", []):
            section = self._generate_section(
                section_name, report_type, portfolio_data, market_data
            )
            sections.append(section)

        # 生成摘要
        summary = self._generate_summary(report_type, portfolio_data, sections)

        report = GeneratedReport(
            report_id=report_id,
            report_type=report_type,
            period=period,
            generated_at=datetime.now().timestamp(),
            sections=sections,
            summary=summary,
        )

        self.history.append(report)
        return report

    def _generate_section(
        self,
        section_name: str,
        report_type: ReportType,
        portfolio_data: Dict,
        market_data: Optional[Dict],
    ) -> ReportSection:
        """生成报告章节"""
        if section_name == "市场概览" or section_name == "市场回顾":
            return self._generate_market_overview(market_data)
        elif section_name == "组合表现" or section_name == "周度绩效" or section_name == "月度绩效":
            return self._generate_portfolio_performance(portfolio_data)
        elif section_name == "交易记录":
            return self._generate_trade_history(portfolio_data)
        elif section_name == "风险提示" or section_name == "风险评估":
            return self._generate_risk_assessment(portfolio_data)
        elif section_name == "策略表现":
            return self._generate_strategy_performance(portfolio_data)
        elif section_name == "因子分析":
            return self._generate_factor_analysis(portfolio_data)
        else:
            return ReportSection(
                title=section_name,
                content=f"{section_name} - 待完善",
            )

    def _generate_market_overview(self, market_data: Optional[Dict]) -> ReportSection:
        """生成市场概览"""
        if not market_data:
            return ReportSection(
                title="市场概览",
                content="市场数据暂无",
            )

        content = f"""
市场指数：{market_data.get('index', 'N/A')}
涨跌幅：{market_data.get('index_return', 'N/A')}
成交量：{market_data.get('volume', 'N/A')}
波动率：{market_data.get('volatility', 'N/A')}
        """

        return ReportSection(
            title="市场概览",
            content=content.strip(),
            metrics={
                "index": market_data.get("index"),
                "return": market_data.get("index_return"),
            },
        )

    def _generate_portfolio_performance(self, portfolio_data: Dict) -> ReportSection:
        """生成组合表现"""
        total_return = portfolio_data.get("total_return", 0)
        sharpe = portfolio_data.get("sharpe_ratio", 0)
        max_dd = portfolio_data.get("max_drawdown", 0)

        content = f"""
总收益率：{total_return:.2%}
夏普比率：{sharpe:.2f}
最大回撤：{max_dd:.2%}
当前仓位：{portfolio_data.get('position_ratio', 0):.2%}
        """

        return ReportSection(
            title="组合表现",
            content=content.strip(),
            metrics={
                "total_return": total_return,
                "sharpe_ratio": sharpe,
                "max_drawdown": max_dd,
            },
        )

    def _generate_trade_history(self, portfolio_data: Dict) -> ReportSection:
        """生成交易记录"""
        trades = portfolio_data.get("trades", [])

        content = f"""
本期交易数：{len(trades)}
买入次数：{sum(1 for t in trades if t.get('side') == 'buy')}
卖出次数：{sum(1 for t in trades if t.get('side') == 'sell')}
胜率：{portfolio_data.get('win_rate', 0):.2%}
        """

        return ReportSection(
            title="交易记录",
            content=content.strip(),
            metrics={"trade_count": len(trades)},
        )

    def _generate_risk_assessment(self, portfolio_data: Dict) -> ReportSection:
        """生成风险评估"""
        var_95 = portfolio_data.get("var_95", 0)
        concentration = portfolio_data.get("max_position_weight", 0)

        content = f"""
VaR (95%)：{var_95:.2%}
最大持仓集中度：{concentration:.2%}
风险等级：{portfolio_data.get('risk_level', '中等')}
        """

        return ReportSection(
            title="风险评估",
            content=content.strip(),
            metrics={"var_95": var_95},
        )

    def _generate_strategy_performance(self, portfolio_data: Dict) -> ReportSection:
        """生成策略表现"""
        strategies = portfolio_data.get("strategies", {})

        content = "策略表现：\n"
        for name, perf in strategies.items():
            content += f"- {name}: 收益 {perf.get('return', 0):.2%}\n"

        return ReportSection(
            title="策略表现",
            content=content.strip(),
        )

    def _generate_factor_analysis(self, portfolio_data: Dict) -> ReportSection:
        """生成因子分析"""
        factors = portfolio_data.get("factors", {})

        content = "因子贡献：\n"
        for name, contrib in factors.items():
            content += f"- {name}: {contrib:.2%}\n"

        return ReportSection(
            title="因子分析",
            content=content.strip(),
        )

    def _generate_summary(
        self,
        report_type: ReportType,
        portfolio_data: Dict,
        sections: List[ReportSection],
    ) -> str:
        """生成报告摘要"""
        total_return = portfolio_data.get("total_return", 0)

        if total_return > 0.05:
            verdict = "表现优秀"
        elif total_return > 0:
            verdict = "表现良好"
        elif total_return > -0.05:
            verdict = "需要关注"
        else:
            verdict = "需要调整"

        return f"本期{report_type.value}总结：组合{verdict}，收益率{total_return:.2%}"

    def _get_default_period(self, report_type: ReportType) -> str:
        """获取默认时间段"""
        now = datetime.now()

        if report_type == ReportType.DAILY:
            return now.strftime("%Y-%m-%d")
        elif report_type == ReportType.WEEKLY:
            week_ago = now - timedelta(days=7)
            return f"{week_ago.strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}"
        elif report_type == ReportType.MONTHLY:
            month_ago = now - timedelta(days=30)
            return f"{month_ago.strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}"
        else:
            return now.strftime("%Y-%m-%d")

    def export_report(self, report: GeneratedReport, format: str = "markdown") -> str:
        """导出报告"""
        if format == "markdown":
            return self._export_markdown(report)
        elif format == "html":
            return self._export_html(report)
        else:
            return str(report.to_dict())

    def _export_markdown(self, report: GeneratedReport) -> str:
        """导出为 Markdown"""
        md = f"# {report.report_type.value} - {report.period}\n\n"
        md += f"**生成时间**: {datetime.fromtimestamp(report.generated_at).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += f"## 摘要\n{report.summary}\n\n"

        for section in report.sections:
            md += f"## {section.title}\n{section.content}\n\n"

        return md

    def _export_html(self, report: GeneratedReport) -> str:
        """导出为 HTML"""
        html = f"<h1>{report.report_type.value} - {report.period}</h1>"
        html += f"<p>生成时间：{datetime.fromtimestamp(report.generated_at).strftime('%Y-%m-%d %H:%M:%S')}</p>"
        html += f"<h2>摘要</h2><p>{report.summary}</p>"

        for section in report.sections:
            html += f"<h2>{section.title}</h2><p>{section.content}</p>"

        return html

    def get_report_history(self, limit: int = 10) -> List[Dict]:
        """获取报告历史"""
        return [r.to_dict() for r in self.history[-limit:]]
