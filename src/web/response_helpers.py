"""统一 API 响应辅助函数 (Phase 272)"""

from typing import Any, Optional
from flask import jsonify, Response


def ok(data: Optional[Any] = None, message: str = 'ok') -> Response:
    """成功响应"""
    result: dict[str, Any] = {'code': 200, 'message': message}
    if data is not None:
        result['data'] = data
    return jsonify(result)


def error(message: str = 'error', code: int = 500, data: Optional[Any] = None) -> Response:
    """错误响应"""
    result: dict[str, Any] = {'code': code, 'message': message}
    if data is not None:
        result['data'] = data
    return jsonify(result)


def not_found(message: str = '资源不存在') -> Response:
    """404 响应"""
    return error(message=message, code=404)


def bad_request(message: str = '请求参数错误') -> Response:
    """400 响应"""
    return error(message=message, code=400)
