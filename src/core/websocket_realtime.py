"""
Phase 68: Real-time WebSocket Integration
Real-time data streaming to WebUI with live updates.
"""

import os
import sys
import json
import time
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Callable, Set

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class WebSocketServer:
    """
    Simple WebSocket server for real-time data streaming.
    """
    def __init__(self, host: str = '0.0.0.0', port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set = set()
        self._running = False
        self._data_publishers: Dict[str, List[Callable]] = {}
        
    async def register(self, websocket):
        """Register a new client."""
        self.clients.add(websocket)
        print(f"🔌 Client connected. Total: {len(self.clients)}")
        
        # Send welcome message
        await websocket.send(json.dumps({
            'type': 'welcome',
            'message': 'Connected to Cuihua Quant WebSocket Server',
            'timestamp': datetime.now().isoformat()
        }))
        
    async def unregister(self, websocket):
        """Unregister a client."""
        self.clients.discard(websocket)
        print(f"🔌 Client disconnected. Total: {len(self.clients)}")
        
    async def broadcast(self, message: Dict, channel: str = 'default'):
        """Broadcast message to all clients."""
        if not self.clients:
            return
            
        message_str = json.dumps(message)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(message_str)
            except Exception as e:
                disconnected.add(client)
                
        # Remove disconnected clients
        self.clients -= disconnected
        
    def publish_data(self, channel: str, data: Dict):
        """Publish data to a channel."""
        message = {
            'type': 'data',
            'channel': channel,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        # Run broadcast in event loop
        if self._running:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.broadcast(message, channel))
            loop.close()
            
    def start(self):
        """Start WebSocket server."""
        try:
            import websockets
        except ImportError:
            print("⚠️ websockets not installed. Run: pip install websockets")
            return
            
        self._running = True
        
        async def handler(websocket, path):
            await self.register(websocket)
            try:
                async for message in websocket:
                    # Handle incoming messages
                    try:
                        data = json.loads(message)
                        await self.handle_message(websocket, data)
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                pass
            finally:
                await self.unregister(websocket)
                
        async def main():
            async with websockets.serve(handler, self.host, self.port):
                print(f"🌐 WebSocket server started on ws://{self.host}:{self.port}")
                await asyncio.Future()  # Run forever
                
        threading.Thread(target=asyncio.run, args=(main(),), daemon=True).start()
        
    async def handle_message(self, websocket, data: Dict):
        """Handle incoming WebSocket messages."""
        msg_type = data.get('type', '')
        
        if msg_type == 'subscribe':
            channel = data.get('channel', 'default')
            await websocket.send(json.dumps({
                'type': 'subscribed',
                'channel': channel
            }))
        elif msg_type == 'ping':
            await websocket.send(json.dumps({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            }))


class RealtimeDataPublisher:
    """
    Publish real-time market data to WebSocket clients.
    """
    def __init__(self, ws_server: WebSocketServer = None):
        self.ws_server = ws_server
        
    def publish_stock_update(self, code: str, price: float, change: float, volume: int):
        """Publish stock price update."""
        if self.ws_server:
            self.ws_server.publish_data('stocks', {
                'code': code,
                'price': price,
                'change': change,
                'change_pct': round(change / price * 100, 2) if price > 0 else 0,
                'volume': volume
            })
            
    def publish_signal(self, code: str, signal: str, score: float, reason: str):
        """Publish trading signal."""
        if self.ws_server:
            self.ws_server.publish_data('signals', {
                'code': code,
                'signal': signal,
                'score': score,
                'reason': reason
            })
            
    def publish_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Publish system alert."""
        if self.ws_server:
            self.ws_server.publish_data('alerts', {
                'type': alert_type,
                'message': message,
                'severity': severity
            })
            
    def publish_portfolio_update(self, total_value: float, daily_pnl: float, 
                                 positions_count: int):
        """Publish portfolio update."""
        if self.ws_server:
            self.ws_server.publish_data('portfolio', {
                'total_value': total_value,
                'daily_pnl': daily_pnl,
                'daily_pnl_pct': round(daily_pnl / (total_value - daily_pnl) * 100, 2) if total_value != daily_pnl else 0,
                'positions_count': positions_count
            })


# JavaScript for WebSocket client integration
WEBSOCKET_CLIENT_JS = """
// WebSocket Client for Cuihua Quant WebUI
class CuihuaWebSocket {
    constructor(url = 'ws://localhost:8765') {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.callbacks = {};
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('✅ Connected to WebSocket server');
            this.reconnectAttempts = 0;
            this._trigger('connected');
            
            // Send ping every 30s
            setInterval(() => {
                if (this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({type: 'ping'}));
                }
            }, 30000);
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this._handleMessage(data);
            } catch (e) {
                console.error('❌ Invalid message:', e);
            }
        };
        
        this.ws.onclose = () => {
            console.log('🔌 Disconnected from WebSocket server');
            this._trigger('disconnected');
            this._reconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };
    }
    
    _handleMessage(data) {
        const channel = data.channel || 'default';
        if (this.callbacks[channel]) {
            this.callbacks[channel].forEach(cb => cb(data));
        }
        if (this.callbacks['*']) {
            this.callbacks['*'].forEach(cb => cb(data));
        }
    }
    
    _reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }
    
    subscribe(channel, callback) {
        if (!this.callbacks[channel]) {
            this.callbacks[channel] = [];
        }
        this.callbacks[channel].push(callback);
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({type: 'subscribe', channel: channel}));
        }
    }
    
    on(event, callback) {
        this._trigger = this._trigger || (() => {});
        const originalTrigger = this._trigger;
        this._trigger = (eventType, data) => {
            if (eventType === event) callback(data);
            originalTrigger(eventType, data);
        };
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Usage:
// const ws = new CuihuaWebSocket();
// ws.connect();
// ws.subscribe('stocks', (data) => {
//     console.log('Stock update:', data.data);
//     // Update UI
// });
// ws.subscribe('signals', (data) => {
//     console.log('New signal:', data.data);
//     // Show notification
// });
"""


if __name__ == "__main__":
    print("✅ WebSocket modules loaded successfully")
    print("\n📝 使用方式:")
    print("1. 启动 WebSocket 服务器:")
    print("   ws_server = WebSocketServer()")
    print("   ws_server.start()")
    print("\n2. 发布数据:")
    print("   publisher = RealtimeDataPublisher(ws_server)")
    print("   publisher.publish_stock_update('SH.600519', 1500.0, 0.02, 1e6)")
    print("\n3. 前端连接:")
    print("   const ws = new CuihuaWebSocket();")
    print("   ws.connect();")
    print("   ws.subscribe('stocks', callback);")
