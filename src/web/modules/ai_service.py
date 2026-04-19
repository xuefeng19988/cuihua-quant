"""
Phase 277: AI 大模型 API 端点
提供智能问答、研报生成、行情解读
"""

import asyncio
from flask import Blueprint, request, jsonify
from src.web.response_helpers import ok, error, bad_request

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/api/ai/status', methods=['GET'])
def api_ai_status():
    """获取 AI 服务状态"""
    from src.ai.llm_engine import get_llm_engine
    engine = get_llm_engine()
    return ok(data=engine.get_config())


@ai_bp.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    """智能问答"""
    from src.ai.llm_engine import get_llm_engine
    engine = get_llm_engine()
    
    if not engine.is_available():
        return error(message='AI 服务未配置，请设置 LLM_API_KEY 环境变量')
    
    data = request.get_json(silent=True) or {}
    question = data.get('question', '')
    if not question:
        return bad_request(message='问题不能为空')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(engine.chat(question))
        return ok(data=result)
    except Exception as e:
        return error(message=f'AI 请求失败: {str(e)}')
    finally:
        loop.close()


@ai_bp.route('/api/ai/analyze-stock', methods=['POST'])
def api_ai_analyze_stock():
    """个股 AI 分析"""
    from src.ai.llm_engine import get_llm_engine
    engine = get_llm_engine()
    
    if not engine.is_available():
        return error(message='AI 服务未配置')
    
    data = request.get_json(silent=True) or {}
    stock_data = {
        'code': data.get('code', ''),
        'name': data.get('name', ''),
        'price': data.get('price', 0),
        'change': data.get('change', 0),
        'score': data.get('score', 50),
    }
    
    if not stock_data['code']:
        return bad_request(message='股票代码不能为空')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(engine.analyze_stock(stock_data))
        return ok(data=result)
    except Exception as e:
        return error(message=f'分析失败: {str(e)}')
    finally:
        loop.close()


@ai_bp.route('/api/ai/generate-report', methods=['POST'])
def api_ai_generate_report():
    """AI 生成研报"""
    from src.ai.llm_engine import get_llm_engine
    engine = get_llm_engine()
    
    if not engine.is_available():
        return error(message='AI 服务未配置')
    
    data = request.get_json(silent=True) or {}
    context = data.get('context', '')
    if not context:
        return bad_request(message='研报上下文不能为空')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(engine.generate_report(context))
        return ok(data=result)
    except Exception as e:
        return error(message=f'研报生成失败: {str(e)}')
    finally:
        loop.close()


@ai_bp.route('/api/ai/market-summary', methods=['POST'])
def api_ai_market_summary():
    """AI 市场总结"""
    from src.ai.llm_engine import get_llm_engine
    engine = get_llm_engine()
    
    if not engine.is_available():
        return error(message='AI 服务未配置')
    
    data = request.get_json(silent=True) or {}
    context = data.get('context', '')
    if not context:
        return bad_request(message='市场数据不能为空')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(engine.market_summary(context))
        return ok(data=result)
    except Exception as e:
        return error(message=f'市场总结失败: {str(e)}')
    finally:
        loop.close()


@ai_bp.route('/api/ai/history', methods=['GET'])
def api_ai_history():
    """获取 AI 调用历史"""
    from src.ai.llm_engine import get_llm_engine
    engine = get_llm_engine()
    limit = request.args.get('limit', 50, type=int)
    return ok(data={'history': engine.get_history(limit), 'count': len(engine.history)})


@ai_bp.route('/api/ai/history/clear', methods=['POST'])
def api_ai_clear_history():
    """清空 AI 调用历史"""
    from src.ai.llm_engine import get_llm_engine
    engine = get_llm_engine()
    engine.clear_history()
    return ok(message='历史已清空')


@ai_bp.route('/api/ai/providers', methods=['GET'])
def api_ai_providers():
    """列出所有支持的 LLM 提供商"""
    from src.ai.llm_engine import LLMEngine
    return ok(data={'providers': LLMEngine.list_providers()})
