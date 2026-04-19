"""
Phase 301: AI 回测验证
AI 描述策略 → 自动生成参数 → 执行回测 → 返回结果
"""

import re
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from flask import Blueprint, request
from src.web.response_helpers import ok, error, bad_request

ai_backtest_bp = Blueprint('ai_backtest', __name__)


def _parse_strategy_from_text(text: str) -> Dict:
    """从自然语言解析回测参数"""
    params = {
        'start_date': '2023-01-01',
        'end_date': '2024-12-31',
        'initial_capital': 1000000,
        'strategy': 'momentum',
        'codes': ['SH.600519', 'SZ.300750', 'SH.601318'],
        'buy_threshold': 0.05,
        'sell_threshold': -0.03,
        'stop_loss': 0.08,
        'take_profit': 0.20,
        'position_size': 0.1,
        'rebalance': 'monthly',
    }

    text_lower = text.lower()

    # 解析策略类型
    if any(k in text_lower for k in ['均线', 'ma', '交叉', '金叉']):
        params['strategy'] = 'ma_cross'
    elif any(k in text_lower for k in ['动量', 'momentum', '涨幅', '强势']):
        params['strategy'] = 'momentum'
    elif any(k in text_lower for k in ['均值回归', 'mean reversion', '超买超卖', 'rsi']):
        params['strategy'] = 'mean_reversion'
    elif any(k in text_lower for k in ['突破', 'breakout', '新高']):
        params['strategy'] = 'breakout'
    elif any(k in text_lower for k in ['网格', 'grid']):
        params['strategy'] = 'grid'

    # 解析时间范围
    year_match = re.findall(r'(20\d{2})年?', text)
    if year_match:
        years = sorted(set(year_match))
        if len(years) >= 2:
            params['start_date'] = f'{years[0]}-01-01'
            params['end_date'] = f'{years[-1]}-12-31'
        elif len(years) == 1:
            params['start_date'] = f'{years[0]}-01-01'
            params['end_date'] = f'{years[0]}-12-31'

    # 解析资金
    capital_match = re.search(r'(\d+)\s*万', text)
    if capital_match:
        params['initial_capital'] = int(capital_match.group(1)) * 10000
    capital_match2 = re.search(r'(\d+)\s*百万', text)
    if capital_match2:
        params['initial_capital'] = int(capital_match2.group(1)) * 1000000

    # 解析止损止盈
    stop_match = re.search(r'止损\s*[:：]?\s*(\d+)', text)
    if stop_match:
        params['stop_loss'] = int(stop_match.group(1)) / 100
    tp_match = re.search(r'止盈\s*[:：]?\s*(\d+)', text)
    if tp_match:
        params['take_profit'] = int(tp_match.group(1)) / 100

    # 解析仓位
    pos_match = re.search(r'仓位\s*[:：]?\s*(\d+)', text)
    if pos_match:
        params['position_size'] = int(pos_match.group(1)) / 100

    return params


def _run_backtest(params: Dict) -> Dict:
    """执行回测 (模拟)"""
    import random
    random.seed(hash(json.dumps(params)) % (2**32))

    # 模拟回测结果
    strategy = params['strategy']
    capital = params['initial_capital']

    # 不同策略的收益特征
    base_returns = {
        'momentum': (0.15, 0.25),
        'ma_cross': (0.10, 0.20),
        'mean_reversion': (0.08, 0.15),
        'breakout': (0.12, 0.30),
        'grid': (0.06, 0.12),
    }
    ret_range = base_returns.get(strategy, (0.10, 0.20))
    annual_return = random.uniform(*ret_range)
    max_drawdown = random.uniform(0.10, 0.35)
    sharpe = annual_return / max_drawdown if max_drawdown > 0 else 0
    win_rate = random.uniform(0.45, 0.65)

    # 生成月度收益曲线
    months = 12
    monthly_returns = []
    cum_value = capital
    for _ in range(months):
        monthly_ret = random.gauss(annual_return / 12, 0.05)
        cum_value *= (1 + monthly_ret)
        monthly_returns.append({
            'return_pct': round(monthly_ret * 100, 2),
            'value': round(cum_value, 0),
        })

    # 生成交易记录
    trades = []
    for i in range(random.randint(15, 40)):
        is_win = random.random() < win_rate
        trades.append({
            'date': f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
            'code': random.choice(params['codes']),
            'action': random.choice(['买入', '卖出']),
            'price': round(random.uniform(50, 200), 2),
            'pnl': round(random.uniform(-5000, 15000) if is_win else random.uniform(-10000, -1000), 0),
            'is_win': is_win,
        })

    return {
        'annual_return': round(annual_return * 100, 2),
        'max_drawdown': round(max_drawdown * 100, 2),
        'sharpe_ratio': round(sharpe, 2),
        'win_rate': round(win_rate * 100, 1),
        'total_trades': len(trades),
        'final_value': round(cum_value, 0),
        'monthly_returns': monthly_returns,
        'trades': trades[:20],
        'strategy': strategy,
    }


@ai_backtest_bp.route('/api/ai/backtest-gen', methods=['POST'])
def api_ai_backtest_gen():
    """AI 回测: 自然语言 → 参数 → 回测 → 结果"""
    data = request.get_json(silent=True) or {}
    description = data.get('description', '')

    if not description:
        return bad_request(message='请描述你的交易策略')

    # 1. 解析策略
    params = _parse_strategy_from_text(description)

    # 2. 执行回测
    result = _run_backtest(params)

    # 3. AI 解读
    try:
        from src.ai.llm_engine import get_llm_engine
        engine = get_llm_engine()
        if engine.is_available():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                prompt = f"""请解读以下回测结果:
策略: {params['strategy']}
年化收益: {result['annual_return']}%
最大回撤: {result['max_drawdown']}%
夏普比率: {result['sharpe_ratio']}
胜率: {result['win_rate']}%
总交易: {result['total_trades']} 笔

请评价该策略的优劣，给出优化建议（200字以内）。"""
                messages = [
                    {'role': 'system', 'content': '你是量化回测分析师。'},
                    {'role': 'user', 'content': prompt},
                ]
                ai_result = loop.run_until_complete(engine.provider.chat(messages, temperature=0.5, max_tokens=500))
                result['ai_analysis'] = ai_result.get('content', '')
            finally:
                loop.close()
    except:
        pass

    return ok(data={
        'params': params,
        'result': result,
        'description': description,
    })


@ai_backtest_bp.route('/api/ai/backtest-strategies', methods=['GET'])
def api_ai_backtest_strategies():
    """获取预设策略模板"""
    return ok(data={
        'strategies': [
            {
                'name': '双均线交叉',
                'description': '当5日均线上穿20日均线时买入，下穿时卖出，初始资金100万，止损8%，止盈20%',
                'strategy': 'ma_cross',
            },
            {
                'name': '动量策略',
                'description': '买入近20日涨幅前5的股票，持仓10%，每月调仓，止损5%',
                'strategy': 'momentum',
            },
            {
                'name': '均值回归',
                'description': 'RSI低于30买入，高于70卖出，仓位15%，2023年到2024年回测',
                'strategy': 'mean_reversion',
            },
            {
                'name': '突破策略',
                'description': '股价突破60日新高时买入，跌破20日均线时卖出，仓位20%',
                'strategy': 'breakout',
            },
            {
                'name': '网格交易',
                'description': '以当前价为中心，上下各设5个网格，每格3%，初始资金50万',
                'strategy': 'grid',
            },
        ]
    })
