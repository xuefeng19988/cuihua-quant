"""
Core module - Type definitions and common utilities.
"""
from typing import Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class MarketType(Enum):
    """Market type enumeration."""
    A_SHARE = "A_SHARE"
    HK_SHARE = "HK_SHARE"
    US_SHARE = "US_SHARE"
    CRYPTO = "CRYPTO"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"

class SignalDirection(Enum):
    """Trading signal direction."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"

class TimeFrame(Enum):
    """K-line time frame."""
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"

@dataclass
class OHLCV:
    """OHLCV data point."""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float = 0.0
    turnover_rate: float = 0.0

@dataclass
class TradeSignal:
    """Trading signal."""
    code: str
    direction: SignalDirection
    score: float
    strength: float
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    strategy: str = ""

@dataclass
class TradeOrder:
    """Trade order."""
    code: str
    action: str  # BUY/SELL
    shares: int
    price: float
    status: OrderStatus = OrderStatus.PENDING
    order_id: str = ""
    filled_price: float = 0.0
    filled_shares: int = 0
    commission: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Position:
    """Stock position."""
    code: str
    shares: int
    avg_cost: float
    current_price: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    entry_date: datetime = field(default_factory=datetime.now)

@dataclass
class Portfolio:
    """Portfolio state."""
    total_value: float = 0.0
    cash: float = 0.0
    market_value: float = 0.0
    positions: Dict[str, Position] = field(default_factory=dict)
    daily_pnl: float = 0.0
    total_pnl: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
