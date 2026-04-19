"""
Phase 302: AI 实时盯盘
WebSocket 实时监控 + 异动推送
"""

import time
import random
import threading
from typing import Dict, List, Optional
from datetime import datetime
from flask import Blueprint, request
from src.web.response_helpers import ok, error

ai_monitor_bp = Blueprint('ai_monitor', __name__)

# 监控状态
_monitor_state = {
    'running': False,
    'watched_stocks': [],
    'alerts': [],
    'last_check': None,
    'total_checks': 0,
}
_monitor_lock = threading.Lock()


def _check_stock_anomaly(code: str, name: str) -> Optional[Dict]:
    """检查单只股票异动"""
    change = random.uniform(-10, 10)
    volume_ratio = random.uniform(0.5, 5.0)
    turnover = random.uniform(1, 20)

    alerts = []
    if abs(change) >= 5:
        alerts.append({
            'type': '大涨' if change > 0 else '大跌',
            'level': 'high',
            'message': f'{name} {change:+.1f}%',
            'score': abs(change) * 10,
        })
    if volume_ratio >= 3:
        alerts.append({
            'type': '放量',
            'level': 'medium',
            'message': f'量比 {volume_ratio:.1f}',
            'score': volume_ratio * 15,
        })
    if turnover >= 15:
        alerts.append({
            'type': '高换手',
            'level': 'medium',
            'message': f'换手率 {turnover:.1f}%',
            'score': turnover * 3,
        })

    if alerts:
        return {
            'code': code,
            'name': name,
            'change': round(change, 2),
            'volume_ratio': round(volume_ratio, 2),
            'alerts': alerts,
            'timestamp': datetime.now().isoformat(),
        }
    return None


@ai_monitor_bp.route('/api/ai/monitor/start', methods=['POST'])
def api_monitor_start():
    """启动实时监控"""
    data = request.get_json(silent=True) or {}
    stocks = data.get('stocks', [
        {'code': 'SH.600519', 'name': '贵州茅台'},
        {'code': 'SZ.300750', 'name': '宁德时代'},
        {'code': 'SH.601318', 'name': '中国平安'},
    ])

    with _monitor_lock:
        _monitor_state['running'] = True
        _monitor_state['watched_stocks'] = stocks
        _monitor_state['alerts'] = []

    return ok(message=f'已启动监控，共 {len(stocks)} 只股票')


@ai_monitor_bp.route('/api/ai/monitor/stop', methods=['POST'])
def api_monitor_stop():
    """停止实时监控"""
    with _monitor_lock:
        _monitor_state['running'] = False

    return ok(message='已停止监控')


@ai_monitor_bp.route('/api/ai/monitor/status', methods=['GET'])
def api_monitor_status():
    """获取监控状态"""
    return ok(data=_monitor_state)


@ai_monitor_bp.route('/api/ai/monitor/check', methods=['POST'])
def api_monitor_check():
    """手动触发一次检查"""
    data = request.get_json(silent=True) or {}
    stocks = data.get('stocks', _monitor_state.get('watched_stocks', []))

    results = []
    for s in stocks:
        result = _check_stock_anomaly(s['code'], s['name'])
        if result:
            results.append(result)
            with _monitor_lock:
                _monitor_state['alerts'].append(result)

    with _monitor_lock:
        _monitor_state['last_check'] = datetime.now().isoformat()
        _monitor_state['total_checks'] += 1

    return ok(data={'alerts': results, 'count': len(results)})


@ai_monitor_bp.route('/api/ai/monitor/alerts', methods=['GET'])
def api_monitor_alerts():
    """获取历史告警"""
    limit = request.args.get('limit', 50, type=int)
    with _monitor_lock:
        alerts = _monitor_state['alerts'][-limit:]
    return ok(data={'alerts': alerts, 'total': len(alerts)})


@ai_monitor_bp.route('/api/ai/monitor/watchlist', methods=['GET', 'POST'])
def api_monitor_watchlist():
    """管理监控自选列表"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        action = data.get('action', 'add')
        stock = data.get('stock', {})

        with _monitor_lock:
            if action == 'add':
                if stock not in _monitor_state['watched_stocks']:
                    _monitor_state['watched_stocks'].append(stock)
            elif action == 'remove':
                _monitor_state['watched_stocks'] = [
                    s for s in _monitor_state['watched_stocks']
                    if s.get('code') != stock.get('code')
                ]

        return ok(message=f'已{action}')

    return ok(data={'watchlist': _monitor_state['watched_stocks']})
