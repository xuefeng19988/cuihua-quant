"""
Phase 101: 加密货币交易模块 (Cryptocurrency Trading Module)

完整加密货币交易支持
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CryptoExchange(Enum):
    """交易所"""
    BINANCE = "币安"
    OKX = "OKX"
    HUOBI = "火币"
    BYBIT = "Bybit"
    COINBASE = "Coinbase"


class CryptoAsset(Enum):
    """加密资产"""
    BTC = "BTC"
    ETH = "ETH"
    BNB = "BNB"
    SOL = "SOL"
    XRP = "XRP"
    DOGE = "DOGE"
    ADA = "ADA"
    AVAX = "AVAX"


@dataclass
class CryptoMarketData:
    """加密货币市场数据"""
    symbol: str
    price: float
    volume_24h: float
    market_cap: float
    price_change_24h: float
    price_change_7d: float
    high_24h: float
    low_24h: float
    timestamp: float

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "price": f"${self.price:,.2f}",
            "volume_24h": f"${self.volume_24h:,.0f}",
            "market_cap": f"${self.market_cap:,.0f}",
            "change_24h": f"{self.price_change_24h:.2%}",
            "change_7d": f"{self.price_change_7d:.2%}",
            "high_24h": f"${self.high_24h:,.2f}",
            "low_24h": f"${self.low_24h:,.2f}",
        }


@dataclass
class CryptoPortfolio:
    """加密货币组合"""
    holdings: Dict[str, float]  # {symbol: amount}
    total_value_usd: float
    allocation_pct: Dict[str, float]
    pnl_24h: float
    pnl_7d: float

    def to_dict(self) -> Dict:
        return {
            "holdings": self.holdings,
            "total_value_usd": f"${self.total_value_usd:,.2f}",
            "allocation_pct": {k: f"{v:.1%}" for k, v in self.allocation_pct.items()},
            "pnl_24h": f"{self.pnl_24h:.2%}",
            "pnl_7d": f"{self.pnl_7d:.2%}",
        }


class CryptoTradingModule:
    """加密货币交易模块"""

    def __init__(self, exchange: CryptoExchange = CryptoExchange.BINANCE):
        self.exchange = exchange
        self.prices: Dict[str, float] = {}
        self.portfolio: Dict[str, float] = {}
        self.trade_history = []

    def fetch_market_data(self, symbols: List[str]) -> List[CryptoMarketData]:
        """
        获取加密货币市场数据
        实际实现应调用交易所 API
        """
        import random

        market_data = []
        base_prices = {
            "BTC": 65000,
            "ETH": 3500,
            "BNB": 580,
            "SOL": 145,
            "XRP": 0.52,
            "DOGE": 0.15,
            "ADA": 0.45,
            "AVAX": 35,
        }

        for symbol in symbols:
            base = base_prices.get(symbol, 100)
            change_24h = random.uniform(-0.05, 0.05)
            change_7d = random.uniform(-0.15, 0.15)

            price = base * (1 + change_24h)
            volume_24h = base * random.uniform(100000, 1000000)
            market_cap = price * random.uniform(1000000, 100000000)

            data = CryptoMarketData(
                symbol=symbol,
                price=price,
                volume_24h=volume_24h,
                market_cap=market_cap,
                price_change_24h=change_24h,
                price_change_7d=change_7d,
                high_24h=price * (1 + abs(change_24h) * 0.5),
                low_24h=price * (1 - abs(change_24h) * 0.5),
                timestamp=datetime.now().timestamp(),
            )
            market_data.append(data)
            self.prices[symbol] = price

        return market_data

    def create_portfolio(self, allocations: Dict[str, float], total_value: float) -> CryptoPortfolio:
        """
        创建加密货币组合

        Args:
            allocations: {symbol: percentage}
            total_value: 总价值 (USD)

        Returns:
            组合信息
        """
        holdings = {}
        for symbol, pct in allocations.items():
            price = self.prices.get(symbol, 0)
            if price > 0:
                amount = (total_value * pct) / price
                holdings[symbol] = amount

        # 计算 PnL (模拟)
        import random
        pnl_24h = random.uniform(-0.03, 0.03)
        pnl_7d = random.uniform(-0.10, 0.10)

        return CryptoPortfolio(
            holdings=holdings,
            total_value_usd=total_value,
            allocation_pct=allocations,
            pnl_24h=pnl_24h,
            pnl_7d=pnl_7d,
        )

    def calculate_crypto_indicators(self, market_data: List[CryptoMarketData]) -> Dict:
        """计算加密货币特有指标"""
        if not market_data:
            return {}

        # 总市值
        total_market_cap = sum(md.market_cap for md in market_data)

        # 总成交量
        total_volume = sum(md.volume_24h for md in market_data)

        # 涨跌比
        gainers = sum(1 for md in market_data if md.price_change_24h > 0)
        losers = len(market_data) - gainers

        # 波动率
        import statistics
        changes = [md.price_change_24h for md in market_data]
        avg_volatility = statistics.stdev(changes) if len(changes) > 1 else 0

        return {
            "total_market_cap": f"${total_market_cap:,.0f}",
            "total_volume_24h": f"${total_volume:,.0f}",
            "gainers": gainers,
            "losers": losers,
            "advance_decline_ratio": f"{gainers / losers:.2f}" if losers > 0 else "N/A",
            "avg_volatility": f"{avg_volatility:.2%}",
            "fear_greed_index": self._calculate_fear_greed(market_data),
        }

    def _calculate_fear_greed(self, market_data: List[CryptoMarketData]) -> str:
        """计算恐惧贪婪指数（简化版）"""
        if not market_data:
            return "neutral"

        avg_change = sum(md.price_change_24h for md in market_data) / len(market_data)

        if avg_change > 0.03:
            return "greed"
        elif avg_change > 0:
            return "neutral"
        elif avg_change > -0.03:
            return "fear"
        else:
            return "extreme_fear"

    def rebalance_crypto_portfolio(
        self,
        current_portfolio: CryptoPortfolio,
        target_allocations: Dict[str, float],
    ) -> List[Dict]:
        """
        再平衡加密货币组合

        Args:
            current_portfolio: 当前组合
            target_allocations: 目标配置

        Returns:
            交易列表
        """
        trades = []
        total_value = current_portfolio.total_value_usd

        for symbol, target_pct in target_allocations.items():
            current_amount = current_portfolio.holdings.get(symbol, 0)
            price = self.prices.get(symbol, 0)

            if price == 0:
                continue

            current_value = current_amount * price
            target_value = total_value * target_pct
            diff_value = target_value - current_value

            if abs(diff_value) > total_value * 0.01:  # 1% 阈值
                diff_amount = abs(diff_value) / price
                side = "buy" if diff_value > 0 else "sell"

                trades.append({
                    "symbol": symbol,
                    "side": side,
                    "amount": diff_amount,
                    "value": abs(diff_value),
                    "price": price,
                })

        return trades

    def get_portfolio_summary(self, portfolio: CryptoPortfolio) -> Dict:
        """获取组合总结"""
        return {
            "exchange": self.exchange.value,
            "portfolio": portfolio.to_dict(),
            "indicators": self.calculate_crypto_indicators([]),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
