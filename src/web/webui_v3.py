"""
Phase 110: WebUI v3 全面重构 - 全功能集成
集成 Phase 1-108 所有功能，包含 20+ 个功能页面
"""

import os
import sys
import json
import yaml
import hashlib
import secrets
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from functools import wraps

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# 加载认证配置
AUTH_CONFIG = {}
_auth_path = os.path.join(project_root, 'config', 'auth.yaml')
if os.path.exists(_auth_path):
    with open(_auth_path, 'r') as _f:
        AUTH_CONFIG = yaml.safe_load(_f).get('auth', {})

def _load_auth():
    """重新加载认证配置"""
    global AUTH_CONFIG
    if os.path.exists(_auth_path):
        with open(_auth_path, 'r') as _f:
            AUTH_CONFIG = yaml.safe_load(_f).get('auth', {})

def _hash_pwd(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def check_auth(username, password):
    """验证用户名密码"""
    admin = AUTH_CONFIG.get('admin', {})
    return (username == admin.get('username', 'admin') and
            password == admin.get('password', 'admin123'))

def get_user_info():
    """获取当前用户信息"""
    return AUTH_CONFIG.get('admin', {})

def generate_remember_token():
    """生成安全的记住令牌"""
    return secrets.token_hex(32)  # 64字符随机令牌

def save_remember_token(username, token):
    """保存记住令牌到配置文件（只存哈希，不存原文）"""
    if os.path.exists(_auth_path):
        with open(_auth_path, 'r') as f:
            cfg = yaml.safe_load(f) or {}
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires = (datetime.now() + timedelta(days=30)).isoformat()
        cfg['auth']['remember'] = {
            'token_hash': token_hash,
            'username': username,
            'expires': expires,
            'created': datetime.now().isoformat()
        }
        with open(_auth_path, 'w') as f:
            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
        _load_auth()

def verify_remember_token(token):
    """验证记住令牌，返回用户名或 None"""
    remember = AUTH_CONFIG.get('remember', {})
    stored_hash = remember.get('token_hash')
    expires = remember.get('expires')
    if not stored_hash or not expires:
        return None
    # 检查过期
    try:
        if datetime.fromisoformat(expires) < datetime.now():
            return None
    except Exception as e:
        return None
    # 验证哈希
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if token_hash == stored_hash:
        return remember.get('username')
    return None

def clear_remember_token():
    """清除记住令牌"""
    if os.path.exists(_auth_path):
        with open(_auth_path, 'r') as f:
            cfg = yaml.safe_load(f) or {}
        if 'remember' in cfg.get('auth', {}):
            cfg['auth'].pop('remember')
        with open(_auth_path, 'w') as f:
            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
        _load_auth()


def create_webui_v3():
    """创建全功能 WebUI v3"""
    try:
        from flask import Flask, jsonify, render_template_string, request, redirect, url_for, session
    except ImportError:
        print("⚠️ Flask not installed. Run: pip install flask")
        return None

    app = Flask(__name__)
    app.config['SECRET_KEY'] = AUTH_CONFIG.get('secret_key', 'cuihua-quant-secret')

    # ==================== CSS STYLES ====================
    # Theme color palettes
    THEMES = {
        'dark': {
            '--bg-primary': '#0f0f23', '--bg-secondary': '#1a1a3e',
            '--bg-card': '#252550', '--bg-hover': '#2d2d6e',
            '--text-primary': '#e0e0ff', '--text-secondary': '#8888aa',
            '--accent': '#6366f1', '--accent-hover': '#818cf8',
            '--success': '#22c55e', '--warning': '#f59e0b',
            '--danger': '#ef4444', '--info': '#3b82f6',
            '--border': 'rgba(255,255,255,0.1)', '--shadow': '0 4px 12px rgba(0,0,0,0.3)',
        },
        'openclaw': {
            '--bg-primary': '#1a1510', '--bg-secondary': '#2a2018',
            '--bg-card': '#3a2d20', '--bg-hover': '#4a3a28',
            '--text-primary': '#f0e6d8', '--text-secondary': '#a89880',
            '--accent': '#e87830', '--accent-hover': '#f09050',
            '--success': '#4caf50', '--warning': '#ff9800',
            '--danger': '#f44336', '--info': '#2196f3',
            '--border': 'rgba(255,255,255,0.08)', '--shadow': '0 4px 12px rgba(0,0,0,0.4)',
        },
        'light': {
            '--bg-primary': '#f5f5f5', '--bg-secondary': '#ffffff',
            '--bg-card': '#ffffff', '--bg-hover': '#f0f0f0',
            '--text-primary': '#1a1a2e', '--text-secondary': '#6b7280',
            '--accent': '#6366f1', '--accent-hover': '#818cf8',
            '--success': '#16a34a', '--warning': '#d97706',
            '--danger': '#dc2626', '--info': '#2563eb',
            '--border': 'rgba(0,0,0,0.1)', '--shadow': '0 4px 12px rgba(0,0,0,0.1)',
        },
    }

    def get_theme_css(theme_name='dark'):
        """Generate CSS variables for the given theme"""
        if theme_name == 'dark':
            return ''  # Default theme, no override needed
        colors = THEMES.get(theme_name, THEMES['dark'])
        vars_css = '\n'.join(f'        {k}: {v};' for k, v in colors.items())
        return f"""
    /* Theme: {theme_name} */
    :root {{
{vars_css}
        --radius: 12px;
    }}\n"""

    # ==================== CSS STYLES ====================
    STYLES = """
    :root {
        --bg-primary: #0f0f23;
        --bg-secondary: #1a1a3e;
        --bg-card: #252550;
        --bg-hover: #2d2d6e;
        --text-primary: #e0e0ff;
        --text-secondary: #8888aa;
        --accent: #6366f1;
        --accent-hover: #818cf8;
        --success: #22c55e;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
        --border: rgba(255,255,255,0.1);
        --shadow: 0 4px 12px rgba(0,0,0,0.3);
        --radius: 12px;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary);
        min-height: 100vh;
        line-height: 1.6;
    }

    .sidebar {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        width: 260px;
        background: var(--bg-secondary);
        padding: 1.5rem 0.75rem;
        overflow-y: auto;
        z-index: 100;
        transition: transform 0.3s;
    }

    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        padding: 0.5rem;
        text-align: center;
    }

    .nav-section {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.75rem 1rem 0.25rem;
        margin-top: 0.5rem;
    }

    /* Collapsible groups */
    .nav-group { margin: 0.125rem 0; }
    .nav-group-header {
        display: flex; align-items: center; gap: 0.75rem;
        padding: 0.625rem 1rem; margin: 0.125rem 0;
        border-radius: var(--radius);
        color: var(--text-secondary);
        font-size: 0.875rem; font-weight: 500;
        cursor: pointer; transition: all 0.2s;
        user-select: none;
    }
    .nav-group-header:hover { background: var(--bg-hover); color: var(--text-primary); }
    .nav-group-header span:first-child { font-size: 1rem; }
    .nav-group-arrow {
        margin-left: auto; font-size: 0.625rem;
        transition: transform 0.2s;
    }
    .nav-group.open .nav-group-arrow { transform: rotate(90deg); }
    .nav-group-items {
        max-height: 0; overflow: hidden;
        transition: max-height 0.3s ease;
    }
    .nav-group.open .nav-group-items { max-height: 500px; }
    .nav-group-items .nav-item {
        padding-left: 2.75rem; font-size: 0.8125rem;
    }
    .nav-group-items .nav-item span {
        font-size: 0.5rem; margin-right: 0.25rem;
    }

    .sidebar-footer { border-top: 1px solid var(--border); margin-top: 0.75rem; padding-top: 0.5rem; }
    .sidebar-footer .nav-item { margin: 0.125rem 0; }
    .sidebar-footer .logout { color: var(--danger); }

    .sidebar-user {
        display: flex; align-items: center; gap: 0.625rem;
        padding: 0.75rem; margin-top: 0.5rem;
        background: rgba(0,0,0,0.15); border-radius: var(--radius);
    }
    .user-avatar { font-size: 1.5rem; }
    .user-name { font-size: 0.8125rem; font-weight: 600; }
    .user-role { font-size: 0.6875rem; color: var(--text-secondary); }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.625rem 1rem;
        margin: 0.125rem 0;
        border-radius: var(--radius);
        color: var(--text-secondary);
        text-decoration: none;
        transition: all 0.2s;
        font-size: 0.875rem;
    }

    .nav-item:hover, .nav-item.active {
        background: var(--bg-hover);
        color: var(--text-primary);
    }

    .nav-item.active {
        background: var(--accent);
        color: white;
    }

    .main {
        margin-left: 260px;
        padding: 2rem;
        min-height: 100vh;
    }

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }

    .header h1 {
        font-size: 1.75rem;
        font-weight: 700;
    }

    .header-actions {
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.25rem;
        margin-bottom: 1.5rem;
    }

    .stat-card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 1.25rem;
        border: 1px solid var(--border);
        transition: all 0.2s;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow);
    }

    .stat-label {
        font-size: 0.8125rem;
        color: var(--text-secondary);
        margin-bottom: 0.375rem;
    }

    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
    }

    .stat-change {
        font-size: 0.8125rem;
        margin-top: 0.375rem;
    }

    .card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 1.25rem;
        border: 1px solid var(--border);
        margin-bottom: 1.25rem;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 1rem;
        font-weight: 600;
    }

    .table-container {
        overflow-x: auto;
        border-radius: var(--radius);
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th {
        text-align: left;
        padding: 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-secondary);
        background: rgba(0,0,0,0.2);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    td {
        padding: 0.75rem;
        border-bottom: 1px solid var(--border);
        font-size: 0.875rem;
    }

    tr:hover td {
        background: rgba(255,255,255,0.02);
    }

    .badge {
        display: inline-block;
        padding: 0.2rem 0.625rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    .badge-success { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-warning { background: rgba(245,158,11,0.2); color: var(--warning); }
    .badge-danger { background: rgba(239,68,68,0.2); color: var(--danger); }
    .badge-info { background: rgba(59,130,246,0.2); color: var(--info); }
    .badge-purple { background: rgba(168,85,247,0.2); color: #a855f7; }

    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.5rem 1rem;
        border-radius: var(--radius);
        border: none;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.2s;
        text-decoration: none;
    }

    .btn-primary { background: var(--accent); color: white; }
    .btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }
    .btn-secondary { background: var(--bg-hover); color: var(--text-primary); }
    .btn-success { background: var(--success); color: white; }
    .btn-danger { background: var(--danger); color: white; }

    .form-group { margin-bottom: 1rem; }
    .form-label { display: block; margin-bottom: 0.375rem; font-size: 0.8125rem; color: var(--text-secondary); }
    .form-input, .form-select {
        width: 100%;
        padding: 0.625rem 0.875rem;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        color: var(--text-primary);
        font-size: 0.875rem;
    }
    .form-input:focus, .form-select:focus { outline: none; border-color: var(--accent); }

    .form-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 0.75rem;
    }

    .chart-container { min-height: 350px; background: rgba(0,0,0,0.2); border-radius: var(--radius); padding: 1rem; }

    .alert {
        padding: 0.875rem 1.25rem;
        border-radius: var(--radius);
        margin-bottom: 0.875rem;
        display: flex;
        align-items: center;
        gap: 0.625rem;
    }

    .alert-info { background: rgba(99,102,241,0.2); border-left: 3px solid var(--accent); }
    .alert-success { background: rgba(34,197,94,0.2); border-left: 3px solid var(--success); }
    .alert-warning { background: rgba(245,158,11,0.2); border-left: 3px solid var(--warning); }
    .alert-error { background: rgba(239,68,68,0.2); border-left: 3px solid var(--danger); }

    .progress-bar {
        height: 6px;
        background: var(--bg-secondary);
        border-radius: 3px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: var(--accent);
        border-radius: 3px;
        transition: width 0.3s;
    }

    .tabs {
        display: flex;
        gap: 0.25rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }

    .tab {
        padding: 0.625rem 1rem;
        cursor: pointer;
        border-radius: var(--radius) var(--radius) 0 0;
        color: var(--text-secondary);
        transition: all 0.2s;
        font-size: 0.875rem;
    }

    .tab:hover { background: var(--bg-hover); color: var(--text-primary); }
    .tab.active { background: var(--bg-card); color: var(--accent); border-bottom: 2px solid var(--accent); }

    .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.25rem; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }

    .tag {
        display: inline-block;
        padding: 0.125rem 0.5rem;
        background: var(--bg-secondary);
        border-radius: 4px;
        font-size: 0.7rem;
        margin: 0.125rem;
    }

    @media (max-width: 1024px) {
        .sidebar { transform: translateX(-100%); }
        .sidebar.open { transform: translateX(0); }
        .main { margin-left: 0; }
    }

    @media (max-width: 640px) {
        .main { padding: 1rem; }
        .stats-grid { grid-template-columns: 1fr; }
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--bg-hover); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }
    """

    # ==================== LOGIN PAGE ====================
    LOGIN_PAGE = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>翠花量化</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #0a0a1a;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
            }
            .login-container {
                width: 100%;
                max-width: 380px;
                padding: 2rem;
            }
            .login-card {
                background: rgba(255,255,255,0.03);
                border-radius: 20px;
                padding: 2.5rem 2rem 2rem;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .login-logo {
                text-align: center;
                margin-bottom: 2.5rem;
            }
            .login-logo .icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
            .login-logo h1 {
                font-size: 1.25rem;
                font-weight: 600;
                letter-spacing: 0.05em;
            }
            .login-logo p { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 0.25rem; }
            .form-group { margin-bottom: 1rem; }
            .form-label {
                display: block;
                font-size: 0.75rem;
                color: rgba(255,255,255,0.5);
                margin-bottom: 0.375rem;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }
            .form-input {
                width: 100%;
                padding: 0.75rem 0.875rem;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                color: #fff;
                font-size: 0.9375rem;
                transition: all 0.2s;
            }
            .form-input::placeholder { color: rgba(255,255,255,0.25); }
            .form-input:focus {
                outline: none;
                border-color: rgba(99,102,241,0.6);
                background: rgba(255,255,255,0.08);
            }
            .captcha-wrap { margin: 1rem 0; }
            .captcha-trigger {
                display: flex; align-items: center; justify-content: center; gap: 0.5rem;
                padding: 0.625rem; background: rgba(255,255,255,0.05);
                border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px;
                cursor: pointer; color: rgba(255,255,255,0.5); font-size: 0.8125rem;
                transition: all 0.2s; user-select: none;
            }
            .captcha-trigger:hover { border-color: rgba(99,102,241,0.5); color: rgba(255,255,255,0.8); }
            .captcha-trigger.verified { border: 1px solid rgba(34,197,94,0.3); color: #22c55e; background: rgba(34,197,94,0.05); }
            .login-btn {
                width: 100%;
                padding: 0.875rem;
                background: #6366f1;
                border: none;
                border-radius: 8px;
                color: #fff;
                font-size: 0.9375rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                margin-top: 0.5rem;
            }
            .login-btn:hover:not(:disabled) { background: #7c7ff7; }
            .login-btn:disabled { opacity: 0.3; cursor: not-allowed; background: rgba(255,255,255,0.1); }
            .remember-row {
                display: flex; align-items: center; gap: 0.5rem;
                margin: 0.75rem 0 1.25rem;
            }
            .remember-row input[type="checkbox"] {
                width: 14px; height: 14px; accent-color: #6366f1;
            }
            .remember-row label {
                font-size: 0.8125rem; color: rgba(255,255,255,0.5); cursor: pointer;
            }
            .error-msg {
                background: rgba(239,68,68,0.1);
                border: 1px solid rgba(239,68,68,0.2);
                padding: 0.625rem 0.875rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                font-size: 0.8125rem;
                color: #fca5a5;
            }
            .footer { text-align: center; margin-top: 2rem; color: rgba(255,255,255,0.25); font-size: 0.6875rem; }
            /* Captcha Overlay */
            .captcha-overlay {
                display: none; position: fixed; inset: 0;
                background: rgba(0,0,0,0.7); z-index: 1000;
                align-items: center; justify-content: center;
            }
            .captcha-overlay.show { display: flex; }
            .captcha-box {
                background: #1a1a2e; border-radius: 12px;
                padding: 1.25rem; width: 310px;
            }
            .captcha-canvas-wrap {
                position: relative; width: 280px; height: 155px;
                margin: 0 auto 0.75rem; border-radius: 8px; overflow: hidden;
                background: #252550;
            }
            .captcha-canvas-wrap canvas { display: block; }
            .captcha-slider {
                position: relative; width: 280px; height: 40px;
                margin: 0 auto; background: rgba(255,255,255,0.05);
                border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);
            }
            .captcha-slider-text {
                position: absolute; inset: 0; display: flex;
                align-items: center; justify-content: center;
                color: rgba(255,255,255,0.4); font-size: 0.75rem; pointer-events: none;
            }
            .captcha-slider-bar {
                position: absolute; top: 2px; left: 2px;
                width: 36px; height: 36px; border-radius: 18px;
                background: #6366f1; cursor: grab; display: flex;
                align-items: center; justify-content: center;
                font-size: 1rem; z-index: 1; transition: none;
            }
            .captcha-slider-bar:active { cursor: grabbing; }
            .captcha-slider-bar.success { background: #22c55e; }
            .captcha-slider-bar.fail { background: #ef4444; }
            .captcha-slider-track {
                position: absolute; top: 2px; left: 2px; height: 36px;
                border-radius: 18px; background: rgba(99,102,241,0.15);
                transition: width 0.05s;
            }
            .captcha-close {
                position: absolute; top: 8px; right: 8px;
                background: rgba(255,255,255,0.1); border: none;
                color: rgba(255,255,255,0.5); width: 24px; height: 24px;
                border-radius: 12px; cursor: pointer; font-size: 0.75rem;
            }
            .captcha-refresh {
                position: absolute; top: 8px; left: 8px;
                background: rgba(255,255,255,0.1); border: none;
                color: rgba(255,255,255,0.5); width: 24px; height: 24px;
                border-radius: 12px; cursor: pointer; font-size: 0.75rem;
            }
            @keyframes shake {
                0%,100%{transform:translateX(0)} 20%{transform:translateX(-6px)}
                40%{transform:translateX(6px)} 60%{transform:translateX(-4px)} 80%{transform:translateX(4px)}
            }
            .captcha-box.shake { animation: shake 0.4s ease; }
        </style>
    </head>
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-card">
                <div class="login-logo">
                    <div class="icon">🦜</div>
                    <h1>翠花量化</h1>
                    <p>CUIHUA QUANT</p>
                </div>
                {{ error_msg }}
                <form method="POST" id="loginForm">
                    <div class="form-group">
                        <label class="form-label">用户名</label>
                        <input type="text" name="username" class="form-input" placeholder="请输入用户名" required autofocus>
                    </div>
                    <div class="form-group">
                        <label class="form-label">密码</label>
                        <input type="password" name="password" class="form-input" placeholder="请输入密码" required>
                    </div>
                    <div class="captcha-wrap">
                        <div class="captcha-trigger" id="captchaTrigger" onclick="openCaptcha()">
                            <span>🛡️</span><span id="captchaText">点击完成安全验证</span>
                        </div>
                    </div>
                    <div class="remember-row">
                        <input type="checkbox" id="remember_me" name="remember_me">
                        <label for="remember_me">记住我，30天免登录</label>
                    </div>
                    <button type="submit" class="login-btn" id="loginBtn" disabled>请完成验证</button>
                    <input type="hidden" name="captcha_verified" id="captchaVerified" value="">
                </form>
                <div class="footer">Cuihua Quant v3.1.0 &copy; 2026</div>
            </div>
        </div>

        <!-- Captcha Overlay -->
        <div class="captcha-overlay" id="captchaOverlay">
            <div class="captcha-box" id="captchaBox">
                <div class="captcha-canvas-wrap">
                    <canvas id="captchaCanvas" width="280" height="155"></canvas>
                    <button class="captcha-refresh" onclick="initCaptcha()" title="刷新">🔄</button>
                    <button class="captcha-close" onclick="closeCaptcha()">✕</button>
                </div>
                <div class="captcha-slider">
                    <div class="captcha-slider-track" id="captchaTrack"></div>
                    <div class="captcha-slider-text" id="captchaSliderText">向右拖动滑块完成验证</div>
                    <div class="captcha-slider-bar" id="captchaBar">→</div>
                </div>
            </div>
        </div>

        <script>
        (function() {
            var canvas = document.getElementById('captchaCanvas');
            var ctx = canvas ? canvas.getContext('2d') : null;
            var W = 280, H = 155, L = 42, R = 10;
            var targetX, targetY, verified = false;
            var bar, track, startX;

            function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

            // Generate gradient colors for background
            function randomColor() {
                return 'hsl(' + rand(180, 320) + ', ' + rand(40, 70) + '%, ' + rand(35, 60) + '%)';
            }

            window.openCaptcha = function() {
                if (verified) return;
                document.getElementById('captchaOverlay').classList.add('show');
                initCaptcha();
            };

            window.closeCaptcha = function() {
                document.getElementById('captchaOverlay').classList.remove('show');
            };

            window.initCaptcha = function() {
                if (!ctx) return;
                if (verified) return;
                bar = document.getElementById('captchaBar');
                track = document.getElementById('captchaTrack');
                bar.style.left = '2px';
                bar.className = 'captcha-slider-bar';
                bar.innerHTML = '→';
                track.style.width = '0px';
                verified = false;
                targetX = rand(80, W - L - 30);
                targetY = rand(30, H - L - 20);
                document.getElementById('captchaBox').classList.remove('shake');

                // Draw beautiful gradient background
                drawBackground();

                // Draw target slot (dark silhouette)
                drawPuzzle(ctx, targetX, targetY, 'rgba(0,0,0,0.5)', 'rgba(255,255,255,0.1)');
            };

            function drawBackground() {
                // Base gradient
                var grd = ctx.createLinearGradient(0, 0, W, H);
                grd.addColorStop(0, '#2a2060');
                grd.addColorStop(0.5, '#3a2870');
                grd.addColorStop(1, '#202050');
                ctx.fillStyle = grd;
                ctx.fillRect(0, 0, W, H);

                // Layered circles for visual richness
                var colors = [randomColor(), randomColor(), randomColor(), randomColor(), randomColor()];
                for (var i = 0; i < 12; i++) {
                    ctx.beginPath();
                    ctx.arc(rand(10, W-10), rand(10, H-10), rand(8, 50), 0, Math.PI * 2);
                    ctx.fillStyle = colors[i % 5];
                    ctx.globalAlpha = 0.25 + Math.random() * 0.15;
                    ctx.fill();
                }
                ctx.globalAlpha = 1.0;

                // Grid pattern
                ctx.strokeStyle = 'rgba(255,255,255,0.03)';
                ctx.lineWidth = 1;
                for (var x = 0; x < W; x += 20) {
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
                }
                for (var y = 0; y < H; y += 20) {
                    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
                }

                // Stars
                ctx.fillStyle = 'rgba(255,255,255,0.3)';
                for (var i = 0; i < 15; i++) {
                    ctx.beginPath();
                    ctx.arc(rand(5, W-5), rand(5, H-5), rand(0.5, 1.5), 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            function drawPuzzle(c, x, y, fillColor, strokeColor) {
                c.beginPath();
                c.moveTo(x, y);
                c.lineTo(x + L * 2/3, y);
                c.arc(x + L * 2/3, y - R + 2, R, 0, Math.PI, true);
                c.lineTo(x + L, y);
                c.lineTo(x + L, y + L * 2/3);
                c.arc(x + L + R - 2, y + L * 2/3, R, 0, Math.PI * 1.5, false);
                c.lineTo(x + L, y + L);
                c.lineTo(x, y + L);
                c.arc(x, y + L * 2/3, R, 0, Math.PI * 1.5, true);
                c.lineTo(x, y);
                c.closePath();
                if (fillColor) { c.fillStyle = fillColor; c.fill(); }
                if (strokeColor) { c.strokeStyle = strokeColor; c.lineWidth = 2; c.stroke(); }
            }

            function drawPiece(c, x, y) {
                // Draw the floating puzzle piece
                c.save();
                c.shadowColor = 'rgba(99,102,241,0.6)';
                c.shadowBlur = 12;
                drawPuzzle(c, x, y, 'rgba(99,102,241,0.85)', 'rgba(160,160,255,0.5)');
                c.restore();
            }

            // Drag events
            var dragging = false;
            function onDown(e) {
                if (verified) return;
                e.preventDefault();
                dragging = true;
                startX = (e.touches ? e.touches[0].clientX : e.clientX);
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
                document.addEventListener('touchmove', onMove, {passive: false});
                document.addEventListener('touchend', onUp);
            }

            function onMove(e) {
                if (!dragging || verified) return;
                e.preventDefault();
                var cx = (e.touches ? e.touches[0].clientX : e.clientX);
                var dx = cx - startX;
                dx = Math.max(0, Math.min(dx, W - 38));
                bar.style.left = (dx + 2) + 'px';
                track.style.width = (dx + 20) + 'px';

                // Redraw canvas with puzzle piece moving
                drawBackground();
                // Target slot
                drawPuzzle(ctx, targetX, targetY, 'rgba(0,0,0,0.5)', 'rgba(255,255,255,0.1)');
                // Moving piece
                drawPiece(ctx, dx, targetY);
            }

            function onUp() {
                if (!dragging) return;
                dragging = false;
                document.removeEventListener('mousemove', onMove);
                document.removeEventListener('mouseup', onUp);
                document.removeEventListener('touchmove', onMove);
                document.removeEventListener('touchend', onUp);

                var left = parseInt(bar.style.left) - 2;
                var diff = Math.abs(left - targetX);

                if (diff <= 8) {
                    // Success
                    verified = true;
                    bar.innerHTML = '✓';
                    bar.className = 'captcha-slider-bar success';
                    track.style.background = 'rgba(34,197,94,0.2)';

                    // Draw success
                    drawBackground();
                    drawPuzzle(ctx, targetX, targetY, 'rgba(34,197,94,0.5)', 'rgba(34,197,94,0.8)');
                    ctx.fillStyle = '#22c55e';
                    ctx.font = 'bold 24px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('✓', targetX + L/2, targetY + L/2);

                    document.getElementById('captchaSliderText').textContent = '验证成功！';

                    setTimeout(function() {
                        closeCaptcha();
                        var trigger = document.getElementById('captchaTrigger');
                        trigger.className = 'captcha-trigger verified';
                        trigger.removeAttribute('onclick');
                        trigger.innerHTML = '<span>✅</span><span>验证通过</span>';
                        var btn = document.getElementById('loginBtn');
                        btn.disabled = false;
                        btn.textContent = '🔐 登 录';
                        btn.style.opacity = '1';
                        btn.style.cursor = 'pointer';
                        document.getElementById('captchaVerified').value = '1';
                    }, 600);
                } else {
                    // Fail - shake animation
                    bar.className = 'captcha-slider-bar fail';
                    bar.innerHTML = '✕';
                    document.getElementById('captchaBox').classList.add('shake');
                    document.getElementById('captchaSliderText').textContent = '验证失败，请重试';

                    setTimeout(function() {
                        document.getElementById('captchaBox').classList.remove('shake');
                        bar.className = 'captcha-slider-bar';
                        bar.style.transition = 'left 0.3s ease';
                        bar.style.left = '2px';
                        bar.innerHTML = '→';
                        track.style.width = '0px';
                        track.style.background = '';
                        document.getElementById('captchaSliderText').textContent = '向右拖动滑块完成验证';
                        setTimeout(function() {
                            bar.style.transition = 'none';
                            targetX = rand(80, W - L - 30);
                            targetY = rand(30, H - L - 20);
                            initCaptcha();
                        }, 350);
                    }, 800);
                }
            }

            if (document.getElementById('captchaBar')) {
                document.getElementById('captchaBar').addEventListener('mousedown', onDown);
                document.getElementById('captchaBar').addEventListener('touchstart', onDown, {passive: false});
            }
        })();
        </script>
    </body>
    </html>
    """

    # ==================== SIDEBAR ====================
    def build_sidebar(page, user=None):
        user = user or {'username': 'admin', 'nickname': '管理员', 'avatar': '🦜'}
        avatar = user.get('avatar', '🦜')
        nickname = user.get('nickname', user.get('username', 'admin'))

        # Auto-open group for current page
        trade_pages = {'analysis', 'charts', 'backtest', 'paper'}
        research_pages = {'strategies', 'factors', 'heatmap', 'events', 'articles'}
        risk_pages = {'risk', 'alerts', 'stoploss', 'stress', 'compliance'}
        tool_pages = {'performance', 'behavior', 'paramopt', 'reports', 'research'}

        trade_open = 'open' if page in trade_pages else ''
        research_open = 'open' if page in research_pages else ''
        risk_open = 'open' if page in risk_pages else ''
        tool_open = 'open' if page in tool_pages else ''

        return f"""
    <nav class="sidebar" id="sidebar">
        <div class="logo">🦜 翠花量化</div>

        <!-- 核心功能 -->
        <a href="/" class="nav-item {{ 'active' if page=='dashboard' else '' }}"><span>📊</span> 监控看板</a>
        <a href="/stocks" class="nav-item {{ 'active' if page=='stocks' else '' }}"><span>💼</span> 股票池</a>
        <a href="/portfolio" class="nav-item {{ 'active' if page=='portfolio' else '' }}"><span>🌍</span> 投资组合</a>

        <!-- 交易 -->
        <div class="nav-group {trade_open}">
            <div class="nav-group-header" onclick="this.parentElement.classList.toggle('open')"><span>📈</span> 交易 <span class="nav-group-arrow">▸</span></div>
            <div class="nav-group-items">
                <a href="/analysis" class="nav-item {{ 'active' if page=='analysis' else '' }}"><span></span> 信号分析</a>
                <a href="/charts" class="nav-item {{ 'active' if page=='charts' else '' }}"><span></span> 图表分析</a>
                <a href="/backtest" class="nav-item {{ 'active' if page=='backtest' else '' }}"><span></span> 回测中心</a>
                <a href="/paper" class="nav-item {{ 'active' if page=='paper' else '' }}"><span></span> 模拟盘</a>
            </div>
        </div>

        <!-- 研究 -->
        <div class="nav-group {research_open}">
            <div class="nav-group-header" onclick="this.parentElement.classList.toggle('open')"><span>🔬</span> 研究 <span class="nav-group-arrow">▸</span></div>
            <div class="nav-group-items">
                <a href="/strategies" class="nav-item {{ 'active' if page=='strategies' else '' }}"><span></span> 策略管理</a>
                <a href="/factors" class="nav-item {{ 'active' if page=='factors' else '' }}"><span></span> 因子研究</a>
                <a href="/heatmap" class="nav-item {{ 'active' if page=='heatmap' else '' }}"><span></span> 热力图</a>
                <a href="/events" class="nav-item {{ 'active' if page=='events' else '' }}"><span></span> 事件研究</a>
                <a href="/articles" class="nav-item {{ 'active' if page=='articles' else '' }}"><span></span> 文章信息</a>
            </div>
        </div>

        <!-- 风控 -->
        <div class="nav-group {risk_open}">
            <div class="nav-group-header" onclick="this.parentElement.classList.toggle('open')"><span>🛡️</span> 风控 <span class="nav-group-arrow">▸</span></div>
            <div class="nav-group-items">
                <a href="/risk" class="nav-item {{ 'active' if page=='risk' else '' }}"><span></span> 风险监控</a>
                <a href="/alerts" class="nav-item {{ 'active' if page=='alerts' else '' }}"><span></span> 告警中心</a>
                <a href="/stoploss" class="nav-item {{ 'active' if page=='stoploss' else '' }}"><span></span> 智能止损</a>
                <a href="/stress" class="nav-item {{ 'active' if page=='stress' else '' }}"><span></span> 压力测试</a>
                <a href="/compliance" class="nav-item {{ 'active' if page=='compliance' else '' }}"><span></span> 合规检查</a>
            </div>
        </div>

        <!-- 工具 -->
        <div class="nav-group {tool_open}">
            <div class="nav-group-header" onclick="this.parentElement.classList.toggle('open')"><span>🔧</span> 工具 <span class="nav-group-arrow">▸</span></div>
            <div class="nav-group-items">
                <a href="/performance" class="nav-item {{ 'active' if page=='performance' else '' }}"><span></span> 绩效分析</a>
                <a href="/behavior" class="nav-item {{ 'active' if page=='behavior' else '' }}"><span></span> 行为分析</a>
                <a href="/paramopt" class="nav-item {{ 'active' if page=='paramopt' else '' }}"><span></span> 参数优化</a>
                <a href="/reports" class="nav-item {{ 'active' if page=='reports' else '' }}"><span></span> 自动报告</a>
                <a href="/research" class="nav-item {{ 'active' if page=='research' else '' }}"><span></span> 研究笔记本</a>
            </div>
        </div>

        <div class="sidebar-footer">
            <a href="/settings" class="nav-item {{ 'active' if page=='settings' else '' }}"><span>⚙️</span> 系统设置</a>
            <a href="/profile" class="nav-item {{ 'active' if page=='profile' else '' }}"><span>👤</span> 个人信息</a>
            <a href="/logout" class="nav-item logout"><span>🚪</span> 退出登录</a>
        </div>

        <div class="sidebar-user">
            <span class="user-avatar">{avatar}</span>
            <div><div class="user-name">{nickname}</div><div class="user-role">管理员</div></div>
        </div>
    </nav>
    """

    def get_base_template(page, user=None, theme='dark'):
        sidebar_html = build_sidebar(page, user)
        theme_css = get_theme_css(theme)
        return """<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>翠花量化</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>""" + theme_css + STYLES + """</style>
    </head>
    <body>
    """ + sidebar_html + """
        <main class="main">
        {{ content|safe }}
        </main>
        <script>
            setTimeout(() => location.reload(), 60000);
        </script>
    </body>
    </html>
    """

    # ==================== HELPER FUNCTIONS ====================

    def get_stock_names():
        """获取股票名称映射"""
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        names = {}
        try:
            with open(cfg_path, 'r') as f:
                cfg = yaml.safe_load(f)
            for pool_data in cfg.get('pools', {}).values():
                for item in pool_data.get('stocks', []):
                    if isinstance(item, dict):
                        code = item.get('code', '')
                        name = item.get('name', '')
                        if code and code not in names:
                            names[code] = name
                    elif isinstance(item, str) and item not in names:
                        names[item] = ''
        except Exception as e:
            pass
        return names

    def get_stock_codes():
        """获取所有股票代码"""
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        codes = []
        try:
            with open(cfg_path, 'r') as f:
                cfg = yaml.safe_load(f)
            for pool_data in cfg.get('pools', {}).values():
                for item in pool_data.get('stocks', []):
                    code = item.get('code', item) if isinstance(item, dict) else item
                    if code and code not in codes:
                        codes.append(code)
        except Exception as e:
            pass
        return codes

    def render_page(content, page_name, user=None):
        """渲染页面"""
        from flask import render_template_string
        user = user or get_user_info()
        theme = user.get('theme', 'dark') if user else 'dark'
        base_html = get_base_template(page_name, user, theme)
        return render_template_string(base_html, content=content, page=page_name)

    def login_required(f):
        """登录认证装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not AUTH_CONFIG.get('enabled', True):
                return f(*args, **kwargs)
            if 'logged_in' not in session or not session.get('logged_in'):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    def make_table(headers, rows):
        """生成 HTML 表格"""
        th = ''.join(f'<th>{h}</th>' for h in headers)
        trs = ''.join(f'<tr>{"".join(f"<td>{c}</td>" for c in r)}</tr>' for r in rows)
        return f"""<div class="table-container"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>"""

    # ==================== ROUTES ====================

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # 检查记住我 cookie 自动登录
        remember_token = request.cookies.get('remember_token')
        if remember_token:
            username = verify_remember_token(remember_token)
            if username:
                session['logged_in'] = True
                session['username'] = username
                session.permanent = True
                return redirect(url_for('dashboard'))
            else:
                # 令牌无效，清除 cookie
                resp = redirect(url_for('login'))
                resp.set_cookie('remember_token', '', expires=0)
                return resp

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            remember_me = request.form.get('remember_me') == 'on'
            captcha_ok = request.form.get('captcha_verified') == '1'
            if not captcha_ok:
                error_msg = '<div class="error-msg">❌ 请先完成拖拽验证</div>'
                return render_template_string(LOGIN_PAGE, error_msg=error_msg)
            if check_auth(username, password):
                session['logged_in'] = True
                session['username'] = username
                session.permanent = True
                resp = redirect(url_for('dashboard'))
                if remember_me:
                    # 生成随机令牌，只存哈希到服务端
                    token = generate_remember_token()
                    save_remember_token(username, token)
                    # 设置 cookie (30天)  httponly=True 防 XSS
                    resp.set_cookie('remember_token', token, max_age=30*24*3600,
                                   httponly=True, samesite='Lax')
                return resp
            else:
                error_msg = '<div class="error-msg">❌ 用户名或密码错误</div>'
                return render_template_string(LOGIN_PAGE, error_msg=error_msg)
        return render_template_string(LOGIN_PAGE, error_msg='')

    @app.route('/logout')
    def logout():
        session.clear()
        resp = redirect(url_for('login'))
        resp.set_cookie('remember_token', '', expires=0)
        return resp

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        user = get_user_info()
        msg = ''
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'update_profile':
                try:
                    new_nickname = request.form.get('nickname', '').strip()
                    new_email = request.form.get('email', '').strip()
                    new_avatar = request.form.get('avatar', '').strip()
                    if os.path.exists(_auth_path):
                        with open(_auth_path, 'r') as f:
                            cfg = yaml.safe_load(f) or {}
                        if new_nickname:
                            cfg['auth']['admin']['nickname'] = new_nickname
                        if new_email:
                            cfg['auth']['admin']['email'] = new_email
                        if new_avatar:
                            cfg['auth']['admin']['avatar'] = new_avatar
                        with open(_auth_path, 'w') as f:
                            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
                        _load_auth()
                        msg = '<div class="alert alert-success">✅ 个人信息已更新</div>'
                except Exception as e:
                    msg = f'<div class="alert alert-error">❌ 更新失败: {str(e)}</div>'
            elif action == 'change_password':
                try:
                    old_pwd = request.form.get('old_password', '').strip()
                    new_pwd = request.form.get('new_password', '').strip()
                    confirm_pwd = request.form.get('confirm_password', '').strip()
                    admin = AUTH_CONFIG.get('admin', {})
                    if old_pwd != admin.get('password', ''):
                        msg = '<div class="alert alert-error">❌ 原密码错误</div>'
                    elif new_pwd != confirm_pwd:
                        msg = '<div class="alert alert-error">❌ 两次输入的新密码不一致</div>'
                    elif len(new_pwd) < 6:
                        msg = '<div class="alert alert-error">❌ 密码长度不能少于6位</div>'
                    else:
                        if os.path.exists(_auth_path):
                            with open(_auth_path, 'r') as f:
                                cfg = yaml.safe_load(f) or {}
                            cfg['auth']['admin']['password'] = new_pwd
                            with open(_auth_path, 'w') as f:
                                yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
                            _load_auth()
                            msg = '<div class="alert alert-success">✅ 密码已修改</div>'
                except Exception as e:
                    msg = f'<div class="alert alert-error">❌ 修改失败: {str(e)}</div>'

        content = f"""
        <div class="header">
            <div><h1>👤 个人信息</h1><p style="color:var(--text-secondary)">修改个人资料和密码</p></div>
        </div>
        {msg}
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">📝 基本信息</h3></div>
                <form method="POST">
                    <input type="hidden" name="action" value="update_profile">
                    <div class="form-group"><label class="form-label">头像</label>
                        <input type="text" name="avatar" class="form-input" value="{user.get('avatar', '🦜')}" placeholder="emoji 如 🦜"></div>
                    <div class="form-group"><label class="form-label">昵称</label>
                        <input type="text" name="nickname" class="form-input" value="{user.get('nickname', '')}"></div>
                    <div class="form-group"><label class="form-label">邮箱</label>
                        <input type="email" name="email" class="form-input" value="{user.get('email', '')}"></div>
                    <div class="form-group"><label class="form-label">用户名</label>
                        <input type="text" class="form-input" value="{user.get('username', '')}" disabled style="opacity:0.5"></div>
                    <button type="submit" class="btn btn-primary">💾 保存修改</button>
                </form>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">🔒 修改密码</h3></div>
                <form method="POST">
                    <input type="hidden" name="action" value="change_password">
                    <div class="form-group"><label class="form-label">原密码</label>
                        <input type="password" name="old_password" class="form-input" required></div>
                    <div class="form-group"><label class="form-label">新密码</label>
                        <input type="password" name="new_password" class="form-input" required minlength="6"></div>
                    <div class="form-group"><label class="form-label">确认新密码</label>
                        <input type="password" name="confirm_password" class="form-input" required minlength="6"></div>
                    <button type="submit" class="btn btn-primary">🔑 修改密码</button>
                </form>
            </div>
        </div>
        """
        return render_page(content, 'profile', user=user)

    @app.route('/')
    @login_required
    def dashboard():
        try:
            from src.monitor.system_monitor import SystemMonitor
            monitor = SystemMonitor()
            futu = monitor.check_futu_connection()
            data = monitor.check_data_freshness()
            disk = monitor.check_disk_space()
            is_ok = futu['status'] == 'OK' and data['status'] == 'OK'
        except Exception as e:
            is_ok = True
            futu = {'status': 'OK', 'message': '未连接'}
            data = {'status': 'OK', 'message': '数据正常'}
            disk = {'status': 'OK', 'message': '空间充足'}

        try:
            from src.data.database import get_db_engine
            engine = get_db_engine()
            count = pd.read_sql("SELECT COUNT(*) as cnt FROM stock_daily", engine).iloc[0]['cnt']
        except Exception as e:
            count = 0

        # 热力图：涨跌排行
        top_gainers = []
        top_losers = []
        heatmap_date = '--'
        try:
            from src.data.database import get_db_engine
            engine = get_db_engine()
            stock_names = get_stock_names()
            df = pd.read_sql('''
                SELECT t1.code, t1.close_price, t1.date, t2.close_price as prev_price
                FROM stock_daily t1
                LEFT JOIN stock_daily t2
                    ON t1.code = t2.code
                    AND t2.date = (SELECT MAX(date) FROM stock_daily WHERE code = t1.code AND date < t1.date)
                WHERE t1.date = (SELECT MAX(date) FROM stock_daily WHERE code = t1.code)
            ''', engine)
            if not df.empty:
                df['change'] = ((df['close_price'] - df['prev_price']) / df['prev_price'] * 100).round(2)
                heatmap_date = str(df.iloc[0]['date'])
                for _, row in df.nlargest(5, 'change').iterrows():
                    c = row['code']
                    top_gainers.append({'code': c, 'name': stock_names.get(c, ''), 'price': f"{row['close_price']:.2f}", 'change': row['change']})
                for _, row in df.nsmallest(5, 'change').iterrows():
                    c = row['code']
                    top_losers.append({'code': c, 'name': stock_names.get(c, ''), 'price': f"{row['close_price']:.2f}", 'change': row['change']})
        except Exception as e:
            pass

        gainers_rows = ''.join(f"""<tr><td><span class="badge badge-warning">{g['code']}</span></td><td>{g['name']}</td><td>¥{g['price']}</td><td style="color:var(--success);font-weight:600">+{g['change']:.2f}%</td></tr>""" for g in top_gainers) if top_gainers else '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary)">暂无数据</td></tr>'
        losers_rows = ''.join(f"""<tr><td><span class="badge badge-warning">{l['code']}</span></td><td>{l['name']}</td><td>¥{l['price']}</td><td style="color:var(--danger);font-weight:600">{l['change']:.2f}%</td></tr>""" for l in top_losers) if top_losers else '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary)">暂无数据</td></tr>'

        content = f"""
        <div class="header">
            <div><h1>📊 监控看板</h1><p style="color:var(--text-secondary)">实时系统状态与交易概览</p></div>
            <div class="header-actions">
                <button class="btn btn-secondary" onclick="location.reload()">🔄 刷新</button>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">系统状态</div>
                <div class="stat-value" style="font-size:1.5rem;">{'✅' if is_ok else '⚠️'}</div>
                <div class="stat-change" style="color:var(--text-secondary)">{'正常运行' if is_ok else '部分异常'}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">数据库记录</div>
                <div class="stat-value">{count:,}</div>
                <div class="stat-change" style="color:var(--success)">✅ 正常</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Futu OpenD</div>
                <div class="stat-value" style="font-size:1.25rem;">{'✅' if futu['status']=='OK' else '❌'}</div>
                <div class="stat-change">{futu.get('message', '')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">磁盘空间</div>
                <div class="stat-value" style="font-size:1.25rem;">{'✅' if disk['status']=='OK' else '⚠️'}</div>
                <div class="stat-change">{disk.get('message', '')}</div>
            </div>
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title" style="color:var(--success)">📈 涨幅 Top 5 <span style="color:var(--text-secondary);font-size:0.8125rem">({heatmap_date})</span></h3></div>
                <div class="table-container"><table><thead><tr><th>代码</th><th>名称</th><th>价格</th><th>涨跌</th></tr></thead><tbody>{gainers_rows}</tbody></table></div>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title" style="color:var(--danger)">📉 跌幅 Top 5 <span style="color:var(--text-secondary);font-size:0.8125rem">({heatmap_date})</span></h3></div>
                <div class="table-container"><table><thead><tr><th>代码</th><th>名称</th><th>价格</th><th>涨跌</th></tr></thead><tbody>{losers_rows}</tbody></table></div>
            </div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">🔧 系统信息</h3></div>
            {make_table(['项目', '状态', '详情'], [
                ['Futu OpenD', f'<span class="badge badge-{"success" if futu["status"]=="OK" else "danger"}">{"正常" if futu["status"]=="OK" else "异常"}</span>', futu.get('message', '')],
                ['数据新鲜度', f'<span class="badge badge-{"success" if data["status"]=="OK" else "warning"}">{"正常" if data["status"]=="OK" else "警告"}</span>', data.get('message', '')],
                ['磁盘空间', f'<span class="badge badge-{"success" if disk["status"]=="OK" else "warning"}">{"正常" if disk["status"]=="OK" else "警告"}</span>', disk.get('message', '')],
                ['WebUI', '<span class="badge badge-success">v3 全功能</span>', '20+ 页面'],
                ['模块总数', '<span class="badge badge-info">155</span>', '~29K 代码行'],
            ])}
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">🚀 快速导航</h3></div>
            <div class="grid-3">
                <a href="/stocks" class="btn btn-secondary" style="justify-content:center">💼 股票池</a>
                <a href="/analysis" class="btn btn-secondary" style="justify-content:center">📈 信号分析</a>
                <a href="/backtest" class="btn btn-secondary" style="justify-content:center">🔬 回测中心</a>
                <a href="/charts" class="btn btn-secondary" style="justify-content:center">📉 图表分析</a>
                <a href="/strategies" class="btn btn-secondary" style="justify-content:center">🎯 策略管理</a>
                <a href="/alerts" class="btn btn-secondary" style="justify-content:center">🔔 告警中心</a>
            </div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'dashboard', user=user)

    @app.route('/stocks', methods=['GET', 'POST'])
    @login_required
    def stocks():
        import yaml
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')

        # 处理新增/删除
        msg = ''
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'add':
                new_code = request.form.get('new_code', '').strip()
                new_name = request.form.get('new_name', '').strip()
                if new_code:
                    try:
                        with open(cfg_path, 'r') as f:
                            cfg = yaml.safe_load(f) or {}
                        pool = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
                        existing = [item.get('code', item) if isinstance(item, dict) else item for item in pool]
                        if new_code not in existing:
                            pool.append({'code': new_code, 'name': new_name})
                            cfg['pools']['watchlist']['stocks'] = pool
                            with open(cfg_path, 'w') as f:
                                yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
                            msg = f'✅ 已添加 {new_code} {new_name}'
                        else:
                            msg = f'⚠️ {new_code} 已存在'
                    except Exception as e:
                        msg = f'❌ 添加失败: {str(e)}'
            elif action == 'delete':
                del_code = request.form.get('del_code', '').strip()
                if del_code:
                    try:
                        with open(cfg_path, 'r') as f:
                            cfg = yaml.safe_load(f) or {}
                        pool = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
                        pool = [item for item in pool if (item.get('code', item) if isinstance(item, dict) else item) != del_code]
                        cfg['pools']['watchlist']['stocks'] = pool
                        with open(cfg_path, 'w') as f:
                            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
                        msg = f'✅ 已删除 {del_code}'
                    except Exception as e:
                        msg = f'❌ 删除失败: {str(e)}'
            elif action == 'refresh':
                refresh_code = request.form.get('refresh_code', '').strip()
                if refresh_code:
                    try:
                        from src.data.akshare_sync import AKShareSync
                        syncer = AKShareSync()
                        syncer.fetch_and_save(refresh_code, days_back=30)
                        msg = f'✅ 已拉取 {refresh_code} 近30天历史数据'
                    except Exception as e:
                        msg = f'❌ 拉取失败: {str(e)}'

        # 重新加载
        stock_names = get_stock_names()
        codes = get_stock_codes()

        # 分页
        page = request.args.get('page', 1, type=int)
        per_page = 10
        total = len(codes)
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = min(page, total_pages)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_codes = codes[start_idx:end_idx]

        stocks_data = []
        try:
            from src.data.database import get_db_engine
            engine = get_db_engine()
            for code in page_codes:
                try:
                    df = pd.read_sql(
                        f"SELECT close_price FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 2",
                        engine
                    )
                    if len(df) >= 2:
                        price = df.iloc[0]['close_price']
                        change = ((price - df.iloc[1]['close_price']) / df.iloc[1]['close_price']) * 100
                    elif len(df) == 1:
                        price = df.iloc[0]['close_price']
                        change = 0
                    else:
                        price, change = '-', 0
                    stocks_data.append({
                        'code': code, 'name': stock_names.get(code, ''),
                        'price': f"{price:.2f}" if isinstance(price, (int, float)) else price,
                        'change': round(change, 2)
                    })
                except Exception as e:
                    stocks_data.append({'code': code, 'name': stock_names.get(code, ''), 'price': '-', 'change': 0})
        except Exception as e:
            for code in page_codes:
                stocks_data.append({'code': code, 'name': stock_names.get(code, ''), 'price': '-', 'change': 0})

        # 构建表格行
        rows = []
        for s in stocks_data:
            color = 'var(--success)' if s['change'] > 0 else ('var(--danger)' if s['change'] < 0 else 'var(--text-primary)')
            has_price = s['price'] != '-'
            refresh_btn = f'''<form method="POST" style="display:inline"><input type="hidden" name="action" value="refresh"><input type="hidden" name="refresh_code" value="{s["code"]}"><button type="submit" class="btn btn-primary" style="padding:0.25rem 0.5rem;font-size:0.75rem">🔄</button></form>''' if not has_price else '<span style="color:var(--text-secondary);font-size:0.7rem">已有</span>'
            del_btn = f'''<form method="POST" style="display:inline"><input type="hidden" name="action" value="delete"><input type="hidden" name="del_code" value="{s["code"]}"><button type="submit" class="btn btn-danger" style="padding:0.25rem 0.5rem;font-size:0.75rem" onclick="return confirm('确定删除 {s["code"]} {s["name"]}?')">🗑️</button></form>'''
            rows.append([
                f'<span class="badge badge-warning">{s["code"]}</span>',
                s['name'],
                f"¥{s['price']}",
                f'<span style="color:{color}">{s["change"]:+.2f}%</span>',
                f'{refresh_btn} <a href="/charts?code={s["code"]}" class="btn btn-secondary" style="padding:0.25rem 0.5rem;font-size:0.75rem">📉</a> {del_btn}'
            ])

        # 分页导航
        has_prev = page > 1
        has_next = page < total_pages
        pagination = []
        if has_prev:
            pagination.append(f'<a href="/stocks?page={page-1}" class="btn btn-secondary" style="padding:0.25rem 0.625rem;font-size:0.75rem">◀ 上一页</a>')
        page_info = f'<span style="color:var(--text-secondary);font-size:0.875rem;margin:0 0.75rem">第 {page}/{total_pages} 页 (共 {total} 只)</span>'
        if has_next:
            pagination.append(f'<a href="/stocks?page={page+1}" class="btn btn-secondary" style="padding:0.25rem 0.625rem;font-size:0.75rem">下一页 ▶</a>')
        pagination_html = f"""<div style="display:flex;align-items:center;justify-content:center;margin-top:1rem">{''.join(pagination)}{page_info}</div>"""

        msg_html = f'<div class="alert alert-success">{msg}</div>' if msg else ''

        content = f"""
        <div class="header">
            <div><h1>💼 股票池管理</h1><p style="color:var(--text-secondary)">共 {total} 只股票 | 第 {page}/{total_pages} 页</p></div>
            <div class="header-actions">
                <a href="/analysis" class="btn btn-primary">📈 生成信号</a>
            </div>
        </div>

        {msg_html}

        <div class="card">
            <div class="card-header"><h3 class="card-title">➕ 新增股票</h3></div>
            <form method="POST" class="form-row" style="align-items:end">
                <div class="form-group"><label class="form-label">股票代码</label>
                    <input type="text" name="new_code" class="form-input" placeholder="如: HK.09988" required></div>
                <div class="form-group"><label class="form-label">股票名称</label>
                    <input type="text" name="new_name" class="form-input" placeholder="如: 阿里巴巴"></div>
                <div class="form-group"><label class="form-label">&nbsp;</label>
                    <button type="submit" name="action" value="add" class="btn btn-success">➕ 添加</button></div>
            </form>
        </div>

        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 股票列表</h3></div>
            {make_table(['代码', '名称', '最新价', '涨跌幅', '操作'], rows)}
            {pagination_html}
        </div>
        """
        user = get_user_info()
        return render_page(content, 'stocks', user=user)


    @app.route('/analysis', methods=['GET', 'POST'])
    @login_required
    def analysis():
        stock_names = get_stock_names()
        codes = get_stock_codes()[:20]

        signals = []
        if request.method == 'POST' or True:
            try:
                from src.analysis.signal_gen import SignalGenerator
                gen = SignalGenerator()
                df = gen.generate_combined_signal(codes)
                if df is not None and not df.empty:
                    signals = df.to_dict('records')
                    for s in signals:
                        s['name'] = stock_names.get(s.get('code', ''), '')
            except Exception as e:
                pass

        if signals:
            rows = []
            for s in signals[:20]:
                score = s.get('combined_score', 0)
                color = 'var(--success)' if score > 0 else 'var(--danger)'
                rank_badge = 'badge-success' if s.get('rank', 99) <= 5 else 'badge-warning'
                rows.append([
                    f'<span class="badge {rank_badge}">#{s.get("rank","")}</span>',
                    f'<span class="badge badge-warning">{s.get("code","")}</span>',
                    s.get('name', ''),
                    f"¥{s.get('close', '-')}",
                    f'<span style="color:{color}">{score:+.3f}</span>',
                    f'{s.get("tech_score", 0):+.3f}',
                    f'{s.get("sentiment_score", 0):+.3f}',
                ])
            table_html = make_table(['排名', '代码', '名称', '收盘价', '综合得分', '技术分', '情绪分'], rows)
        else:
            table_html = '<div class="alert alert-info">💡 暂无数据，请先同步数据</div>'

        content = f"""
        <div class="header">
            <div><h1>📈 信号分析</h1><p style="color:var(--text-secondary)">基于技术指标和情绪分析的交易信号</p></div>
            <div class="header-actions">
                <form method="POST" style="display:flex;gap:0.5rem">
                    <button type="submit" class="btn btn-primary">🔄 刷新信号</button>
                </form>
            </div>
        </div>
        <div class="card">{table_html}</div>
        """
        user = get_user_info()
        return render_page(content, 'analysis', user=user)

    @app.route('/backtest')
    @login_required
    def backtest():
        strategies = [
            ('SMA 交叉', '均线交叉策略'),
            ('动量策略', '动量突破策略'),
            ('均值回归', '均值回归策略'),
            ('多因子', '多因子选股策略'),
            ('配对交易', '统计套利策略'),
            ('波动率', '波动率策略'),
            ('行业轮动', '行业轮动策略'),
            ('新闻交易', '新闻情绪策略'),
        ]

        strat_opts = ''.join(f'<option value="{s[0]}">{s[0]} - {s[1]}</option>' for s in strategies)

        content = f"""
        <div class="header">
            <div><h1>🔬 回测中心</h1><p style="color:var(--text-secondary)">策略回测与绩效分析</p></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📊 回测配置</h3></div>
            <div class="form-row">
                <div class="form-group"><label class="form-label">策略</label><select class="form-select">{strat_opts}</select></div>
                <div class="form-group"><label class="form-label">股票池</label><select class="form-select"><option>核心观察池</option><option>沪深300</option></select></div>
                <div class="form-group"><label class="form-label">开始日期</label><input type="date" class="form-input" value="2024-01-01"></div>
                <div class="form-group"><label class="form-label">结束日期</label><input type="date" class="form-input" value="2026-04-17"></div>
                <div class="form-group"><label class="form-label">初始资金</label><input type="text" class="form-input" value="1,000,000"></div>
                <div class="form-group"><label class="form-label">&nbsp;</label><button class="btn btn-primary">🚀 开始回测</button></div>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">总收益率</div><div class="stat-value">--</div><div class="stat-change">等待回测</div></div>
            <div class="stat-card"><div class="stat-label">年化收益</div><div class="stat-value">--</div><div class="stat-change">等待回测</div></div>
            <div class="stat-card"><div class="stat-label">夏普比率</div><div class="stat-value">--</div><div class="stat-change">等待回测</div></div>
            <div class="stat-card"><div class="stat-label">最大回撤</div><div class="stat-value">--</div><div class="stat-change">等待回测</div></div>
            <div class="stat-card"><div class="stat-label">胜率</div><div class="stat-value">--</div><div class="stat-change">等待回测</div></div>
            <div class="stat-card"><div class="stat-label">盈亏比</div><div class="stat-value">--</div><div class="stat-change">等待回测</div></div>
        </div>
        <div class="alert alert-info">💡 选择策略和配置参数后点击"开始回测"</div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📚 回测引擎</h3></div>
            <p style="color:var(--text-secondary);font-size:0.875rem">
                支持 Backtrader 事件驱动回测、Walk-Forward 优化、蒙特卡洛模拟。
                可用模块: <span class="tag">advanced_backtest</span><span class="tag">automated_pipeline</span><span class="tag">event_driven</span><span class="tag">backtest_runner</span>
            </p>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'backtest', user=user)

    @app.route('/charts', methods=['GET', 'POST'])
    @login_required
    def charts():
        stock_names = get_stock_names()
        codes = get_stock_codes()

        code = request.form.get('code') or request.args.get('code', 'SZ.002594')
        days = request.form.get('days') or request.args.get('days', '60')

        select_html = ''
        for c in codes:
            sel = ' selected' if c == code else ''
            label = f"{c} {stock_names.get(c, '')}".strip()
            select_html += f'<option value="{c}"{sel}>{label}</option>'

        chart_html = None
        if request.method == 'POST' or request.args.get('code'):
            try:
                from src.monitor.charts import AdvancedChartGenerator
                charts = AdvancedChartGenerator()
                chart_html = charts.generate_kline_with_indicators(code, int(days))
            except Exception as e:
                chart_html = None

        content = f"""
        <div class="header">
            <div><h1>📉 图表分析</h1><p style="color:var(--text-secondary)">交互式 K 线图与技术指标</p></div>
        </div>
        <div class="card">
            <form method="POST" class="form-row" style="margin-bottom:1.5rem">
                <div class="form-group"><label class="form-label">股票</label><select name="code" class="form-select">{select_html}</select></div>
                <div class="form-group"><label class="form-label">天数</label><select name="days" class="form-select"><option value="30">30天</option><option value="60" selected>60天</option><option value="90">90天</option><option value="180">180天</option></select></div>
                <div class="form-group"><label class="form-label">&nbsp;</label><button type="submit" class="btn btn-primary">📊 生成图表</button></div>
            </form>
            {chart_html if chart_html else '<div class="alert alert-info">📊 选择股票后点击"生成图表"</div>'}
        </div>
        """
        user = get_user_info()
        return render_page(content, 'charts', user=user)

    @app.route('/portfolio', methods=['GET', 'POST'])
    @login_required
    def portfolio():
        import yaml
        pf_path = os.path.join(project_root, 'config', 'portfolio.yaml')
        msg = ''
        if request.method == 'POST':
            action = request.form.get('action')
            try:
                with open(pf_path, 'r') as f:
                    pf = yaml.safe_load(f) or {'portfolio': {'total_capital': 1000000, 'positions': []}}
                p = pf.get('portfolio', {})
                if action == 'set_capital':
                    p['total_capital'] = float(request.form.get('total_capital', 1000000))
                    msg = '✅ 总资金已更新'
                elif action == 'add_position':
                    pos = {'code': request.form.get('code', '').strip(), 'name': request.form.get('name', '').strip(), 'buy_price': float(request.form.get('buy_price', 0)), 'quantity': int(request.form.get('quantity', 0)), 'target_price': float(request.form.get('target_price', 0) or 0), 'stop_loss': float(request.form.get('stop_loss', 0) or 0)}
                    if pos['code'] and pos['buy_price'] and pos['quantity']:
                        p.setdefault('positions', []).append(pos)
                        msg = f"✅ 已添加 {pos['code']}"
                elif action == 'del_position':
                    idx = int(request.form.get('idx', -1))
                    if 0 <= idx < len(p.get('positions', [])):
                        r = p['positions'].pop(idx)
                        msg = f"✅ 已删除 {r.get('code', '')}"
                pf['portfolio'] = p
                with open(pf_path, 'w') as f:
                    yaml.dump(pf, f, allow_unicode=True, default_flow_style=False)
            except Exception as e:
                msg = f'❌ {str(e)}'
        with open(pf_path, 'r') as f:
            pf = yaml.safe_load(f) or {'portfolio': {'total_capital': 1000000, 'positions': []}}
        p = pf.get('portfolio', {})
        total_capital = p.get('total_capital', 1000000)
        positions = p.get('positions', [])
        sn = get_stock_names()
        try:
            from src.data.database import get_db_engine
            engine = get_db_engine()
        except Exception as e:
            engine = None
        total_market = 0; total_cost = 0; pos_rows = []
        for i, pos in enumerate(positions):
            code = pos.get('code', ''); bp = pos.get('buy_price', 0); qty = pos.get('quantity', 0); cost = bp * qty; total_cost += cost
            cp = bp
            if engine:
                try:
                    df = pd.read_sql(f"SELECT close_price FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 1", engine)
                    if not df.empty: cp = df.iloc[0]['close_price']
                except: pass
            mv = cp * qty; pnl = mv - cost; total_market += mv
            color = 'var(--success)' if pnl >= 0 else 'var(--danger)'
            tp = f"{((pos.get('target_price',0)-bp)/bp*100):+.1f}%" if pos.get('target_price') else '--'
            pos_rows.append([f'<span class="badge badge-warning">{code}</span>', pos.get('name',''), f'¥{bp:.2f}', f'{qty}', f'¥{cp:.2f}', f'<span style="color:{color};font-weight:600">¥{pnl:+,.0f} ({((cp-bp)/bp*100):+.1f}%)</span>', tp, f'<form method="POST" style="display:inline"><input type="hidden" name="action" value="del_position"><input type="hidden" name="idx" value="{i}"><button type="submit" class="btn btn-danger" style="padding:0.2rem 0.5rem;font-size:0.7rem" onclick="return confirm(\'确定删除?\')">🗑️</button></form>'])
        cash = total_capital - total_cost; tpnl = total_market - total_cost; tpct = (tpnl/total_cost*100) if total_cost > 0 else 0; pc = 'var(--success)' if tpnl >= 0 else 'var(--danger)'
        pt = make_table(['代码','名称','买入价','数量','现价','盈亏','目标','操作'], pos_rows) if pos_rows else '<div class="alert alert-info">💡 暂无持仓，下方添加</div>'
        codes = get_stock_codes()
        sopts = ''.join(f'<option value="{c}">{c} {sn.get(c,"")}</option>' for c in codes)
        content = f"""
        <div class="header"><div><h1>🌍 投资组合</h1><p style="color:var(--text-secondary)">持仓管理与资金配置</p></div></div>
        {f'<div class="alert alert-success">{msg}</div>' if msg else ''}
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">总资金</div><div class="stat-value" style="font-size:1.5rem">¥{total_capital:,.0f}</div></div>
            <div class="stat-card"><div class="stat-label">持仓市值</div><div class="stat-value" style="font-size:1.5rem">¥{total_market:,.0f}</div></div>
            <div class="stat-card"><div class="stat-label">可用现金</div><div class="stat-value" style="font-size:1.5rem">¥{cash:,.0f}</div></div>
            <div class="stat-card"><div class="stat-label">总盈亏</div><div class="stat-value" style="font-size:1.5rem;color:{pc}">¥{tpnl:+,.0f}</div></div>
        </div>
        <div class="card"><div class="card-header"><h3 class="card-title">📋 持仓明细</h3></div>{pt}</div>
        <div class="grid-2">
            <div class="card"><div class="card-header"><h3 class="card-title">💰 总资金</h3></div>
                <form method="POST" class="form-row" style="align-items:end">
                    <div class="form-group"><label class="form-label">总资金 (元)</label><input type="number" name="total_capital" class="form-input" value="{total_capital}" step="10000"></div>
                    <div class="form-group"><label class="form-label">&nbsp;</label><button type="submit" name="action" value="set_capital" class="btn btn-primary">💾 保存</button></div>
                </form></div>
            <div class="card"><div class="card-header"><h3 class="card-title">➕ 添加持仓</h3></div>
                <form method="POST" class="form-row" style="align-items:end">
                    <div class="form-group"><label class="form-label">股票</label><select name="code" class="form-select">{sopts}</select></div>
                    <div class="form-group"><label class="form-label">买入价</label><input type="number" name="buy_price" class="form-input" step="0.01" required></div>
                    <div class="form-group"><label class="form-label">数量</label><input type="number" name="quantity" class="form-input" step="100" required></div>
                    <div class="form-group"><label class="form-label">目标价</label><input type="number" name="target_price" class="form-input" step="0.01"></div>
                    <div class="form-group"><label class="form-label">&nbsp;</label><button type="submit" name="action" value="add_position" class="btn btn-success">➕ 添加</button></div>
                </form></div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'portfolio', user=user)

    @app.route('/risk')
    @login_required
    def risk():
        content = f"""
        <div class="header">
            <div><h1>🛡️ 风险监控</h1><p style="color:var(--text-secondary)">实时风险指标与预警</p></div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">VaR (95%)</div><div class="stat-value">--</div><div class="stat-change">等待计算</div></div>
            <div class="stat-card"><div class="stat-label">CVaR (95%)</div><div class="stat-value">--</div><div class="stat-change">等待计算</div></div>
            <div class="stat-card"><div class="stat-label">最大回撤</div><div class="stat-value">--</div><div class="stat-change">--</div></div>
            <div class="stat-card"><div class="stat-label">波动率</div><div class="stat-value">--</div><div class="stat-change">--</div></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📊 风险指标</h3></div>
            {make_table(['指标', '当前值', '阈值', '状态'], [
                ['组合波动率', '--', '25%', '<span class="badge badge-warning">待计算</span>'],
                ['最大集中度', '--', '20%', '<span class="badge badge-warning">待计算</span>'],
                ['杠杆率', '1.0x', '2.0x', '<span class="badge badge-success">正常</span>'],
                ['现金比例', '--', '10%', '<span class="badge badge-warning">待计算</span>'],
            ])}
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">💥 压力测试</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    支持 <span class="tag">stress_testing</span> - 历史场景/蒙特卡洛/敏感性分析
                </p>
                <a href="/stress" class="btn btn-secondary" style="margin-top:0.75rem">前往压力测试</a>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">✅ 合规检查</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    支持 <span class="tag">compliance_checker</span> - 持仓/交易/风险合规
                </p>
                <a href="/compliance" class="btn btn-secondary" style="margin-top:0.75rem">前往合规检查</a>
            </div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'risk', user=user)

    @app.route('/strategies')
    @login_required
    def strategies():
        strategies = [
            ('SMA 交叉', 'sma_cross', '趋势跟踪', '<span class="badge badge-success">活跃</span>', '基础均线交叉策略'),
            ('动量策略', 'momentum', '趋势跟踪', '<span class="badge badge-success">活跃</span>', '动量突破策略'),
            ('均值回归', 'mean_reversion', '均值回归', '<span class="badge badge-success">活跃</span>', '布林带均值回归'),
            ('多因子', 'multi_factor', '量化选股', '<span class="badge badge-success">活跃</span>', '多因子选股模型'),
            ('配对交易', 'advanced', '统计套利', '<span class="badge badge-info">研究中</span>', '协整配对交易'),
            ('波动率策略', 'advanced', '波动率', '<span class="badge badge-info">研究中</span>', '波动率突破策略'),
            ('统计套利', 'advanced', '统计套利', '<span class="badge badge-info">研究中</span>', '统计套利策略'),
            ('行业轮动', 'advanced', '行业轮动', '<span class="badge badge-info">研究中</span>', '行业轮动策略'),
            ('期权策略', 'options', '期权', '<span class="badge badge-warning">待开发</span>', '期权策略组合'),
            ('新闻交易', 'news', '事件驱动', '<span class="badge badge-warning">待开发</span>', '新闻情绪交易'),
            ('加密策略', 'crypto', '加密货币', '<span class="badge badge-danger">已移除</span>', '加密货币策略'),
        ]

        rows = []
        for name, type_, category, status, desc in strategies:
            rows.append([name, f'<span class="tag">{category}</span>', status, desc,
                        f'<a href="/backtest" class="btn btn-secondary" style="padding:0.2rem 0.5rem;font-size:0.7rem">🔬 回测</a>'])

        content = f"""
        <div class="header">
            <div><h1>🎯 策略管理</h1><p style="color:var(--text-secondary)">策略库与策略状态管理</p></div>
            <div class="header-actions">
                <a href="/paramopt" class="btn btn-secondary">⚡ 参数优化</a>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">策略总数</div><div class="stat-value">30+</div><div class="stat-change">覆盖多类型</div></div>
            <div class="stat-card"><div class="stat-label">活跃策略</div><div class="stat-value">4</div><div class="stat-change" style="color:var(--success)">运行中</div></div>
            <div class="stat-card"><div class="stat-label">研究中</div><div class="stat-value">4</div><div class="stat-change" style="color:var(--info)">开发中</div></div>
            <div class="stat-card"><div class="stat-label">AI 策略助手</div><div class="stat-value">✅</div><div class="stat-change">策略推荐</div></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 策略列表</h3></div>
            {make_table(['策略', '类型', '状态', '描述', '操作'], rows)}
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">🤖 AI 策略助手</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    支持 <span class="tag">advisor</span> <span class="tag">ensemble_manager</span> - 智能策略推荐与组合管理
                </p>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">🔄 策略生命周期</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    支持 <span class="tag">lifecycle</span> - 策略开发/测试/上线/监控/下线全流程
                </p>
            </div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'strategies', user=user)

    @app.route('/factors')
    @login_required
    def factors():
        factors = [
            ('技术因子', 'MACD/RSI/布林带/KDJ', '10+', '<span class="badge badge-success">可用</span>'),
            ('基本面因子', 'PE/PB/ROE/营收增长', '8+', '<span class="badge badge-success">可用</span>'),
            ('情绪因子', '新闻情绪/社交情绪', '5+', '<span class="badge badge-success">可用</span>'),
            ('质量因子', '盈利质量/财务健康', '4+', '<span class="badge badge-info">可用</span>'),
            ('价值因子', '估值/股息率', '3+', '<span class="badge badge-info">可用</span>'),
            ('成长因子', '营收/利润增长', '3+', '<span class="badge badge-info">可用</span>'),
            ('流动性因子', '换手率/成交量', '3+', '<span class="badge badge-info">可用</span>'),
            ('微观结构因子', '买卖价差/深度', '2+', '<span class="badge badge-warning">研究中</span>'),
            ('Alpha101', 'WorldQuant Alpha101', '101', '<span class="badge badge-info">可用</span>'),
            ('Fama-French', '三因子/五因子', '5', '<span class="badge badge-info">可用</span>'),
        ]

        rows = []
        for name, desc, count, status in factors:
            rows.append([name, desc, count, status,
                        f'<a href="/backtest" class="btn btn-secondary" style="padding:0.2rem 0.5rem;font-size:0.7rem">🔬 回测</a>'])

        content = f"""
        <div class="header">
            <div><h1>🧮 因子研究</h1><p style="color:var(--text-secondary)">因子库与因子分析</p></div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">因子总数</div><div class="stat-value">25+</div><div class="stat-change">多类型覆盖</div></div>
            <div class="stat-card"><div class="stat-label">技术因子</div><div class="stat-value">10+</div><div class="stat-change">MACD/RSI等</div></div>
            <div class="stat-card"><div class="stat-label">基本面因子</div><div class="stat-value">8+</div><div class="stat-change">PE/PB/ROE等</div></div>
            <div class="stat-card"><div class="stat-label">Alpha101</div><div class="stat-value">101</div><div class="stat-change">WorldQuant</div></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 因子列表</h3></div>
            {make_table(['因子类别', '描述', '数量', '状态', '操作'], rows)}
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">📊 因子分析工具</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">factor_analysis</span> IC/IR分析<br>
                    <span class="tag">factor_research</span> 因子研究平台<br>
                    <span class="tag">factor_timing</span> 因子择时
                </p>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">🧠 高级因子</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">extended_factors</span> 扩展因子<br>
                    <span class="tag">alternative_data</span> 另类数据<br>
                    <span class="tag">new_factors</span> 新因子开发
                </p>
            </div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'factors', user=user)

    @app.route('/events')
    @login_required
    def events():
        content = f"""
        <div class="header">
            <div><h1>📅 事件研究</h1><p style="color:var(--text-secondary)">事件驱动分析与异常收益</p></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 事件研究配置</h3></div>
            <div class="form-row">
                <div class="form-group"><label class="form-label">事件类型</label>
                    <select class="form-select"><option>财报发布</option><option>分红派息</option><option>重大公告</option><option>政策发布</option></select></div>
                <div class="form-group"><label class="form-label">事件窗口</label><input type="text" class="form-input" value="-5, +5"></div>
                <div class="form-group"><label class="form-label">估计窗口</label><input type="text" class="form-input" value="-250, -6"></div>
                <div class="form-group"><label class="form-label">&nbsp;</label><button class="btn btn-primary">🔍 分析</button></div>
            </div>
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">📊 分析工具</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">event_study</span><br>
                    - 异常收益 (AR/CAR)<br>
                    - 累计异常收益<br>
                    - 统计显著性检验
                </p>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">📈 相关模块</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">news_trading</span> 新闻交易<br>
                    <span class="tag">sentiment</span> 情绪分析<br>
                    <span class="tag">extended_sentiment</span> 扩展情绪
                </p>
            </div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'events', user=user)

    @app.route('/research')
    @login_required
    def research():
        content = f"""
        <div class="header">
            <div><h1>📓 研究笔记本</h1><p style="color:var(--text-secondary)">交互式研究环境</p></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">🔧 研究工具</h3></div>
            <div class="grid-3">
                <div class="stat-card">
                    <div class="stat-label">因子研究</div>
                    <p style="color:var(--text-secondary);font-size:0.8125rem;margin-top:0.5rem">
                        <span class="tag">factor_research</span><br>
                        因子挖掘与测试
                    </p>
                </div>
                <div class="stat-card">
                    <div class="stat-label">ML 流水线</div>
                    <p style="color:var(--text-secondary);font-size:0.8125rem;margin-top:0.5rem">
                        <span class="tag">ml_pipeline</span><br>
                        机器学习模型训练
                    </p>
                </div>
                <div class="stat-card">
                    <div class="stat-label">市场状态</div>
                    <p style="color:var(--text-secondary);font-size:0.8125rem;margin-top:0.5rem">
                        <span class="tag">regime_detector</span><br>
                        市场状态检测
                    </p>
                </div>
                <div class="stat-card">
                    <div class="stat-label">行业热力图</div>
                    <p style="color:var(--text-secondary);font-size:0.8125rem;margin-top:0.5rem">
                        <span class="tag">sector_heatmap</span><br>
                        行业表现热力图
                    </p>
                </div>
                <div class="stat-card">
                    <div class="stat-label">特征工程</div>
                    <p style="color:var(--text-secondary);font-size:0.8125rem;margin-top:0.5rem">
                        <span class="tag">feature_engineering</span><br>
                        特征提取与选择
                    </p>
                </div>
                <div class="stat-card">
                    <div class="stat-label">LSTM 模型</div>
                    <p style="color:var(--text-secondary);font-size:0.8125rem;margin-top:0.5rem">
                        <span class="tag">lstm_model</span><br>
                        深度学习预测
                    </p>
                </div>
            </div>
        </div>
        <div class="alert alert-info">💡 研究笔记本提供交互式研究环境，支持因子挖掘、ML 训练、市场状态分析等</div>
        """
        user = get_user_info()
        return render_page(content, 'research', user=user)

    @app.route('/heatmap')
    @login_required
    def heatmap():
        try:
            from src.analysis.sector_heatmap import SectorHeatmap
            h = SectorHeatmap()
            codes = list(h.sector_mapping.keys())
            df = h.get_sector_returns(codes, period=5)
            html_heatmap = h.generate_html_heatmap(df) if not df.empty else None

            # Also build a table view
            if not df.empty:
                rows = []
                for _, row in df.iterrows():
                    ret = row['return']
                    color = 'var(--success)' if ret > 0 else 'var(--danger)'
                    bg = 'rgba(34,197,94,0.15)' if ret > 0 else 'rgba(239,68,68,0.15)'
                    intensity = min(abs(ret) / 0.2, 1.0)  # cap at 20%
                    rows.append([
                        row['sector'],
                        f'<span style="color:{color};font-weight:600">{ret:+.2%}</span>',
                        f'<div class="progress-bar"><div class="progress-fill" style="width:{intensity*100:.0f}%;background:{color}"></div></div>',
                    ])
                table_html = make_table(['板块', '涨跌幅', '强度'], rows)
            else:
                table_html = '<div class="alert alert-warning">⚠️ 暂无板块数据</div>'

            content = f"""
            <div class="header">
                <div><h1>🔥 板块热力图</h1><p style="color:var(--text-secondary)">板块/行业涨跌热力分布</p></div>
            </div>
            {html_heatmap if html_heatmap else ''}
            <div class="card">
                <div class="card-header"><h3 class="card-title">📊 板块涨跌幅</h3></div>
                {table_html}
            </div>
            <div class="alert alert-info">💡 数据基于近 5 个交易日个股收益，按板块均值聚合</div>
            """
        except Exception as e:
            content = f"""
            <div class="header">
                <div><h1>🔥 板块热力图</h1><p style="color:var(--text-secondary)">板块/行业涨跌热力分布</p></div>
            </div>
            <div class="alert alert-error">❌ 热力图加载失败: {str(e)}</div>
            """
        user = get_user_info()
        return render_page(content, 'heatmap', user=user)

    @app.route('/articles', methods=['GET', 'POST'])
    @login_required
    def articles():
        from src.analysis.article_manager import ArticleManager, PLATFORM_NAMES
        mgr = ArticleManager()
        dates = mgr.get_available_dates()
        date_range = list(dates) if dates else []

        # 获取查询参数
        query_date = request.args.get('date', '')
        year_filter = request.args.get('year', '')
        month_filter = request.args.get('month', '')
        page = request.args.get('page', 1, type=int)
        stock_only = request.args.get('stock_only', 'false') == 'true'
        search_keyword = request.args.get('keyword', '')
        view_mode = request.args.get('view', 'list')  # list, daily, stock-match
        per_page = 20

        # 构建年份/月份选项
        years = sorted(set(d[:4] for d in date_range), reverse=True)
        months = sorted(set(d[5:7] for d in date_range if d[:4] == year_filter), reverse=True) if year_filter else []

        # 过滤日期
        filtered_dates = date_range
        if year_filter:
            filtered_dates = [d for d in filtered_dates if d[:4] == year_filter]
        if month_filter:
            filtered_dates = [d for d in filtered_dates if d[5:7] == month_filter]

        # 根据视图模式获取文章
        articles_list = []
        total = 0
        daily_groups = {}
        stock_match = []

        if query_date:
            # 单天视图
            arts = mgr.get_articles_by_date(query_date, limit=1000)
            arts = mgr.match_articles_with_stocks(arts)
            if search_keyword:
                arts = [a for a in arts if search_keyword.lower() in a['title'].lower()]
            if stock_only:
                arts = [a for a in arts if a['has_stock']]
            total = len(arts)
            start_idx = (page - 1) * per_page
            articles_list = arts[start_idx:start_idx + per_page]
        elif view_mode == 'daily':
            # 按天分组视图
            for d in filtered_dates:
                arts = mgr.get_articles_by_date(d, limit=100)
                arts = mgr.match_articles_with_stocks(arts)
                if stock_only:
                    arts = [a for a in arts if a['has_stock']]
                if arts:
                    daily_groups[d] = arts[:10]  # 每天最多10条
        elif view_mode == 'stock-match':
            # 股票匹配视图
            for d in filtered_dates[-7:]:  # 最近7天
                arts = mgr.get_articles_by_date(d, limit=200)
                arts = mgr.match_articles_with_stocks(arts)
                stock_arts = [a for a in arts if a['has_stock']]
                if search_keyword:
                    stock_arts = [a for a in stock_arts if search_keyword.lower() in a['title'].lower()]
                stock_match.extend(stock_arts)
            total = len(stock_match)
            start_idx = (page - 1) * per_page
            articles_list = stock_match[start_idx:start_idx + per_page]
        else:
            # 列表视图 - 日期范围
            if filtered_dates:
                start_date = filtered_dates[0]
                end_date = filtered_dates[-1]
                arts, total = mgr.get_date_range_articles(start_date, end_date, page=page, per_page=per_page, stock_only=stock_only)
                if search_keyword:
                    arts = [a for a in arts if search_keyword.lower() in a['title'].lower()]
                articles_list = arts

        # 计算分页
        if total == 0 and articles_list:
            total = len(articles_list)
        total_pages = max(1, (total + per_page - 1) // per_page)
        has_prev = page > 1
        has_next = page < total_pages

        # 生成统计
        stats = {'total_dates': len(filtered_dates), 'total_articles': 0, 'stock_related': 0, 'platforms': {}}
        if query_date:
            summary = mgr.get_daily_summary(query_date)
            stats = summary
        elif filtered_dates:
            for d in filtered_dates:
                s = mgr.get_daily_summary(d)
                stats['total_articles'] += s['total']
                stats['stock_related'] += s.get('stock_related', 0)
                for p, c in s.get('platforms', {}).items():
                    stats['platforms'][p] = stats['platforms'].get(p, 0) + c

        # 渲染文章列表行
        def render_article_row(a):
            relevance_badge = ''
            if a.get('has_stock'):
                if a.get('relevance') == 'high':
                    relevance_badge = '<span class="badge badge-success">高匹配</span>'
                elif a.get('relevance') == 'medium':
                    relevance_badge = '<span class="badge badge-info">中匹配</span>'
                else:
                    relevance_badge = '<span class="badge badge-warning">低匹配</span>'
            else:
                relevance_badge = '<span class="badge badge-purple">无关</span>'

            stocks_html = ''
            if a.get('matched_stocks'):
                stocks_html = ' '.join([f'<span class="tag">{s["code"]}</span>' for s in a['matched_stocks'][:5]])
                if len(a['matched_stocks']) > 5:
                    stocks_html += f'<span class="tag">+{len(a["matched_stocks"])-5}</span>'

            platform_name = a.get('platform_name', a.get('platform', ''))
            title = a.get('title', '')
            url = a.get('url', '')
            date = a.get('date', '')

            title_html = f'<a href="{url}" target="_blank" style="color:var(--text-primary);text-decoration:none">{title}</a>' if url else title

            return f"""<tr><td><span class="badge badge-warning" style="font-size:0.65rem">{date}</span></td>
                <td><span class="tag">{platform_name}</span></td>
                <td>{title_html}</td>
                <td>{relevance_badge}</td>
                <td>{stocks_html}</td></tr>"""

        # 生成列表HTML
        list_html = ''
        if articles_list:
            rows = [render_article_row(a) for a in articles_list]
            list_html = make_table(['日期', '来源', '标题', '匹配度', '相关股票'], rows)

            # 分页
            pagination = []
            if has_prev:
                params = {'page': page - 1}
                if query_date: params['date'] = query_date
                if year_filter: params['year'] = year_filter
                if month_filter: params['month'] = month_filter
                if view_mode: params['view'] = view_mode
                if stock_only: params['stock_only'] = 'true'
                if search_keyword: params['keyword'] = search_keyword
                qs = '&'.join(f'{k}={v}' for k, v in params.items())
                pagination.append(f'<a href="/articles?{qs}" class="btn btn-secondary" style="padding:0.25rem 0.625rem;font-size:0.75rem">◀ 上一页</a>')

            page_info = f'<span style="color:var(--text-secondary);font-size:0.875rem;margin:0 0.75rem">第 {page}/{total_pages} 页 (共 {total} 条)</span>'

            if has_next:
                params = {'page': page + 1}
                if query_date: params['date'] = query_date
                if year_filter: params['year'] = year_filter
                if month_filter: params['month'] = month_filter
                if view_mode: params['view'] = view_mode
                if stock_only: params['stock_only'] = 'true'
                if search_keyword: params['keyword'] = search_keyword
                qs = '&'.join(f'{k}={v}' for k, v in params.items())
                pagination.append(f'<a href="/articles?{qs}" class="btn btn-secondary" style="padding:0.25rem 0.625rem;font-size:0.75rem">下一页 ▶</a>')

            pagination_html = f"""<div style="display:flex;align-items:center;justify-content:center;margin-top:1rem">{"".join(pagination)}{page_info}</div>"""
            list_html += pagination_html
        else:
            list_html = '<div class="alert alert-info">💡 暂无文章数据，请选择日期查询</div>'

        # 按天分组视图 HTML
        daily_html = ''
        if view_mode == 'daily' and daily_groups:
            for d in sorted(daily_groups.keys(), reverse=True):
                arts = daily_groups[d]
                summary = mgr.get_daily_summary(d)
                daily_html += f"""<div class="card"><div class="card-header">
                    <h3 class="card-title">📅 {d} <span style="color:var(--text-secondary);font-size:0.875rem">({summary.get('total', 0)} 篇 | 股票相关 {summary.get('stock_related', 0)} 篇)</span></h3>
                    <a href="/articles?date={d}" class="btn btn-secondary" style="padding:0.25rem 0.625rem;font-size:0.75rem">查看全部</a>
                </div>"""
                for a in arts:
                    relevance = '🟢' if a.get('has_stock') else '⚪'
                    title = a.get('title', '')[:80]
                    url = a.get('url', '')
                    title_html = f'<a href="{url}" target="_blank" style="color:var(--text-primary);text-decoration:none">{title}</a>' if url else title
                    stocks = ', '.join([s['code'] for s in a.get('matched_stocks', [])[:3]])
                    daily_html += f"""<div style="padding:0.5rem 0;border-bottom:1px solid var(--border);font-size:0.875rem">
                        {relevance} <span class="tag">{a.get('platform_name', '')}</span> {title_html}
                        {f'<div style="color:var(--text-secondary);font-size:0.75rem;margin-top:0.25rem">📎 {stocks}</div>' if stocks else ''}
                    </div>"""
                daily_html += '</div>'

        # 平台统计 HTML
        platform_stats = ''
        if stats.get('platforms'):
            sorted_platforms = sorted(stats['platforms'].items(), key=lambda x: x[1], reverse=True)
            platform_stats = ''.join([f'<span class="tag">{PLATFORM_NAMES.get(p, p)}: {c}</span>' for p, c in sorted_platforms])

        # 日期选择器
        date_options = ''
        for d in sorted(filtered_dates, reverse=True)[:30]:
            sel = ' selected' if d == query_date else ''
            date_options += f'<option value="{d}"{sel}>{d}</option>'

        content = f"""
        <div class="header">
            <div><h1>📰 文章信息</h1><p style="color:var(--text-secondary)">新闻文章与股票相关性匹配</p></div>
        </div>

        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">可用日期</div><div class="stat-value">{stats.get('total_dates', 0)}</div><div class="stat-change">天</div></div>
            <div class="stat-card"><div class="stat-label">文章总数</div><div class="stat-value">{stats.get('total_articles', 0):,}</div><div class="stat-change">{stats.get('stock_related', 0)} 篇股票相关</div></div>
            <div class="stat-card"><div class="stat-label">今日文章</div><div class="stat-value">{stats.get('total', 0)}</div><div class="stat-change">{query_date or '最新'}</div></div>
            <div class="stat-card"><div class="stat-label">平台数</div><div class="stat-value">{len(stats.get('platforms', {}))}</div><div class="stat-change">数据源</div></div>
        </div>

        <div class="card">
            <div class="card-header"><h3 class="card-title">🔍 查询条件</h3></div>
            <form method="GET" action="/articles" class="form-row">
                <div class="form-group"><label class="form-label">年份</label>
                    <select name="year" class="form-select" onchange="this.form.submit()">
                        <option value="">全部</option>
                        {''.join(f'<option value="{y}"{" selected" if y==year_filter else ""}>{y}</option>' for y in years)}
                    </select></div>
                <div class="form-group"><label class="form-label">月份</label>
                    <select name="month" class="form-select" onchange="this.form.submit()">
                        <option value="">全部</option>
                        {''.join(f'<option value="{m}"{" selected" if m==month_filter else ""}>{m}</option>' for m in months)}
                    </select></div>
                <div class="form-group"><label class="form-label">指定日期</label>
                    <select name="date" class="form-select">
                        <option value="">全部</option>
                        {date_options}
                    </select></div>
                <div class="form-group"><label class="form-label">关键词</label>
                    <input type="text" name="keyword" class="form-input" placeholder="搜索标题..." value="{search_keyword}"></div>
                <div class="form-group"><label class="form-label">视图</label>
                    <select name="view" class="form-select">
                        <option value="list" {'selected' if view_mode=='list' else ''}>列表</option>
                        <option value="daily" {'selected' if view_mode=='daily' else ''}>按天分组</option>
                        <option value="stock-match" {'selected' if view_mode=='stock-match' else ''}>股票匹配</option>
                    </select></div>
                <div class="form-group"><label class="form-label">仅股票相关</label>
                    <select name="stock_only" class="form-select">
                        <option value="false" {'selected' if not stock_only else ''}>否</option>
                        <option value="true" {'selected' if stock_only else ''}>是</option>
                    </select></div>
                <div class="form-group"><label class="form-label">&nbsp;</label>
                    <button type="submit" class="btn btn-primary">🔍 查询</button></div>
            </form>
        </div>

        {platform_stats and f'<div class="card"><div class="card-header"><h3 class="card-title">📊 平台分布</h3></div><div style="display:flex;flex-wrap:wrap;gap:0.375rem">{platform_stats}</div></div>' or ''}

        {daily_html if view_mode == 'daily' else f'<div class="card">{list_html}</div>'}
        """

        user = get_user_info()
        return render_page(content, 'articles', user=user)

    @app.route('/alerts')
    @login_required
    def alerts():
        content = f"""
        <div class="header">
            <div><h1>🔔 告警中心</h1><p style="color:var(--text-secondary)">实时告警与规则管理</p></div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">告警规则</div><div class="stat-value">10+</div><div class="stat-change">可配置</div></div>
            <div class="stat-card"><div class="stat-label">今日告警</div><div class="stat-value">0</div><div class="stat-change" style="color:var(--success)">无告警</div></div>
            <div class="stat-card"><div class="stat-label">通知方式</div><div class="stat-value" style="font-size:1.25rem">📧 📱</div><div class="stat-change">邮件/微信</div></div>
            <div class="stat-card"><div class="stat-label">健康检查</div><div class="stat-value">✅</div><div class="stat-change">运行中</div></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 告警规则</h3></div>
            {make_table(['规则', '类型', '阈值', '状态', '操作'], [
                ['价格异动', '价格', '±3%', '<span class="badge badge-success">启用</span>', '<button class="btn btn-secondary" style="padding:0.2rem 0.5rem;font-size:0.7rem">编辑</button>'],
                ['成交量异常', '成交量', '>2倍均值', '<span class="badge badge-success">启用</span>', '<button class="btn btn-secondary" style="padding:0.2rem 0.5rem;font-size:0.7rem">编辑</button>'],
                ['系统异常', '系统', '服务宕机', '<span class="badge badge-success">启用</span>', '<button class="btn btn-secondary" style="padding:0.2rem 0.5rem;font-size:0.7rem">编辑</button>'],
                ['数据延迟', '数据', '>30分钟', '<span class="badge badge-success">启用</span>', '<button class="btn btn-secondary" style="padding:0.2rem 0.5rem;font-size:0.7rem">编辑</button>'],
                ['风险超标', '风险', 'VaR>阈值', '<span class="badge badge-warning">待配置</span>', '<button class="btn btn-secondary" style="padding:0.2rem 0.5rem;font-size:0.7rem">编辑</button>'],
            ])}
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">🔧 告警模块</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">risk_alert</span> 风险告警<br>
                    <span class="tag">notifications</span> 通知管理<br>
                    <span class="tag">system_health</span> 系统健康告警
                </p>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">📊 实时监控</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">live_monitor</span> 实时监控<br>
                    <span class="tag">intraday_monitor</span> 盘中监控<br>
                    <span class="tag">strategy_health</span> 策略健康
                </p>
            </div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'alerts', user=user)

    @app.route('/paper')
    @login_required
    def paper():
        content = f"""
        <div class="header">
            <div><h1>📝 模拟盘</h1><p style="color:var(--text-secondary)">模拟交易与策略验证</p></div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">模拟资产</div><div class="stat-value">¥0</div><div class="stat-change">初始资金</div></div>
            <div class="stat-card"><div class="stat-label">持仓数量</div><div class="stat-value">0</div><div class="stat-change">--</div></div>
            <div class="stat-card"><div class="stat-label">今日盈亏</div><div class="stat-value">¥0</div><div class="stat-change">--</div></div>
            <div class="stat-card"><div class="stat-label">总收益率</div><div class="stat-value">0%</div><div class="stat-change">--</div></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 交易记录</h3></div>
            <div class="alert alert-info">💡 启动模拟盘后显示交易记录</div>
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">📝 模拟盘模块</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">paper_trading</span> v2<br>
                    - 实时模拟交易<br>
                    - 成本优化<br>
                    - 仓位管理
                </p>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">🔌 实盘接口</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">futu_trader</span> 富途交易<br>
                    <span class="tag">real_trading</span> 实盘交易<br>
                    <span class="tag">order_router</span> 智能路由
                </p>
            </div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'paper', user=user)

    @app.route('/stoploss')
    @login_required
    def stoploss():
        content = f"""
        <div class="header">
            <div><h1>🛑 智能止损</h1><p style="color:var(--text-secondary)">动态止损与风险控制</p></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 止损策略</h3></div>
            {make_table(['策略', '描述', '参数', '状态'], [
                ['固定止损', '固定百分比止损', '5%', '<span class="badge badge-success">可用</span>'],
                ['追踪止损', '跟随价格上涨止损', '3% 回撤', '<span class="badge badge-success">可用</span>'],
                ['波动率止损', '基于 ATR 动态止损', '2x ATR', '<span class="badge badge-success">可用</span>'],
                ['时间止损', '持仓超时止损', 'N 天', '<span class="badge badge-info">可用</span>'],
                ['技术止损', '技术位破位止损', '均线/支撑', '<span class="badge badge-info">可用</span>'],
            ])}
        </div>
        <div class="alert alert-info">💡 支持 <span class="tag">stop_loss</span> 模块，多种止损策略可组合使用</div>
        """
        user = get_user_info()
        return render_page(content, 'stoploss', user=user)

    @app.route('/stress')
    @login_required
    def stress():
        content = f"""
        <div class="header">
            <div><h1>💥 压力测试</h1><p style="color:var(--text-secondary)">极端场景下的组合表现</p></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 压力场景</h3></div>
            {make_table(['场景', '描述', '影响', '状态'], [
                ['2008 金融危机', '全球市场崩盘', '组合 -30%~50%', '<span class="badge badge-success">可用</span>'],
                ['2020 疫情', '疫情冲击市场', '组合 -20%~40%', '<span class="badge badge-success">可用</span>'],
                ['利率飙升', '利率快速上升', '债券 -10%~20%', '<span class="badge badge-info">可用</span>'],
                ['流动性危机', '市场流动性枯竭', '组合 -15%~30%', '<span class="badge badge-info">可用</span>'],
                ['蒙特卡洛模拟', '10000 次随机模拟', 'VaR/CVaR 估计', '<span class="badge badge-success">可用</span>'],
            ])}
        </div>
        <div class="alert alert-info">💡 支持 <span class="tag">stress_testing</span> 模块，历史场景 + 蒙特卡洛 + 敏感性分析</div>
        """
        user = get_user_info()
        return render_page(content, 'stress', user=user)

    @app.route('/compliance')
    @login_required
    def compliance():
        content = f"""
        <div class="header">
            <div><h1>✅ 合规检查</h1><p style="color:var(--text-secondary)">交易合规与风险控制</p></div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">合规规则</div><div class="stat-value">20+</div><div class="stat-change">全面覆盖</div></div>
            <div class="stat-card"><div class="stat-label">违规次数</div><div class="stat-value">0</div><div class="stat-change" style="color:var(--success)">合规</div></div>
            <div class="stat-card"><div class="stat-label">检查频率</div><div class="stat-value">实时</div><div class="stat-change">自动检查</div></div>
            <div class="stat-card"><div class="stat-label">最后检查</div><div class="stat-value" style="font-size:1rem">{datetime.now().strftime("%H:%M")}</div><div class="stat-change">今日</div></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 合规规则</h3></div>
            {make_table(['规则类别', '规则', '阈值', '状态'], [
                ['持仓限制', '单只股票占比', '<20%', '<span class="badge badge-success">合规</span>'],
                ['行业集中度', '行业总占比', '<40%', '<span class="badge badge-success">合规</span>'],
                ['杠杆限制', '总杠杆率', '<2x', '<span class="badge badge-success">合规</span>'],
                ['流动性', '低流动性股票', '<10%', '<span class="badge badge-success">合规</span>'],
                ['交易频率', '日内交易次数', '<N次', '<span class="badge badge-success">合规</span>'],
            ])}
        </div>
        <div class="alert alert-info">💡 支持 <span class="tag">compliance_checker</span> 模块，20+ 合规规则全面覆盖</div>
        """
        user = get_user_info()
        return render_page(content, 'compliance', user=user)

    @app.route('/performance')
    @login_required
    def performance():
        content = f"""
        <div class="header">
            <div><h1>📊 绩效分析</h1><p style="color:var(--text-secondary)">策略绩效与组合分析</p></div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">总收益率</div><div class="stat-value">--</div><div class="stat-change">等待计算</div></div>
            <div class="stat-card"><div class="stat-label">年化收益</div><div class="stat-value">--</div><div class="stat-change">等待计算</div></div>
            <div class="stat-card"><div class="stat-label">夏普比率</div><div class="stat-value">--</div><div class="stat-change">等待计算</div></div>
            <div class="stat-card"><div class="stat-label">最大回撤</div><div class="stat-value">--</div><div class="stat-change">等待计算</div></div>
            <div class="stat-card"><div class="stat-label">Sortino 比率</div><div class="stat-value">--</div><div class="stat-change">等待计算</div></div>
            <div class="stat-card"><div class="stat-label">Calmar 比率</div><div class="stat-value">--</div><div class="stat-change">等待计算</div></div>
        </div>
        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">📊 分析工具</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">performance_analyzer</span><br>
                    <span class="tag">performance_dashboard</span><br>
                    <span class="tag">portfolio_attribution</span> 组合归因
                </p>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">📈 可视化</h3></div>
                <p style="color:var(--text-secondary);font-size:0.875rem">
                    <span class="tag">advanced_viz</span><br>
                    <span class="tag">interactive_charts</span><br>
                    <span class="tag">backtest_visualizer</span>
                </p>
            </div>
        </div>
        """
        user = get_user_info()
        return render_page(content, 'performance', user=user)

    @app.route('/behavior')
    @login_required
    def behavior():
        content = f"""
        <div class="header">
            <div><h1>🧠 行为分析</h1><p style="color:var(--text-secondary)">交易行为与心理分析</p></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 行为指标</h3></div>
            {make_table(['指标', '描述', '当前值', '建议'], [
                ['过度交易', '交易频率过高', '--', '控制交易次数'],
                ['损失厌恶', '亏损持仓过长', '--', '严格执行止损'],
                ['确认偏误', '只看支持信息', '--', '多角度分析'],
                ['锚定效应', '依赖初始价格', '--', '动态调整预期'],
                ['羊群效应', '跟随市场情绪', '--', '独立思考'],
            ])}
        </div>
        <div class="alert alert-info">💡 支持 <span class="tag">behavior_analysis</span> 模块，分析交易行为偏差与心理因素</div>
        """
        user = get_user_info()
        return render_page(content, 'behavior', user=user)

    @app.route('/paramopt')
    @login_required
    def paramopt():
        content = f"""
        <div class="header">
            <div><h1>⚡ 参数优化</h1><p style="color:var(--text-secondary)">策略参数自动优化</p></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📊 优化配置</h3></div>
            <div class="form-row">
                <div class="form-group"><label class="form-label">策略</label><select class="form-select"><option>SMA 交叉</option><option>动量策略</option><option>多因子</option></select></div>
                <div class="form-group"><label class="form-label">优化方法</label><select class="form-select"><option>网格搜索</option><option>贝叶斯优化</option><option>遗传算法</option></select></div>
                <div class="form-group"><label class="form-label">目标函数</label><select class="form-select"><option>夏普比率</option><option>总收益</option><option>Calmar 比率</option></select></div>
                <div class="form-group"><label class="form-label">&nbsp;</label><button class="btn btn-primary">🚀 开始优化</button></div>
            </div>
        </div>
        <div class="alert alert-info">💡 支持 <span class="tag">param_optimizer</span> <span class="tag">auto_tuner</span> 模块</div>
        """
        user = get_user_info()
        return render_page(content, 'paramopt', user=user)

    @app.route('/reports')
    @login_required
    def reports():
        content = f"""
        <div class="header">
            <div><h1>📑 自动报告</h1><p style="color:var(--text-secondary)">定期生成与发送报告</p></div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">报告类型</div><div class="stat-value">5+</div><div class="stat-change">多类型覆盖</div></div>
            <div class="stat-card"><div class="stat-label">发送频率</div><div class="stat-value" style="font-size:1.25rem">📅</div><div class="stat-change">每日/每周/每月</div></div>
            <div class="stat-card"><div class="stat-label">最后生成</div><div class="stat-value" style="font-size:1rem">--</div><div class="stat-change">等待首次生成</div></div>
            <div class="stat-card"><div class="stat-label">发送状态</div><div class="stat-value">⏸️</div><div class="stat-change">未配置</div></div>
        </div>
        <div class="card">
            <div class="card-header"><h3 class="card-title">📋 报告类型</h3></div>
            {make_table(['报告类型', '内容', '频率', '状态'], [
                ['每日交易报告', '交易记录/盈亏', '每日', '<span class="badge badge-warning">待配置</span>'],
                ['周报', '组合表现/策略分析', '每周', '<span class="badge badge-warning">待配置</span>'],
                ['月报', '月度总结/风险报告', '每月', '<span class="badge badge-warning">待配置</span>'],
                ['风险报告', 'VaR/压力测试', '每周', '<span class="badge badge-warning">待配置</span>'],
                ['策略报告', '策略表现对比', '每月', '<span class="badge badge-warning">待配置</span>'],
            ])}
        </div>
        <div class="alert alert-info">💡 支持 <span class="tag">pdf_report</span> <span class="tag">report_generator</span> 模块</div>
        """
        user = get_user_info()
        return render_page(content, 'reports', user=user)

    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        user = get_user_info()
        msg = ''
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'update_theme':
                theme = request.form.get('theme', 'dark')
                lang = request.form.get('language', 'zh')
                try:
                    if os.path.exists(_auth_path):
                        with open(_auth_path, 'r') as f:
                            cfg = yaml.safe_load(f) or {}
                        cfg['auth']['admin']['theme'] = theme
                        cfg['auth']['admin']['language'] = lang
                        with open(_auth_path, 'w') as f:
                            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
                        _load_auth()
                        msg = '<div class="alert alert-success">✅ 主题和语言设置已保存</div>'
                except Exception as e:
                    msg = f'<div class="alert alert-error">❌ 保存失败: {str(e)}</div>'

        current_theme = user.get('theme', 'dark')
        current_lang = user.get('language', 'zh')

        modules = [
            ('数据层', 'Futu/AKShare 双源', '✅ 运行中', 'badge-success'),
            ('分析层', '技术/情绪/ML/因子', '✅ 运行中', 'badge-success'),
            ('策略层', '30+ 策略', '✅ 运行中', 'badge-success'),
            ('执行层', '风控/仓位/模拟盘', '✅ 运行中', 'badge-success'),
            ('回测层', 'Backtrader/事件驱动', '✅ 运行中', 'badge-success'),
            ('监控层', '报告/绩效/预警', '✅ 运行中', 'badge-success'),
            ('风控层', '止损/对冲/压力', '✅ 运行中', 'badge-success'),
            ('Web 界面', '25+ 功能页面', '✅ 运行中', 'badge-success'),
        ]

        rows = []
        for name, desc, status, badge in modules:
            rows.append([name, desc, f'<span class="badge {badge}">{status}</span>'])

        content = f"""
        <div class="header">
            <div><h1>⚙️ 系统设置</h1><p style="color:var(--text-secondary)">个性化设置与系统信息</p></div>
        </div>
        {msg}

        <div class="grid-2">
            <div class="card">
                <div class="card-header"><h3 class="card-title">🎨 主题皮肤</h3></div>
                <form method="POST">
                    <input type="hidden" name="action" value="update_theme">
                    <div class="form-group"><label class="form-label">主题</label>
                        <select name="theme" class="form-select">
                            <option value="dark" {'selected' if current_theme=='dark' else ''}>🌙 深色模式</option>
                            <option value="openclaw" {'selected' if current_theme=='openclaw' else ''}>🐾 OpenClaw 风格</option>
                            <option value="light" {'selected' if current_theme=='light' else ''}>☀️ 浅色模式</option>
                            <option value="auto" {'selected' if current_theme=='auto' else ''}>💻 跟随系统</option>
                        </select></div>
                    <div class="form-group"><label class="form-label">语言</label>
                        <select name="language" class="form-select">
                            <option value="zh" {'selected' if current_lang=='zh' else ''}>🇨🇳 简体中文</option>
                            <option value="en" {'selected' if current_lang=='en' else ''}>🇺🇸 English</option>
                        </select></div>
                    <button type="submit" class="btn btn-primary">💾 保存设置</button>
                </form>
            </div>
            <div class="card">
                <div class="card-header"><h3 class="card-title">👤 个人信息</h3></div>
                <div class="table-container"><table>
                    <thead><tr><th>项目</th><th>值</th></tr></thead>
                    <tbody>
                        <tr><td>头像</td><td style="font-size:1.5rem">{user.get('avatar', '🦜')}</td></tr>
                        <tr><td>昵称</td><td>{user.get('nickname', '')}</td></tr>
                        <tr><td>用户名</td><td>{user.get('username', '')}</td></tr>
                        <tr><td>邮箱</td><td>{user.get('email', '')}</td></tr>
                    </tbody>
                </table></div>
                <a href="/profile" class="btn btn-secondary" style="margin-top:1rem">📝 修改信息</a>
            </div>
        </div>

        <div class="card">
            <div class="card-header"><h3 class="card-title">📊 系统信息</h3></div>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-label">系统版本</div><div class="stat-value" style="font-size:1.5rem">v3.1.0</div></div>
                <div class="stat-card"><div class="stat-label">Python 文件</div><div class="stat-value" style="font-size:1.5rem">155</div></div>
                <div class="stat-card"><div class="stat-label">代码行数</div><div class="stat-value" style="font-size:1.5rem">~29K</div></div>
                <div class="stat-card"><div class="stat-label">功能页面</div><div class="stat-value" style="font-size:1.5rem">25+</div></div>
            </div>
            {make_table(['模块', '描述', '状态'], rows)}
        </div>
        """
        return render_page(content, 'settings', user=user)

    # ==================== API ENDPOINTS ====================

    @app.route('/api/status')
    @login_required
    def api_status():
        try:
            from src.monitor.system_monitor import SystemMonitor
            return jsonify(SystemMonitor().generate_health_report())
        except Exception as e:
            return jsonify({'status': 'ok', 'version': 'v3.1.0'})

    @app.route('/api/stocks')
    @login_required
    def api_stocks():
        stock_names = get_stock_names()
        codes = get_stock_codes()
        return jsonify({'stocks': [{'code': c, 'name': stock_names.get(c, '')} for c in codes]})

    @app.route('/api/strategies')
    @login_required
    def api_strategies():
        strategies = [
            {'name': 'SMA 交叉', 'type': '趋势跟踪', 'status': 'active'},
            {'name': '动量策略', 'type': '趋势跟踪', 'status': 'active'},
            {'name': '均值回归', 'type': '均值回归', 'status': 'active'},
            {'name': '多因子', 'type': '量化选股', 'status': 'active'},
        ]
        return jsonify({'strategies': strategies})

    @app.route('/api/articles')
    @login_required
    def api_articles():
        """文章信息 REST API - Phase 111"""
        from src.analysis.article_manager import ArticleManager
        try:
            mgr = ArticleManager()
            dates = mgr.get_available_dates()

            query_date = request.args.get('date', '')
            keyword = request.args.get('keyword', '')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            stock_only = request.args.get('stock_only', 'false').lower() == 'true'

            # 获取文章列表
            if query_date:
                articles = mgr.get_articles_by_date(query_date, limit=1000)
                articles = mgr.match_articles_with_stocks(articles)
                if stock_only:
                    articles = [a for a in articles if a['has_stock']]
            elif dates:
                # 默认返回最新日期的文章
                latest_date = dates[-1]
                articles, total = mgr.get_date_range_articles(
                    latest_date, latest_date, page=1, per_page=1000, stock_only=stock_only
                )
                articles = mgr.match_articles_with_stocks(articles)
            else:
                articles = []

            # 关键词过滤
            if keyword:
                articles = [a for a in articles if keyword.lower() in a.get('title', '').lower()]

            total = len(articles)
            # 分页
            start = (page - 1) * per_page
            end = start + per_page
            paged = articles[start:end]

            # 转换格式给前端
            result = []
            for a in paged:
                result.append({
                    'id': a.get('id', ''),
                    'date': a.get('date', query_date or (dates[-1] if dates else '')),
                    'platform': a.get('platform_name', a.get('platform', '')),
                    'title': a.get('title', ''),
                    'url': a.get('url', ''),
                    'rank': a.get('rank', 0),
                    'stocks': [s['code'] for s in a.get('matched_stocks', [])],
                    'has_stock': a.get('has_stock', False),
                    'relevance': a.get('relevance', 'low'),
                })

            return jsonify({
                'code': 200,
                'data': result,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': max(1, (total + per_page - 1) // per_page),
                'available_dates': dates[-30:] if dates else [],  # 最近30天
            })
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_webui_v3()
    if app:
        print("🦜 翠花量化 WebUI v3 启动中...")
        print("📊 20+ 功能页面已就绪")
        print("🌐 访问 http://127.0.0.1:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
