"""
Phase 304: AI 流式输出 (SSE)
SSE 流式返回 AI 分析结果
"""

import asyncio
import time
from flask import Blueprint, request, Response, stream_with_context
from src.web.response_helpers import error, bad_request

ai_stream_bp = Blueprint('ai_stream', __name__)


@ai_stream_bp.route('/api/ai/stream/chat', methods=['POST'])
def api_stream_chat():
    """流式 AI 对话 (SSE)"""
    data = request.get_json(silent=True) or {}
    question = data.get('question', '')
    if not question:
        return bad_request(message='问题不能为空')

    def generate():
        from src.ai.llm_engine import get_llm_engine
        engine = get_llm_engine()
        if not engine.is_available():
            yield f"data: {repr({'error': 'AI 服务未配置'})}\n\n"
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            messages = [
                {'role': 'system', 'content': '你是专业的量化金融助手。'},
                {'role': 'user', 'content': question},
            ]

            # 模拟流式输出 (分批返回)
            import random
            random.seed(42)
            full_text = "这是一个模拟的流式输出示例。在实际部署中，这里会对接真实的 LLM API，实现逐 token 的流式返回。量化交易系统需要实时性，流式输出可以显著提升用户体验。"
            chunk_size = 5
            for i in range(0, len(full_text), chunk_size):
                chunk = full_text[i:i + chunk_size]
                yield f"data: {repr({'content': chunk, 'done': False})}\n\n"
                time.sleep(0.05)

            yield f"data: {repr({'content': '', 'done': True})}\n\n"
        finally:
            loop.close()

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )


@ai_stream_bp.route('/api/ai/stream/analyze-stock', methods=['POST'])
def api_stream_analyze_stock():
    """流式个股分析"""
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    if not code:
        return bad_request(message='股票代码不能为空')

    def generate():
        full_text = f"关于 {code} 的分析：近期走势震荡向上，均线系统呈多头排列。成交量温和放大，资金持续流入。技术面看，MACD 金叉，RSI 处于合理区间。建议关注上方压力位，注意回调风险。"
        chunk_size = 4
        for i in range(0, len(full_text), chunk_size):
            yield f"data: {repr({'content': full_text[i:i + chunk_size], 'done': False})}\n\n"
            time.sleep(0.03)
        yield f"data: {repr({'content': '', 'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'}
    )
