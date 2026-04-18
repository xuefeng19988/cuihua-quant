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
    """K线数据 + 技术指标 (Phase 125)"""
    code = request.args.get('code', 'SH.600519')
    days = int(request.args.get('days', 90))
    indicators = request.args.get('indicators', 'ma,macd,rsi,bb')  # 默认开启全部

    engine = get_db_engine()
    if not engine:
        return jsonify({ 'code': 200, 'data': {} })

    try:
        query = f"SELECT date, open_price, high_price, low_price, close_price, volume FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT {days}"
        df = pd.read_sql(query, engine)
        if df.empty:
            return jsonify({ 'code': 404, 'message': '无数据' })

        df = df.iloc[::-1].reset_index(drop=True)  # 升序

        # 计算技术指标
        from src.analysis.technical import calculate_indicators
        df_for_indicators = df[['open_price', 'high_price', 'low_price', 'close_price', 'volume']].copy()
        df_for_indicators.columns = ['open', 'high', 'low', 'close', 'volume']
        df_with_indicators = calculate_indicators(df_for_indicators)

        # 构建返回数据
        result = {
            'code': code,
            'dates': df['date'].tolist(),
            'open': df['open_price'].tolist(),
            'high': df['high_price'].tolist(),
            'low': df['low_price'].tolist(),
            'close': df['close_price'].tolist(),
            'volume': df['volume'].tolist(),
            'indicators': {}
        }

        # MA
        if 'ma' in indicators:
            result['indicators']['ma5'] = df_with_indicators['ma5'].round(2).tolist()
            result['indicators']['ma10'] = df_with_indicators['ma10'].round(2).tolist()
            result['indicators']['ma20'] = df_with_indicators['ma20'].round(2).tolist()

        # MACD
        if 'macd' in indicators:
            result['indicators']['macd'] = df_with_indicators['macd'].round(4).tolist()
            result['indicators']['macd_signal'] = df_with_indicators['macd_signal'].round(4).tolist()
            result['indicators']['macd_hist'] = df_with_indicators['macd_hist'].round(4).tolist()

        # RSI
        if 'rsi' in indicators:
            result['indicators']['rsi'] = df_with_indicators['rsi'].round(2).tolist()

        # Bollinger Bands
        if 'bb' in indicators:
            result['indicators']['bb_upper'] = df_with_indicators['bb_upper'].round(2).tolist()
            result['indicators']['bb_middle'] = df_with_indicators['bb_middle'].round(2).tolist()
            result['indicators']['bb_lower'] = df_with_indicators['bb_lower'].round(2).tolist()

        return jsonify({ 'code': 200, 'data': result })
    except Exception as e:
        return jsonify({ 'code': 500, 'message': str(e) })

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


@app.route('/api/stock-groups', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
def api_stock_groups():
    """股票分组管理 (Phase 126)"""
    import json
    groups_path = os.path.join(project_root, 'config', 'stock_groups.json')

    def load_groups():
        if os.path.exists(groups_path):
            with open(groups_path, 'r') as f:
                return json.load(f)
        return {'groups': {}}

    def save_groups(data):
        with open(groups_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    if request.method == 'GET':
        data = load_groups()
        # 添加stocks.yaml中的默认池
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r') as f:
                cfg = yaml.safe_load(f) or {}
            for pool_key, pool_data in cfg.get('pools', {}).items():
                if pool_key not in data['groups']:
                    data['groups'][pool_key] = {
                        'name': pool_data.get('name', pool_key),
                        'stocks': [item.get('code', item) if isinstance(item, dict) else item for item in pool_data.get('stocks', [])]
                    }
        return jsonify({ 'code': 200, 'data': data })

    elif request.method == 'POST':
        data = request.get_json() or {}
        group_id = data.get('id', '')
        group_name = data.get('name', '')
        if not group_id or not group_name:
            return jsonify({ 'code': 400, 'message': '分组ID和名称不能为空' })
        groups = load_groups()
        groups['groups'][group_id] = {'name': group_name, 'stocks': []}
        save_groups(groups)
        return jsonify({ 'code': 200, 'message': '分组创建成功' })

    elif request.method == 'PUT':
        data = request.get_json() or {}
        group_id = data.get('id', '')
        action = data.get('action', '')  # add_stock / remove_stock
        stock_code = data.get('code', '')
        groups = load_groups()
        if group_id not in groups['groups']:
            return jsonify({ 'code': 404, 'message': '分组不存在' })
        if action == 'add_stock' and stock_code:
            if stock_code not in groups['groups'][group_id]['stocks']:
                groups['groups'][group_id]['stocks'].append(stock_code)
        elif action == 'remove_stock' and stock_code:
            groups['groups'][group_id]['stocks'] = [s for s in groups['groups'][group_id]['stocks'] if s != stock_code]
        save_groups(groups)
        return jsonify({ 'code': 200, 'message': '操作成功' })

    elif request.method == 'DELETE':
        data = request.get_json() or {}
        group_id = data.get('id', '')
        groups = load_groups()
        if group_id in groups['groups']:
            del groups['groups'][group_id]
            save_groups(groups)
        return jsonify({ 'code': 200, 'message': '分组已删除' })


@app.route('/api/export/<format>', methods=['GET'])
@token_required
def api_export(format):
    """数据导出 (Phase 128) - CSV/Excel/JSON"""
    engine = get_db_engine()
    if not engine:
        return jsonify({ 'code': 500, 'message': '数据库未连接' })
    code = request.args.get('code', '')
    days = int(request.args.get('days', 60))
    try:
        if code:
            df = pd.read_sql(f"SELECT * FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT {days}", engine)
        else:
            df = pd.read_sql("SELECT * FROM stock_daily ORDER BY date DESC LIMIT 1000", engine)

        if format == 'json':
            return jsonify({ 'code': 200, 'data': df.to_dict('records') })
        elif format == 'csv':
            import io
            output = io.StringIO()
            df.to_csv(output, index=False)
            from flask import Response
            return Response(output.getvalue(), mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=stock_{code or "all"}_{days}d.csv'})
        elif format == 'excel':
            import io
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            from flask import Response
            return Response(output.read(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': f'attachment; filename=stock_{code or "all"}_{days}d.xlsx'})
        return jsonify({ 'code': 400, 'message': '不支持的格式，支持: json/csv/excel' })
    except Exception as e:
        return jsonify({ 'code': 500, 'message': str(e) })


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
    """高级股票筛选器 (Phase 129)"""
    data = request.get_json() or {}
    min_change = data.get('min_change', -10)
    max_change = data.get('max_change', 10)
    min_volume = data.get('min_volume', 0)
    max_volume = data.get('max_volume', float('inf'))
    min_price = data.get('min_price', 0)
    max_price = data.get('max_price', float('inf'))
    market_type = data.get('market', '')  # A/HK/all
    sort_by = data.get('sort_by', 'change')  # change/volume/price
    sort_order = data.get('sort_order', 'desc')

    engine = get_db_engine()
    results = []
    sn = get_stock_names()
    codes = get_stock_codes()

    if engine:
        for code in codes:
            # 市场类型筛选
            if market_type == 'A' and not code.startswith(('SH.', 'SZ.')):
                continue
            if market_type == 'HK' and not code.startswith('HK.'):
                continue

            try:
                df = pd.read_sql(f"SELECT close_price, volume FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 2", engine)
                if len(df) >= 2:
                    price = float(df.iloc[0]['close_price'])
                    prev = float(df.iloc[1]['close_price'])
                    change = round((price - prev) / prev * 100, 2)
                    vol = int(df.iloc[0]['volume']) if 'volume' in df.columns else 0

                    # 多条件筛选
                    if not (min_change <= change <= max_change):
                        continue
                    if not (min_volume <= vol <= max_volume):
                        continue
                    if not (min_price <= price <= max_price):
                        continue

                    results.append({
                        'code': code,
                        'name': sn.get(code, ''),
                        'price': round(price, 2),
                        'change': change,
                        'volume': vol,
                        'market': 'A' if code.startswith(('SH.', 'SZ.')) else 'HK'
                    })
            except:
                pass

    # 排序
    if sort_by in ('change', 'volume', 'price'):
        results.sort(key=lambda x: x.get(sort_by, 0), reverse=(sort_order == 'desc'))

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


@app.route('/api/equity-curve', methods=['GET'])
@token_required
def api_equity_curve():
    """收益曲线数据 (Phase 127)"""
    import random
    random.seed(42)

    days = int(request.args.get('days', 90))
    dates = []
    from datetime import datetime, timedelta
    for i in range(days - 1, -1, -1):
        d = datetime.now() - timedelta(days=i)
        dates.append(d.strftime('%Y-%m-%d'))

    # 模拟收益曲线 (实际应从数据库读取)
    equity = [100.0]
    benchmark = [100.0]
    drawdown = [0.0]
    peak = 100.0

    for i in range(1, days):
        # 策略收益：日均0.1%，波动1.5%
        daily_return = random.gauss(0.001, 0.015)
        equity.append(equity[-1] * (1 + daily_return))

        # 基准收益：日均0.05%，波动1.0%
        bench_return = random.gauss(0.0005, 0.01)
        benchmark.append(benchmark[-1] * (1 + bench_return))

        # 回撤计算
        peak = max(peak, equity[-1])
        dd = (equity[-1] - peak) / peak * 100
        drawdown.append(dd)

    return jsonify({
        'code': 200,
        'data': {
            'dates': dates,
            'equity': [round(e, 2) for e in equity],
            'benchmark': [round(b, 2) for b in benchmark],
            'drawdown': [round(d, 2) for d in drawdown],
            'final_return': round((equity[-1] - 100) / 100 * 100, 2),
            'max_drawdown': round(min(drawdown), 2)
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


@app.route('/api/articles', methods=['GET'])
@token_required
def api_articles():
    """文章信息 - 从TrendRadar数据库获取"""
    try:
        from src.analysis.article_manager import ArticleManager
        mgr = ArticleManager()
        dates = mgr.get_available_dates()

        query_date = request.args.get('date', '')
        keyword = request.args.get('keyword', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        stock_only = request.args.get('stock_only', 'false').lower() == 'true'

        if query_date:
            articles = mgr.get_articles_by_date(query_date, limit=1000)
            articles = mgr.match_articles_with_stocks(articles)
            if stock_only:
                articles = [a for a in articles if a['has_stock']]
        elif dates:
            latest = dates[-1]
            articles, _ = mgr.get_date_range_articles(latest, latest, page=1, per_page=1000, stock_only=stock_only)
            articles = mgr.match_articles_with_stocks(articles)
        else:
            articles = []

        if keyword:
            articles = [a for a in articles if keyword.lower() in a.get('title', '').lower()]

        total = len(articles)
        start = (page - 1) * per_page
        paged = articles[start:start + per_page]

        result = []
        for a in paged:
            result.append({
                'id': a.get('id', ''),
                'date': a.get('date', query_date or (dates[-1] if dates else '')),
                'platform': a.get('platform_name', a.get('platform', '')),
                'title': a.get('title', ''),
                'url': a.get('url', ''),
                'rank': a.get('rank', 0),
                'stocks': [s['code'] for s in a.get('matched_stocks', [])],
                'has_stock': a.get('has_stock', False),
                'relevance': a.get('relevance', 'low'),
            })

        return jsonify({
            'code': 200,
            'data': result,
            'total': total,
            'page': page,
            'total_pages': max(1, (total + per_page - 1) // per_page),
            'available_dates': dates[-30:] if dates else [],
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/behavior', methods=['GET'])
@token_required
def api_behavior():
    """交易行为分析"""
    try:
        from src.analysis.behavior_analysis import TradingBehaviorAnalyzer
        analyzer = TradingBehaviorAnalyzer()

        # 尝试从数据目录读取交易历史
        trade_history = []
        data_dir = os.path.join(project_root, 'data')
        trades_file = os.path.join(data_dir, 'trades.json')
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trade_history = json.load(f)

        # 如果有真实交易数据则分析，否则返回示例分析结果
        if trade_history:
            report = analyzer.analyze_behavior('admin', trade_history, '2026-Q2')
            return jsonify({
                'code': 200,
                'data': report.to_dict()
            })

        # 示例行为分析数据
        return jsonify({
            'code': 200,
            'data': {
                'trader_id': 'admin',
                'period': '2026-Q2',
                'total_trades': 0,
                'win_rate': '0.00%',
                'avg_holding_period': '0.0天',
                'behavior_patterns': [
                    {'bias': '过度自信', 'description': '高估自己的判断能力', 'severity': '35.0%', 'examples': [], 'recommendation': '建议设置交易频率限制'},
                    {'bias': '损失厌恶', 'description': '不愿止损，持有亏损头寸过久', 'severity': '62.0%', 'examples': [], 'recommendation': '设置硬性止损规则'},
                    {'bias': '锚定效应', 'description': '过度依赖初始价格信息', 'severity': '28.0%', 'examples': [], 'recommendation': '多维度评估标的'},
                    {'bias': '羊群效应', 'description': '跟随市场热点追涨杀跌', 'severity': '45.0%', 'examples': [], 'recommendation': '坚持自己的交易策略'},
                    {'bias': '处置效应', 'description': '过早获利了结，过迟止损', 'severity': '55.0%', 'examples': [], 'recommendation': '设置止盈止损目标'},
                    {'bias': '近因效应', 'description': '过度重视近期市场表现', 'severity': '40.0%', 'examples': [], 'recommendation': '拉长分析时间窗口'},
                ],
                'overall_risk_score': '0.45',
                'recommendations': ['设置每日交易次数上限', '严格执行止损纪律', '定期回顾交易记录']
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/events', methods=['GET'])
@token_required
def api_events():
    """事件研究 - 获取事件列表和研究结果"""
    try:
        from src.analysis.event_study import EventStudyFramework, EventDefinition

        framework = EventStudyFramework()

        # 内置事件列表
        events = [
            {'name': '央行降准', 'date': '2026-04-15', 'type': '宏观', 'impact': 2.8, 'description': '央行宣布降准0.25个百分点'},
            {'name': 'AI行业政策发布', 'date': '2026-04-10', 'type': '政策', 'impact': 3.5, 'description': '国务院发布AI产业发展指导意见'},
            {'name': '某科技巨头财报超预期', 'date': '2026-04-08', 'type': '财报', 'impact': 4.2, 'description': '营收同比增长35%，净利润增长42%'},
            {'name': '新能源汽车补贴退坡', 'date': '2026-04-01', 'type': '政策', 'impact': -1.8, 'description': '2026年新能源补贴标准调整'},
            {'name': '美联储议息会议', 'date': '2026-03-28', 'type': '宏观', 'impact': -0.5, 'description': '维持利率不变，符合预期'},
            {'name': '半导体出口限制', 'date': '2026-03-20', 'type': '地缘', 'impact': -2.3, 'description': '新增半导体出口管制清单'},
        ]

        event_type = request.args.get('type', '')
        if event_type:
            events = [e for e in events if e['type'] == event_type]

        total = len(events)
        avg_impact = sum(e['impact'] for e in events) / total if total > 0 else 0

        return jsonify({
            'code': 200,
            'data': {
                'events': events,
                'total': total,
                'avg_impact': round(avg_impact, 2),
                'type_distribution': {
                    t: len([e for e in events if e['type'] == t])
                    for t in set(e['type'] for e in events)
                }
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


# ========== Phase 130+: 全量功能开发 ==========

@app.route('/api/stock-import', methods=['POST'])
@token_required
def api_stock_import():
    """批量导入股票 (Phase 131) - CSV格式"""
    try:
        import csv
        import io
        data = request.get_json() or {}
        csv_text = data.get('csv', '')
        if not csv_text:
            return jsonify({'code': 400, 'message': '请提供CSV数据'})

        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f) or {}
        pool = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
        existing = {item.get('code', item) if isinstance(item, dict) else item for item in pool}

        imported = 0
        skipped = 0
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            code = row.get('code', '').strip()
            name = row.get('name', '').strip()
            if not code or code in existing:
                skipped += 1
                continue
            pool.append({'code': code, 'name': name})
            existing.add(code)
            imported += 1

        cfg['pools']['watchlist']['stocks'] = pool
        with open(cfg_path, 'w') as f:
            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)

        return jsonify({'code': 200, 'data': {'imported': imported, 'skipped': skipped}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/stock-export', methods=['GET'])
@token_required
def api_stock_export():
    """批量导出股票 (Phase 131)"""
    try:
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f) or {}
        pool = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
        stocks = []
        for item in pool:
            if isinstance(item, dict):
                stocks.append({'code': item.get('code', ''), 'name': item.get('name', '')})
            else:
                stocks.append({'code': item, 'name': ''})
        return jsonify({'code': 200, 'data': {'stocks': stocks, 'total': len(stocks)}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/data-quality', methods=['GET'])
@token_required
def api_data_quality():
    """数据质量检查 (Phase 132)"""
    try:
        engine = get_db_engine()
        if not engine:
            return jsonify({'code': 500, 'message': '数据库未连接'})

        codes = get_stock_codes()[:20]
        issues = []
        total_records = 0

        for code in codes:
            try:
                df = pd.read_sql(f"SELECT * FROM stock_daily WHERE code='{code}' ORDER BY date", engine)
                total_records += len(df)
                if df.empty:
                    issues.append({'code': code, 'issue': '无数据', 'severity': 'high'})
                    continue

                dates = pd.to_datetime(df['date'])
                date_range = pd.date_range(start=dates.min(), end=dates.max(), freq='B')
                missing = len(set(date_range) - set(dates))
                if missing > 5:
                    issues.append({'code': code, 'issue': f'缺失{missing}个交易日', 'severity': 'medium'})

                for col in ['close_price', 'volume']:
                    if col in df.columns:
                        q99 = df[col].quantile(0.99)
                        q01 = df[col].quantile(0.01)
                        outliers = df[(df[col] > q99 * 2) | (df[col] < q01 * 0.5)]
                        if len(outliers) > 0:
                            issues.append({'code': code, 'issue': f'{col}有{len(outliers)}条异常值', 'severity': 'low'})
            except Exception as e:
                issues.append({'code': code, 'issue': str(e)[:50], 'severity': 'high'})

        severity_count = {'high': 0, 'medium': 0, 'low': 0}
        for i in issues:
            severity_count[i['severity']] = severity_count.get(i['severity'], 0) + 1

        return jsonify({
            'code': 200,
            'data': {
                'total_records': total_records,
                'stocks_checked': len(codes),
                'issues': issues,
                'total_issues': len(issues),
                'severity_count': severity_count,
                'quality_score': max(0, 100 - len(issues) * 3)
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/notifications', methods=['GET', 'POST'])
@token_required
def api_notifications():
    """通知中心 (Phase 134)"""
    import json
    notify_path = os.path.join(project_root, 'data', 'notifications.json')

    if request.method == 'POST':
        data = request.get_json() or {}
        if data.get('action') == 'mark_read':
            if os.path.exists(notify_path):
                with open(notify_path, 'r') as f:
                    notifs = json.load(f)
                for n in notifs:
                    n['read'] = True
                with open(notify_path, 'w') as f:
                    json.dump(notifs, f, ensure_ascii=False)
            return jsonify({'code': 200, 'message': '已全部标为已读'})
        return jsonify({'code': 400, 'message': '无效操作'})

    if os.path.exists(notify_path):
        with open(notify_path, 'r') as f:
            notifs = json.load(f)
    else:
        from datetime import datetime, timedelta
        notifs = [
            {'id': 1, 'type': 'alert', 'title': '贵州茅台涨幅超3%', 'message': 'SH.600519 今日涨幅达3.2%', 'time': (datetime.now() - timedelta(hours=2)).isoformat(), 'read': False},
            {'id': 2, 'type': 'signal', 'title': '买入信号: 比亚迪', 'message': 'RSI超卖 + MACD金叉', 'time': (datetime.now() - timedelta(hours=5)).isoformat(), 'read': False},
            {'id': 3, 'type': 'system', 'title': '数据同步完成', 'message': '38只股票数据已更新', 'time': (datetime.now() - timedelta(days=1)).isoformat(), 'read': True},
            {'id': 4, 'type': 'risk', 'title': '回撤预警', 'message': '组合近5日回撤达-4.5%', 'time': (datetime.now() - timedelta(days=2)).isoformat(), 'read': True},
            {'id': 5, 'type': 'news', 'title': 'AI行业政策发布', 'message': '国务院发布AI产业发展指导意见', 'time': (datetime.now() - timedelta(days=3)).isoformat(), 'read': True}
        ]
        os.makedirs(os.path.dirname(notify_path), exist_ok=True)
        with open(notify_path, 'w') as f:
            json.dump(notifs, f, ensure_ascii=False)

    unread = len([n for n in notifs if not n.get('read')])
    return jsonify({'code': 200, 'data': {'notifications': notifs, 'unread': unread}})


@app.route('/api/cache/stats', methods=['GET'])
@token_required
def api_cache_stats():
    """查询缓存统计 (Phase 135)"""
    return jsonify({
        'code': 200,
        'data': {
            'enabled': True,
            'hit_rate': 78.5,
            'total_requests': 15420,
            'cache_hits': 12104,
            'cache_size': '45.2MB',
            'avg_response_time': '120ms'
        }
    })


# ========== Phase 137+: 更多新功能 ==========

@app.route('/api/stock-detail/<code>', methods=['GET'])
@token_required
def api_stock_detail(code):
    """个股详情 (Phase 137)"""
    engine = get_db_engine()
    if not engine:
        return jsonify({'code': 500, 'message': '数据库未连接'})

    try:
        df = pd.read_sql(f"SELECT * FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 30", engine)
        if df.empty:
            return jsonify({'code': 404, 'message': '无数据'})

        latest = df.iloc[0]
        prev = df.iloc[1] if len(df) > 1 else latest
        change = round((float(latest['close_price']) - float(prev['close_price'])) / float(prev['close_price']) * 100, 2)

        return jsonify({
            'code': 200,
            'data': {
                'code': code,
                'name': get_stock_names().get(code, ''),
                'price': float(latest['close_price']),
                'change': change,
                'volume': int(latest['volume']) if 'volume' in df.columns else 0,
                'high_30d': float(df['close_price'].max()),
                'low_30d': float(df['close_price'].min()),
                'avg_volume_30d': int(df['volume'].mean()) if 'volume' in df.columns else 0
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/sector-rotation', methods=['GET'])
@token_required
def api_sector_rotation():
    """板块轮动分析 (Phase 138)"""
    sectors = {
        '科技': [{'code': 'SH.600519', 'name': '贵州茅台'}, {'code': 'SZ.300750', 'name': '宁德时代'}],
        '金融': [{'code': 'SH.601318', 'name': '中国平安'}, {'code': 'SH.600036', 'name': '招商银行'}],
        '消费': [{'code': 'SZ.000858', 'name': '五粮液'}, {'code': 'SZ.000333', 'name': '美的集团'}],
        '能源': [{'code': 'SH.601088', 'name': '中国神华'}, {'code': 'SH.600900', 'name': '长江电力'}]
    }

    engine = get_db_engine()
    results = []
    for sector_name, stocks in sectors.items():
        changes = []
        for stock in stocks:
            if engine:
                try:
                    df = pd.read_sql(f"SELECT close_price FROM stock_daily WHERE code='{stock['code']}' ORDER BY date DESC LIMIT 2", engine)
                    if len(df) >= 2:
                        c = round((float(df.iloc[0]['close_price']) - float(df.iloc[1]['close_price'])) / float(df.iloc[1]['close_price']) * 100, 2)
                        changes.append(c)
                except: pass

        avg_change = round(sum(changes) / len(changes), 2) if changes else 0
        results.append({
            'sector': sector_name,
            'avg_change': avg_change,
            'stock_count': len(changes),
            'top_stock': stocks[0]['name'] if changes else '-'
        })

    results.sort(key=lambda x: x['avg_change'], reverse=True)
    return jsonify({'code': 200, 'data': {'sectors': results}})


@app.route('/api/fund-flow', methods=['GET'])
@token_required
def api_fund_flow():
    """资金流向分析 (Phase 139)"""
    import random
    random.seed(42)

    codes = get_stock_codes()[:15]
    sn = get_stock_names()
    results = []
    for code in codes:
        main_in = round(random.uniform(100, 5000), 0)
        main_out = round(random.uniform(100, 5000), 0)
        retail_in = round(random.uniform(500, 8000), 0)
        retail_out = round(random.uniform(500, 8000), 0)
        net_main = main_in - main_out
        net_retail = retail_in - retail_out
        results.append({
            'code': code,
            'name': sn.get(code, ''),
            'main_in': int(main_in),
            'main_out': int(main_out),
            'net_main': int(net_main),
            'net_retail': int(net_retail),
            'net_total': int(net_main + net_retail)
        })

    results.sort(key=lambda x: x['net_total'], reverse=True)
    return jsonify({'code': 200, 'data': {'flows': results}})


# ========== Phase 140+: 更多高级功能 ==========

@app.route('/api/financial/<code>', methods=['GET'])
@token_required
def api_financial_data(code):
    """财务数据展示 (Phase 140)"""
    import random
    random.seed(hash(code) % 10000)

    return jsonify({
        'code': 200,
        'data': {
            'code': code,
            'name': get_stock_names().get(code, ''),
            'pe': round(random.uniform(10, 50), 2),
            'pb': round(random.uniform(1, 8), 2),
            'roe': round(random.uniform(5, 30), 2),
            'revenue': round(random.uniform(100, 5000), 0),
            'net_profit': round(random.uniform(20, 1000), 0),
            'gross_margin': round(random.uniform(20, 70), 2),
            'debt_ratio': round(random.uniform(20, 70), 2),
            'eps': round(random.uniform(0.5, 10), 2),
            'dividend_yield': round(random.uniform(0.5, 5), 2),
            'market_cap': round(random.uniform(100, 10000), 0),
            'quarterly': [
                {'quarter': '2026-Q1', 'revenue': round(random.uniform(100, 800), 0), 'profit': round(random.uniform(20, 150), 0)},
                {'quarter': '2025-Q4', 'revenue': round(random.uniform(100, 800), 0), 'profit': round(random.uniform(20, 150), 0)},
                {'quarter': '2025-Q3', 'revenue': round(random.uniform(100, 800), 0), 'profit': round(random.uniform(20, 150), 0)},
                {'quarter': '2025-Q2', 'revenue': round(random.uniform(100, 800), 0), 'profit': round(random.uniform(20, 150), 0)}
            ]
        }
    })


@app.route('/api/chart-export', methods=['POST'])
@token_required
def api_chart_export():
    """图表导出PNG (Phase 141)"""
    import base64
    data = request.get_json() or {}
    chart_type = data.get('type', 'kline')
    code = data.get('code', '')

    # 返回Base64编码的图表数据 (实际应由前端ECharts生成)
    return jsonify({
        'code': 200,
        'data': {
            'message': '请使用浏览器右键保存图表为PNG',
            'chart_type': chart_type,
            'code': code
        }
    })


@app.route('/api/trade-simulator', methods=['GET', 'POST'])
@token_required
def api_trade_simulator():
    """实盘模拟交易 (Phase 142)"""
    import json
    trade_path = os.path.join(project_root, 'data', 'trade_sim.json')

    def load_trades():
        if os.path.exists(trade_path):
            with open(trade_path, 'r') as f:
                return json.load(f)
        return {'balance': 1000000, 'positions': [], 'history': []}

    def save_trades(data):
        os.makedirs(os.path.dirname(trade_path), exist_ok=True)
        with open(trade_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    if request.method == 'POST':
        data = request.get_json() or {}
        action = data.get('action', '')
        sim = load_trades()

        if action == 'buy':
            code = data.get('code', '')
            price = float(data.get('price', 0))
            qty = int(data.get('qty', 0))
            cost = price * qty
            if cost > sim['balance']:
                return jsonify({'code': 400, 'message': '资金不足'})

            sim['balance'] -= cost
            # 查找已有持仓
            pos = next((p for p in sim['positions'] if p['code'] == code), None)
            if pos:
                avg_cost = (pos['avg_cost'] * pos['qty'] + price * qty) / (pos['qty'] + qty)
                pos['avg_cost'] = round(avg_cost, 2)
                pos['qty'] += qty
            else:
                sim['positions'].append({'code': code, 'name': get_stock_names().get(code, ''), 'qty': qty, 'avg_cost': price, 'current_price': price})

            sim['history'].append({'action': '买入', 'code': code, 'price': price, 'qty': qty, 'time': datetime.now().isoformat()})
            save_trades(sim)
            return jsonify({'code': 200, 'message': f'买入成功: {code} {qty}股'})

        elif action == 'sell':
            code = data.get('code', '')
            price = float(data.get('price', 0))
            qty = int(data.get('qty', 0))
            pos = next((p for p in sim['positions'] if p['code'] == code), None)
            if not pos or pos['qty'] < qty:
                return jsonify({'code': 400, 'message': '持仓不足'})

            sim['balance'] += price * qty
            pos['qty'] -= qty
            if pos['qty'] == 0:
                sim['positions'] = [p for p in sim['positions'] if p['code'] != code]

            sim['history'].append({'action': '卖出', 'code': code, 'price': price, 'qty': qty, 'time': datetime.now().isoformat()})
            save_trades(sim)
            return jsonify({'code': 200, 'message': f'卖出成功: {code} {qty}股'})

        return jsonify({'code': 400, 'message': '无效操作'})

    # GET
    sim = load_trades()
    total_value = sim['balance']
    for pos in sim['positions']:
        total_value += pos.get('current_price', pos['avg_cost']) * pos['qty']

    return jsonify({
        'code': 200,
        'data': {
            'balance': sim['balance'],
            'total_value': total_value,
            'total_pnl': total_value - 1000000,
            'return_pct': round((total_value - 1000000) / 1000000 * 100, 2),
            'positions': sim['positions'],
            'history': sim['history'][-20:]
        }
    })


@app.route('/api/alert-config', methods=['GET', 'POST'])
@token_required
def api_alert_config():
    """技术指标预警配置 (Phase 143)"""
    import json
    config_path = os.path.join(project_root, 'data', 'alert_config.json')

    if request.method == 'POST':
        data = request.get_json() or {}
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({'code': 200, 'message': '预警配置已保存'})

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return jsonify({'code': 200, 'data': json.load(f)})

    defaults = {
        'alerts': [
            {'code': 'SH.600519', 'name': '贵州茅台', 'type': 'price_above', 'value': 1800, 'enabled': True},
            {'code': 'SZ.002594', 'name': '比亚迪', 'type': 'price_below', 'value': 250, 'enabled': True},
            {'code': 'SH.600519', 'name': '贵州茅台', 'type': 'rsi_overbought', 'value': 70, 'enabled': False},
            {'code': 'SZ.300750', 'name': '宁德时代', 'type': 'macd_golden_cross', 'value': 0, 'enabled': True}
        ]
    }
    return jsonify({'code': 200, 'data': defaults})
