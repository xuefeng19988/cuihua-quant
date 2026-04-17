"""
Phase 26: Enhanced Web Dashboard v2
Full integration of all new features: groups, charts, export, reports.
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

def create_enhanced_app_v2():
    """Create enhanced Flask application v2 with all features integrated."""
    try:
        from flask import Flask, jsonify, render_template_string, request, redirect, url_for, send_file
    except ImportError:
        print("⚠️ Flask not installed. Run: pip install flask")
        return None
        
    app = Flask(__name__)
    
    # ==================== BASE TEMPLATE ====================
    BASE_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>翠花量化 - {% block title %}监控看板{% endblock %}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            :root {
                --bg-primary: #1a1a2e;
                --bg-secondary: #16213e;
                --bg-card: #0f3460;
                --text-primary: #eaeaea;
                --text-secondary: #a0a0a0;
                --accent: #e94560;
                --success: #4ecca3;
                --warning: #ffc947;
                --danger: #ff6b6b;
            }
            
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--bg-primary);
                color: var(--text-primary);
                min-height: 100vh;
            }
            
            .header {
                background: var(--bg-secondary);
                padding: 1rem 2rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
            }
            
            .header h1 {
                font-size: 1.5rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .nav {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }
            
            .nav a {
                color: var(--text-secondary);
                text-decoration: none;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                transition: all 0.3s;
                font-size: 0.9rem;
            }
            
            .nav a:hover, .nav a.active {
                color: var(--text-primary);
                background: var(--bg-card);
            }
            
            .container {
                max-width: 1400px;
                margin: 2rem auto;
                padding: 0 1rem;
            }
            
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .card {
                background: var(--bg-card);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            }
            
            .card h2 {
                font-size: 1.1rem;
                margin-bottom: 1rem;
                color: var(--text-secondary);
                border-bottom: 2px solid var(--accent);
                padding-bottom: 0.5rem;
            }
            
            .metric {
                display: flex;
                justify-content: space-between;
                padding: 0.75rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            
            .metric:last-child { border-bottom: none; }
            .metric-label { color: var(--text-secondary); }
            .metric-value { font-weight: bold; }
            .positive { color: var(--success); }
            .negative { color: var(--danger); }
            
            .btn {
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background: var(--accent);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.3s;
                font-size: 0.9rem;
            }
            
            .btn:hover {
                background: #d63851;
                transform: translateY(-2px);
            }
            
            .btn-success { background: var(--success); color: #1a1a2e; }
            .btn-warning { background: var(--warning); color: #1a1a2e; }
            .btn-small { padding: 0.5rem 1rem; font-size: 0.8rem; }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
                font-size: 0.9rem;
            }
            
            th, td {
                padding: 0.75rem;
                text-align: left;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            
            th {
                color: var(--text-secondary);
                font-weight: 600;
            }
            
            tr:hover {
                background: rgba(255,255,255,0.05);
            }
            
            .stock-code {
                font-family: 'Courier New', monospace;
                color: var(--warning);
            }
            
            .form-group {
                margin-bottom: 1rem;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            
            .form-group input, .form-group select {
                width: 100%;
                padding: 0.75rem;
                background: var(--bg-secondary);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                color: var(--text-primary);
                font-size: 0.9rem;
            }
            
            .form-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-bottom: 1rem;
            }
            
            .refresh {
                text-align: center;
                padding: 2rem;
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            
            .refresh a {
                color: var(--accent);
                text-decoration: none;
            }
            
            @media (max-width: 768px) {
                .grid { grid-template-columns: 1fr; }
                .header { flex-direction: column; gap: 1rem; }
                .nav { justify-content: center; }
                .container { padding: 0 0.5rem; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🦜 翠花量化系统 v1.4</h1>
            <div class="nav">
                <a href="/" class="{% if page == 'dashboard' %}active{% endif %}">📊 仪表板</a>
                <a href="/stocks" class="{% if page == 'stocks' %}active{% endif %}">💼 股票池</a>
                <a href="/groups" class="{% if page == 'groups' %}active{% endif %}">📁 分组</a>
                <a href="/query" class="{% if page == 'query' %}active{% endif %}">🔍 查询</a>
                <a href="/filter" class="{% if page == 'filter' %}active{% endif %}">🎯 筛选</a>
                <a href="/charts" class="{% if page == 'charts' %}active{% endif %}">📈 图表</a>
                <a href="/export" class="{% if page == 'export' %}active{% endif %}">📤 导出</a>
                <a href="/report" class="{% if page == 'report' %}active{% endif %}">📋 报告</a>
            </div>
        </div>
        
        <div class="container">
            {% block content %}{% endblock %}
        </div>
        
        <div class="refresh">
            <p>自动刷新: 每 60 秒 | <a href="javascript:location.reload()">立即刷新</a></p>
        </div>
        
        <script>
            setTimeout(() => location.reload(), 60000);
        </script>
    </body>
    </html>
    """
    
    # ==================== PAGE TEMPLATES ====================
    
    DASHBOARD_TEMPLATE = """
    {% extends "base" %}
    {% block title %}监控看板{% endblock %}
    {% block content %}
    <div class="grid">
        <div class="card">
            <h2>📊 系统状态</h2>
            {% for item in system_status %}
            <div class="metric">
                <span class="metric-label">{{ item.name }}</span>
                <span class="metric-value">{{ item.value }}</span>
            </div>
            {% endfor %}
        </div>
        <div class="card">
            <h2>💰 交易统计</h2>
            {% for item in trade_stats %}
            <div class="metric">
                <span class="metric-label">{{ item.name }}</span>
                <span class="metric-value {{ item.class }}">{{ item.value }}</span>
            </div>
            {% endfor %}
        </div>
        <div class="card">
            <h2>📊 数据覆盖</h2>
            {% for item in data_coverage %}
            <div class="metric">
                <span class="metric-label">{{ item.name }}</span>
                <span class="metric-value">{{ item.value }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}
    """
    
    STOCKS_TEMPLATE = """
    {% extends "base" %}
    {% block title %}股票池管理{% endblock %}
    {% block content %}
    <div class="card">
        <h2>💼 股票池 - {{ pool_name }} ({{ stock_count }} 只)</h2>
        <table>
            <thead>
                <tr><th>代码</th><th>最新价</th><th>涨跌幅</th><th>信号</th></tr>
            </thead>
            <tbody>
                {% for stock in stocks %}
                <tr>
                    <td class="stock-code">{{ stock.code }}</td>
                    <td>¥{{ stock.price }}</td>
                    <td class="{{ 'positive' if stock.change > 0 else 'negative' }}">{{ stock.change:+.2f }}%</td>
                    <td>{{ stock.signal }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endblock %}
    """
    
    GROUPS_TEMPLATE = """
    {% extends "base" %}
    {% block title %}股票分组{% endblock %}
    {% block content %}
    <div class="card">
        <h2>📁 股票分组管理</h2>
        {% for name, group in groups.items() %}
        <div style="margin: 1rem 0; padding: 1rem; background: var(--bg-secondary); border-radius: 8px;">
            <h3 style="margin-bottom: 0.5rem;">{{ name }} <span style="color: var(--text-secondary); font-size: 0.9rem;">({{ group.stocks|length }} 只)</span></h3>
            <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">{{ group.description }}</p>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                {% for code in group.stocks %}
                <span class="stock-code" style="background: var(--bg-card); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">{{ code }}</span>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endblock %}
    """
    
    QUERY_TEMPLATE = """
    {% extends "base" %}
    {% block title %}数据查询{% endblock %}
    {% block content %}
    <div class="card">
        <h2>🔍 历史数据查询</h2>
        <form method="POST">
            <div class="form-row">
                <div class="form-group">
                    <label>股票代码</label>
                    <input type="text" name="code" value="{{ request.args.get('code', 'SH.600519') }}">
                </div>
                <div class="form-group">
                    <label>开始日期</label>
                    <input type="date" name="start_date" value="{{ request.args.get('start_date', '') }}">
                </div>
                <div class="form-group">
                    <label>结束日期</label>
                    <input type="date" name="end_date" value="{{ request.args.get('end_date', '') }}">
                </div>
            </div>
            <button type="submit" class="btn">🔍 查询</button>
        </form>
        
        {% if data %}
        <div style="margin-top: 2rem;">
            <h3 style="margin-bottom: 1rem;">查询结果 ({{ data|length }} 条)</h3>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr><th>日期</th><th>开盘</th><th>最高</th><th>最低</th><th>收盘</th><th>成交量</th><th>涨跌幅</th></tr>
                    </thead>
                    <tbody>
                        {% for row in data %}
                        <tr>
                            <td>{{ row.date }}</td>
                            <td>{{ row.open }}</td>
                            <td>{{ row.high }}</td>
                            <td>{{ row.low }}</td>
                            <td>{{ row.close }}</td>
                            <td>{{ row.volume }}</td>
                            <td class="{{ 'positive' if row.change > 0 else 'negative' }}">{{ row.change:+.2f }}%</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
    </div>
    {% endblock %}
    """
    
    FILTER_TEMPLATE = """
    {% extends "base" %}
    {% block title %}高级筛选{% endblock %}
    {% block content %}
    <div class="card">
        <h2>🎯 高级股票筛选</h2>
        <form method="POST">
            <div class="form-row">
                <div class="form-group">
                    <label>最低价格</label>
                    <input type="number" name="min_price" step="0.01" value="{{ request.args.get('min_price', '') }}">
                </div>
                <div class="form-group">
                    <label>最高价格</label>
                    <input type="number" name="max_price" step="0.01" value="{{ request.args.get('max_price', '') }}">
                </div>
                <div class="form-group">
                    <label>最小涨跌幅 (%)</label>
                    <input type="number" name="min_change" step="0.1" value="{{ request.args.get('min_change', '') }}">
                </div>
                <div class="form-group">
                    <label>最大涨跌幅 (%)</label>
                    <input type="number" name="max_change" step="0.1" value="{{ request.args.get('max_change', '') }}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>所属分组</label>
                    <select name="group">
                        <option value="">全部分组</option>
                        {% for name in groups %}
                        <option value="{{ name }}" {% if request.args.get('group') == name %}selected{% endif %}>{{ name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <button type="submit" class="btn">🎯 筛选</button>
        </form>
        
        {% if data %}
        <div style="margin-top: 2rem;">
            <h3 style="margin-bottom: 1rem;">筛选结果 ({{ data|length }} 只)</h3>
            <table>
                <thead>
                    <tr><th>代码</th><th>收盘价</th><th>涨跌幅</th><th>成交量</th></tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        <td class="stock-code">{{ row.code }}</td>
                        <td>¥{{ row.close_price }}</td>
                        <td class="{{ 'positive' if row.change_pct > 0 else 'negative' }}">{{ row.change_pct:+.2f }}%</td>
                        <td>{{ row.volume }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
    </div>
    {% endblock %}
    """
    
    CHARTS_TEMPLATE = """
    {% extends "base" %}
    {% block title %}图表分析{% endblock %}
    {% block content %}
    <div class="card">
        <h2>📈 交互式图表分析</h2>
        <form method="POST">
            <div class="form-row">
                <div class="form-group">
                    <label>股票代码</label>
                    <input type="text" name="code" value="{{ request.args.get('code', 'SH.600519') }}">
                </div>
                <div class="form-group">
                    <label>天数</label>
                    <select name="days">
                        <option value="30" {% if request.args.get('days') == '30' %}selected{% endif %}>30 天</option>
                        <option value="60" {% if request.args.get('days') == '60' %}selected{% endif %}>60 天</option>
                        <option value="90" {% if request.args.get('days') == '90' %}selected{% endif %}>90 天</option>
                        <option value="180" {% if request.args.get('days') == '180' %}selected{% endif %}>180 天</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>技术指标</label>
                    <select name="indicators" multiple style="height: 80px;">
                        <option value="ma" selected>MA 均线</option>
                        <option value="volume" selected>成交量</option>
                        <option value="macd">MACD</option>
                        <option value="rsi">RSI</option>
                        <option value="bb">布林带</option>
                    </select>
                </div>
            </div>
            <button type="submit" class="btn">📊 生成图表</button>
        </form>
        
        {% if chart_html %}
        <div style="margin-top: 2rem;">
            {{ chart_html|safe }}
        </div>
        {% endif %}
    </div>
    {% endblock %}
    """
    
    EXPORT_TEMPLATE = """
    {% extends "base" %}
    {% block title %}数据导出{% endblock %}
    {% block content %}
    <div class="card">
        <h2>📤 数据导出</h2>
        <form method="POST">
            <div class="form-row">
                <div class="form-group">
                    <label>股票代码</label>
                    <input type="text" name="code" value="{{ request.args.get('code', 'SH.600519') }}">
                </div>
                <div class="form-group">
                    <label>导出格式</label>
                    <select name="format">
                        <option value="csv">CSV</option>
                        <option value="excel">Excel</option>
                        <option value="pdf">PDF/HTML</option>
                    </select>
                </div>
            </div>
            <button type="submit" class="btn">📤 导出</button>
        </form>
        
        {% if message %}
        <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-secondary); border-radius: 8px;">
            {{ message }}
        </div>
        {% endif %}
        
        {% if exports %}
        <div style="margin-top: 2rem;">
            <h3 style="margin-bottom: 1rem;">最近导出</h3>
            <table>
                <thead>
                    <tr><th>文件名</th><th>大小</th><th>时间</th><th>操作</th></tr>
                </thead>
                <tbody>
                    {% for file in exports[:10] %}
                    <tr>
                        <td>{{ file.filename }}</td>
                        <td>{{ file.size }}</td>
                        <td>{{ file.created }}</td>
                        <td><a href="/download/{{ file.filename }}" class="btn btn-small">下载</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
    </div>
    {% endblock %}
    """
    
    REPORT_TEMPLATE = """
    {% extends "base" %}
    {% block title %}报告{% endblock %}
    {% block content %}
    <div class="card">
        <h2>📋 绩效报告</h2>
        <div style="margin-bottom: 1rem;">
            <a href="/report/daily" class="btn">📊 每日报告</a>
            <a href="/report/portfolio" class="btn btn-success">💼 投资组合报告</a>
        </div>
        
        {% if report_content %}
        <div style="margin-top: 2rem; white-space: pre-wrap; font-family: monospace; background: var(--bg-secondary); padding: 1rem; border-radius: 8px;">
            {{ report_content }}
        </div>
        {% endif %}
    </div>
    {% endblock %}
    """
    
    # ==================== ROUTES ====================
    
    @app.template_context_processors['none'] = lambda: {'page': 'dashboard'}
    
    @app.route('/')
    def dashboard():
        from src.monitor.system_monitor import SystemMonitor
        from src.data.trade_logger import TradeLogger
        
        monitor = SystemMonitor()
        logger = TradeLogger()
        
        futu = monitor.check_futu_connection()
        data = monitor.check_data_freshness()
        disk = monitor.check_disk_space()
        
        system_status = [
            {'name': 'Futu 连接', 'value': '✅ 正常' if futu['status'] == 'OK' else '❌ 异常'},
            {'name': '数据新鲜度', 'value': data.get('message', '')},
            {'name': '磁盘空间', 'value': disk.get('message', '')},
        ]
        
        summary = logger.get_summary()
        trade_stats = [
            {'name': '总信号数', 'value': str(summary['total_signals'])},
            {'name': '总订单数', 'value': str(summary['total_orders'])},
            {'name': '胜率', 'value': f"{summary['win_rate']:.1%}", 'class': 'positive' if summary['win_rate'] > 0.5 else 'negative'},
            {'name': '总盈亏', 'value': f"¥{summary['total_pnl']:,.2f}", 'class': 'positive' if summary['total_pnl'] > 0 else 'negative'},
        ]
        
        try:
            from src.data.database import get_db_engine
            engine = get_db_engine()
            df = pd.read_sql("SELECT COUNT(*) as cnt FROM stock_daily", engine)
            count = df.iloc[0]['cnt']
        except:
            count = 0
            
        data_coverage = [
            {'name': '总记录数', 'value': f"{count:,}"},
            {'name': '股票池', 'value': '38 只'},
        ]
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', DASHBOARD_TEMPLATE),
            system_status=system_status,
            trade_stats=trade_stats,
            data_coverage=data_coverage,
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
                    f"SELECT close_price, date FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 2",
                    engine
                )
                if len(df) >= 2:
                    price = df.iloc[0]['close_price']
                    change = ((price - df.iloc[1]['close_price']) / df.iloc[1]['close_price']) * 100
                elif len(df) == 1:
                    price = df.iloc[0]['close_price']
                    change = 0
                else:
                    price = 0
                    change = 0
                    
                stocks_data.append({
                    'code': code,
                    'price': f"{price:.2f}",
                    'change': round(change, 2),
                    'signal': '-'
                })
            except:
                stocks_data.append({'code': code, 'price': '-', 'change': 0, 'signal': '-'})
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', STOCKS_TEMPLATE),
            pool_name='watchlist',
            stock_count=len(stocks_list),
            stocks=stocks_data,
            page='stocks'
        )
        
    @app.route('/groups')
    def groups():
        from src.data.stock_groups import StockGroupManager
        mgr = StockGroupManager()
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', GROUPS_TEMPLATE),
            groups=mgr.get_groups(),
            page='groups'
        )
        
    @app.route('/query', methods=['GET', 'POST'])
    def query():
        from src.data.database import get_db_engine
        
        data = []
        if request.method == 'POST' or request.args:
            code = request.form.get('code') or request.args.get('code', 'SH.600519')
            start_date = request.form.get('start_date') or request.args.get('start_date')
            end_date = request.form.get('end_date') or request.args.get('end_date')
            
            query = f"SELECT * FROM stock_daily WHERE code='{code}'"
            if start_date:
                query += f" AND date >= '{start_date}'"
            if end_date:
                query += f" AND date <= '{end_date}'"
            query += " ORDER BY date DESC LIMIT 100"
            
            try:
                engine = get_db_engine()
                df = pd.read_sql(query, engine)
                if not df.empty:
                    for _, row in df.iterrows():
                        data.append({
                            'date': str(row.get('date', ''))[:10],
                            'open': f"{row.get('open_price', 0):.2f}",
                            'high': f"{row.get('high_price', 0):.2f}",
                            'low': f"{row.get('low_price', 0):.2f}",
                            'close': f"{row.get('close_price', 0):.2f}",
                            'volume': f"{row.get('volume', 0):,.0f}",
                            'change': round(row.get('change_pct', 0), 2)
                        })
            except Exception as e:
                data = [{'error': str(e)}]
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', QUERY_TEMPLATE),
            data=data,
            page='query'
        )
        
    @app.route('/filter', methods=['GET', 'POST'])
    def filter_stocks():
        from src.data.stock_groups import StockGroupManager
        from src.data.database import get_db_engine
        
        mgr = StockGroupManager()
        data = []
        
        if request.method == 'POST' or request.args:
            criteria = {}
            if request.form.get('min_price'):
                criteria['min_price'] = float(request.form['min_price'])
            if request.form.get('max_price'):
                criteria['max_price'] = float(request.form['max_price'])
            if request.form.get('min_change'):
                criteria['min_change'] = float(request.form['min_change'])
            if request.form.get('max_change'):
                criteria['max_change'] = float(request.form['max_change'])
            if request.form.get('group'):
                criteria['group'] = request.form['group']
                
            try:
                engine = get_db_engine()
                df = mgr.filter_stocks(criteria, engine)
                if not df.empty:
                    data = df.to_dict('records')
            except Exception as e:
                data = [{'error': str(e)}]
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', FILTER_TEMPLATE),
            groups=mgr.get_groups(),
            data=data,
            page='filter'
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
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', CHARTS_TEMPLATE),
            chart_html=chart_html,
            page='charts'
        )
        
    @app.route('/export', methods=['GET', 'POST'])
    def export():
        from src.data.data_export import DataExporter
        from src.data.database import get_db_engine
        
        exporter = DataExporter()
        message = None
        exports = exporter.list_exports()
        
        if request.method == 'POST' or request.args:
            code = request.form.get('code') or request.args.get('code', 'SH.600519')
            format = request.form.get('format') or request.args.get('format', 'csv')
            
            try:
                engine = get_db_engine()
                filepath = exporter.export_stock_data(code, engine, format=format)
                if filepath:
                    message = f"✅ 导出成功: {os.path.basename(filepath)}"
                else:
                    message = "❌ 导出失败"
            except Exception as e:
                message = f"❌ 错误: {str(e)}"
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', EXPORT_TEMPLATE),
            message=message,
            exports=exports,
            page='export'
        )
        
    @app.route('/download/<filename>')
    def download(filename):
        from flask import send_from_directory
        export_dir = os.path.join(project_root, 'data', 'exports')
        return send_from_directory(export_dir, filename, as_attachment=True)
        
    @app.route('/report')
    def report():
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', REPORT_TEMPLATE),
            page='report'
        )
        
    @app.route('/report/daily')
    def daily_report():
        from src.monitor.report_generator import PerformanceReporter
        reporter = PerformanceReporter()
        content = reporter.daily_report()
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', REPORT_TEMPLATE),
            report_content=content,
            page='report'
        )
        
    @app.route('/report/portfolio')
    def portfolio_report():
        from src.monitor.pdf_report import PDFReportGenerator
        from src.data.trade_logger import TradeLogger
        
        logger = TradeLogger()
        summary = logger.get_summary()
        
        report_gen = PDFReportGenerator()
        data = {
            'metrics': {
                '总信号数': str(summary['total_signals']),
                '总订单数': str(summary['total_orders']),
                '胜率': f"{summary['win_rate']:.1%}",
                '总盈亏': f"¥{summary['total_pnl']:,.2f}"
            },
            'positions': [],
            'trades': logger.get_recent_orders(limit=10)
        }
        
        filepath = report_gen.generate_daily_report(data)
        return redirect(f'/download/{os.path.basename(filepath)}')
        
    @app.route('/api/status')
    def api_status():
        from src.monitor.system_monitor import SystemMonitor
        return jsonify(SystemMonitor().generate_health_report())
        
    return app


if __name__ == "__main__":
    app = create_enhanced_app_v2()
    if app:
        print("🌐 启动增强版 Web 看板 v2: http://localhost:5000")
        print("📊 功能: 仪表板 | 股票池 | 分组 | 查询 | 筛选 | 图表 | 导出 | 报告")
        app.run(host='0.0.0.0', port=5000, debug=True)
