"""
Phase 314: AI 选股 2.0 + AI 组合诊断
"""
from flask import Blueprint, request, jsonify
from src.web.response_helpers import ok, error
import random
import math

ai_stock_v2_bp = Blueprint('ai_stock_v2', __name__)


@ai_stock_v2_bp.route('/api/ai/stock-screen', methods=['POST'])
def ai_stock_screen():
    """AI 自然语言选股"""
    data = request.get_json(silent=True) or {}
    query = data.get('query', '')
    
    # 解析自然语言条件
    conditions = parse_natural_query(query)
    
    # 模拟筛选结果
    results = mock_screen_stocks(conditions)
    
    return ok(data={
        'query': query,
        'conditions': conditions,
        'results': results,
        'total': len(results),
        'ai_summary': generate_screen_summary(query, results)
    })


@ai_stock_v2_bp.route('/api/ai/sector-forecast', methods=['GET'])
def ai_sector_forecast():
    """AI 板块轮动预测"""
    sectors = [
        {'name': '半导体', score: 92, signal: '买入', reason: 'AI算力需求爆发，国产替代加速'},
        {'name': '新能源车', score: 85, signal: '买入', reason: '政策利好+销量超预期'},
        {'name': '医药', score: 72, signal: '关注', reason: '创新药审批加速'},
        {'name': '消费', score: 65, signal: '观望', reason: '复苏节奏偏慢'},
        {'name': '地产', score: 45, signal: '谨慎', reason: '政策效果待观察'},
        {'name': '银行', score: 55, signal: '观望', reason: '息差压力持续'},
    ]
    return ok(data={
        'sectors': sectors,
        'top_pick': sectors[0]['name'],
        'ai_comment': '建议重点关注科技板块，半导体/AI算力方向确定性最高'
    })


@ai_stock_v2_bp.route('/api/ai/capital-analysis/<code>', methods=['GET'])
def ai_capital_analysis(code):
    """AI 资金流向解读"""
    return ok(data={
        'code': code,
        'main_force': {'net_inflow': 12500, 'trend': '连续3日净流入'},
        'north_bound': {'net_inflow': 8200, 'trend': '北向持续加仓'},
        'south_bound': {'net_inflow': 0, 'trend': '非港股通'},
        'retail': {'net_inflow': -3500, 'trend': '散户小幅流出'},
        'ai_comment': '主力资金持续流入，北向资金加仓明显，筹码趋于集中',
        'signal': '偏多',
        'confidence': 0.78
    })


@ai_stock_v2_bp.route('/api/ai/dragon-tiger', methods=['GET'])
def ai_dragon_tiger():
    """AI 龙虎榜解读"""
    return ok(data={
        'stocks': [
            {'code': '688256', 'name': '寒武纪', 'net_buy': 28500, 'seats': 5, 'ai_comment': '机构主导买入，游资跟风'},
            {'code': '002415', 'name': '海康威视', 'net_buy': 15200, 'seats': 3, 'ai_comment': '外资+机构联合买入'},
            {'code': '300750', 'name': '宁德时代', 'net_sell': -18000, 'seats': 4, 'ai_comment': '机构分歧较大，部分获利了结'},
        ],
        'ai_summary': '今日龙虎榜显示机构偏好科技股，半导体/AI方向获集中买入'
    })


@ai_stock_v2_bp.route('/api/ai/limit-up-analysis', methods=['GET'])
def ai_limit_up_analysis():
    """AI 涨停板分析"""
    return ok(data={
        'limit_up': [
            {'code': '603256', 'name': '宏微科技', 'days': 3, 'ai_comment': '3连板，半导体封测概念龙头'},
            {'code': '002156', 'name': '通富微电', 'days': 2, 'ai_comment': '2连板，先进封装概念'},
        ],
        'limit_down': [],
        'ai_summary': '涨停集中在半导体板块，板块效应明显，连板高度3板',
        'market_mood': '偏暖'
    })


@ai_stock_v2_bp.route('/api/ai/financial-report/<code>', methods=['GET'])
def ai_financial_report(code):
    """AI 财报解读"""
    return ok(data={
        'code': code,
        'revenue': {'value': 125.6, 'yoy': '+18.5%', 'comment': '营收稳健增长'},
        'profit': {'value': 28.3, 'yoy': '+25.2%', 'comment': '利润增速超营收'},
        'gross_margin': {'value': '42.5%', 'change': '+1.8pp', 'comment': '毛利率提升'},
        'roe': {'value': '18.2%', 'change': '+2.1pp', 'comment': 'ROE持续改善'},
        'cash_flow': {'value': 32.1, 'comment': '经营性现金流健康'},
        'ai_summary': '财报整体表现优秀，营收利润双增，盈利能力持续提升，建议关注',
        'rating': '优秀',
        'risks': ['应收账款增速略快于营收']
    })


@ai_stock_v2_bp.route('/api/ai/portfolio-diagnosis', methods=['POST'])
def ai_portfolio_diagnosis():
    """AI 组合诊断"""
    data = request.get_json(silent=True) or {}
    positions = data.get('positions', [])
    
    # 分析持仓集中度
    total_value = sum(p.get('value', 0) for p in positions)
    sectors = {}
    for p in positions:
        s = p.get('sector', '其他')
        sectors[s] = sectors.get(s, 0) + p.get('value', 0)
    
    sector_weights = {k: v/total_value*100 for k, v in sectors.items()} if total_value > 0 else {}
    
    # 集中度评分
    max_weight = max(sector_weights.values()) if sector_weights else 0
    concentration_score = max(0, 100 - max_weight * 2)
    
    diagnosis = {
        'total_value': total_value,
        'position_count': len(positions),
        'sector_weights': sector_weights,
        'concentration': {
            'score': concentration_score,
            'level': '分散' if concentration_score > 70 else '集中' if concentration_score > 40 else '过度集中',
            'comment': '行业分布' + ('合理' if concentration_score > 60 else '偏集中，建议适当分散')
        },
        'risk_level': '中' if concentration_score > 50 else '高',
        'suggestions': generate_portfolio_suggestions(sector_weights, positions),
        'ai_comment': f'当前持仓{len(positions)}只股票，行业集中度{"偏高" if max_weight > 40 else "合理"}'
    }
    
    return ok(data=diagnosis)


@ai_stock_v2_bp.route('/api/ai/rebalance-suggestion', methods=['POST'])
def ai_rebalance_suggestion():
    """AI 调仓建议"""
    data = request.get_json(silent=True) or {}
    positions = data.get('positions', [])
    
    suggestions = []
    for p in positions:
        change_pct = p.get('change_pct', 0)
        if change_pct > 20:
            suggestions.append({
                'action': '减仓',
                'code': p['code'],
                'name': p['name'],
                'reason': f'涨幅{change_pct}%，建议获利了结部分仓位',
                'suggested_pct': 30
            })
        elif change_pct < -15:
            suggestions.append({
                'action': '止损',
                'code': p['code'],
                'name': p['name'],
                'reason': f'跌幅{change_pct}%，建议设置止损',
                'suggested_pct': 50
            })
    
    return ok(data={
        'suggestions': suggestions,
        'ai_comment': '建议对涨幅过大的个股适当获利了结，对跌幅过大的设置止损'
    })


@ai_stock_v2_bp.route('/api/ai/return-attribution', methods=['POST'])
def ai_return_attribution():
    """AI 收益归因"""
    data = request.get_json(silent=True) or {}
    return ok(data={
        'total_return': '+12.5%',
        'benchmark_return': '+8.2%',
        'alpha': '+4.3%',
        'attribution': {
            'sector_allocation': '+2.1%',
            'stock_selection': '+1.8%',
            'market_timing': '+0.4%',
        },
        'top_contributors': [
            {'code': '688256', 'name': '寒武纪', 'contribution': '+5.2%'},
            {'code': '002415', 'name': '海康威视', 'contribution': '+3.1%'},
        ],
        'top_drags': [
            {'code': '300750', 'name': '宁德时代', 'contribution': '-2.8%'},
        ],
        'ai_comment': '超额收益主要来自半导体板块的配置和个股选择，选股能力突出'
    })


# ========== 辅助函数 ==========

def parse_natural_query(query):
    """解析自然语言选股条件"""
    conditions = []
    q = query.lower()
    
    if any(kw in q for kw in ['放量', '成交量放大']):
        conditions.append({'type': 'volume', 'op': '>', 'value': '2倍均量'})
    if any(kw in q for kw in ['突破', '上穿']):
        conditions.append({'type': 'breakout', 'op': '>', 'value': '均线'})
    if any(kw in q for kw in ['低估', '低pe']):
        conditions.append({'type': 'pe', 'op': '<', 'value': 15})
    if any(kw in q for kw in ['涨停', '连板']):
        conditions.append({'type': 'limit_up', 'op': '>=', 'value': 1})
    if any(kw in q for kw in ['大跌', '超跌']):
        conditions.append({'type': 'change', 'op': '<', 'value': -5})
    
    return conditions


def mock_screen_stocks(conditions):
    """模拟筛选结果"""
    return [
        {'code': '688256', 'name': '寒武纪', 'price': 125.8, 'change': 7.23, 'volume_ratio': 3.2, 'reason': '放量突破年线'},
        {'code': '002415', 'name': '海康威视', 'price': 35.6, 'change': 4.56, 'volume_ratio': 2.1, 'reason': '底部放量'},
        {'code': '603256', 'name': '宏微科技', 'price': 42.3, 'change': 9.98, 'volume_ratio': 4.5, 'reason': '涨停突破'},
    ]


def generate_screen_summary(query, results):
    """生成选股摘要"""
    return f'根据"{query}"条件，筛选出{len(results)}只股票。主要特征：放量突破个股居多，建议关注量能持续性。'


def generate_portfolio_suggestions(sector_weights, positions):
    """生成组合建议"""
    suggestions = []
    for sector, weight in sector_weights.items():
        if weight > 40:
            suggestions.append(f'{sector}行业占比{weight:.0f}%过高，建议降至25%以内')
    if len(positions) > 10:
        suggestions.append('持仓个股过多，建议精简至5-8只')
    if not suggestions:
        suggestions.append('组合结构合理，保持当前配置')
    return suggestions
