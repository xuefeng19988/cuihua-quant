"""
Futu Trading Interface
Connects to Futu OpenD for order placement and portfolio management.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from futu import (
    OpenQuoteContext, 
    OpenSecTradeContext, 
    RET_OK, 
    TrdEnv,
    TrdMarket,
    TrdSide,
    OrderType,
    OrderStatus
)

class FutuTrader:
    """
    Trading execution via Futu OpenD.
    Supports both simulated (paper) trading and live trading.
    """
    
    def __init__(self, config: Dict = None, paper_trading: bool = True):
        """
        Initialize Futu Trader.
        
        Args:
            config: Trading configuration dict
            paper_trading: If True, use simulated trading
        """
        self.config = config or {}
        self.paper_trading = paper_trading
        
        # Connection settings
        self.host = os.getenv('FUTU_HOST', '127.0.0.1')
        self.quote_port = int(os.getenv('FUTU_QUOTE_PORT', '11112'))
        self.trd_port = int(os.getenv('FUTU_TRD_PORT', '11113'))
        
        self.quote_ctx = None
        self.trd_ctx = None
        self.acc_id = None
        
        # Order tracking
        self.order_log = []
        
    def connect(self) -> bool:
        """Connect to Futu OpenD for both quote and trading."""
        try:
            # Connect quote context
            self.quote_ctx = OpenQuoteContext(host=self.host, port=self.quote_port)
            
            # Connect trading context (A-share market)
            self.trd_ctx = OpenSecTradeContext(
                filter_trdmarket=TrdMarket.CN,
                host=self.host,
                port=self.trd_port,
                security_firm=None
            )
            
            # Unlock trade if real trading (requires RSA key)
            if not self.paper_trading:
                rsa_path = os.getenv('FUTU_RSA_KEY', '')
                if rsa_path:
                    ret, msg = self.trd_ctx.unlock_trade(rsa_path)
                    if ret != RET_OK:
                        print(f"❌ Unlock trade failed: {msg}")
                        return False
                else:
                    print("⚠️ No RSA key found, defaulting to paper trading")
                    self.paper_trading = True
                    
            # Get account list
            trd_env = TrdEnv.SIMULATE if self.paper_trading else TrdEnv.REAL
            ret, acc_list = self.trd_ctx.get_acc_list()
            if ret == RET_OK and not acc_list.empty:
                # Filter by environment
                sim_accs = acc_list[acc_list['trd_env'] == trd_env]
                if not sim_accs.empty:
                    self.acc_id = sim_accs.iloc[0]['acc_id']
                else:
                    self.acc_id = acc_list.iloc[0]['acc_id']
                    
            mode = "SIMULATED" if self.paper_trading else "LIVE"
            print(f"✅ Futu Trader Connected ({mode}, Acc: {self.acc_id})")
            return True
            
        except Exception as e:
            print(f"❌ Futu connection error: {e}")
            return False
            
    def disconnect(self):
        """Close connections."""
        if self.quote_ctx:
            self.quote_ctx.close()
        if self.trd_ctx:
            self.trd_ctx.close()
        print("🔌 Disconnected from Futu.")
        
    def place_order(self, code: str, side: str, qty: int, price: Optional[float] = None) -> Dict:
        """
        Place a buy/sell order.
        
        Args:
            code: Stock code (e.g., 'SH.600519')
            side: 'BUY' or 'SELL'
            qty: Number of shares (must be multiple of 100 for A-shares)
            price: Limit price. If None, uses market price.
            
        Returns:
            Order result dict
        """
        if not self.trd_ctx:
            return {'success': False, 'error': 'Not connected'}
            
        trd_env = TrdEnv.SIMULATE if self.paper_trading else TrdEnv.REAL
        
        # Convert side
        if side.upper() == 'BUY':
            trd_side = TrdSide.BUY
        else:
            trd_side = TrdSide.SELL
            
        # Get current price if not provided
        if price is None:
            ret, snapshot = self.quote_ctx.get_market_snapshot([code])
            if ret == RET_OK and not snapshot.empty:
                price = snapshot.iloc[0]['last_price']
            else:
                return {'success': False, 'error': f'Cannot get price for {code}'}
                
        # Place order (Limit order)
        ret, data = self.trd_ctx.place_order(
            price=price,
            qty=qty,
            code=code,
            trd_side=trd_side,
            order_type=OrderType.NORMAL,
            trd_env=trd_env,
            acc_id=self.acc_id
        )
        
        if ret == RET_OK:
            order_id = data.iloc[0]['order_id'] if not data.empty else None
            result = {
                'success': True,
                'order_id': order_id,
                'code': code,
                'side': side,
                'qty': qty,
                'price': price,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.order_log.append(result)
            print(f"✅ Order placed: {side} {qty} {code} @ {price}")
            return result
        else:
            return {'success': False, 'error': data}
            
    def check_order_status(self, order_id: str) -> Dict:
        """Check status of a specific order."""
        if not self.trd_ctx:
            return {'error': 'Not connected'}
            
        trd_env = TrdEnv.SIMULATE if self.paper_trading else TrdEnv.REAL
        
        ret, data = self.trd_ctx.order_filter_query(
            order_id=order_id,
            trd_env=trd_env,
            acc_id=self.acc_id
        )
        
        if ret == RET_OK and not data.empty:
            return {
                'order_id': order_id,
                'status': data.iloc[0].get('order_status', 'UNKNOWN'),
                'filled_qty': data.iloc[0].get('qty', 0)
            }
        return {'error': 'Order not found'}
        
    def get_positions(self) -> List[Dict]:
        """Get current positions."""
        if not self.trd_ctx:
            return []
            
        trd_env = TrdEnv.SIMULATE if self.paper_trading else TrdEnv.REAL
        
        ret, data = self.trd_ctx.position_list_query(
            trd_env=trd_env,
            acc_id=self.acc_id
        )
        
        if ret == RET_OK and not data.empty:
            positions = []
            for _, row in data.iterrows():
                positions.append({
                    'code': row.get('code'),
                    'name': row.get('stock_name', ''),
                    'qty': row.get('qty', 0),
                    'cost_price': row.get('cost_price', 0),
                    'market_value': row.get('market_val', 0),
                    'pnl': row.get('pl_val', 0),
                    'pnl_pct': row.get('pl_ratio', 0)
                })
            return positions
        return []
        
    def get_account_info(self) -> Dict:
        """Get account funds and assets info."""
        if not self.trd_ctx:
            return {}
            
        trd_env = TrdEnv.SIMULATE if self.paper_trading else TrdEnv.REAL
        
        ret, data = self.trd_ctx.acc_cash_query(
            trd_env=trd_env,
            acc_id=self.acc_id
        )
        
        if ret == RET_OK and not data.empty:
            row = data.iloc[0]
            return {
                'total_assets': row.get('total_assets', 0),
                'cash': row.get('cash', 0),
                'market_value': row.get('market_val', 0),
                'available_cash': row.get('avl_withdrawal_cash', 0),
                'frozen_cash': row.get('frozen_cash', 0),
                'currency': row.get('currency', 'CNY')
            }
        return {}

    def execute_signal(self, signal: Dict) -> Dict:
        """
        Execute a trading signal from the strategy engine.
        
        Args:
            signal: Dict with keys: 'code', 'action' (BUY/SELL), 'shares', 'price'
            
        Returns:
            Execution result
        """
        code = signal.get('code')
        action = signal.get('action', 'BUY')
        shares = signal.get('shares', 0)
        price = signal.get('price')
        
        if not code or shares <= 0:
            return {'success': False, 'error': 'Invalid signal'}
            
        # Round down to nearest 100 (A-share lot size)
        shares = (shares // 100) * 100
        if shares == 0:
            return {'success': False, 'error': 'Shares too small'}
            
        return self.place_order(code, action, shares, price)
