"""
Phase 66: WebUI v3 - Complete Redesign
Modern responsive dashboard with real-time data and advanced features.
"""

import os
import sys
import json
import yaml
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

def create_webui_v3():
    """
    Create enhanced WebUI v3 with modern design.
    """
    try:
        from flask import Flask, jsonify, render_template_string, request
    except ImportError:
        print("⚠️ Flask not installed. Run: pip install flask")
        return None
        
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cuihua-quant-secret'
    
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
    
    /* Sidebar Navigation */
    .sidebar {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        width: 260px;
        background: var(--bg-secondary);
        padding: 1.5rem 1rem;
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
        margin-bottom: 2rem;
        padding: 0.5rem;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.875rem 1rem;
        margin: 0.25rem 0;
        border-radius: var(--radius);
        color: var(--text-secondary);
        text-decoration: none;
        transition: all 0.2s;
        font-size: 0.9375rem;
    }
    
    .nav-item:hover, .nav-item.active {
        background: var(--bg-hover);
        color: var(--text-primary);
    }
    
    .nav-item.active {
        background: var(--accent);
        color: white;
    }
    
    /* Main Content */
    .main {
        margin-left: 260px;
        padding: 2rem;
        min-height: 100vh;
    }
    
    /* Header */
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
    }
    
    /* Cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 1.5rem;
        border: 1px solid var(--border);
        transition: all 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow);
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .stat-change {
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }
    
    /* Content Cards */
    .card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 1.5rem;
        border: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .card-title {
        font-size: 1.125rem;
        font-weight: 600;
    }
    
    /* Tables */
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
        padding: 1rem;
        font-size: 0.8125rem;
        font-weight: 600;
        color: var(--text-secondary);
        background: rgba(0,0,0,0.2);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    td {
        padding: 1rem;
        border-bottom: 1px solid var(--border);
        font-size: 0.9375rem;
    }
    
    tr:hover td {
        background: rgba(255,255,255,0.02);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-success { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-warning { background: rgba(245,158,11,0.2); color: var(--warning); }
    .badge-danger { background: rgba(239,68,68,0.2); color: var(--danger); }
    
    /* Buttons */
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem 1.25rem;
        border-radius: var(--radius);
        border: none;
        cursor: pointer;
        font-size: 0.9375rem;
        font-weight: 500;
        transition: all 0.2s;
        text-decoration: none;
    }
    
    .btn-primary {
        background: var(--accent);
        color: white;
    }
    
    .btn-primary:hover {
        background: var(--accent-hover);
        transform: translateY(-1px);
    }
    
    .btn-secondary {
        background: var(--bg-hover);
        color: var(--text-primary);
    }
    
    /* Forms */
    .form-group {
        margin-bottom: 1.25rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        color: var(--text-secondary);
    }
    
    .form-input, .form-select {
        width: 100%;
        padding: 0.75rem 1rem;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        color: var(--text-primary);
        font-size: 0.9375rem;
        transition: border-color 0.2s;
    }
    
    .form-input:focus, .form-select:focus {
        outline: none;
        border-color: var(--accent);
    }
    
    .form-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    /* Charts */
    .chart-container {
        min-height: 400px;
        background: rgba(0,0,0,0.2);
        border-radius: var(--radius);
        padding: 1rem;
    }
    
    /* Loading */
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid var(--border);
        border-top-color: var(--accent);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Alerts */
    .alert {
        padding: 1rem 1.5rem;
        border-radius: var(--radius);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .alert-info { background: rgba(99,102,241,0.2); border-left: 4px solid var(--accent); }
    .alert-success { background: rgba(34,197,94,0.2); border-left: 4px solid var(--success); }
    .alert-warning { background: rgba(245,158,11,0.2); border-left: 4px solid var(--warning); }
    .alert-error { background: rgba(239,68,68,0.2); border-left: 4px solid var(--danger); }
    
    /* Responsive */
    @media (max-width: 1024px) {
        .sidebar {
            transform: translateX(-100%);
        }
        .sidebar.open {
            transform: translateX(0);
        }
        .main {
            margin-left: 0;
        }
    }
    
    @media (max-width: 640px) {
        .main {
            padding: 1rem;
        }
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--bg-hover);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent);
    }
    """
    
    # ==================== LAYOUT TEMPLATE ====================
    BASE_LAYOUT = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>翠花量化 - """ + '{% block title %}监控看板{% endblock %}' + """</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
    """ + STYLES + """
        </style>
    </head>
    <body>
        <nav class="sidebar" id="sidebar">
            <div class="logo">🦜 翠花量化</div>
            <a href="/" class="nav-item """ + '{% if page == "dashboard" %}active{% endif %}' + """">
                <span>📊</span> 仪表板
            </a>
            <a href="/stocks" class="nav-item """ + '{% if page == "stocks" %}active{% endif %}' + """">
                <span>💼</span> 股票池
            </a>
            <a href="/analysis" class="nav-item """ + '{% if page == "analysis" %}active{% endif %}' + """">
                <span>📈</span> 信号分析
            </a>
            <a href="/backtest" class="nav-item """ + '{% if page == "backtest" %}active{% endif %}' + """">
                <span>🔬</span> 回测中心
            </a>
            <a href="/charts" class="nav-item """ + '{% if page == "charts" %}active{% endif %}' + """">
                <span>📉</span> 图表分析
            </a>
            <a href="/portfolio" class="nav-item """ + '{% if page == "portfolio" %}active{% endif %}' + """">
                <span>🌍</span> 投资组合
            </a>
            <a href="/risk" class="nav-item """ + '{% if page == "risk" %}active{% endif %}' + """">
                <span>🛡️</span> 风险监控
            </a>
            <a href="/settings" class="nav-item """ + '{% if page == "settings" %}active{% endif %}' + """">
                <span>⚙️</span> 系统设置
            </a>
        </nav>
        
        <main class="main">
            """ + '{{ content|safe }}' + """
        </main>
        
        <script>
            // Auto refresh every 60s
            setTimeout(() => location.reload(), 60000);
            
            // Mobile sidebar toggle
            function toggleSidebar() {
                document.getElementById('sidebar').classList.toggle('open');
            }
        </script>
    </body>
    </html>
    """
    
    # ==================== PAGE TEMPLATES ====================
    
    # Full page templates (no extends, all content inline)
    
    DASHBOARD_PAGE = """<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>翠花量化 - 监控看板</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>""" + STYLES + """</style>
    </head>
    <body>
        <nav class="sidebar" id="sidebar">
            <div class="logo">🦜 翠花量化</div>
            <a href="/" class="nav-item active"><span>📊</span> 仪表板</a>
            <a href="/stocks" class="nav-item"><span>💼</span> 股票池</a>
            <a href="/analysis" class="nav-item"><span>📈</span> 信号分析</a>
            <a href="/backtest" class="nav-item"><span>🔬</span> 回测中心</a>
            <a href="/charts" class="nav-item"><span>📉</span> 图表分析</a>
            <a href="/portfolio" class="nav-item"><span>🌍</span> 投资组合</a>
            <a href="/risk" class="nav-item"><span>🛡️</span> 风险监控</a>
            <a href="/settings" class="nav-item"><span>⚙️</span> 系统设置</a>
        </nav>
        <main class="main">
    <div class="header">
        <div><h1>📊 监控看板</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">实时系统状态与交易概览</p></div>
        <div class="header-actions">
            <button class="btn btn-secondary" onclick="location.reload()">🔄 刷新</button>
            <a href="/analysis" class="btn btn-primary">📈 查看信号</a>
        </div>
    </div>
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-label">系统状态</div><div class="stat-value">{{ system_status_icon }}</div><div class="stat-change" style="color: var(--text-secondary);">{{ system_status_text }}</div></div>
        <div class="stat-card"><div class="stat-label">数据库记录</div><div class="stat-value">{{ db_records }}</div><div class="stat-change" style="color: var(--success);">✅ 正常</div></div>
        <div class="stat-card"><div class="stat-label">信号总数</div><div class="stat-value">{{ total_signals }}</div><div class="stat-change" style="color: var(--accent);">📈 持续更新</div></div>
        <div class="stat-card"><div class="stat-label">总盈亏</div><div class="stat-value" style="color: {{ pnl_color }};">{{ total_pnl }}</div><div class="stat-change">胜率: {{ win_rate }}</div></div>
    </div>
    <div class="card"><div class="card-header"><h3 class="card-title">🔧 系统信息</h3></div>
        <div class="table-container"><table>
            <thead><tr><th>项目</th><th>状态</th><th>详情</th></tr></thead>
            <tbody>{% for item in system_info %}<tr><td>{{ item.name }}</td><td><span class="badge {{ item.badge }}">{{ item.status }}</span></td><td>{{ item.details }}</td></tr>{% endfor %}</tbody>
        </table></div></div>
        </main>
        <script>setTimeout(() => location.reload(), 60000);</script>
    </body></html>"""
    
    STOCKS_PAGE = """
    {% extends "base" %}
    {% block title %}股票池{% endblock %}
    {% block content %}
    <div class="header">
        <div>
            <h1>💼 股票池管理</h1>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">共 {{ stock_count }} 只股票</p>
        </div>
        <div class="header-actions">
            <a href="/sync" class="btn btn-primary">🔄 同步数据</a>
        </div>
    </div>
    
    <div class="card">
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>代码</th>
                        <th>最新价</th>
                        <th>涨跌幅</th>
                        <th>信号</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in stocks %}
                    <tr>
                        <td><span class="badge badge-warning">{{ stock.code }}</span></td>
                        <td>¥{{ stock.price }}</td>
                        <td style="color: {{ 'var(--success)' if stock.change > 0 else 'var(--danger)' }}">
                            {{ stock.change:+.2f }}%
                        </td>
                        <td>{{ stock.signal }}</td>
                        <td>
                            <a href="/charts?code={{ stock.code }}" class="btn btn-secondary" style="padding: 0.375rem 0.75rem; font-size: 0.8125rem;">
                                📉 图表
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    """
    
    ANALYSIS_PAGE = """
    {% extends "base" %}
    {% block title %}信号分析{% endblock %}
    {% block content %}
    <div class="header">
        <div>
            <h1>📈 信号分析</h1>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">基于技术指标和情绪分析的交易信号</p>
        </div>
        <div class="header-actions">
            <form method="POST" style="display: flex; gap: 0.5rem;">
                <select name="pool" class="form-select" style="width: auto;">
                    <option value="watchlist">核心观察池</option>
                    <option value="csi300_top">沪深 300</option>
                </select>
                <button type="submit" class="btn btn-primary">🔍 生成信号</button>
            </form>
        </div>
    </div>
    
    {% if signals %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">🎯 交易信号 (Top 20)</h3>
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>代码</th>
                        <th>收盘价</th>
                        <th>综合得分</th>
                        <th>技术分</th>
                        <th>情绪分</th>
                        <th>信号</th>
                    </tr>
                </thead>
                <tbody>
                    {% for sig in signals[:20] %}
                    <tr>
                        <td><span class="badge {{ 'badge-success' if sig.rank <= 5 else 'badge-warning' }}">#{{ sig.rank }}</span></td>
                        <td><span class="badge badge-warning">{{ sig.code }}</span></td>
                        <td>¥{{ sig.close }}</td>
                        <td style="color: {{ 'var(--success)' if sig.combined_score > 0 else 'var(--danger)' }}">
                            {{ sig.combined_score:+.3f }}
                        </td>
                        <td>{{ sig.tech_score:+.3f }}</td>
                        <td>{{ sig.sentiment_score:+.3f }}</td>
                        <td>{{ sig.signals }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% else %}
    <div class="alert alert-info">
        💡 点击"生成信号"按钮开始分析
    </div>
    {% endif %}
    {% endblock %}
    """
    
    CHARTS_PAGE = """
    {% extends "base" %}
    {% block title %}图表分析{% endblock %}
    {% block content %}
    <div class="header">
        <div>
            <h1>📉 图表分析</h1>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">交互式 K 线图与技术指标</p>
        </div>
    </div>
    
    <div class="card">
        <form method="POST" class="form-row" style="margin-bottom: 1.5rem;">
            <div class="form-group">
                <label class="form-label">股票代码</label>
                <input type="text" name="code" value="{{ request.args.get('code', 'SH.600519') }}" class="form-input">
            </div>
            <div class="form-group">
                <label class="form-label">时间范围</label>
                <select name="days" class="form-select">
                    <option value="30">30 天</option>
                    <option value="60" selected>60 天</option>
                    <option value="90">90 天</option>
                    <option value="180">180 天</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">技术指标</label>
                <select name="indicators" class="form-select">
                    <option value="ma">均线</option>
                    <option value="ma,macd">均线 + MACD</option>
                    <option value="ma,rsi">均线+RSI</option>
                    <option value="ma,macd,rsi">全部指标</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">&nbsp;</label>
                <button type="submit" class="btn btn-primary">📊 生成图表</button>
            </div>
        </form>
        
        {% if chart_html %}
        <div class="chart-container">
            {{ chart_html|safe }}
        </div>
        {% endif %}
    </div>
    {% endblock %}
    """
    
    SETTINGS_PAGE = """
    {% extends "base" %}
    {% block title %}系统设置{% endblock %}
    {% block content %}
    <div class="header">
        <div>
            <h1>⚙️ 系统设置</h1>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">配置管理与系统信息</p>
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">系统版本</div>
            <div class="stat-value" style="font-size: 1.5rem;">v1.5.0</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">模块总数</div>
            <div class="stat-value" style="font-size: 1.5rem;">85+</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">代码行数</div>
            <div class="stat-value" style="font-size: 1.5rem;">~37K</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">文件总数</div>
            <div class="stat-value" style="font-size: 1.5rem;">160+</div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">📊 系统状态</h3>
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr><th>模块</th><th>状态</th><th>描述</th></tr>
                </thead>
                <tbody>
                    {% for module in modules %}
                    <tr>
                        <td>{{ module.name }}</td>
                        <td><span class="badge {{ module.badge }}">{{ module.status }}</span></td>
                        <td>{{ module.desc }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    """
    
    # ==================== ROUTES ====================
    
    @app.route('/')
    def dashboard():
        from src.monitor.system_monitor import SystemMonitor
        from src.data.trade_logger import TradeLogger
        from src.data.database import get_db_engine
        
        monitor = SystemMonitor()
        logger = TradeLogger()
        
        # System checks
        futu = monitor.check_futu_connection()
        data = monitor.check_data_freshness()
        disk = monitor.check_disk_space()
        
        is_ok = futu['status'] == 'OK' and data['status'] == 'OK'
        
        summary = logger.get_summary()
        
        try:
            engine = get_db_engine()
            count = pd.read_sql("SELECT COUNT(*) as cnt FROM stock_daily", engine).iloc[0]['cnt']
        except:
            count = 0
            
        pnl = summary.get('total_pnl', 0)
        pnl_color = 'var(--success)' if pnl >= 0 else 'var(--danger)'
        
        system_info = [
            {'name': 'Futu OpenD', 'status': '正常' if futu['status'] == 'OK' else '异常', 
             'badge': 'badge-success' if futu['status'] == 'OK' else 'badge-danger',
             'details': f"{futu.get('message', '')}"},
            {'name': '数据新鲜度', 'status': '正常' if data['status'] == 'OK' else '警告',
             'badge': 'badge-success' if data['status'] == 'OK' else 'badge-warning',
             'details': data.get('message', '')},
            {'name': '磁盘空间', 'status': '正常' if disk['status'] == 'OK' else '警告',
             'badge': 'badge-success' if disk['status'] == 'OK' else 'badge-warning',
             'details': disk.get('message', '')},
        ]
        
        return render_template_string(DASHBOARD_PAGE,
            system_status_icon='✅' if is_ok else '⚠️',
            system_status_text='系统正常运行' if is_ok else '部分功能异常',
            db_records=f"{count:,}",
            total_signals=summary.get('total_signals', 0),
            total_pnl=f"¥{pnl:,.0f}",
            pnl_color=pnl_color,
            win_rate=f"{summary.get('win_rate', 0):.1%}",
            system_info=system_info,
            page='dashboard'
        )
        
    @app.route('/stocks')
    def stocks():
        import yaml
        from src.data.database import get_db_engine
        
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
        stocks_list = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
        
        engine = get_db_engine()
        stocks_data = []
        for code in stocks_list:
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
                    price = '-'
                    change = 0
                stocks_data.append({
                    'code': code, 'price': f"{price:.2f}" if isinstance(price, (int, float)) else price,
                    'change': round(change, 2), 'signal': '-'
                })
            except:
                stocks_data.append({'code': code, 'price': '-', 'change': 0, 'signal': '-'})
        
        stocks_rows = ''.join(
            f"""<tr><td><span class="badge badge-warning">{s['code']}</span></td>
            <td>¥{s['price']}</td>
            <td style="color: {'var(--success)' if s['change'] > 0 else 'var(--danger)'}">{s['change']:+.2f}%</td>
            <td>{s['signal']}</td></tr>""" for s in stocks_data
        )
        content = f"""<div class="header"><div><h1>💼 股票池管理</h1><p style="color: var(--text-secondary); margin-top: 0.5rem;">共 {len(stocks_list)} 只股票</p></div></div>
        <div class="card"><div class="table-container"><table>
        <thead><tr><th>代码</th><th>最新价</th><th>涨跌幅</th><th>信号</th></tr></thead>
        <tbody>{stocks_rows}</tbody></table></div></div>"""
        return render_template_string(BASE_LAYOUT,
            content=content,
            stock_count=len(stocks_list),
            stocks=stocks_data,
            page='stocks'
        )
        
    @app.route('/analysis', methods=['GET', 'POST'])
    def analysis():
        from src.analysis.signal_gen import SignalGenerator
        import yaml
        
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
            
        pool = request.form.get('pool', 'watchlist') if request.method == 'POST' else 'watchlist'
        codes = cfg.get('pools', {}).get(pool, {}).get('stocks', [])
        
        signals = []
        if codes:
            gen = SignalGenerator()
            df = gen.generate_combined_signal(codes[:20])
            if df is not None and not df.empty:
                signals = df.to_dict('records')
                for s in signals:
                    s['signals'] = ', '.join(s.get('signals', [])) if s.get('signals') else 'None'
        
        signal_rows = ''.join(
            f"""<tr><td>#{s.get('rank','')}</td><td>{s.get('code','')}</td><td>{s.get('close','')}</td><td>{s.get('combined_score','')}</td></tr>"""
            for s in signals
        ) if signals else ''
        card_html = f'<div class="card"><div class="table-container"><table><thead><tr><th>排名</th><th>代码</th><th>收盘价</th><th>综合得分</th></tr></thead><tbody>{signal_rows}</tbody></table></div></div>' if signals else '<div class="card"><div class="alert alert-info">💡 暂无数据，请先同步数据</div></div>'
        content = f"""<div class="header"><div><h1>📈 信号分析</h1><p style="color: var(--text-secondary); margin-top: 0.5rem;">基于技术指标和情绪分析的交易信号</p></div></div>{card_html}"""
        return render_template_string(BASE_LAYOUT,
            content=content,
            signals=signals,
            page='analysis'
        )
        
    @app.route('/charts', methods=['GET', 'POST'])
    def charts():
        from src.monitor.advanced_charts import AdvancedChartGenerator
        
        chart_html = None
        if request.method == 'POST' or request.args:
            code = request.form.get('code') or request.args.get('code', 'SH.600519')
            days = int(request.form.get('days') or request.args.get('days', 60))
            
            charts = AdvancedChartGenerator()
            chart_html = charts.generate_kline_with_indicators(code, days)
        
        content = f"""<div class="header"><div><h1>📉 图表分析</h1><p style="color: var(--text-secondary); margin-top: 0.5rem;">交互式 K 线图与技术指标</p></div></div>
        <div class="card">{'<div class="alert alert-info">📊 选择股票生成图表</div></div>' if not chart_html else chart_html}"""
        return render_template_string(BASE_LAYOUT,
            content=content,
            chart_html=chart_html,
            page='charts'
        )
        
    @app.route('/settings')
    def settings():
        modules = [
            {'name': '数据层', 'status': '运行中', 'badge': 'badge-success', 'desc': 'Futu/AKShare 双数据源'},
            {'name': '分析层', 'status': '运行中', 'badge': 'badge-success', 'desc': '技术指标/情绪/ML/因子'},
            {'name': '策略层', 'status': '运行中', 'badge': 'badge-success', 'desc': '25+ 策略'},
            {'name': '执行层', 'status': '运行中', 'badge': 'badge-success', 'desc': '风控/仓位/模拟盘'},
            {'name': '回测层', 'status': '运行中', 'badge': 'badge-success', 'desc': 'Backtrader/事件驱动'},
            {'name': '监控层', 'status': '运行中', 'badge': 'badge-success', 'desc': '报告/绩效/预警'},
            {'name': 'Web 界面', 'status': '运行中', 'badge': 'badge-success', 'desc': '8 个功能页面'},
        ]
        mod_rows = ''.join(f"""<tr><td>{m['name']}</td><td><span class="badge {m['badge']}">{m['status']}</span></td><td>{m['desc']}</td></tr>""" for m in modules)
        content = f"""<div class="header"><div><h1>⚙️ 系统设置</h1><p style="color: var(--text-secondary); margin-top: 0.5rem;">配置管理与系统信息</p></div></div>
        <div class="stats-grid">
        <div class="stat-card"><div class="stat-label">系统版本</div><div class="stat-value" style="font-size:1.5rem;">v3.0.0</div></div>
        <div class="stat-card"><div class="stat-label">模块总数</div><div class="stat-value" style="font-size:1.5rem;">155</div></div>
        <div class="stat-card"><div class="stat-label">代码行数</div><div class="stat-value" style="font-size:1.5rem;">~29K</div></div>
        <div class="stat-card"><div class="stat-label">文件总数</div><div class="stat-value" style="font-size:1.5rem;">155+</div></div>
        </div>
        <div class="card"><div class="card-header"><h3 class="card-title">📊 系统模块</h3></div>
        <div class="table-container"><table><thead><tr><th>模块</th><th>状态</th><th>描述</th></tr></thead>
        <tbody>{mod_rows}</tbody></table></div></div>"""
        return render_template_string(BASE_LAYOUT,
            content=content,
            modules=modules,
            page='settings'
        )
        
    @app.route('/api/status')
    def api_status():
        from src.monitor.system_monitor import SystemMonitor
        return jsonify(SystemMonitor().generate_health_report())
        
    return app


if __name__ == "__main__":
    app = create_webui_v3()
    if app:
        print("🌐 启动翠花量化 WebUI v3: http://localhost:5000")
        print("✨ 全新设计：现代响应式界面")
        app.run(host='0.0.0.0', port=5000, debug=False)
