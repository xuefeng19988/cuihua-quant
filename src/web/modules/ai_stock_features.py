"""
Phase 282-294: AI × 股票深度对接模块
集中管理所有 AI 股票相关功能
"""

import os
import json
import httpx
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from flask import Blueprint, request
from src.web.response_helpers import ok, error, bad_request

ai_stock_bp = Blueprint('ai_stock', __name__)


# ============================================================
# 通用 AI 调用辅助
# ============================================================

def _call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> Dict:
    """同步调用 LLM (用于 API 端点)"""
    from src.ai.llm_engine import get_llm_engine
    engine = get_llm_engine()
    if not engine.is_available():
        return {'error': 'AI 服务未配置，请设置 LLM_API_KEY'}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]
        result = loop.run_until_complete(engine.provider.chat(messages, temperature=temperature, max_tokens=max_tokens))
        engine.history.append({'type': 'ai_stock', 'timestamp': datetime.now().isoformat(), 'result': result})
        return result
    except Exception as e:
        return {'error': f'AI 请求失败: {str(e)}'}
    finally:
        loop.close()


def _get_db_engine():
    """获取数据库引擎"""
    from src.data.database import get_db_engine
    return get_db_engine()


def _query_sql(query, params=None):
    """安全查询"""
    from sqlalchemy import text
    import pandas as pd
    engine = _get_db_engine()
    if not engine:
        return None
    if params:
        return pd.read_sql(text(query), engine, params=params)
    return pd.read_sql(text(query), engine)


# ============================================================
# Phase 282: AI 选股策略
# ============================================================

@ai_stock_bp.route('/api/ai/stock-pick', methods=['POST'])
def api_ai_stock_pick():
    """AI 选股: 从评分排行中筛选推荐"""
    data = request.get_json(silent=True) or {}
    top_n = data.get('top_n', 10)
    criteria = data.get('criteria', '')
    style = data.get('style', 'balanced')  # balanced / aggressive / conservative

    try:
        # 获取评分排行数据
        from src.web.modules.batch_scorer import BatchScorer
        from src.data.database import get_db_engine
        engine = get_db_engine()
        if not engine:
            return error(message='数据库未连接')

        df = _query_sql("SELECT code, close_price, change_pct, volume, turnover_rate, pe_ratio, pb_ratio, roe FROM stock_daily WHERE date = (SELECT MAX(date) FROM stock_daily) ORDER BY code")
        if df is None or df.empty:
            return error(message='无股票数据')

        # 取前 50 只评分最高的
        df = df.head(min(50, len(df)))
        
        # 构建上下文
        stock_context = []
        for _, row in df.iterrows():
            stock_context.append(
                f"代码:{row['code']} 价:{row['close_price']} 涨跌:{row.get('change_pct', 0):.1f}%"
                f" 换手率:{row.get('turnover_rate', 0):.1f}% PE:{row.get('pe_ratio', 0):.1f}"
            )

        context_text = '\n'.join(stock_context[:30])

        style_desc = {
            'aggressive': '激进型，偏好高成长高波动',
            'conservative': '保守型，偏好低估值稳定',
            'balanced': '均衡型，兼顾成长与估值'
        }.get(style, '均衡型')

        system_prompt = f"""你是专业的量化选股分析师。请根据以下股票数据，为用户推荐 Top {top_n} 只股票。
投资风格: {style_desc}
{f"额外筛选条件: {criteria}" if criteria else ""}

请以 JSON 格式返回，格式为:
{{"picks": [{{"code": "代码", "name": "名称", "reason": "推荐理由(50字以内)", "risk": "风险等级:低/中/高", "score": 评分(0-100)}}]}}"""

        user_prompt = f"股票数据:\n{context_text}\n\n请推荐 Top {top_n} 只股票（{style_desc}）。"

        result = _call_llm(system_prompt, user_prompt, temperature=0.6, max_tokens=2000)

        if 'error' in result:
            return error(message=result['error'])

        return ok(data={
            'picks': result.get('content', ''),
            'style': style,
            'total_analyzed': len(df),
        })

    except Exception as e:
        return error(message=f'选股失败: {str(e)}')


# ============================================================
# Phase 283: 异动 AI 解读
# ============================================================

@ai_stock_bp.route('/api/ai/analyze-anomaly', methods=['POST'])
def api_ai_analyze_anomaly():
    """异动股票 AI 解读"""
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    name = data.get('name', '')
    change_pct = data.get('change_pct', 0)
    volume_ratio = data.get('volume_ratio', 1)
    turnover_rate = data.get('turnover_rate', 0)

    if not code:
        return bad_request(message='股票代码不能为空')

    try:
        # 获取近 5 日数据
        df = _query_sql(
            "SELECT date, close_price, volume, change_pct FROM stock_daily WHERE code=:code ORDER BY date DESC LIMIT 5",
            {'code': code}
        )

        history_text = ''
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                history_text += f"  {row['date']}: 收{row['close_price']} 涨跌{row.get('change_pct', 0):.1f}% 量{row.get('volume', 0)}\n"

        system_prompt = "你是股票异动分析专家。请分析以下股票异动原因，从技术面、资金面、消息面三个维度解读。"

        user_prompt = f"""股票: {name} ({code})
今日涨跌幅: {change_pct}%
量比: {volume_ratio}
换手率: {turnover_rate}%

近5日走势:
{history_text}

请分析异动原因并给出解读（200字以内）。"""

        result = _call_llm(system_prompt, user_prompt, temperature=0.5, max_tokens=500)

        if 'error' in result:
            return error(message=result['error'])

        return ok(data={
            'code': code,
            'name': name,
            'change_pct': change_pct,
            'analysis': result.get('content', ''),
        })

    except Exception as e:
        return error(message=f'异动分析失败: {str(e)}')


# ============================================================
# Phase 284: 持仓 AI 诊断
# ============================================================

@ai_stock_bp.route('/api/ai/portfolio-diagnosis', methods=['POST'])
def api_ai_portfolio_diagnosis():
    """持仓 AI 全面诊断"""
    data = request.get_json(silent=True) or {}
    positions = data.get('positions', [])
    total_capital = data.get('total_capital', 1000000)

    if not positions:
        return bad_request(message='持仓数据不能为空')

    try:
        # 构建持仓上下文
        pos_text = []
        total_value = 0
        sectors = {}
        for p in positions:
            code = p.get('code', '')
            name = p.get('name', '')
            value = p.get('market_value', p.get('cost_price', 0) * p.get('qty', 0))
            pnl_pct = p.get('pnl_pct', 0)
            sector = p.get('sector', '未知')
            total_value += value
            sectors[sector] = sectors.get(sector, 0) + value

            pos_text.append(f"  {name}({code}): 市值{value:.0f} 盈亏{pnl_pct:.1f}% 行业{sector}")

        # 计算集中度
        weights = []
        for p in positions:
            value = p.get('market_value', p.get('cost_price', 0) * p.get('qty', 0))
            if total_value > 0:
                weights.append(value / total_value * 100)

        max_weight = max(weights) if weights else 0
        hhi = sum(w**2 for w in weights) / 100 if weights else 0  # 赫芬达尔指数

        sector_text = '\n'.join([f"  {k}: {v/total_value*100:.1f}%" for k, v in sectors.items()]) if total_value > 0 else '无'

        system_prompt = "你是资深投资组合经理。请对用户持仓进行全面诊断，指出风险和优化建议。"

        user_prompt = f"""持仓概况:
总资金: {total_capital:,.0f}
持仓市值: {total_value:,.0f}
持仓数量: {len(positions)} 只
最大仓位: {max_weight:.1f}%
HHI 集中度: {hhi:.2f}

行业分布:
{sector_text}

持仓明细:
{chr(10).join(pos_text)}

请从以下维度诊断:
1. 仓位集中度风险
2. 行业分散度
3. 盈亏结构
4. 优化建议
(300字以内)"""

        result = _call_llm(system_prompt, user_prompt, temperature=0.5, max_tokens=800)

        if 'error' in result:
            return error(message=result['error'])

        return ok(data={
            'diagnosis': result.get('content', ''),
            'stats': {
                'total_value': total_value,
                'position_count': len(positions),
                'max_weight': round(max_weight, 1),
                'hhi': round(hhi, 2),
                'sector_count': len(sectors),
            }
        })

    except Exception as e:
        return error(message=f'持仓诊断失败: {str(e)}')


# ============================================================
# Phase 285: 新闻 AI 摘要
# ============================================================

@ai_stock_bp.route('/api/ai/news-summary', methods=['POST'])
def api_ai_news_summary():
    """新闻 AI 摘要 + 情绪标注"""
    data = request.get_json(silent=True) or {}
    news_list = data.get('news', [])
    batch_size = data.get('batch_size', 10)

    if not news_list:
        return bad_request(message='新闻列表不能为空')

    try:
        results = []
        for news in news_list[:batch_size]:
            title = news.get('title', '')
            summary = news.get('summary', '')

            system_prompt = "你是金融新闻分析师。请对以下新闻进行摘要和情绪分析。"
            user_prompt = f"""新闻标题: {title}
新闻摘要: {summary}

请以 JSON 格式返回:
{{"summary": "50字以内摘要", "sentiment": "positive/negative/neutral", "related_stocks": ["相关股票代码"], "impact": "影响程度: 高/中/低"}}"""

            result = _call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=300)

            if 'error' not in result:
                results.append({
                    'title': title,
                    'analysis': result.get('content', ''),
                })

        return ok(data={'summaries': results, 'total': len(results)})

    except Exception as e:
        return error(message=f'新闻摘要失败: {str(e)}')


# ============================================================
# Phase 286: 财报 AI 解读
# ============================================================

@ai_stock_bp.route('/api/ai/financial-reading', methods=['GET'])
def api_ai_financial_reading():
    """财报 AI 解读"""
    code = request.args.get('code', '')
    if not code:
        return bad_request(message='股票代码不能为空')

    try:
        # 获取财务数据
        df = _query_sql(
            "SELECT date, close_price, volume, turnover FROM stock_daily WHERE code=:code ORDER BY date DESC LIMIT 60",
            {'code': code}
        )

        # 获取评分
        score_data = None
        try:
            from src.web.modules.stock_scorer import StockScorer
            scorer = StockScorer()
            # 简化的评分
            if df is not None and not df.empty:
                latest = df.iloc[0]
                score_data = {
                    'price': float(latest['close_price']),
                    'volume': int(latest.get('volume', 0)),
                }
        except:
            pass

        history_text = ''
        if df is not None and not df.empty:
            closes = df['close_price'].tolist()
            history_text = f"近20日收盘价: {', '.join([f'{c:.2f}' for c in closes[:20]])}"

        system_prompt = "你是金融分析师，擅长用通俗易懂的语言解读股票财报和技术面。"
        user_prompt = f"""请解读以下股票数据:

股票: {code}
{f"最新价: {score_data['price']}" if score_data else ""}
{history_text}

请从以下角度解读:
1. 近期走势判断
2. 成交量变化
3. 技术面评估
4. 风险提示
(300字以内)"""

        result = _call_llm(system_prompt, user_prompt, temperature=0.5, max_tokens=800)

        if 'error' in result:
            return error(message=result['error'])

        return ok(data={
            'code': code,
            'reading': result.get('content', ''),
        })

    except Exception as e:
        return error(message=f'财报解读失败: {str(e)}')


# ============================================================
# Phase 287: AI 研报中心
# ============================================================

@ai_stock_bp.route('/api/ai/generate-research', methods=['POST'])
def api_ai_generate_research():
    """AI 生成研报"""
    data = request.get_json(silent=True) or {}
    stock_code = data.get('code', '')
    report_type = data.get('type', 'individual')  # individual / industry

    if not stock_code:
        return bad_request(message='股票代码不能为空')

    try:
        # 获取完整数据
        df = _query_sql(
            "SELECT * FROM stock_daily WHERE code=:code ORDER BY date DESC LIMIT 120",
            {'code': stock_code}
        )

        context_lines = []
        if df is not None and not df.empty:
            latest = df.iloc[0]
            context_lines.append(f"股票: {stock_code}")
            context_lines.append(f"最新价: {latest['close_price']}")
            context_lines.append(f"成交量: {latest.get('volume', 0)}")

            # 计算均线
            closes = df['close_price'].tolist()
            if len(closes) >= 5:
                context_lines.append(f"5日均线: {sum(closes[:5])/5:.2f}")
            if len(closes) >= 20:
                context_lines.append(f"20日均线: {sum(closes[:20])/20:.2f}")
            if len(closes) >= 60:
                context_lines.append(f"60日均线: {sum(closes[:60])/60:.2f}")

            # 高低点
            context_lines.append(f"120日最高: {max(closes):.2f}")
            context_lines.append(f"120日最低: {min(closes):.2f}")

        system_prompt = "你是一位资深证券分析师，请生成一份专业的个股研究报告。"
        user_prompt = f"""请生成一份个股研究报告:

{chr(10).join(context_lines)}

要求:
1. 公司概述
2. 行业地位分析
3. 财务分析
4. 技术面分析
5. 估值分析
6. 投资建议
7. 风险提示

格式清晰，1000字以内。"""

        result = _call_llm(system_prompt, user_prompt, temperature=0.6, max_tokens=2000)

        if 'error' in result:
            return error(message=result['error'])

        return ok(data={
            'code': stock_code,
            'report_type': report_type,
            'report': result.get('content', ''),
            'generated_at': datetime.now().isoformat(),
        })

    except Exception as e:
        return error(message=f'研报生成失败: {str(e)}')


# ============================================================
# Phase 288: AI 策略推荐
# ============================================================

@ai_stock_bp.route('/api/ai/strategy-recommend', methods=['POST'])
def api_ai_strategy_recommend():
    """AI 策略推荐"""
    data = request.get_json(silent=True) or {}
    positions = data.get('positions', [])
    market_context = data.get('market_context', '')

    if not positions:
        return bad_request(message='持仓数据不能为空')

    try:
        pos_summary = []
        for p in positions[:10]:
            pos_summary.append(f"  {p.get('name', p.get('code', ''))}: 占比{p.get('weight', 0):.1f}% 盈亏{p.get('pnl_pct', 0):.1f}%")

        system_prompt = "你是资深交易策略师，请根据用户持仓和市场情况，给出具体的交易策略建议。"
        user_prompt = f"""当前持仓:
{chr(10).join(pos_summary)}

市场环境:
{market_context or '未知'}

请给出:
1. 当前持仓调整建议（加仓/减仓/持有）
2. 止盈止损位设置
3. 新增配置建议
4. 仓位管理建议
(300字以内)"""

        result = _call_llm(system_prompt, user_prompt, temperature=0.5, max_tokens=800)

        if 'error' in result:
            return error(message=result['error'])

        return ok(data={
            'strategy': result.get('content', ''),
            'position_count': len(positions),
        })

    except Exception as e:
        return error(message=f'策略推荐失败: {str(e)}')


# ============================================================
# Phase 289: 风险预警 AI
# ============================================================

@ai_stock_bp.route('/api/ai/risk-alert', methods=['POST'])
def api_ai_risk_alert():
    """风险预警 AI"""
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    current_price = data.get('price', 0)
    cost_price = data.get('cost_price', 0)
    position_pct = data.get('position_pct', 0)
    change_pct = data.get('change_pct', 0)

    if not code:
        return bad_request(message='股票代码不能为空')

    try:
        # 获取近 20 日数据计算风险指标
        df = _query_sql(
            "SELECT close_price FROM stock_daily WHERE code=:code ORDER BY date DESC LIMIT 20",
            {'code': code}
        )

        risk_signals = []
        if df is not None and not df.empty:
            closes = df['close_price'].tolist()
            ma20 = sum(closes) / len(closes)
            vol = (max(closes) - min(closes)) / ma20 * 100

            # 风险信号
            if cost_price > 0 and current_price < cost_price * 0.9:
                risk_signals.append(f"⚠️ 亏损超过10% ({(current_price/cost_price-1)*100:.1f}%)")
            if position_pct > 30:
                risk_signals.append(f"⚠️ 仓位过重 ({position_pct:.1f}%)")
            if current_price < ma20 * 0.95:
                risk_signals.append(f"⚠️ 跌破20日均线 (MA20={ma20:.2f})")
            if vol > 30:
                risk_signals.append(f"⚠️ 波动率过高 ({vol:.1f}%)")
            if change_pct < -5:
                risk_signals.append(f"🔴 今日大跌 {change_pct:.1f}%")

        risk_level = '高' if len(risk_signals) >= 3 else '中' if len(risk_signals) >= 1 else '低'

        if risk_signals:
            system_prompt = "你是风控专家，请根据风险信号给出具体的应对建议。"
            user_prompt = f"""股票: {code}
当前价: {current_price}
成本价: {cost_price}
仓位: {position_pct}%
今日涨跌: {change_pct}%

风险信号:
{chr(10).join(risk_signals)}

请给出具体应对建议（150字以内）。"""

            result = _call_llm(system_prompt, user_prompt, temperature=0.4, max_tokens=400)
            advice = result.get('content', '') if 'error' not in result else '无法生成建议'
        else:
            advice = '✅ 当前无明显风险信号，持仓状态健康。'

        return ok(data={
            'code': code,
            'risk_level': risk_level,
            'risk_signals': risk_signals,
            'advice': advice,
        })

    except Exception as e:
        return error(message=f'风险预警失败: {str(e)}')


# ============================================================
# Phase 290: 板块 AI 分析
# ============================================================

@ai_stock_bp.route('/api/ai/sector-analysis', methods=['POST'])
def api_ai_sector_analysis():
    """板块 AI 分析"""
    data = request.get_json(silent=True) or {}
    sector_name = data.get('sector', '')
    stocks = data.get('stocks', [])

    if not sector_name:
        return bad_request(message='板块名称不能为空')

    try:
        stock_text = ''
        for s in stocks[:10]:
            stock_text += f"  {s.get('name', s.get('code', ''))}: 涨跌{s.get('change_pct', 0):.1f}%\n"

        system_prompt = "你是板块分析专家，请分析板块走势和龙头股。"
        user_prompt = f"""板块: {sector_name}

板块成分股表现:
{stock_text or '暂无数据'}

请分析:
1. 板块整体走势
2. 热点解读
3. 龙头股推荐
4. 资金流向
(200字以内)"""

        result = _call_llm(system_prompt, user_prompt, temperature=0.5, max_tokens=500)

        if 'error' in result:
            return error(message=result['error'])

        return ok(data={
            'sector': sector_name,
            'analysis': result.get('content', ''),
            'stock_count': len(stocks),
        })

    except Exception as e:
        return error(message=f'板块分析失败: {str(e)}')


# ============================================================
# Phase 293: AI 交易日志
# ============================================================

@ai_stock_bp.route('/api/ai/trading-journal', methods=['POST'])
def api_ai_trading_journal():
    """AI 交易日志生成"""
    data = request.get_json(silent=True) or {}
    trades = data.get('trades', [])
    market_summary = data.get('market_summary', '')

    try:
        trade_text = ''
        for t in trades[:20]:
            trade_text += f"  {t.get('action', '')} {t.get('code', '')} {t.get('name', '')} {t.get('qty', 0)}股 @{t.get('price', 0)}\n"

        system_prompt = "你是专业交易员，请帮助用户生成今日的交易日志。"
        user_prompt = f"""今日交易记录:
{trade_text}

市场概况:
{market_summary}

请生成:
1. 今日交易总结
2. 得失分析
3. 明日计划建议
(300字以内)"""

        result = _call_llm(system_prompt, user_prompt, temperature=0.5, max_tokens=800)

        if 'error' in result:
            return error(message=result['error'])

        return ok(data={
            'journal': result.get('content', ''),
            'trade_count': len(trades),
            'generated_at': datetime.now().isoformat(),
        })

    except Exception as e:
        return error(message=f'日志生成失败: {str(e)}')
