"""
Core module interfaces for dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime

class IDataFetcher(ABC):
    """Interface for data fetching."""
    
    @abstractmethod
    def fetch(self, code: str, **kwargs) -> Any:
        """Fetch data for a stock."""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if data source is available."""
        pass

class ISignalGenerator(ABC):
    """Interface for signal generation."""
    
    @abstractmethod
    def generate(self, codes: List[str], **kwargs) -> Any:
        """Generate trading signals."""
        pass

class IStrategy(ABC):
    """Interface for trading strategies."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass
        
    @abstractmethod
    def generate_signals(self, data: Any) -> Any:
        """Generate signals from data."""
        pass
        
    @abstractmethod
    def get_parameters(self) -> Dict:
        """Get strategy parameters."""
        pass

class IOrderExecutor(ABC):
    """Interface for order execution."""
    
    @abstractmethod
    def execute(self, order: Any) -> Any:
        """Execute an order."""
        pass
        
    @abstractmethod
    def cancel(self, order_id: str) -> bool:
        """Cancel an order."""
        pass
        
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to broker."""
        pass

class IRiskManager(ABC):
    """Interface for risk management."""
    
    @abstractmethod
    def check_order(self, order: Any) -> bool:
        """Check if order passes risk checks."""
        pass
        
    @abstractmethod
    def check_portfolio(self, portfolio: Any) -> bool:
        """Check portfolio risk limits."""
        pass
        
    @abstractmethod
    def emergency_halt(self, reason: str) -> None:
        """Emergency halt all trading."""
        pass

class INotifier(ABC):
    """Interface for notifications."""
    
    @abstractmethod
    def send(self, message: str, channel: str = "", **kwargs) -> bool:
        """Send notification."""
        pass
        
    @abstractmethod
    def get_channels(self) -> List[str]:
        """Get available notification channels."""
        pass

class ICache(ABC):
    """Interface for caching."""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache."""
        pass
        
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
        
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache."""
        pass
