"""统一 API 响应辅助函数 (Phase 272)"""

from flask import jsonify


def ok(data=None, message='ok'):
    """成功响应"""
    result = {'code': 200, 'message': message}
    if data is not None:
        result['data'] = data
    return jsonify(result)


def error(message='error', code=500, data=None):
    """错误响应"""
    result = {'code': code, 'message': message}
    if data is not None:
        result['data'] = data
    return jsonify(result)


def not_found(message='资源不存在'):
    """404 响应"""
    return error(message=message, code=404)


def bad_request(message='请求参数错误'):
    """400 响应"""
    return error(message=message, code=400)
