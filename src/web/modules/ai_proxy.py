"""
Phase 306: 多模型并发 + 自动降级
bailian → openai → deepseek 自动降级
"""

import asyncio
from typing import Dict, List
from flask import Blueprint, request
from src.web.response_helpers import ok, error, bad_request
from src.ai.llm_engine import LLMProvider, PROVIDER_PRESETS

ai_proxy_bp = Blueprint('ai_proxy', __name__)

# 优先级队列
_provider_order = ['bailian', 'openai', 'deepseek']
_provider_cache: Dict[str, LLMProvider] = {}


def _get_providers(api_key_map: Dict[str, str]) -> List[LLMProvider]:
    """按优先级获取可用提供商"""
    providers = []
    for name in _provider_order:
        key = api_key_map.get(name)
        if not key:
            continue
        if name not in _provider_cache:
            preset = PROVIDER_PRESETS[name]
            _provider_cache[name] = LLMProvider(
                api_key=key,
                base_url=preset['base_url'],
                model=preset['default_model'],
                provider_name=name,
            )
        providers.append(_provider_cache[name])
    return providers


async def _chat_with_fallback(providers: List[LLMProvider], messages: List[Dict], **kwargs) -> Dict:
    """带降级的对话"""
    errors = []
    for provider in providers:
        try:
            result = await provider.chat(messages, **kwargs)
            result['used_provider'] = provider.provider_name
            return result
        except Exception as e:
            errors.append(f"{provider.provider_name}: {str(e)}")
            continue
    return {'error': '所有提供商均失败', 'details': errors}


@ai_proxy_bp.route('/api/ai/proxy/chat', methods=['POST'])
def api_proxy_chat():
    """多模型代理对话 (自动降级)"""
    data = request.get_json(silent=True) or {}
    question = data.get('question', '')
    api_keys = data.get('api_keys', {})  # {'bailian': 'sk-...', 'openai': 'sk-...'}

    if not question:
        return bad_request(message='问题不能为空')

    providers = _get_providers(api_keys)
    if not providers:
        return error(message='未配置任何 API Key')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        messages = [
            {'role': 'system', 'content': '你是专业的量化金融助手。'},
            {'role': 'user', 'content': question},
        ]
        result = loop.run_until_complete(
            _chat_with_fallback(providers, messages, temperature=0.7, max_tokens=1000)
        )
        return ok(data=result)
    finally:
        loop.close()


@ai_proxy_bp.route('/api/ai/proxy/status', methods=['GET'])
def api_proxy_status():
    """多模型代理状态"""
    return ok(data={
        'provider_order': _provider_order,
        'available': list(_provider_cache.keys()),
    })
