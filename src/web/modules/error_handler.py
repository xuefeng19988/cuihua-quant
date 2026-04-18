"""
错误处理模块 - Phase 231
统一错误处理，友好错误提示
"""
from flask import jsonify, request
import logging
import traceback

class ErrorHandler:
    """全局错误处理器"""
    
    @staticmethod
    def register(app):
        """注册错误处理器"""
        
        @app.errorhandler(400)
        def bad_request(e):
            return jsonify({
                'code': 400,
                'message': '请求参数错误',
                'path': request.path
            }), 400
        
        @app.errorhandler(401)
        def unauthorized(e):
            return jsonify({
                'code': 401,
                'message': '未授权访问，请先登录',
                'path': request.path
            }), 401
        
        @app.errorhandler(403)
        def forbidden(e):
            return jsonify({
                'code': 403,
                'message': '权限不足',
                'path': request.path
            }), 403
        
        @app.errorhandler(404)
        def not_found(e):
            return jsonify({
                'code': 404,
                'message': '资源不存在',
                'path': request.path
            }), 404
        
        @app.errorhandler(405)
        def method_not_allowed(e):
            return jsonify({
                'code': 405,
                'message': '请求方法不允许',
                'path': request.path
            }), 405
        
        @app.errorhandler(429)
        def rate_limited(e):
            return jsonify({
                'code': 429,
                'message': '请求过于频繁',
                'path': request.path
            }), 429
        
        @app.errorhandler(500)
        def internal_error(e):
            logging.error(f"Internal Server Error: {request.path}\n{traceback.format_exc()}")
            return jsonify({
                'code': 500,
                'message': '服务器内部错误',
                'path': request.path
            }), 500
        
        @app.errorhandler(Exception)
        def handle_exception(e):
            logging.error(f"Unhandled Exception: {request.path}\n{traceback.format_exc()}")
            return jsonify({
                'code': 500,
                'message': '服务器错误',
                'path': request.path
            }), 500
