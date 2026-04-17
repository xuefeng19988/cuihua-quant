"""
Phase 32: WebSocket Real-time Updates
Real-time data push to web clients.
"""

import os
import sys
import json
import asyncio
import time
from typing import Dict, List, Set, Optional
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class WebSocketManager:
    """
    WebSocket connection manager for real-time updates.
    """
    
    def __init__(self):
        self.clients: Dict[str, object] = {}  # client_id -> websocket
        self.client_info: Dict[str, Dict] = {}  # client_id -> info
        self._channels: Dict[str, Set[str]] = {}  # channel -> client_ids
        
    async def connect(self, client_id: str, websocket, channels: List[str] = None):
        """Register a new WebSocket client."""
        self.clients[client_id] = websocket
        self.client_info[client_id] = {
            'connected_at': datetime.now().isoformat(),
            'channels': channels or ['default'],
            'messages_sent': 0
        }
        
        # Subscribe to channels
        for channel in (channels or ['default']):
            if channel not in self._channels:
                self._channels[channel] = set()
            self._channels[channel].add(client_id)
            
    async def disconnect(self, client_id: str):
        """Remove a WebSocket client."""
        if client_id in self.clients:
            del self.clients[client_id]
        if client_id in self.client_info:
            # Unsubscribe from channels
            for channel in self.client_info[client_id].get('channels', []):
                if channel in self._channels:
                    self._channels[channel].discard(client_id)
            del self.client_info[client_id]
            
    async def send_to_client(self, client_id: str, message: Dict):
        """Send message to specific client."""
        if client_id not in self.clients:
            return False
            
        ws = self.clients[client_id]
        try:
            await ws.send_json(message)
            if client_id in self.client_info:
                self.client_info[client_id]['messages_sent'] += 1
            return True
        except:
            await self.disconnect(client_id)
            return False
            
    async def broadcast(self, message: Dict, channel: str = 'default'):
        """Broadcast message to all clients in a channel."""
        if channel not in self._channels:
            return 0
            
        client_ids = self._channels[channel].copy()
        sent_count = 0
        
        for client_id in client_ids:
            if await self.send_to_client(client_id, message):
                sent_count += 1
                
        return sent_count
        
    async def broadcast_all(self, message: Dict):
        """Broadcast message to all connected clients."""
        client_ids = list(self.clients.keys())
        sent_count = 0
        
        for client_id in client_ids:
            if await self.send_to_client(client_id, message):
                sent_count += 1
                
        return sent_count
        
    def get_stats(self) -> Dict:
        """Get WebSocket statistics."""
        return {
            'connected_clients': len(self.clients),
            'channels': {ch: len(clients) for ch, clients in self._channels.items()},
            'client_info': self.client_info
        }
        
    def generate_report(self) -> str:
        """Generate WebSocket status report."""
        stats = self.get_stats()
        
        lines = []
        lines.append("=" * 50)
        lines.append("🔌 WebSocket 连接状态")
        lines.append("=" * 50)
        lines.append(f"\n📊 已连接客户端: {stats['connected_clients']}")
        
        if stats['channels']:
            lines.append(f"\n📡 频道")
            for channel, count in stats['channels'].items():
                lines.append(f"  {channel}: {count} 个客户端")
                
        return "\n".join(lines)


# Global WebSocket manager
ws_manager = WebSocketManager()


class RealtimeDataPublisher:
    """
    Publishes real-time market data to WebSocket clients.
    """
    
    def __init__(self):
        self.ws_manager = ws_manager
        self._running = False
        
    async def publish_stock_price(self, code: str, price: float, change: float):
        """Publish stock price update."""
        message = {
            'type': 'price_update',
            'code': code,
            'price': price,
            'change': change,
            'change_pct': round((change / price) * 100, 2) if price > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        await self.ws_manager.broadcast(message, channel='prices')
        
    async def publish_signal(self, signal: Dict):
        """Publish trading signal."""
        message = {
            'type': 'signal',
            **signal,
            'timestamp': datetime.now().isoformat()
        }
        await self.ws_manager.broadcast(message, channel='signals')
        
    async def publish_alert(self, alert: Dict):
        """Publish alert notification."""
        message = {
            'type': 'alert',
            **alert,
            'timestamp': datetime.now().isoformat()
        }
        await self.ws_manager.broadcast(message, channel='alerts')
        
    async def publish_portfolio_update(self, portfolio: Dict):
        """Publish portfolio update."""
        message = {
            'type': 'portfolio',
            **portfolio,
            'timestamp': datetime.now().isoformat()
        }
        await self.ws_manager.broadcast(message, channel='portfolio')
        
    async def publish_system_status(self, status: Dict):
        """Publish system status update."""
        message = {
            'type': 'system',
            **status,
            'timestamp': datetime.now().isoformat()
        }
        await self.ws_manager.broadcast_all(message)
