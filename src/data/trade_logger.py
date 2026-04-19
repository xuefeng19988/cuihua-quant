"""
Trade Logger
Records all trading activity to SQLite for audit and analysis.
"""

import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class TradeLogger:
    """
    Logs trading signals, orders, and executions to SQLite.
    Tables:
    - signal_log: Generated signals
    - order_log: Placed orders
    - pnl_log: Daily P&L snapshots
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(project_root, 'data', 'trade_log.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
        
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def _init_db(self):
        """Create tables if not exist."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Signal log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                code TEXT NOT NULL,
                strategy TEXT NOT NULL,
                direction TEXT NOT NULL,
                score REAL,
                strength REAL,
                reason TEXT,
                price REAL
            )
        ''')
        
        # Order log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                code TEXT NOT NULL,
                action TEXT NOT NULL,
                shares INTEGER,
                price REAL,
                estimated_value REAL,
                status TEXT DEFAULT 'PENDING',
                order_id TEXT,
                filled_price REAL,
                filled_shares INTEGER,
                pnl REAL,
                notes TEXT
            )
        ''')
        
        # P&L daily snapshot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pnl_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                total_value REAL,
                cash REAL,
                market_value REAL,
                daily_pnl REAL,
                daily_pnl_pct REAL,
                num_positions INTEGER,
                num_trades INTEGER,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_signal(self, code: str, strategy: str, direction: str, 
                   score: float = 0.0, strength: float = 0.0, 
                   reason: str = "", price: float = 0.0):
        """Log a trading signal."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO signal_log (timestamp, code, strategy, direction, score, strength, reason, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), code, strategy, direction, score, strength, reason, price))
        conn.commit()
        conn.close()
        
    def log_order(self, code: str, action: str, shares: int = 0, price: float = 0.0,
                  estimated_value: float = 0.0, status: str = 'PENDING',
                  order_id: str = None, notes: str = ""):
        """Log an order."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO order_log (timestamp, code, action, shares, price, estimated_value, status, order_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), code, action, shares, price, estimated_value, status, order_id, notes))
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        return order_id
        
    def update_order(self, order_id: int, filled_price: float = None, 
                     filled_shares: int = None, pnl: float = None, 
                     status: str = None, notes: str = None):
        """Update order with fill info."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        updates = []
        params = []
        if filled_price is not None:
            updates.append('filled_price = ?')
            params.append(filled_price)
        if filled_shares is not None:
            updates.append('filled_shares = ?')
            params.append(filled_shares)
        if pnl is not None:
            updates.append('pnl = ?')
            params.append(pnl)
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        if notes is not None:
            updates.append('notes = ?')
            params.append(notes)
            
        if updates:
            params.append(order_id)
            sql = f"UPDATE order_log SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, params)
            conn.commit()
        conn.close()
        
    def log_daily_pnl(self, date: str = None, total_value: float = 0.0,
                      cash: float = 0.0, market_value: float = 0.0,
                      daily_pnl: float = 0.0, daily_pnl_pct: float = 0.0,
                      num_positions: int = 0, num_trades: int = 0,
                      notes: str = ""):
        """Log daily P&L snapshot."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO pnl_log 
            (date, total_value, cash, market_value, daily_pnl, daily_pnl_pct, num_positions, num_trades, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, total_value, cash, market_value, daily_pnl, daily_pnl_pct, num_positions, num_trades, notes))
        conn.commit()
        conn.close()
        
    def get_recent_signals(self, limit: int = 20) -> List[Dict]:
        """Get recent trading signals."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM signal_log ORDER BY id DESC LIMIT ?', (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
        
    def get_recent_orders(self, limit: int = 20) -> List[Dict]:
        """Get recent orders."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM order_log ORDER BY id DESC LIMIT ?', (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
        
    def get_pnl_history(self, days: int = 30) -> List[Dict]:
        """Get P&L history for last N days."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pnl_log ORDER BY date DESC LIMIT ?', (days,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
        
    def get_summary(self) -> Dict:
        """Get trade log summary."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Count signals
        cursor.execute('SELECT COUNT(*) FROM signal_log')
        total_signals = cursor.fetchone()[0]
        
        # Count orders
        cursor.execute('SELECT COUNT(*) FROM order_log')
        total_orders = cursor.fetchone()[0]
        
        # Total P&L
        cursor.execute('SELECT SUM(pnl) FROM order_log WHERE pnl IS NOT NULL')
        result = cursor.fetchone()[0]
        total_pnl = result if result else 0.0
        
        # Win rate
        cursor.execute('SELECT COUNT(*) FROM order_log WHERE pnl > 0')
        wins = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM order_log WHERE pnl IS NOT NULL AND pnl != 0')
        closed = cursor.fetchone()[0]
        win_rate = wins / closed if closed > 0 else 0.0
        
        conn.close()
        
        return {
            'total_signals': total_signals,
            'total_orders': total_orders,
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'closed_trades': closed
        }
