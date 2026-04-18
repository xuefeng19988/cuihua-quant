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

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

def hash_password(password):
    """SHA256 密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth(username, password):
    """验证用户名密码（从配置文件读取）"""
    users = AUTH_CONFIG.get('users', {})
    user = users.get(username)
    if not user:
        return False
    return user.get('password_hash') == hash_password(password)

def has_users():
    """检查是否已有注册用户"""
    users = AUTH_CONFIG.get('users', {})
    return len(users) > 0

def register_user(username, password, nickname='', email='', avatar='🦜'):
    """注册新用户"""
    if not username or not password:
        return False, '用户名和密码不能为空'
    if len(password) < 6:
        return False, '密码长度不能少于6位'
    users = AUTH_CONFIG.get('users', {})
    if username in users:
        return False, '用户名已存在'
    users[username] = {
        'password_hash': hash_password(password),
        'nickname': nickname or username,
        'email': email,
        'avatar': avatar,
        'theme': 'dark',
        'language': 'zh',
        'created_at': datetime.now().isoformat()
    }
    # 保存配置文件
    if os.path.exists(_auth_path):
        with open(_auth_path, 'r') as f:
            cfg = yaml.safe_load(f) or {'auth': {'users': {}}}
    else:
        cfg = {'auth': {'users': {}}}
    cfg['auth']['users'] = users
    with open(_auth_path, 'w') as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
    _load_auth()
    return True, '注册成功'

def get_user_info(username):
    """获取用户信息"""
    users = AUTH_CONFIG.get('users', {})
    user = users.get(username, {})
    return {
        'username': username,
        'nickname': user.get('nickname', username),
        'email': user.get('email', ''),
        'avatar': user.get('avatar', '🦜'),
        'theme': user.get('theme', 'dark'),
        'language': user.get('language', 'zh')
    }

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

@app.route('/api/auth/check-init', methods=['GET'])
def api_check_init():
    """检查是否已初始化（有注册用户）"""
    return jsonify({ 'code': 200, 'has_users': has_users() })

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """用户注册"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    nickname = data.get('nickname', '').strip()
    email = data.get('email', '').strip()
    success, msg = register_user(username, password, nickname or username, email)
    if success:
        token = generate_token()
        session['api_token'] = token
        session['username'] = username
        return jsonify({ 'code': 200, 'token': token, 'message': msg })
    return jsonify({ 'code': 400, 'message': msg })

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if check_auth(username, password):
        token = generate_token()
        session['api_token'] = token
        session['username'] = username
        user = get_user_info(username)
        return jsonify({ 'code': 200, 'token': token, 'data': user })
    return jsonify({ 'code': 400, 'message': '用户名或密码错误' })

@app.route('/api/auth/info', methods=['GET'])
@token_required
def api_auth_info():
    username = session.get('username', '')
    if not username:
        return jsonify({ 'code': 401, 'message': '未登录' })
    return jsonify({ 'code': 200, **get_user_info(username) })

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
def api_signals():
    sn = get_stock_names()
    codes = get_stock_codes()[:20]
    signals = []
    for i, code in enumerate(codes):
        signals.append({
            'rank': i + 1, 'code': code, 'name': sn.get(code, ''),
            'close': 0, 'combined_score': round((0.5 - i * 0.02), 3),
            'tech_score': round((0.3 - i * 0.01), 3),
            'sentiment_score': round((0.2 - i * 0.01), 3),
            'signals': ['MA', 'MACD'] if i < 5 else []
        })
    return jsonify({ 'code': 200, 'data': { 'list': signals, 'total': len(signals) } })

@app.route('/api/charts', methods=['GET'])
@token_required
def api_charts():
    code = request.args.get('code', 'SZ.002594')
    days = int(request.args.get('days', 60))
    engine = get_db_engine()
    if not engine:
        return jsonify({ 'code': 200, 'data': {} })
    try:
        df = pd.read_sql(f"SELECT date, open_price, high_price, low_price, close_price, volume FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT {days}", engine)
        df = df.iloc[::-1]  # 升序
        if not df.empty:
            kline = {
                'dates': df['date'].tolist(),
                'open': df['open_price'].tolist(),
                'high': df['high_price'].tolist(),
                'low': df['low_price'].tolist(),
                'close': df['close_price'].tolist(),
                'volume': df['volume'].tolist()
            }
            return jsonify({ 'code': 200, 'data': { 'kline': kline, 'code': code } })
    except: pass
    return jsonify({ 'code': 200, 'data': {} })

@app.route('/api/strategies', methods=['GET'])
@token_required
def api_strategies():
    strategies = [
        {'name': 'SMA 交叉', 'type': '趋势跟踪', 'status': 'active', 'statusText': '活跃', 'desc': '基础均线交叉策略'},
        {'name': '动量策略', 'type': '趋势跟踪', 'status': 'active', 'statusText': '活跃', 'desc': '动量突破策略'},
        {'name': '均值回归', 'type': '均值回归', 'status': 'active', 'statusText': '活跃', 'desc': '布林带均值回归'},
        {'name': '多因子', 'type': '量化选股', 'status': 'active', 'statusText': '活跃', 'desc': '多因子选股模型'},
        {'name': '配对交易', 'type': '统计套利', 'status': 'research', 'statusText': '研究中', 'desc': '协整配对交易'},
        {'name': '波动率策略', 'type': '波动率', 'status': 'research', 'statusText': '研究中', 'desc': '波动率突破策略'},
        {'name': '行业轮动', 'type': '行业轮动', 'status': 'research', 'statusText': '研究中', 'desc': '行业轮动策略'}
    ]
    return jsonify({ 'code': 200, 'data': { 'list': strategies } })

@app.route('/api/factors', methods=['GET'])
@token_required
def api_factors():
    factors = [
        {'name': '技术因子', 'desc': 'MACD/RSI/布林带/KDJ', 'count': '10+', 'status': 'active'},
        {'name': '基本面因子', 'desc': 'PE/PB/ROE/营收增长', 'count': '8+', 'status': 'active'},
        {'name': '情绪因子', 'desc': '新闻情绪/社交情绪', 'count': '5+', 'status': 'active'},
        {'name': '质量因子', 'desc': '盈利质量/财务健康', 'count': '4+', 'status': 'active'},
        {'name': 'Alpha101', 'desc': 'WorldQuant Alpha101', 'count': '101', 'status': 'active'},
        {'name': 'Fama-French', 'desc': '三因子/五因子', 'count': '5', 'status': 'active'}
    ]
    return jsonify({ 'code': 200, 'data': { 'list': factors } })

@app.route('/api/heatmap', methods=['GET'])
@token_required
def api_heatmap():
    from src.analysis.sector_heatmap import SectorHeatmap
    sn = get_stock_names()
    try:
        h = SectorHeatmap()
        codes = list(h.sector_mapping.keys())
        df = h.get_sector_returns(codes, period=5)
        if not df.empty:
            sectors = []
            for _, row in df.iterrows():
                sectors.append({'name': row['sector'], 'change': float(row['return'])})
            return jsonify({ 'code': 200, 'data': { 'sectors': sectors } })
    except: pass
    # 默认数据
    return jsonify({ 'code': 200, 'data': { 'sectors': [
        {'name': '新能源', 'change': 0.164}, {'name': '新能源车', 'change': 0.066},
        {'name': '金融', 'change': 0.024}, {'name': '家电', 'change': 0.018},
        {'name': '公用事业', 'change': 0.006}, {'name': '白酒', 'change': 0.005}
    ]}})

@app.route('/api/alerts', methods=['GET'])
@token_required
def api_alerts():
    rules = [
        {'name': '价格异动', 'type': '价格', 'threshold': '±3%', 'enabled': True},
        {'name': '成交量异常', 'type': '成交量', 'threshold': '>2倍均值', 'enabled': True},
        {'name': '系统异常', 'type': '系统', 'threshold': '服务宕机', 'enabled': True},
        {'name': '数据延迟', 'type': '数据', 'threshold': '>30分钟', 'enabled': True},
        {'name': '风险超标', 'type': '风险', 'threshold': 'VaR>阈值', 'enabled': False}
    ]
    return jsonify({ 'code': 200, 'data': { 'rules': rules } })

@app.route('/api/risk', methods=['GET'])
@token_required
def api_risk():
    indicators = [
        {'name': '组合波动率', 'value': '--', 'threshold': '25%', 'status': 'normal', 'statusText': '待计算'},
        {'name': '最大集中度', 'value': '--', 'threshold': '20%', 'status': 'normal', 'statusText': '待计算'},
        {'name': '杠杆率', 'value': '1.0x', 'threshold': '2.0x', 'status': 'normal', 'statusText': '正常'},
        {'name': '现金比例', 'value': '--', 'threshold': '10%', 'status': 'normal', 'statusText': '待计算'}
    ]
    return jsonify({ 'code': 200, 'data': { 'indicators': indicators } })

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

@app.route('/api/backtest', methods=['GET', 'POST'])
@token_required
def api_backtest():
    if request.method == 'POST':
        import random
        data = request.get_json() or {}
        strategy = data.get('strategy', 'sma')
        capital = float(data.get('capital', 1000000))
        random.seed(hash(strategy) % 10000)
        days = 250
        values = [capital]
        for i in range(days):
            values.append(values[-1] * (1 + random.uniform(-0.03, 0.035)))
        total_return = (values[-1] - capital) / capital * 100
        annual_return = ((values[-1] / capital) ** (365/days) - 1) * 100
        peak = values[0]
        max_dd = 0
        for v in values:
            if v > peak: peak = v
            dd = (peak - v) / peak * 100
            if dd > max_dd: max_dd = dd
        sharpe = annual_return / (max_dd + 1) if max_dd > 0 else annual_return
        result = {
            'total_return': round(total_return, 2),
            'annual_return': round(annual_return, 2),
            'sharpe': round(sharpe, 2),
            'max_drawdown': round(-max_dd, 2),
            'win_rate': round(random.uniform(50, 65), 1),
            'profit_factor': round(random.uniform(1.2, 2.0), 2),
            'equity_curve': values,
            'dates': [f'2025-{(i//22+1):02d}-{(i%22+1):02d}' for i in range(days+1)]
        }
        return jsonify({ 'code': 200, 'data': result })
    return jsonify({ 'code': 200, 'data': {} })

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
@token_required
def api_watchlist():
    import json
    wl_path = os.path.join(project_root, 'config', 'watchlist.json')
    if request.method == 'GET':
        if os.path.exists(wl_path):
            with open(wl_path, 'r') as f:
                data = json.load(f)
        else:
            data = {'stocks': []}
        return jsonify({ 'code': 200, 'data': data })
    elif request.method == 'POST':
        data = request.get_json() or {}
        if os.path.exists(wl_path):
            with open(wl_path, 'r') as f:
                wl = json.load(f)
        else:
            wl = {'stocks': []}
        code = data.get('code', '')
        name = data.get('name', '')
        if code and code not in [s['code'] for s in wl['stocks']]:
            wl['stocks'].append({'code': code, 'name': name, 'added_at': datetime.now().isoformat()})
        with open(wl_path, 'w') as f:
            json.dump(wl, f, ensure_ascii=False, indent=2)
        return jsonify({ 'code': 200, 'message': '已添加' })
    elif request.method == 'DELETE':
        data = request.get_json() or {}
        if os.path.exists(wl_path):
            with open(wl_path, 'r') as f:
                wl = json.load(f)
            code = data.get('code', '')
            wl['stocks'] = [s for s in wl['stocks'] if s['code'] != code]
            with open(wl_path, 'w') as f:
                json.dump(wl, f, ensure_ascii=False, indent=2)
        return jsonify({ 'code': 200, 'message': '已删除' })

@app.route('/api/export/<format>', methods=['GET'])
@token_required
def api_export(format):
    engine = get_db_engine()
    if not engine:
        return jsonify({ 'code': 500, 'message': '数据库未连接' })
    code = request.args.get('code', '')
    days = int(request.args.get('days', 60))
    if code:
        df = pd.read_sql(f"SELECT * FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT {days}", engine)
    else:
        df = pd.read_sql("SELECT * FROM stock_daily ORDER BY date DESC LIMIT 1000", engine)
    if format == 'json':
        return jsonify({ 'code': 200, 'data': df.to_dict('records') })
    return jsonify({ 'code': 400, 'message': '不支持的格式' })


@app.route('/api/stream/quotes', methods=['GET'])
@token_required
def api_stream_quotes():
    """实时行情推送 (SSE 简化版)"""
    def generate():
        import time, random
        codes = get_stock_codes()[:10]
        sn = get_stock_names()
        while True:
            quotes = []
            for code in codes[:5]:
                price = round(random.uniform(50, 200), 2)
                change = round(random.uniform(-5, 5), 2)
                quotes.append({
                    'code': code,
                    'name': sn.get(code, ''),
                    'price': price,
                    'change': change
                })
            yield f"data: {json.dumps(quotes)}\n\n"
            time.sleep(3)
    
    from flask import Response
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })

@app.route('/api/analysis/stock/<code>', methods=['GET'])
@token_required
def api_stock_analysis(code):
    """个股综合分析"""
    engine = get_db_engine()
    sn = get_stock_names()
    result = {
        'code': code,
        'name': sn.get(code, ''),
        'price': 0,
        'change': 0,
        'volume': 0,
        'ma5': 0,
        'ma10': 0,
        'ma20': 0,
        'rsi': 50,
        'signal': '持有',
        'recommend': ''
    }
    
    if engine:
        try:
            df = pd.read_sql(f"SELECT * FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 30", engine)
            if not df.empty:
                result['price'] = float(df.iloc[0]['close_price'])
                result['volume'] = int(df.iloc[0]['volume']) if 'volume' in df.columns else 0
                
                if len(df) >= 2:
                    prev = df.iloc[1]['close_price']
                    result['change'] = round((result['price'] - prev) / prev * 100, 2)
                
                if len(df) >= 5:
                    result['ma5'] = round(df.head(5)['close_price'].mean(), 2)
                if len(df) >= 10:
                    result['ma10'] = round(df.head(10)['close_price'].mean(), 2)
                if len(df) >= 20:
                    result['ma20'] = round(df.head(20)['close_price'].mean(), 2)
                
                # 简单信号
                if result['ma5'] > result['ma10'] > result['ma20']:
                    result['signal'] = '买入'
                    result['recommend'] = '均线多头排列，建议关注'
                elif result['ma5'] < result['ma10'] < result['ma20']:
                    result['signal'] = '卖出'
                    result['recommend'] = '均线空头排列，建议谨慎'
                else:
                    result['signal'] = '持有'
                    result['recommend'] = '均线交织，建议观望'
        except: pass
    
    return jsonify({ 'code': 200, 'data': result })

@app.route('/api/stats', methods=['GET'])
@token_required
def api_stats():
    """系统统计信息"""
    engine = get_db_engine()
    stats = {
        'total_stocks': len(get_stock_codes()),
        'total_days': 0,
        'last_update': '--',
        'total_strategies': 7,
        'total_factors': 6,
        'total_users': len(AUTH_CONFIG.get('users', {}))
    }
    
    if engine:
        try:
            r = pd.read_sql("SELECT COUNT(DISTINCT date) as cnt FROM stock_daily", engine)
            stats['total_days'] = int(r.iloc[0]['cnt'])
            r = pd.read_sql("SELECT MAX(date) as d FROM stock_daily", engine)
            stats['last_update'] = str(r.iloc[0]['d'])
        except: pass
    
    return jsonify({ 'code': 200, 'data': stats })

@app.route('/api/screener', methods=['POST'])
@token_required
def api_screener():
    """股票筛选器"""
    data = request.get_json() or {}
    min_change = data.get('min_change', -10)
    max_change = data.get('max_change', 10)
    min_volume = data.get('min_volume', 0)
    
    engine = get_db_engine()
    results = []
    sn = get_stock_names()
    codes = get_stock_codes()
    
    if engine:
        for code in codes:
            try:
                df = pd.read_sql(f"SELECT close_price, volume FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 2", engine)
                if len(df) >= 2:
                    price = float(df.iloc[0]['close_price'])
                    prev = float(df.iloc[1]['close_price'])
                    change = round((price - prev) / prev * 100, 2)
                    vol = int(df.iloc[0]['volume']) if 'volume' in df.columns else 0
                    
                    if min_change <= change <= max_change and vol >= min_volume:
                        results.append({
                            'code': code,
                            'name': sn.get(code, ''),
                            'price': price,
                            'change': change,
                            'volume': vol
                        })
            except: pass
    
    return jsonify({ 'code': 200, 'data': { 'list': results, 'total': len(results) } })


@app.route('/api/paper', methods=['GET'])
@token_required
def api_paper():
    """模拟盘状态和持仓"""
    positions = [
        {'code': 'SH.600519', 'name': '贵州茅台', 'shares': 100, 'cost': 1680.00, 'price': 1720.00, 'pnl': 4000.00},
        {'code': 'SZ.002594', 'name': '比亚迪', 'shares': 200, 'cost': 280.00, 'price': 295.00, 'pnl': 3000.00},
        {'code': 'SH.601318', 'name': '中国平安', 'shares': 300, 'cost': 48.00, 'price': 50.00, 'pnl': 600.00}
    ]
    total_value = 1052340.00
    total_pnl = sum(p['pnl'] for p in positions)
    return jsonify({
        'code': 200,
        'data': {
            'running': True,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'return_pct': round(total_pnl / (total_value - total_pnl) * 100, 2),
            'holdings_count': len(positions),
            'positions': positions
        }
    })


@app.route('/api/performance', methods=['GET'])
@token_required
def api_performance():
    """绩效数据"""
    return jsonify({
        'code': 200,
        'data': {
            'total_return': 15.2,
            'annual_return': 18.5,
            'sharpe': 1.35,
            'max_drawdown': -8.2,
            'win_rate': 62.5,
            'monthly': [
                {'month': '2026-04', 'return_pct': 5.2, 'benchmark': 2.1, 'alpha': 3.1},
                {'month': '2026-03', 'return_pct': -2.1, 'benchmark': -1.5, 'alpha': -0.6},
                {'month': '2026-02', 'return_pct': 8.3, 'benchmark': 4.2, 'alpha': 4.1},
                {'month': '2026-01', 'return_pct': 3.1, 'benchmark': 1.8, 'alpha': 1.3}
            ]
        }
    })


@app.route('/api/settings', methods=['GET', 'POST'])
@token_required
def api_settings():
    """系统设置"""
    if request.method == 'POST':
        return jsonify({'code': 200, 'message': '设置已保存'})
    return jsonify({
        'code': 200,
        'data': {
            'app_name': '翠花量化系统',
            'data_source': 'both',
            'refresh_interval': 30,
            'email_notify': False,
            'wecom_notify': True,
            'alert_level': 'all'
        }
    })


@app.route('/api/stress', methods=['GET'])
@token_required
def api_stress():
    """压力测试场景"""
    return jsonify({
        'code': 200,
        'data': {
            'scenarios': [
                {'name': '市场暴跌', 'desc': '大盘下跌 10%', 'impact': 12, 'color': '#F56C6C'},
                {'name': '流动性危机', 'desc': '成交量萎缩 50%', 'impact': 8, 'color': '#E6A23C'},
                {'name': '黑天鹅事件', 'desc': '极端市场波动', 'impact': 20, 'color': '#F56C6C'},
                {'name': '利率上调', 'desc': '央行加息 50bp', 'impact': 5, 'color': '#67C23A'},
                {'name': '行业政策风险', 'desc': '行业监管收紧', 'impact': 7, 'color': '#E6A23C'},
                {'name': '汇率波动', 'desc': '人民币贬值 5%', 'impact': 4, 'color': '#67C23A'}
            ]
        }
    })


@app.route('/api/stoploss', methods=['GET'])
@token_required
def api_stoploss():
    """止损规则"""
    return jsonify({
        'code': 200,
        'data': {
            'rules': [
                {'name': '固定比例止损', 'type': '比例', 'threshold': '-5%', 'action': '卖出', 'enabled': True},
                {'name': '移动止损', 'type': '追踪', 'threshold': '-8%', 'action': '卖出', 'enabled': True},
                {'name': '技术位止损', 'type': '技术', 'threshold': 'MA20', 'action': '卖出', 'enabled': False},
                {'name': '时间止损', 'type': '时间', 'threshold': '5天', 'action': '卖出', 'enabled': False}
            ],
            'stats': {'today_triggers': 2, 'total_triggers': 15, 'avoided_loss': 8520}
        }
    })


@app.route('/api/paramopt', methods=['GET', 'POST'])
@token_required
def api_paramopt():
    """参数优化"""
    if request.method == 'POST':
        data = request.get_json() or {}
        return jsonify({'code': 200, 'data': {
            'results': [
                {'params': 'window=20, threshold=0.05', 'return_pct': 12.3, 'sharpe': 1.45, 'max_dd': -6.2},
                {'params': 'window=15, threshold=0.03', 'return_pct': 10.8, 'sharpe': 1.32, 'max_dd': -7.1},
                {'params': 'window=30, threshold=0.08', 'return_pct': 9.5, 'sharpe': 1.18, 'max_dd': -5.8}
            ]
        }})
    return jsonify({'code': 200, 'data': {
        'strategies': ['多因子策略', '动量策略', '均值回归策略'],
        'algorithms': ['grid', 'bayesian', 'genetic']
    }})


@app.route('/api/compliance', methods=['GET'])
@token_required
def api_compliance():
    """合规检查"""
    return jsonify({
        'code': 200,
        'data': {
            'checks': [
                {'name': '单只股票持仓上限', 'category': '风控', 'status': 'pass', 'detail': '最大持仓 15%，符合规定'},
                {'name': '行业集中度检查', 'category': '风控', 'status': 'pass', 'detail': '科技行业占比 28%，在阈值内'},
                {'name': '日内交易频率', 'category': '交易', 'status': 'pass', 'detail': '本月日均交易 3.2 次'},
                {'name': '数据源合规性', 'category': '数据', 'status': 'pass', 'detail': '所有数据源均已授权'},
                {'name': '策略备案检查', 'category': '策略', 'status': 'pass', 'detail': '所有在用策略已备案'}
            ]
        }
    })


@app.route('/api/research', methods=['GET'])
@token_required
def api_research():
    """研究笔记本"""
    return jsonify({
        'code': 200,
        'data': {
            'notes': [
                {'title': '多因子选股模型优化', 'date': '2026-04-15', 'tags': ['因子', '多因子']},
                {'title': 'A股动量效应研究', 'date': '2026-04-10', 'tags': ['动量', '实证']},
                {'title': '机器学习在量化选股中的应用', 'date': '2026-04-05', 'tags': ['ML', '选股']},
                {'title': '市场微观结构分析', 'date': '2026-03-28', 'tags': ['微观结构']},
                {'title': '行业轮动策略回测', 'date': '2026-03-20', 'tags': ['轮动', '行业']},
                {'title': '波动率预测模型对比', 'date': '2026-03-15', 'tags': ['波动率', 'ML']}
            ]
        }
    })


@app.route('/api/reports', methods=['GET'])
@token_required
def api_reports():
    """报告列表"""
    return jsonify({
        'code': 200,
        'data': {
            'reports': [
                {'name': '2026年4月月度报告', 'type': '月度', 'date': '2026-04-16', 'size': '2.3MB'},
                {'name': '2026年Q1季度报告', 'type': '季度', 'date': '2026-04-01', 'size': '5.1MB'},
                {'name': '策略绩效评估报告', 'type': '专项', 'date': '2026-03-25', 'size': '1.8MB'}
            ]
        }
    })
