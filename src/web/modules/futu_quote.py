"""
Futu风格行情模块 - Phase 244
提供专业级股票行情数据，参考Futu牛牛设计
"""
from flask import Blueprint, request, jsonify
import random
from datetime import datetime, timedelta

futu_bp = Blueprint('futu', __name__)

# 模拟Futu风格数据
def _generate_futu_data(code, name):
    """生成Futu风格股票数据"""
    random.seed(hash(code) % 10000)
    
    # 基础价格
    base_price = random.uniform(20, 2000)
    prev_close = round(base_price * (1 + random.uniform(-0.03, 0.03)), 2)
    current_price = round(prev_close * (1 + random.uniform(-0.05, 0.05)), 2)
    change = round(current_price - prev_close, 2)
    change_pct = round(change / prev_close * 100, 2)
    
    # 盘口数据 (5档)
    ask_levels = []
    bid_levels = []
    for i in range(5):
        ask_price = round(current_price + (i + 1) * current_price * 0.001, 2)
        bid_price = round(current_price - (i + 1) * current_price * 0.001, 2)
        ask_vol = random.randint(10, 500)
        bid_vol = random.randint(10, 500)
        ask_levels.append({'price': ask_price, 'volume': ask_vol, 'turnover': round(ask_price * ask_vol, 2)})
        bid_levels.append({'price': bid_price, 'volume': bid_vol, 'turnover': round(bid_price * bid_vol, 2)})
    
    # 交易统计
    high = round(current_price * (1 + random.uniform(0, 0.05)), 2)
    low = round(current_price * (1 - random.uniform(0, 0.05)), 2)
    open_price = round(prev_close * (1 + random.uniform(-0.02, 0.02)), 2)
    volume = random.randint(100000, 50000000)
    turnover = round(volume * current_price, 2)
    amplitude = round((high - low) / prev_close * 100, 2)
    
    # 市值数据
    total_shares = random.randint(1000000000, 100000000000)
    float_shares = int(total_shares * random.uniform(0.6, 0.9))
    total_market_cap = round(total_shares * current_price, 2)
    float_market_cap = round(float_shares * current_price, 2)
    
    # 估值指标
    pe_ttm = round(random.uniform(5, 80), 2)
    pe_static = round(pe_ttm * random.uniform(0.9, 1.1), 2)
    pe_dynamic = round(pe_ttm * random.uniform(0.95, 1.05), 2)
    pb = round(random.uniform(0.5, 15), 2)
    ps_ttm = round(random.uniform(0.5, 10), 2)
    dividend_yield = round(random.uniform(0.5, 5), 2)
    roe = round(random.uniform(5, 35), 2)
    
    # 52周高低
    week52_high = round(current_price * (1 + random.uniform(0.1, 0.5)), 2)
    week52_low = round(current_price * (1 - random.uniform(0.1, 0.5)), 2)
    
    # 涨跌停价 (A股10%, 科创板/创业板20%, 港股无)
    is_a_share = code.startswith(('SH.', 'SZ.'))
    is_star = code.startswith(('SH.688', 'SH.689'))
    is_gem = code.startswith(('SZ.300', 'SZ.301'))
    limit_pct = 0.2 if (is_star or is_gem) else (0.1 if is_a_share else 0)
    
    data = {
        'basic': {
            'code': code,
            'name': name,
            'market': 'A股' if is_a_share else ('港股' if code.startswith('HK.') else '美股'),
            'sector': random.choice(['白酒', '新能源', '金融', '科技', '医药', '消费']),
            'industry': random.choice(['制造业', '信息技术', '金融业', '消费品']),
            'list_date': '2010-01-01',
            'exchange': '上交所' if code.startswith('SH.') else ('深交所' if code.startswith('SZ.') else '港交所')
        },
        'quote': {
            'current_price': current_price,
            'prev_close': prev_close,
            'open': open_price,
            'high': high,
            'low': low,
            'change': change,
            'change_pct': change_pct,
            'volume': volume,
            'turnover': turnover,
            'amplitude': amplitude,
            'turnover_rate': round(volume / float_shares * 100, 2),
            'volume_ratio': round(random.uniform(0.5, 3.0), 2),
            'bid_price': bid_levels[0]['price'],
            'ask_price': ask_levels[0]['price'],
            'bid_vol': bid_levels[0]['volume'],
            'ask_vol': ask_levels[0]['volume']
        },
        'order_book': {
            'asks': ask_levels,
            'bids': bid_levels
        },
        'market_cap': {
            'total_shares': total_shares,
            'float_shares': float_shares,
            'total_market_cap': total_market_cap,
            'float_market_cap': float_market_cap
        },
        'valuation': {
            'pe_ttm': pe_ttm,
            'pe_static': pe_static,
            'pe_dynamic': pe_dynamic,
            'pb': pb,
            'ps_ttm': ps_ttm,
            'dividend_yield': dividend_yield,
            'roe': roe
        },
        'price_range': {
            'week52_high': week52_high,
            'week52_low': week52_low,
            'day_limit_up': round(prev_close * (1 + limit_pct), 2) if limit_pct > 0 else None,
            'day_limit_down': round(prev_close * (1 - limit_pct), 2) if limit_pct > 0 else None
        },
        'capital_flow': {
            'main_net_inflow': round(random.uniform(-5000, 5000), 0),
            'retail_net_inflow': round(random.uniform(-3000, 3000), 0),
            'northbound_net_inflow': round(random.uniform(-2000, 2000), 0),
            'super_large_net_inflow': round(random.uniform(-2000, 2000), 0),
            'large_net_inflow': round(random.uniform(-2000, 2000), 0),
            'medium_net_inflow': round(random.uniform(-2000, 2000), 0),
            'small_net_inflow': round(random.uniform(-2000, 2000), 0)
        },
        'technical': {
            'ma5': round(current_price * random.uniform(0.98, 1.02), 2),
            'ma10': round(current_price * random.uniform(0.96, 1.04), 2),
            'ma20': round(current_price * random.uniform(0.94, 1.06), 2),
            'ma60': round(current_price * random.uniform(0.90, 1.10), 2),
            'rsi14': round(random.uniform(20, 80), 2),
            'macd_dif': round(random.uniform(-2, 2), 4),
            'macd_dea': round(random.uniform(-2, 2), 4),
            'macd_hist': round(random.uniform(-1, 1), 4),
            'boll_upper': round(current_price * 1.05, 2),
            'boll_mid': round(current_price, 2),
            'boll_lower': round(current_price * 0.95, 2)
        },
        'support_resistance': [
            {'type': '压力3', 'price': round(current_price * 1.10, 2), 'strength': '弱'},
            {'type': '压力2', 'price': round(current_price * 1.05, 2), 'strength': '中'},
            {'type': '压力1', 'price': round(current_price * 1.03, 2), 'strength': '强'},
            {'type': '支撑1', 'price': round(current_price * 0.97, 2), 'strength': '强'},
            {'type': '支撑2', 'price': round(current_price * 0.95, 2), 'strength': '中'},
            {'type': '支撑3', 'price': round(current_price * 0.90, 2), 'strength': '弱'}
        ]
    }
    
    return data


@futu_bp.route('/api/futu/quote/<code>', methods=['GET'])
def api_futu_quote(code):
    """获取Futu风格行情数据"""
    # 从股票池获取名称
    try:
        from src.data.database import get_db_engine
        from sqlalchemy import text
        engine = get_db_engine()
        if engine:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT close_price FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 1"))
                row = result.fetchone()
                if not row:
                    return jsonify({'code': 404, 'message': '股票不存在'})
    except:
        pass
    
    name = f"股票{code}"
    data = _generate_futu_data(code, name)
    
    return jsonify({'code': 200, 'data': data})


@futu_bp.route('/api/futu/intraday/<code>', methods=['GET'])
def api_futu_intraday(code):
    """获取Futu风格分时数据"""
    period = request.args.get('period', 'today')
    
    # 生成分时数据
    data_points = []
    base_price = random.uniform(100, 2000)
    now = datetime.now()
    
    if period == 'today':
        # 今日分时 (每5分钟一个点)
        for i in range(48):
            hour = 9 + i // 12
            minute = (i % 12) * 5
            if hour == 12:
                continue
            if hour > 12:
                hour = 13 + (hour - 13)
            time_str = f"{hour:02d}:{minute:02d}"
            price = round(base_price * (1 + random.uniform(-0.02, 0.02)), 2)
            volume = random.randint(10000, 500000)
            data_points.append({'time': time_str, 'price': price, 'avg_price': round(price * random.uniform(0.99, 1.01), 2), 'volume': volume})
    else:
        # 5日分时
        for d in range(5):
            date = now - timedelta(days=4-d)
            for i in range(48):
                hour = 9 + i // 12
                minute = (i % 12) * 5
                if hour == 12:
                    continue
                if hour > 12:
                    hour = 13 + (hour - 13)
                time_str = f"{date.strftime('%m-%d')} {hour:02d}:{minute:02d}"
                price = round(base_price * (1 + random.uniform(-0.03, 0.03)), 2)
                volume = random.randint(10000, 500000)
                data_points.append({'time': time_str, 'price': price, 'avg_price': round(price * random.uniform(0.99, 1.01), 2), 'volume': volume})
    
    return jsonify({'code': 200, 'data': {'code': code, 'period': period, 'data': data_points}})


@futu_bp.route('/api/futu/kline/<code>', methods=['GET'])
def api_futu_kline(code):
    """获取Futu风格K线数据"""
    ktype = request.args.get('ktype', 'D')  # D日K/W周K/M月K
    days = int(request.args.get('days', 90))
    
    try:
        from src.data.database import get_db_engine
        from sqlalchemy import text
        engine = get_db_engine()
        if engine:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT {days}"))
                rows = result.fetchall()
                if rows:
                    kline_data = []
                    for row in reversed(rows):
                        kline_data.append({
                            'date': str(row[1]) if len(row) > 1 else '',
                            'open': float(row[2]) if len(row) > 2 else 0,
                            'high': float(row[3]) if len(row) > 3 else 0,
                            'low': float(row[4]) if len(row) > 4 else 0,
                            'close': float(row[5]) if len(row) > 5 else 0,
                            'volume': float(row[6]) if len(row) > 6 else 0,
                            'turnover': float(row[7]) if len(row) > 7 else 0
                        })
                    return jsonify({'code': 200, 'data': {'code': code, 'ktype': ktype, 'data': kline_data}})
    except Exception as e:
        pass
    
    return jsonify({'code': 404, 'message': 'K线数据不存在'})


@futu_bp.route('/api/futu/financials/<code>', methods=['GET'])
def api_futu_financials(code):
    """获取Futu风格财务数据"""
    return jsonify({
        'code': 200,
        'data': {
            'code': code,
            'income_statement': {
                'revenue': {'ttm': 1253.5, 'q1': 285.2, 'q2': 312.5, 'q3': 328.8, 'q4': 327.0, 'yoy': 15.2},
                'gross_profit': {'ttm': 656.3, 'q1': 148.5, 'q2': 164.2, 'q3': 173.8, 'q4': 169.8, 'yoy': 12.8},
                'net_profit': {'ttm': 456.2, 'q1': 102.5, 'q2': 115.8, 'q3': 121.2, 'q4': 116.7, 'yoy': 18.5},
                'gross_margin': 52.3,
                'net_margin': 36.4,
                'roe': 18.5,
                'eps': 5.62
            },
            'balance_sheet': {
                'total_assets': 2568.5,
                'total_liabilities': 1235.8,
                'equity': 1332.7,
                'cash': 568.2,
                'debt_ratio': 48.1
            },
            'cash_flow': {
                'operating_cf': 523.8,
                'investing_cf': -185.5,
                'financing_cf': -125.2,
                'free_cf': 385.2
            },
            'valuation_ratios': {
                'pe_ttm': 30.2,
                'pe_static': 28.5,
                'pe_dynamic': 29.8,
                'pb': 6.5,
                'ps_ttm': 5.2,
                'dividend_yield': 2.5,
                'peg': 1.8
            }
        }
    })


@futu_bp.route('/api/futu/capital-flow/<code>', methods=['GET'])
def api_futu_capital_flow(code):
    """获取Futu风格资金流向数据"""
    data = _generate_futu_data(code, '')
    
    # 生成历史资金流向
    flow_history = []
    for i in range(20):
        date = (datetime.now() - timedelta(days=19-i)).strftime('%Y-%m-%d')
        flow_history.append({
            'date': date,
            'main_net_inflow': round(random.uniform(-5000, 5000), 0),
            'northbound_net_inflow': round(random.uniform(-2000, 2000), 0)
        })
    
    result = data['capital_flow']
    result['history'] = flow_history
    
    return jsonify({'code': 200, 'data': result})


@futu_bp.route('/api/futu/technical/<code>', methods=['GET'])
def api_futu_technical(code):
    """获取Futu风格技术指标"""
    data = _generate_futu_data(code, '')
    return jsonify({'code': 200, 'data': data['technical']})


@futu_bp.route('/api/futu/related-stocks/<code>', methods=['GET'])
def api_futu_related_stocks(code):
    """获取Futu风格相关股票"""
    related = [
        {'code': 'SH.600519', 'name': '贵州茅台', 'change': 2.35, 'reason': '同行业'},
        {'code': 'SZ.000858', 'name': '五粮液', 'change': 1.85, 'reason': '同行业'},
        {'code': 'SZ.000568', 'name': '泸州老窖', 'change': -0.75, 'reason': '同行业'},
        {'code': 'SH.600809', 'name': '山西汾酒', 'change': 3.15, 'reason': '同行业'},
        {'code': 'SZ.002304', 'name': '洋河股份', 'change': 0.95, 'reason': '同行业'}
    ]
    return jsonify({'code': 200, 'data': related})
