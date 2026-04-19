"""
Phase 276: 实盘交易模块 (Live Trading)
通过 FutuTrader 对接实盘/模拟盘交易
"""

import os
import json
import threading
from flask import Blueprint, request, jsonify
from src.web.response_helpers import ok, error, bad_request

live_trading_bp = Blueprint('live_trading', __name__)

# 全局交易实例 (惰性初始化)
_trader = None
_trader_lock = threading.Lock()
_trader_state = {'connected': False, 'mode': None, 'acc_id': None}


def _get_trader():
    """获取或创建 FutuTrader 实例"""
    global _trader
    if _trader is None:
        with _trader_lock:
            if _trader is None:
                from src.execution.futu_trader import FutuTrader
                paper = os.getenv('TRADING_MODE', 'paper') != 'live'
                _trader = FutuTrader(paper_trading=paper)
    return _trader


@live_trading_bp.route('/api/trading/connect', methods=['POST'])
def api_trading_connect():
    """连接 Futu OpenD"""
    try:
        trader = _get_trader()
        data = request.get_json(silent=True) or {}
        
        # 可选覆盖配置
        if 'host' in data:
            trader.host = data['host']
        if 'quote_port' in data:
            trader.quote_port = int(data['quote_port'])
        if 'trd_port' in data:
            trader.trd_port = int(data['trd_port'])
        if 'paper_trading' in data:
            trader.paper_trading = bool(data['paper_trading'])
        
        success = trader.connect()
        if success:
            _trader_state.update({
                'connected': True,
                'mode': 'paper' if trader.paper_trading else 'live',
                'acc_id': trader.acc_id
            })
            return ok(data={
                'connected': True,
                'mode': _trader_state['mode'],
                'acc_id': _trader_state['acc_id']
            }, message='连接成功')
        else:
            return error(message='连接失败，请检查 Futu OpenD 是否运行')
    except Exception as e:
        return error(message=f'连接异常: {str(e)}')


@live_trading_bp.route('/api/trading/disconnect', methods=['POST'])
def api_trading_disconnect():
    """断开 Futu 连接"""
    try:
        trader = _get_trader()
        trader.disconnect()
        _trader_state.update({'connected': False, 'mode': None, 'acc_id': None})
        return ok(message='已断开连接')
    except Exception as e:
        return error(message=f'断开异常: {str(e)}')


@live_trading_bp.route('/api/trading/status', methods=['GET'])
def api_trading_status():
    """获取交易状态"""
    return ok(data=_trader_state)


@live_trading_bp.route('/api/trading/order', methods=['POST'])
def api_place_order():
    """下单"""
    if not _trader_state.get('connected'):
        return error(message='交易未连接', code=400)
    
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code')
        side = data.get('side', 'BUY').upper()
        qty = int(data.get('qty', 0))
        price = data.get('price')
        
        if not code:
            return bad_request(message='股票代码不能为空')
        if qty <= 0:
            return bad_request(message='数量必须大于0')
        if side not in ('BUY', 'SELL'):
            return bad_request(message='side 必须为 BUY 或 SELL')
        
        trader = _get_trader()
        result = trader.place_order(code, side, qty, price)
        
        if result.get('success'):
            return ok(data=result, message='下单成功')
        else:
            return error(message=result.get('error', '下单失败'))
    except Exception as e:
        return error(message=f'下单异常: {str(e)}')


@live_trading_bp.route('/api/trading/orders/<order_id>', methods=['GET'])
def api_order_status(order_id):
    """查询订单状态"""
    if not _trader_state.get('connected'):
        return error(message='交易未连接', code=400)
    
    try:
        trader = _get_trader()
        result = trader.check_order_status(order_id)
        return ok(data=result)
    except Exception as e:
        return error(message=f'查询异常: {str(e)}')


@live_trading_bp.route('/api/trading/positions', methods=['GET'])
def api_positions():
    """获取持仓"""
    if not _trader_state.get('connected'):
        return error(message='交易未连接', code=400)
    
    try:
        trader = _get_trader()
        positions = trader.get_positions()
        return ok(data={'positions': positions, 'count': len(positions)})
    except Exception as e:
        return error(message=f'查询持仓异常: {str(e)}')


@live_trading_bp.route('/api/trading/account', methods=['GET'])
def api_account():
    """获取账户资金"""
    if not _trader_state.get('connected'):
        return error(message='交易未连接', code=400)
    
    try:
        trader = _get_trader()
        account = trader.get_account_info()
        return ok(data=account)
    except Exception as e:
        return error(message=f'查询账户异常: {str(e)}')


@live_trading_bp.route('/api/trading/signal', methods=['POST'])
def api_execute_signal():
    """执行策略信号"""
    if not _trader_state.get('connected'):
        return error(message='交易未连接', code=400)
    
    try:
        data = request.get_json(silent=True) or {}
        signal = {
            'code': data.get('code'),
            'action': data.get('action', 'BUY'),
            'shares': int(data.get('shares', 0)),
            'price': data.get('price'),
        }
        
        trader = _get_trader()
        result = trader.execute_signal(signal)
        
        if result.get('success'):
            return ok(data=result, message='信号执行成功')
        else:
            return error(message=result.get('error', '信号执行失败'))
    except Exception as e:
        return error(message=f'信号执行异常: {str(e)}')
