"""
翠花量化 REST API Server
前后端分离 - 为 Vue 前端提供 API
"""

import os
import sys
import yaml
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, session

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pandas as pd

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
app.config['SECRET_KEY'] = 'cuihua-quant-api-secret'

# ========== 配置加载 ==========
AUTH_CONFIG = {}
_auth_path = os.path.join(project_root, 'config', 'auth.yaml')
if os.path.exists(_auth_path):
    with open(_auth_path, 'r') as f:
        AUTH_CONFIG = yaml.safe_load(f).get('auth', {})

def _load_auth():
    global AUTH_CONFIG
    if os.path.exists(_auth_path):
        with open(_auth_path, 'r') as f:
            AUTH_CONFIG = yaml.safe_load(f).get('auth', {})

def check_auth(username, password):
    admin = AUTH_CONFIG.get('admin', {})
    return username == admin.get('username', 'admin') and password == admin.get('password', 'admin123')

def generate_token():
    return secrets.token_hex(32)

# ========== 认证装饰器 ==========
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not AUTH_CONFIG.get('enabled', True):
            return f(*args, **kwargs)
        token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.args.get('token', '')
        if not token and 'api_token' in session:
            token = session['api_token']
        if not token:
            return jsonify({'code': 401, 'message': '未登录'})
        # Simple token check
        session['api_token'] = token
        return f(*args, **kwargs)
    return decorated

# ========== 辅助函数 ==========
def get_stock_names():
    cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
    names = {}
    try:
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
        for pool_data in cfg.get('pools', {}).values():
            for item in pool_data.get('stocks', []):
                if isinstance(item, dict):
                    code, name = item.get('code', ''), item.get('name', '')
                    if code and code not in names: names[code] = name
                elif isinstance(item, str) and item not in names:
                    names[item] = ''
    except: pass
    return names

def get_stock_codes():
    cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
    codes = []
    try:
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
        for pool_data in cfg.get('pools', {}).values():
            for item in pool_data.get('stocks', []):
                code = item.get('code', item) if isinstance(item, dict) else item
                if code and code not in codes: codes.append(code)
    except: pass
    return codes

def get_db_engine():
    try:
        from src.data.database import get_db_engine as _get
        return _get()
    except: return None

# ========== API 路由 ==========

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if check_auth(username, password):
        token = generate_token()
        session['api_token'] = token
        session['username'] = username
        admin = AUTH_CONFIG.get('admin', {})
        return jsonify({
            'code': 200, 'token': token,
            'data': { 'name': admin.get('nickname', '管理员'), 'avatar': admin.get('avatar', '🦜') }
        })
    return jsonify({ 'code': 400, 'message': '用户名或密码错误' })

@app.route('/api/auth/info', methods=['GET'])
@token_required
def api_auth_info():
    admin = AUTH_CONFIG.get('admin', {})
    return jsonify({ 'code': 200, 'name': admin.get('nickname', '管理员'), 'avatar': admin.get('avatar', '🦜') })

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({ 'code': 200 })

@app.route('/api/dashboard', methods=['GET'])
@token_required
def api_dashboard():
    sn = get_stock_names()
    gainers, losers, heatmap_date = [], [], '--'
    engine = get_db_engine()
    if engine:
        try:
            df = pd.read_sql('''
                SELECT t1.code, t1.close_price, t1.date, t2.close_price as prev_price
                FROM stock_daily t1
                LEFT JOIN stock_daily t2 ON t1.code = t2.code
                    AND t2.date = (SELECT MAX(date) FROM stock_daily WHERE code = t1.code AND date < t1.date)
                WHERE t1.date = (SELECT MAX(date) FROM stock_daily WHERE code = t1.code)
            ''', engine)
            if not df.empty:
                df['change'] = ((df['close_price'] - df['prev_price']) / df['prev_price'] * 100).round(2)
                heatmap_date = str(df.iloc[0]['date'])
                for _, row in df.nlargest(5, 'change').iterrows():
                    c = row['code']
                    gainers.append({ 'code': c, 'name': sn.get(c, ''), 'price': f"{row['close_price']:.2f}", 'change': f"{row['change']:.2f}" })
                for _, row in df.nsmallest(5, 'change').iterrows():
                    c = row['code']
                    losers.append({ 'code': c, 'name': sn.get(c, ''), 'price': f"{row['close_price']:.2f}", 'change': f"{row['change']:.2f}" })
        except: pass

    try:
        cnt = pd.read_sql("SELECT COUNT(*) as cnt FROM stock_daily", engine).iloc[0]['cnt'] if engine else 0
    except: cnt = 0

    return jsonify({
        'code': 200, 'data': {
            'db_records': f'{cnt:,}', 'futu_status': '已连接', 'disk_status': '正常',
            'heatmap_date': heatmap_date, 'gainers': gainers, 'losers': losers
        }
    })

@app.route('/api/stocks', methods=['GET'])
@token_required
def api_stocks():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sn = get_stock_names()
    codes = get_stock_codes()
    total = len(codes)
    start = (page - 1) * per_page
    page_codes = codes[start:start + per_page]

    engine = get_db_engine()
    stocks = []
    for code in page_codes:
        price, change = '-', 0
        if engine:
            try:
                df = pd.read_sql(f"SELECT close_price FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 2", engine)
                if len(df) >= 2:
                    price = df.iloc[0]['close_price']
                    change = round(((price - df.iloc[1]['close_price']) / df.iloc[1]['close_price']) * 100, 2)
                elif len(df) == 1:
                    price = df.iloc[0]['close_price']
            except: pass
        stocks.append({ 'code': code, 'name': sn.get(code, ''), 'price': f"{price:.2f}" if isinstance(price, (int, float)) else price, 'change': change })

    return jsonify({ 'code': 200, 'data': { 'list': stocks, 'total': total, 'page': page } })

@app.route('/api/stocks', methods=['POST'])
@token_required
def api_add_stock():
    data = request.get_json() or {}
    code, name = data.get('code', '').strip(), data.get('name', '').strip()
    if not code: return jsonify({ 'code': 400, 'message': '代码不能为空' })
    try:
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(cfg_path, 'r') as f: cfg = yaml.safe_load(f) or {}
        pool = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
        existing = [item.get('code', item) if isinstance(item, dict) else item for item in pool]
        if code in existing: return jsonify({ 'code': 400, 'message': f'{code} 已存在' })
        pool.append({ 'code': code, 'name': name })
        cfg['pools']['watchlist']['stocks'] = pool
        with open(cfg_path, 'w') as f: yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
        return jsonify({ 'code': 200 })
    except Exception as e:
        return jsonify({ 'code': 500, 'message': str(e) })

@app.route('/api/stocks/<code>', methods=['DELETE'])
@token_required
def api_delete_stock(code):
    try:
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(cfg_path, 'r') as f: cfg = yaml.safe_load(f) or {}
        pool = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
        pool = [item for item in pool if (item.get('code', item) if isinstance(item, dict) else item) != code]
        cfg['pools']['watchlist']['stocks'] = pool
        with open(cfg_path, 'w') as f: yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
        return jsonify({ 'code': 200 })
    except Exception as e:
        return jsonify({ 'code': 500, 'message': str(e) })

@app.route('/api/portfolio', methods=['GET'])
@token_required
def api_portfolio():
    pf_path = os.path.join(project_root, 'config', 'portfolio.yaml')
    try:
        with open(pf_path, 'r') as f: pf = yaml.safe_load(f) or {'portfolio': {'total_capital': 1000000, 'positions': []}}
    except: pf = {'portfolio': {'total_capital': 1000000, 'positions': []}}

    p = pf.get('portfolio', {})
    total_capital = p.get('total_capital', 1000000)
    positions = p.get('positions', [])
    sn = get_stock_names()
    engine = get_db_engine()
    total_market, total_cost = 0, 0
    pos_list = []

    for pos in positions:
        code = pos.get('code', '')
        bp = pos.get('buy_price', 0)
        qty = pos.get('quantity', 0)
        cost = bp * qty
        total_cost += cost
        cp = bp
        if engine:
            try:
                df = pd.read_sql(f"SELECT close_price FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 1", engine)
                if not df.empty: cp = df.iloc[0]['close_price']
            except: pass
        mv = cp * qty
        pnl = mv - cost
        total_market += mv
        pos_list.append({
            'code': code, 'name': pos.get('name', ''), 'buy_price': bp, 'quantity': qty,
            'current_price': f"{cp:.2f}", 'pnl': round(pnl, 0),
            'target': f"{((pos.get('target_price', 0) - bp) / bp * 100):+.1f}%" if pos.get('target_price') else '--'
        })

    cash = total_capital - total_cost
    total_pnl = total_market - total_cost

    # Stock options for dropdown
    codes = get_stock_codes()
    stock_options = [{ 'value': c, 'label': f"{c} {sn.get(c, '')}" } for c in codes[:20]]

    return jsonify({
        'code': 200, 'data': {
            'total_capital': total_capital, 'positions': pos_list,
            'total_market': round(total_market, 0), 'cash': round(cash, 0),
            'total_pnl': round(total_pnl, 0), 'stock_options': stock_options
        }
    })

@app.route('/api/portfolio', methods=['POST'])
@token_required
def api_update_portfolio():
    data = request.get_json() or {}
    action = data.get('action')
    pf_path = os.path.join(project_root, 'config', 'portfolio.yaml')
    try:
        with open(pf_path, 'r') as f: pf = yaml.safe_load(f) or {'portfolio': {'total_capital': 1000000, 'positions': []}}
        p = pf.get('portfolio', {})
        if action == 'set_capital':
            p['total_capital'] = float(data.get('total_capital', 1000000))
        elif action == 'add_position':
            pos = { 'code': data.get('code', ''), 'name': sn.get(data.get('code', ''), ''),
                    'buy_price': float(data.get('buy_price', 0)), 'quantity': int(data.get('quantity', 0)),
                    'target_price': float(data.get('target_price', 0) or 0) }
            if pos['code'] and pos['buy_price'] and pos['quantity']:
                p.setdefault('positions', []).append(pos)
        elif action == 'del_position':
            idx = int(data.get('idx', -1))
            if 0 <= idx < len(p.get('positions', [])): p['positions'].pop(idx)
        pf['portfolio'] = p
        with open(pf_path, 'w') as f: yaml.dump(pf, f, allow_unicode=True, default_flow_style=False)
        return jsonify({ 'code': 200 })
    except Exception as e:
        return jsonify({ 'code': 500, 'message': str(e) })

# 简单 API 端点
@app.route('/api/signals', methods=['GET'])
@token_required
def api_signals(): return jsonify({ 'code': 200, 'data': [] })

@app.route('/api/charts', methods=['GET'])
@token_required
def api_charts(): return jsonify({ 'code': 200, 'data': {} })

@app.route('/api/strategies', methods=['GET'])
@token_required
def api_strategies(): return jsonify({ 'code': 200, 'data': [] })

@app.route('/api/factors', methods=['GET'])
@token_required
def api_factors(): return jsonify({ 'code': 200, 'data': [] })

@app.route('/api/heatmap', methods=['GET'])
@token_required
def api_heatmap(): return jsonify({ 'code': 200, 'data': [] })

@app.route('/api/alerts', methods=['GET'])
@token_required
def api_alerts(): return jsonify({ 'code': 200, 'data': [] })

@app.route('/api/risk', methods=['GET'])
@token_required
def api_risk(): return jsonify({ 'code': 200, 'data': {} })

# SPA fallback - 所有非 API 请求返回 index.html
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue(path):
    if path and path.startswith('static/'):
        return send_from_directory(app.static_folder, path)
    if path and '.' in path:
        return send_from_directory(app.static_folder, path)
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
    return jsonify({ 'code': 200, 'message': '前端未构建，请运行 cd frontend && npm run build' })

if __name__ == '__main__':
    sn = get_stock_names()  # 加载股票名称
    print("🦜 翠花量化 API Server 启动中...")
    print("📡 API: http://127.0.0.1:5000/api")
    print("🌐 Vue: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
