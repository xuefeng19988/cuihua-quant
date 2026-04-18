"""
认证模块 - Phase 219
处理用户认证相关 API
"""
from flask import Blueprint, request, jsonify, session
import hashlib, secrets, os, yaml
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# 认证配置
AUTH_CONFIG = {}
_auth_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config', 'auth.yaml')

def _load_auth():
    global AUTH_CONFIG
    if os.path.exists(_auth_path):
        with open(_auth_path, 'r') as f:
            AUTH_CONFIG = yaml.safe_load(f).get('auth', {})

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def has_users():
    _load_auth()
    return len(AUTH_CONFIG.get('users', {})) > 0

@auth_bp.route('/api/auth/check-init', methods=['GET'])
def api_check_init():
    return jsonify({'code': 200, 'has_users': has_users()})

@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    nickname = data.get('nickname', username)
    email = data.get('email', '')
    avatar = data.get('avatar', '🦜')
    
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'})
    
    _load_auth()
    users = AUTH_CONFIG.get('users', {})
    if username in users:
        return jsonify({'code': 400, 'message': f'用户名 {username} 已存在'})
    
    users[username] = {
        'password_hash': hash_password(password),
        'nickname': nickname,
        'email': email,
        'avatar': avatar,
        'role': 'admin' if not has_users() else 'user',
        'created_at': datetime.now().isoformat()
    }
    AUTH_CONFIG['users'] = users
    
    with open(_auth_path, 'w') as f:
        yaml.dump({'auth': AUTH_CONFIG}, f, allow_unicode=True, default_flow_style=False)
    
    return jsonify({'code': 200, 'message': '注册成功'})

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    _load_auth()
    users = AUTH_CONFIG.get('users', {})
    user = users.get(username)
    
    if not user or user.get('password_hash') != hash_password(password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'})
    
    token = secrets.token_hex(32)
    session['api_token'] = token
    session['username'] = username
    
    return jsonify({
        'code': 200,
        'data': {
            'token': token,
            'user': {
                'username': username,
                'nickname': user.get('nickname', username),
                'email': user.get('email', ''),
                'avatar': user.get('avatar', '🦜'),
                'role': user.get('role', 'user')
            }
        }
    })

@auth_bp.route('/api/auth/info', methods=['GET'])
def api_auth_info():
    username = session.get('username', '')
    _load_auth()
    user = AUTH_CONFIG.get('users', {}).get(username, {})
    if not user:
        return jsonify({'code': 401, 'message': '未登录'})
    return jsonify({
        'code': 200,
        'data': {
            'username': username,
            'nickname': user.get('nickname', username),
            'email': user.get('email', ''),
            'avatar': user.get('avatar', '🦜'),
            'role': user.get('role', 'user')
        }
    })

@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'code': 200, 'message': '已退出登录'})
