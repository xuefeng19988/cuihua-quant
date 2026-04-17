"""
Phase 99: 多账户管理系统 (Multi-Account Management)

统一管理多个投资组合
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AccountType(Enum):
    """账户类型"""
    PERSONAL = "个人账户"
    INSTITUTIONAL = "机构账户"
    PAPER = "模拟账户"
    FAMILY = "家族账户"


class AccountStatus(Enum):
    """账户状态"""
    ACTIVE = "活跃"
    PAUSED = "暂停"
    CLOSED = "已关闭"


@dataclass
AccountInfo:
    """账户信息"""
    account_id: str
    name: str
    account_type: AccountType
    status: AccountStatus
    initial_capital: float
    current_value: float
    currency: str = "CNY"
    owner: str = ""
    created_at: float = 0
    strategies: List[str] = field(default_factory=list)
    risk_limit: float = 0.15  # 最大风险敞口

    def to_dict(self) -> Dict:
        return {
            "account_id": self.account_id,
            "name": self.name,
            "type": self.account_type.value,
            "status": self.status.value,
            "initial_capital": f"¥{self.initial_capital:,.2f}",
            "current_value": f"¥{self.current_value:,.2f}",
            "return": f"{(self.current_value - self.initial_capital) / self.initial_capital:.2%}",
            "currency": self.currency,
            "owner": self.owner,
            "strategies": self.strategies,
            "risk_limit": f"{self.risk_limit:.2%}",
        }


@dataclass
class MultiAccountReport:
    """多账户报告"""
    total_accounts: int
    total_aum: float  # 管理资产总额
    total_return: float
    avg_return: float
    accounts: List[AccountInfo]
    allocation_by_type: Dict
    allocation_by_strategy: Dict

    def to_dict(self) -> Dict:
        return {
            "total_accounts": self.total_accounts,
            "total_aum": f"¥{self.total_aum:,.2f}",
            "total_return": f"{self.total_return:.2%}",
            "avg_return": f"{self.avg_return:.2%}",
            "accounts": [a.to_dict() for a in self.accounts],
            "allocation_by_type": self.allocation_by_type,
            "allocation_by_strategy": self.allocation_by_strategy,
        }


class MultiAccountManager:
    """多账户管理器"""

    def __init__(self):
        self.accounts: Dict[str, AccountInfo] = {}

    def create_account(
        self,
        account_id: str,
        name: str,
        account_type: AccountType,
        initial_capital: float,
        owner: str = "",
        currency: str = "CNY",
        risk_limit: float = 0.15,
    ) -> AccountInfo:
        """创建账户"""
        account = AccountInfo(
            account_id=account_id,
            name=name,
            account_type=account_type,
            status=AccountStatus.ACTIVE,
            initial_capital=initial_capital,
            current_value=initial_capital,
            currency=currency,
            owner=owner,
            created_at=datetime.now().timestamp(),
            risk_limit=risk_limit,
        )

        self.accounts[account_id] = account
        return account

    def update_account_value(
        self,
        account_id: str,
        new_value: float,
    ) -> AccountInfo:
        """更新账户价值"""
        if account_id not in self.accounts:
            raise ValueError(f"Account {account_id} not found")

        account = self.accounts[account_id]
        account.current_value = new_value

        return account

    def add_strategy_to_account(
        self,
        account_id: str,
        strategy_name: str,
    ):
        """为账户添加策略"""
        if account_id not in self.accounts:
            raise ValueError(f"Account {account_id} not found")

        account = self.accounts[account_id]
        if strategy_name not in account.strategies:
            account.strategies.append(strategy_name)

    def pause_account(self, account_id: str):
        """暂停账户"""
        if account_id not in self.accounts:
            raise ValueError(f"Account {account_id} not found")

        self.accounts[account_id].status = AccountStatus.PAUSED

    def resume_account(self, account_id: str):
        """恢复账户"""
        if account_id not in self.accounts:
            raise ValueError(f"Account {account_id} not found")

        self.accounts[account_id].status = AccountStatus.ACTIVE

    def close_account(self, account_id: str):
        """关闭账户"""
        if account_id not in self.accounts:
            raise ValueError(f"Account {account_id} not found")

        self.accounts[account_id].status = AccountStatus.CLOSED

    def get_account(self, account_id: str) -> AccountInfo:
        """获取账户信息"""
        if account_id not in self.accounts:
            raise ValueError(f"Account {account_id} not found")
        return self.accounts[account_id]

    def get_active_accounts(self) -> List[AccountInfo]:
        """获取所有活跃账户"""
        return [a for a in self.accounts.values() if a.status == AccountStatus.ACTIVE]

    def generate_report(self) -> MultiAccountReport:
        """生成多账户报告"""
        active_accounts = self.get_active_accounts()

        if not active_accounts:
            return MultiAccountReport(
                total_accounts=0,
                total_aum=0,
                total_return=0,
                avg_return=0,
                accounts=[],
                allocation_by_type={},
                allocation_by_strategy={},
            )

        # 计算总额
        total_aum = sum(a.current_value for a in active_accounts)
        total_initial = sum(a.initial_capital for a in active_accounts)
        total_return = (total_aum - total_initial) / total_initial if total_initial > 0 else 0
        avg_return = sum(
            (a.current_value - a.initial_capital) / a.initial_capital
            for a in active_accounts
        ) / len(active_accounts)

        # 按类型分配
        allocation_by_type = {}
        for account in active_accounts:
            type_name = account.account_type.value
            allocation_by_type[type_name] = allocation_by_type.get(type_name, 0) + account.current_value

        # 按策略分配
        allocation_by_strategy = {}
        for account in active_accounts:
            for strategy in account.strategies:
                allocation = account.current_value / len(account.strategies) if account.strategies else 0
                allocation_by_strategy[strategy] = allocation_by_strategy.get(strategy, 0) + allocation

        return MultiAccountReport(
            total_accounts=len(active_accounts),
            total_aum=total_aum,
            total_return=total_return,
            avg_return=avg_return,
            accounts=active_accounts,
            allocation_by_type=allocation_by_type,
            allocation_by_strategy=allocation_by_strategy,
        )

    def cross_account_analysis(self) -> Dict:
        """跨账户分析"""
        if not self.accounts:
            return {"error": "No accounts available"}

        # 最佳/最差账户
        accounts = list(self.accounts.values())
        returns = [
            (a.current_value - a.initial_capital) / a.initial_capital
            for a in accounts
        ]

        best_idx = returns.index(max(returns))
        worst_idx = returns.index(min(returns))

        return {
            "best_account": {
                "name": accounts[best_idx].name,
                "return": f"{returns[best_idx]:.2%}",
            },
            "worst_account": {
                "name": accounts[worst_idx].name,
                "return": f"{returns[worst_idx]:.2%}",
            },
            "return_spread": f"{max(returns) - min(returns):.2%}",
            "avg_aum": f"¥{sum(a.current_value for a in accounts) / len(accounts):,.2f}",
        }
