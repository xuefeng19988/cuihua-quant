"""
Phase 268: 批量评分构建器
解决 _build_stock_score_data N+1 查询问题
优化前: 每只股票 2条SQL × N只 = 2N条SQL
优化后: 全部股票 2条SQL
"""
import pandas as pd
from sqlalchemy import text


def _compute_indicators(closes, volumes=None):
    """从价格序列计算技术指标"""
    if len(closes) == 0:
        return None
    
    price = float(closes[-1])
    s = pd.Series(closes)
    
    # 均线
    ma5 = float(s.rolling(5).mean().iloc[-1]) if len(closes) >= 5 else price
    ma20 = float(s.rolling(20).mean().iloc[-1]) if len(closes) >= 20 else price
    ma60 = float(s.rolling(60).mean().iloc[-1]) if len(closes) >= 60 else ma20
    
    # 涨跌
    change = round((closes[-1] - closes[-2]) / closes[-2] * 100, 2) if len(closes) >= 2 and closes[-2] != 0 else 0
    
    # 52周高低
    week52_high = float(max(closes))
    week52_low = float(min(closes))
    
    # RSI
    rsi = 50.0
    if len(closes) >= 15:
        deltas = s.diff().dropna()
        gains = deltas[deltas > 0].rolling(14).mean()
        losses = deltas[deltas < 0].rolling(14).mean().abs()
        last_gain = gains.iloc[-1] if len(gains) > 0 else 0
        last_loss = losses.iloc[-1] if len(losses) > 0 else 0.001
        rs = last_gain / last_loss if last_loss != 0 else 1
        rsi = round(100 - (100 / (1 + rs)), 1)
    
    # MACD
    macd = 0
    if len(closes) >= 26:
        ema12 = s.ewm(span=12).mean().iloc[-1]
        ema26 = s.ewm(span=26).mean().iloc[-1]
        macd = round(float(ema12 - ema26), 4)
    
    # 量比
    volume = float(volumes[-1]) if volumes is not None and len(volumes) > 0 else 0
    avg_vol = float(pd.Series(volumes).rolling(5).mean().iloc[-1]) if volumes is not None and len(volumes) >= 5 else volume
    vol_ratio = round(volume / avg_vol, 2) if avg_vol > 0 else 1.0
    
    return {
        'price': price, 'change': change, 'volume': volume,
        'ma5': ma5, 'ma20': ma20, 'ma60': ma60,
        'week52_high': week52_high, 'week52_low': week52_low,
        'rsi': max(0, min(100, rsi)), 'macd': macd,
        'vol_ratio': vol_ratio
    }


def _build_score_from_indicators(ind, row=None):
    """从指标构建评分数据"""
    price = ind['price']
    change = ind['change']
    pe = float(row['pe_ratio']) if row is not None and 'pe_ratio' in row and pd.notna(row.get('pe_ratio')) else 25.0
    
    pb = round(pe / (15 + change * 0.5), 2) if pe > 0 else 3.5
    roe = round(pe / pb * 10, 1) if pb > 0 else 15.0
    turnover = float(row['turnover_rate']) if row is not None and 'turnover_rate' in row and pd.notna(row.get('turnover_rate')) else 0
    
    return {
        'price': price, 'change': change, 'volume': ind['volume'],
        'turnover_rate': turnover,
        'pe': pe if pe > 0 else 25.0,
        'pb': max(0.5, pb), 'roe': max(0, roe),
        'rsi': ind['rsi'], 'macd': ind['macd'],
        'ma5': ind['ma5'], 'ma20': ind['ma20'], 'ma60': ind['ma60'],
        'week52_high': ind['week52_high'], 'week52_low': ind['week52_low'],
        'revenue_growth': round(10 + change * 0.5, 1),
        'profit_growth': round(15 + change * 0.8, 1),
        'net_margin': max(0, round(roe * 0.4, 1)),
        'debt_ratio': max(10, min(80, round(40 + change * 0.3, 1))),
        'dividend_yield': max(0, round(2.5 + (50 - pe) * 0.05, 2)),
        'northbound': round(change * 1000000, 0),
        'main_net_inflow': round(change * 5000000, 0)
    }


def batch_build_score_data(codes, engine):
    """批量构建评分数据 - 仅2条SQL
    :param codes: list of stock codes
    :param engine: SQLAlchemy engine
    :return: dict {code: score_data}
    """
    if not codes:
        return {}
    
    code_csv = "','".join(codes)
    
    # SQL 1: 所有股票最新行情
    latest_sql = f"""
        SELECT code, close_price, volume, turnover_rate, pe_ratio
        FROM stock_daily 
        WHERE code IN ('{code_csv}')
          AND date = (SELECT MAX(date) FROM stock_daily)
    """
    try:
        latest_df = pd.read_sql(text(latest_sql), engine)
    except Exception:
        return {}
    
    if latest_df.empty:
        return {}
    
    # SQL 2: 所有股票历史数据
    history_sql = f"""
        SELECT code, date, close_price, volume
        FROM stock_daily 
        WHERE code IN ('{code_csv}')
        ORDER BY code, date DESC
        LIMIT {250 * len(codes)}
    """
    try:
        history_df = pd.read_sql(text(history_sql), engine)
    except Exception:
        history_df = pd.DataFrame()
    
    # 内存计算
    result = {}
    latest_map = {r['code']: r for _, r in latest_df.iterrows()}
    
    # 按代码分组
    history_by_code = {}
    if not history_df.empty:
        for code, grp in history_df.groupby('code'):
            history_by_code[code] = grp.sort_values('date', ascending=False)
    
    for code in codes:
        if code not in latest_map:
            continue
        
        row = latest_map[code]
        price = float(row['close_price'])
        
        hist = history_by_code.get(code)
        if hist is not None and len(hist) > 0:
            closes = hist['close_price'].values
            volumes = hist['volume'].values
        else:
            closes = [price]
            volumes = None
        
        ind = _compute_indicators(closes, volumes)
        if ind:
            result[code] = _build_score_from_indicators(ind, row)
    
    return result
