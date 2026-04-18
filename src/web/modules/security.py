"""
安全模块 - Phase 220
提供安全防护功能：SQL注入防护、XSS防护、请求限流
"""
import re
import time
from functools import wraps
from flask import request, jsonify

# SQL注入检测模式
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|EXEC)\b)",
    r"(--|;|\/\*|\*\/|@@|@)",
    r"(CHAR\(|CONCAT\(|GROUP_CONCAT\(|INFORMATION_SCHEMA)",
    r"(\bOR\b|\bAND\b)\s+\d+\s*=\s*\d+",
]

# XSS检测模式
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
]

# 请求限流存储
_request_counts = {}

def check_sql_injection(text):
    """检测SQL注入"""
    if not text:
        return False
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def check_xss(text):
    """检测XSS攻击"""
    if not text:
        return False
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def sanitize_input(text):
    """清理输入"""
    if not text:
        return text
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE|re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    return text.strip()

def rate_limit(max_requests=100, window=60):
    """请求限流装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            if client_ip not in _request_counts:
                _request_counts[client_ip] = []
            
            # 清理过期记录
            _request_counts[client_ip] = [
                t for t in _request_counts[client_ip] 
                if current_time - t < window
            ]
            
            if len(_request_counts[client_ip]) >= max_requests:
                return jsonify({
                    'code': 429,
                    'message': '请求过于频繁，请稍后再试'
                }), 429
            
            _request_counts[client_ip].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def security_middleware(f):
    """安全中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查请求参数
        for key, value in request.args.items():
            if check_sql_injection(value):
                return jsonify({'code': 400, 'message': '检测到非法输入'}), 400
            if check_xss(value):
                return jsonify({'code': 400, 'message': '检测到非法输入'}), 400
        
        # 检查JSON body
        if request.is_json:
            data = request.get_json(silent=True) or {}
            for key, value in data.items():
                if isinstance(value, str):
                    if check_sql_injection(value):
                        return jsonify({'code': 400, 'message': '检测到非法输入'}), 400
        
        return f(*args, **kwargs)
    return decorated_function
