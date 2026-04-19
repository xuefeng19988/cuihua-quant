"""
Phase 279: LLM 管理 API 端点
"""

import httpx
from flask import Blueprint, request
from src.web.response_helpers import ok, error, bad_request

llm_mgmt_bp = Blueprint('llm_mgmt', __name__)


@llm_mgmt_bp.route('/api/llm/configs', methods=['GET'])
def api_llm_list_configs():
    """列出所有 LLM 配置"""
    from src.ai.llm_manager import get_llm_manager
    mgr = get_llm_manager()
    return ok(data={'configs': mgr.list_configs(), 'stats': mgr.get_stats()})


@llm_mgmt_bp.route('/api/llm/configs/<name>', methods=['GET'])
def api_llm_get_config(name):
    """获取单个配置详情"""
    from src.ai.llm_manager import get_llm_manager
    mgr = get_llm_manager()
    cfg = mgr.get_config(name)
    if cfg:
        return ok(data=cfg)
    return error(message=f'配置 {name} 不存在', code=404)


@llm_mgmt_bp.route('/api/llm/configs', methods=['POST'])
def api_llm_add_config():
    """添加新配置"""
    from src.ai.llm_manager import get_llm_manager
    mgr = get_llm_manager()
    
    data = request.get_json(silent=True) or {}
    name = data.get('name', '')
    provider = data.get('provider', '')
    api_key = data.get('api_key', '')
    model = data.get('model', '')
    base_url = data.get('base_url', '')
    
    if not name:
        return bad_request(message='配置名称不能为空')
    if not provider:
        return bad_request(message='提供商不能为空')
    if not api_key:
        return bad_request(message='API Key 不能为空')
    if not model:
        return bad_request(message='模型不能为空')
    
    result = mgr.add_config(name, provider, api_key, model, base_url)
    if result['success']:
        return ok(data=result, message='配置已添加')
    return error(message=result['error'])


@llm_mgmt_bp.route('/api/llm/configs/<name>', methods=['PUT'])
def api_llm_update_config(name):
    """更新配置"""
    from src.ai.llm_manager import get_llm_manager
    mgr = get_llm_manager()
    
    data = request.get_json(silent=True) or {}
    result = mgr.update_config(name, **data)
    if result['success']:
        return ok(message='配置已更新')
    return error(message=result['error'])


@llm_mgmt_bp.route('/api/llm/configs/<name>', methods=['DELETE'])
def api_llm_delete_config(name):
    """删除配置"""
    from src.ai.llm_manager import get_llm_manager
    mgr = get_llm_manager()
    result = mgr.delete_config(name)
    if result['success']:
        return ok(message='配置已删除')
    return error(message=result['error'])


@llm_mgmt_bp.route('/api/llm/switch/<name>', methods=['POST'])
def api_llm_switch(name):
    """切换活动配置"""
    from src.ai.llm_manager import get_llm_manager
    mgr = get_llm_manager()
    result = mgr.switch_config(name)
    if result['success']:
        return ok(data=result, message=f'已切换到 {name}')
    return error(message=result['error'])


@llm_mgmt_bp.route('/api/llm/test', methods=['POST'])
def api_llm_test_connection():
    """测试 LLM 连接"""
    from src.ai.llm_engine import PROVIDER_PRESETS
    
    data = request.get_json(silent=True) or {}
    provider = data.get('provider', 'bailian')
    api_key = data.get('api_key', '')
    model = data.get('model', '')
    base_url = data.get('base_url', '')
    
    if not api_key:
        return bad_request(message='API Key 不能为空')
    
    preset = PROVIDER_PRESETS.get(provider)
    if preset:
        if not base_url:
            base_url = preset['base_url']
        if not model:
            model = preset['default_model']
    
    try:
        import asyncio
        
        async def _test():
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f'{base_url}/chat/completions',
                    json={
                        'model': model,
                        'messages': [{'role': 'user', 'content': '你好'}],
                        'max_tokens': 10,
                    },
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {api_key}',
                    }
                )
                resp.raise_for_status()
                return resp.json()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_test())
            return ok(data={
                'status': 'ok',
                'model': result.get('model', model),
                'usage': result.get('usage', {}),
            }, message='连接测试成功')
        finally:
            loop.close()
    except httpx.HTTPStatusError as e:
        return error(message=f'HTTP 错误: {e.response.status_code} - {e.response.text[:200]}')
    except Exception as e:
        return error(message=f'连接失败: {str(e)}')


@llm_mgmt_bp.route('/api/llm/stats', methods=['GET'])
def api_llm_stats():
    """获取 LLM 使用统计"""
    from src.ai.llm_manager import get_llm_manager
    mgr = get_llm_manager()
    return ok(data=mgr.get_stats())


@llm_mgmt_bp.route('/api/llm/providers', methods=['GET'])
def api_llm_providers():
    """列出所有支持的提供商"""
    from src.ai.llm_engine import LLMEngine
    return ok(data={'providers': LLMEngine.list_providers()})
