"""
Core module - Dependency Injection container.
"""

import os
import sys
from typing import Dict, Any, Type, TypeVar, Optional, Callable
from dataclasses import dataclass, field

T = TypeVar("T")

@dataclass
class ServiceRegistration:
    """Service registration info."""
    instance: Optional[Any] = None
    factory: Optional[Callable] = None
    singleton: bool = True

class DIContainer:
    """
    Simple dependency injection container.
    Supports singleton, transient, and factory registrations.
    """
    
    def __init__(self):
        self._services: Dict[str, ServiceRegistration] = {}
        self._singletons: Dict[str, Any] = {}
        
    def register_singleton(self, interface: str, instance: Any) -> None:
        """Register a singleton instance."""
        self._services[interface] = ServiceRegistration(instance=instance, singleton=True)
        
    def register_transient(self, interface: str, factory: Callable) -> None:
        """Register a transient factory."""
        self._services[interface] = ServiceRegistration(factory=factory, singleton=False)
        
    def register_factory(self, interface: str, factory: Callable) -> None:
        """Register a singleton factory."""
        self._services[interface] = ServiceRegistration(factory=factory, singleton=True)
        
    def resolve(self, interface: str) -> Any:
        """Resolve a service by interface name."""
        if interface not in self._services:
            raise KeyError(f"Service not registered: {interface}")
            
        registration = self._services[interface]
        
        # Return existing singleton
        if registration.singleton and interface in self._singletons:
            return self._singletons[interface]
            
        # Create from factory
        if registration.factory:
            instance = registration.factory(self)
        elif registration.instance:
            instance = registration.instance
        else:
            raise ValueError(f"Invalid registration for {interface}")
            
        # Cache singleton
        if registration.singleton:
            self._singletons[interface] = instance
            
        return instance
        
    def has(self, interface: str) -> bool:
        """Check if service is registered."""
        return interface in self._services
        
    def build(self) -> None:
        """Initialize all singleton services."""
        for interface in self._services:
            if self._services[interface].singleton:
                self.resolve(interface)
                
    def generate_report(self) -> str:
        """Generate DI container report."""
        lines = []
        lines.append("=" * 50)
        lines.append("📦 依赖注入容器报告")
        lines.append("=" * 50)
        lines.append(f"\n已注册服务: {len(self._services)}")
        for interface, reg in self._services.items():
            type_str = "Singleton" if reg.singleton else "Transient"
            lines.append(f"  ✅ {interface} ({type_str})")
        return "\n".join(lines)

# Global container instance
container = DIContainer()
