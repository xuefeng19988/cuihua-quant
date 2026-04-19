"""
Phase 88: 策略生命周期管理系统 (Strategy Lifecycle Management)

从研发到退役的完整策略管理
"""


from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time


class StrategyPhase(Enum):
    """策略阶段"""
    RESEARCH = "研究中"
    PAPER_TRADING = "模拟交易中"
    LIVE_SMALL = "实盘小资金"
    LIVE_FULL = "实盘全仓"
    DECLINING = "衰退中"
    RETIRED = "已退役"


class StrategyStatus(Enum):
    """策略状态"""
    ACTIVE = "活跃"
    PAUSED = "暂停"
    DISABLED = "禁用"


@dataclass
class StrategyInfo:
    """策略信息"""
    id: str
    name: str
    description: str
    author: str
    created_at: float
    phase: StrategyPhase
    status: StrategyStatus

    # 绩效指标
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0

    # 风险控制
    risk_limit: float = 0.1  # 最大风险敞口
    stop_loss: float = 0.15  # 止损线

    # 元数据
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "created_at": datetime.fromtimestamp(self.created_at).strftime("%Y-%m-%d"),
            "phase": self.phase.value,
            "status": self.status.value,
            "total_return": f"{self.total_return:.2%}",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "win_rate": f"{self.win_rate:.2%}",
            "profit_factor": f"{self.profit_factor:.2f}",
            "risk_limit": f"{self.risk_limit:.2%}",
            "stop_loss": f"{self.stop_loss:.2%}",
            "tags": self.tags,
        }


class StrategyLifecycleManager:
    """策略生命周期管理器"""

    def __init__(self):
        self.strategies: Dict[str, StrategyInfo] = {}
        self.phase_transitions: List[Dict] = []

    def create_strategy(
        self,
        id: str,
        name: str,
        description: str,
        author: str = "Unknown",
        tags: List[str] = None,
    ) -> StrategyInfo:
        """创建新策略（研究阶段）"""
        strategy = StrategyInfo(
            id=id,
            name=name,
            description=description,
            author=author,
            created_at=time.time(),
            phase=StrategyPhase.RESEARCH,
            status=StrategyStatus.ACTIVE,
            tags=tags or [],
        )

        self.strategies[id] = strategy
        self._log_transition(id, None, StrategyPhase.RESEARCH, "策略创建")
        return strategy

    def update_performance(self, strategy_id: str, metrics: Dict) -> StrategyInfo:
        """更新策略绩效"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy {strategy_id} not found")

        strategy = self.strategies[strategy_id]

        if "total_return" in metrics:
            strategy.total_return = metrics["total_return"]
        if "sharpe_ratio" in metrics:
            strategy.sharpe_ratio = metrics["sharpe_ratio"]
        if "max_drawdown" in metrics:
            strategy.max_drawdown = metrics["max_drawdown"]
        if "win_rate" in metrics:
            strategy.win_rate = metrics["win_rate"]
        if "profit_factor" in metrics:
            strategy.profit_factor = metrics["profit_factor"]

        # 自动评估是否需要降级
        self._auto_evaluate(strategy)

        return strategy

    def transition_phase(
        self,
        strategy_id: str,
        new_phase: StrategyPhase,
        reason: str = "",
    ) -> StrategyInfo:
        """转换策略阶段"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy {strategy_id} not found")

        strategy = self.strategies[strategy_id]
        old_phase = strategy.phase
        strategy.phase = new_phase

        self._log_transition(strategy_id, old_phase, new_phase, reason)

        return strategy

    def pause_strategy(self, strategy_id: str, reason: str = "") -> StrategyInfo:
        """暂停策略"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy {strategy_id} not found")

        strategy = self.strategies[strategy_id]
        strategy.status = StrategyStatus.PAUSED
        self._log_transition(
            strategy_id,
            strategy.phase,
            strategy.phase,
            f"策略暂停：{reason}",
        )

        return strategy

    def resume_strategy(self, strategy_id: str) -> StrategyInfo:
        """恢复策略"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy {strategy_id} not found")

        strategy = self.strategies[strategy_id]
        strategy.status = StrategyStatus.ACTIVE

        return strategy

    def retire_strategy(self, strategy_id: str, reason: str = "") -> StrategyInfo:
        """退役策略"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy {strategy_id} not found")

        strategy = self.strategies[strategy_id]
        old_phase = strategy.phase
        strategy.phase = StrategyPhase.RETIRED
        strategy.status = StrategyStatus.DISABLED

        self._log_transition(strategy_id, old_phase, StrategyPhase.RETIRED, f"退役：{reason}")

        return strategy

    def get_strategies_by_phase(self, phase: StrategyPhase) -> List[StrategyInfo]:
        """获取指定阶段的所有策略"""
        return [s for s in self.strategies.values() if s.phase == phase]

    def get_strategies_by_status(self, status: StrategyStatus) -> List[StrategyInfo]:
        """获取指定状态的所有策略"""
        return [s for s in self.strategies.values() if s.status == status]

    def get_dashboard(self) -> Dict:
        """获取策略仪表板"""
        phase_counts = {}
        for phase in StrategyPhase:
            phase_counts[phase.value] = len(self.get_strategies_by_phase(phase))

        status_counts = {}
        for status in StrategyStatus:
            status_counts[status.value] = len(self.get_strategies_by_status(status))

        # 活跃策略绩效
        active_strategies = self.get_strategies_by_status(StrategyStatus.ACTIVE)
        avg_sharpe = (
            sum(s.sharpe_ratio for s in active_strategies) / len(active_strategies)
            if active_strategies
            else 0
        )
        avg_return = (
            sum(s.total_return for s in active_strategies) / len(active_strategies)
            if active_strategies
            else 0
        )

        return {
            "total_strategies": len(self.strategies),
            "by_phase": phase_counts,
            "by_status": status_counts,
            "active_count": len(active_strategies),
            "avg_sharpe_ratio": f"{avg_sharpe:.2f}",
            "avg_total_return": f"{avg_return:.2%}",
            "recent_transitions": self.phase_transitions[-10:],
        }

    def _auto_evaluate(self, strategy: StrategyInfo):
        """自动评估策略是否需要阶段转换"""
        if strategy.phase == StrategyPhase.RETIRED:
            return

        # 研究 -> 模拟交易：夏普 > 1.0 且最大回撤 < 15%
        if (
            strategy.phase == StrategyPhase.RESEARCH
            and strategy.sharpe_ratio > 1.0
            and strategy.max_drawdown > -0.15
        ):
            self.transition_phase(
                strategy.id,
                StrategyPhase.PAPER_TRADING,
                "回测表现良好，进入模拟交易",
            )

        # 模拟交易 -> 实盘小资金：模拟夏普 > 1.2
        elif (
            strategy.phase == StrategyPhase.PAPER_TRADING
            and strategy.sharpe_ratio > 1.2
            and strategy.max_drawdown > -0.12
        ):
            self.transition_phase(
                strategy.id,
                StrategyPhase.LIVE_SMALL,
                "模拟交易表现优秀，进入小资金实盘",
            )

        # 实盘小资金 -> 实盘全仓：实盘夏普 > 1.5
        elif (
            strategy.phase == StrategyPhase.LIVE_SMALL
            and strategy.sharpe_ratio > 1.5
            and strategy.max_drawdown > -0.10
        ):
            self.transition_phase(
                strategy.id,
                StrategyPhase.LIVE_FULL,
                "小资金实盘表现优异，进入全仓实盘",
            )

        # 衰退判断：夏普 < 0.5 或最大回撤 < -20%
        elif (
            strategy.phase in [StrategyPhase.LIVE_SMALL, StrategyPhase.LIVE_FULL]
            and (strategy.sharpe_ratio < 0.5 or strategy.max_drawdown < -0.20)
        ):
            self.transition_phase(
                strategy.id,
                StrategyPhase.DECLINING,
                "绩效衰退，需要重新评估",
            )

    def _log_transition(
        self,
        strategy_id: str,
        old_phase: Optional[StrategyPhase],
        new_phase: StrategyPhase,
        reason: str,
    ):
        """记录阶段转换"""
        self.phase_transitions.append({
            "strategy_id": strategy_id,
            "from_phase": old_phase.value if old_phase else None,
            "to_phase": new_phase.value,
            "reason": reason,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
