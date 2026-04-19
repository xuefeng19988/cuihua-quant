"""
Phase 307: Prompt 模板管理
可视化配置 Prompt 模板，支持版本管理
"""

import os
import json
from typing import Dict, List
from datetime import datetime
from flask import Blueprint, request
from src.web.response_helpers import ok, error, bad_request

prompt_templates_bp = Blueprint('prompt_templates', __name__)

DEFAULT_TEMPLATES = {
    'stock_analysis': {
        'name': '个股分析',
        'system': '你是专业的量化金融分析师，擅长技术面和基本面分析。',
        'user': '请分析股票 {code} ({name})。\n最新价: {price}\n涨跌幅: {change}%\n评分: {score}/100\n请给出投资建议（200字以内）。',
        'temperature': 0.5,
        'max_tokens': 500,
        'version': '1.0',
    },
    'market_summary': {
        'name': '市场总结',
        'system': '你是首席策略师，擅长宏观分析和市场解读。',
        'user': '请总结今日市场：\n{context}\n(150字以内)',
        'temperature': 0.5,
        'max_tokens': 300,
        'version': '1.0',
    },
    'report_generate': {
        'name': '研报生成',
        'system': '你是一位资深金融研究员，擅长撰写专业研报。',
        'user': '请生成研报：\n{context}\n(1000字以内，包含基本面、技术面、风险提示)',
        'temperature': 0.6,
        'max_tokens': 2000,
        'version': '1.0',
    },
    'risk_alert': {
        'name': '风险预警',
        'system': '你是风控专家，擅长识别和评估投资风险。',
        'user': '请评估风险：\n股票: {code}\n价格: {price}\n信号: {signals}\n给出建议（150字以内）。',
        'temperature': 0.3,
        'max_tokens': 400,
        'version': '1.0',
    },
}

_templates = {}
_template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'prompt_templates.json')


def _load_templates():
    global _templates
    if os.path.exists(_template_path):
        try:
            with open(_template_path) as f:
                _templates = json.load(f)
        except:
            pass
    if not _templates:
        _templates = DEFAULT_TEMPLATES.copy()


def _save_templates():
    os.makedirs(os.path.dirname(_template_path), exist_ok=True)
    with open(_template_path, 'w') as f:
        json.dump(_templates, f, ensure_ascii=False, indent=2)


_load_templates()


@prompt_templates_bp.route('/api/prompt-templates', methods=['GET'])
def api_list_templates():
    """列出所有 Prompt 模板"""
    return ok(data={'templates': _templates})


@prompt_templates_bp.route('/api/prompt-templates/<name>', methods=['GET'])
def api_get_template(name):
    """获取单个模板"""
    tpl = _templates.get(name)
    if tpl:
        return ok(data=tpl)
    return error(message='模板不存在', code=404)


@prompt_templates_bp.route('/api/prompt-templates', methods=['POST'])
def api_create_template():
    """创建新模板"""
    data = request.get_json(silent=True) or {}
    name = data.get('name', '')
    if not name:
        return bad_request(message='模板名称不能为空')

    _templates[name] = {
        'name': name,
        'system': data.get('system', ''),
        'user': data.get('user', ''),
        'temperature': data.get('temperature', 0.7),
        'max_tokens': data.get('max_tokens', 1000),
        'version': data.get('version', '1.0'),
    }
    _save_templates()
    return ok(message='模板已创建')


@prompt_templates_bp.route('/api/prompt-templates/<name>', methods=['PUT'])
def api_update_template(name):
    """更新模板"""
    if name not in _templates:
        return error(message='模板不存在', code=404)

    data = request.get_json(silent=True) or {}
    _templates[name].update({
        'system': data.get('system', _templates[name]['system']),
        'user': data.get('user', _templates[name]['user']),
        'temperature': data.get('temperature', _templates[name]['temperature']),
        'max_tokens': data.get('max_tokens', _templates[name]['max_tokens']),
        'version': data.get('version', _templates[name]['version']),
    })
    _save_templates()
    return ok(message='模板已更新')


@prompt_templates_bp.route('/api/prompt-templates/<name>', methods=['DELETE'])
def api_delete_template(name):
    """删除模板"""
    if name in _templates:
        del _templates[name]
        _save_templates()
        return ok(message='模板已删除')
    return error(message='模板不存在', code=404)
