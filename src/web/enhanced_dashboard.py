"""
Phase 26: Enhanced Web Dashboard
Full-featured web interface with stock management, charts, and data query.
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

def create_enhanced_app():
    """Create enhanced Flask application with full features."""
    try:
        from flask import Flask, jsonify, render_template_string, request, redirect, url_for
    except ImportError:
        print("⚠️ Flask not installed. Run: pip install flask")
        return None
        
    app = Flask(__name__)
    
    # ==================== TEMPLATES ====================
    
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
            }
            
            .header h1 {
                font-size: 1.5rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .nav {
                display: flex;
                gap: 1rem;
            }
            
            .nav a {
                color: var(--text-secondary);
                text-decoration: none;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                transition: all 0.3s;
            }
            
            .nav a:hover, .nav a.active {
                color: var(--text-primary);
                background: var(--bg-card);
            }
            
            .container {
                max-width: 1400px;
                margin: 2rem auto;
                padding: 0 2rem;
            }
            
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
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
            }
            
            .btn:hover {
                background: #d63851;
                transform: translateY(-2px);
            }
            
            .btn-success { background: var(--success); color: #1a1a2e; }
            .btn-warning { background: var(--warning); color: #1a1a2e; }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
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
            
            .refresh {
                text-align: center;
                padding: 2rem;
                color: var(--text-secondary);
            }
            
            .refresh a {
                color: var(--accent);
                text-decoration: none;
            }
            
            @media (max-width: 768px) {
                .grid { grid-template-columns: 1fr; }
                .header { flex-direction: column; gap: 1rem; }
                .nav { flex-wrap: wrap; justify-content: center; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🦜 翠花量化系统</h1>
            <div class="nav">
                <a href="/" class="{% if page == 'dashboard' %}active{% endif %}">📊 仪表板</a>
                <a href="/stocks" class="{% if page == 'stocks' %}active{% endif %}">💼 股票管理</a>
                <a href="/query" class="{% if page == 'query' %}active{% endif %}">🔍 数据查询</a>
                <a href="/charts" class="{% if page == 'charts' %}active{% endif %}">📈 图表分析</a>
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
            <h2>💰 投资组合</h2>
            {% for item in portfolio %}
            <div class="metric">
                <span class="metric-label">{{ item.name }}</span>
                <span class="metric-value {{ item.class }}">{{ item.value }}</span>
            </div>
            {% endfor %}
        </div>
        
        <div class="card">
            <h2>📈 交易统计</h2>
            {% for item in trade_stats %}
            <div class="metric">
                <span class="metric-label">{{ item.name }}</span>
                <span class="metric-value">{{ item.value }}</span>
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
    {% block title %}股票管理{% endblock %}
    
    {% block content %}
    <div class="card">
        <h2>💼 股票池管理</h2>
        <p style="margin-bottom: 1rem; color: var(--text-secondary);">
            当前股票池: <strong>{{ pool_name }}</strong> | 股票数量: <strong>{{ stock_count }}</strong>
        </p>
        
        <table>
            <thead>
                <tr>
                    <th>代码</th>
                    <th>最新价</th>
                    <th>涨跌幅</th>
                    <th>成交量</th>
                    <th>信号</th>
                </tr>
            </thead>
            <tbody>
                {% for stock in stocks %}
                <tr>
                    <td class="stock-code">{{ stock.code }}</td>
                    <td>¥{{ stock.price }}</td>
                    <td class="{{ 'positive' if stock.change > 0 else 'negative' }}">
                        {{ stock.change:+.2f }}%
                    </td>
                    <td>{{ stock.volume }}</td>
                    <td>{{ stock.signal }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endblock %}
    """
    
    QUERY_TEMPLATE = """
    {% extends "base" %}
    {% block title %}数据查询{% endblock %}
    
    {% block content %}
    <div class="card">
        <h2>🔍 历史数据查询</h2>
        <form method="POST" style="margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-secondary);">股票代码</label>
                    <input type="text" name="code" value="{{ request.args.get('code', 'SH.600519') }}" 
                           style="width: 100%; padding: 0.75rem; background: var(--bg-secondary); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: var(--text-primary);">
                </div>
                <div>
                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-secondary);">开始日期</label>
                    <input type="date" name="start_date" value="{{ request.args.get('start_date', '') }}" 
                           style="width: 100%; padding: 0.75rem; background: var(--bg-secondary); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: var(--text-primary);">
                </div>
                <div>
                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-secondary);">结束日期</label>
                    <input type="date" name="end_date" value="{{ request.args.get('end_date', '') }}" 
                           style="width: 100%; padding: 0.75rem; background: var(--bg-secondary); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: var(--text-primary);">
                </div>
            </div>
            <button type="submit" class="btn">🔍 查询</button>
        </form>
        
        {% if data %}
        <div style="margin-top: 2rem;">
            <h3 style="margin-bottom: 1rem;">查询结果 ({{ data|length }} 条记录)</h3>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>开盘</th>
                            <th>最高</th>
                            <th>最低</th>
                            <th>收盘</th>
                            <th>成交量</th>
                            <th>涨跌幅</th>
                        </tr>
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
    
    CHARTS_TEMPLATE = """
    {% extends "base" %}
    {% block title %}图表分析{% endblock %}
    
    {% block content %}
    <div class="card">
        <h2>📈 交互式图表分析</h2>
        <form method="POST" action="/charts" style="margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-secondary);">股票代码</label>
                    <input type="text" name="code" value="{{ request.args.get('code', 'SH.600519') }}" 
                           style="width: 100%; padding: 0.75rem; background: var(--bg-secondary); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: var(--text-primary);">
                </div>
                <div>
                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-secondary);">天数</label>
                    <select name="days" style="width: 100%; padding: 0.75rem; background: var(--bg-secondary); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: var(--text-primary);">
                        <option value="30" {% if request.args.get('days') == '30' %}selected{% endif %}>30 天</option>
                        <option value="60" {% if request.args.get('days') == '60' %}selected{% endif %}>60 天</option>
                        <option value="90" {% if request.args.get('days') == '90' %}selected{% endif %}>90 天</option>
                        <option value="180" {% if request.args.get('days') == '180' %}selected{% endif %}>180 天</option>
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
    
    # ==================== ROUTES ====================
    
    @app.template_context_processors['none'] = lambda: {'page': 'dashboard'}
    
    @app.route('/')
    def dashboard():
        """Main dashboard."""
        from src.monitor.system_monitor import SystemMonitor
        from src.data.trade_logger import TradeLogger
        
        monitor = SystemMonitor()
        logger = TradeLogger()
        
        # System status
        futu = monitor.check_futu_connection()
        data = monitor.check_data_freshness()
        disk = monitor.check_disk_space()
        
        system_status = [
            {'name': 'Futu 连接', 'value': '✅ 正常' if futu['status'] == 'OK' else '❌ 异常'},
            {'name': '数据新鲜度', 'value': data.get('message', '')},
            {'name': '磁盘空间', 'value': disk.get('message', '')},
        ]
        
        # Portfolio
        summary = logger.get_summary()
        portfolio = [
            {'name': '总信号数', 'value': str(summary['total_signals'])},
            {'name': '总订单数', 'value': str(summary['total_orders'])},
            {'name': '胜率', 'value': f"{summary['win_rate']:.1%}", 'class': 'positive' if summary['win_rate'] > 0.5 else 'negative'},
            {'name': '总盈亏', 'value': f"¥{summary['total_pnl']:,.2f}", 'class': 'positive' if summary['total_pnl'] > 0 else 'negative'},
        ]
        
        trade_stats = [
            {'name': '已平仓', 'value': str(summary['closed_trades'])},
            {'name': '当前持仓', 'value': '待接入'},
        ]
        
        try:
            from src.data.database import get_db_engine
            import pandas as pd
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
            portfolio=portfolio,
            trade_stats=trade_stats,
            data_coverage=data_coverage,
            page='dashboard'
        )
        
    @app.route('/stocks')
    def stocks():
        """Stock pool management."""
        import yaml
        from src.data.database import get_db_engine
        import pandas as pd
        
        # Load stock pool
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
        stocks_list = cfg.get('pools', {}).get('watchlist', {}).get('stocks', [])
        
        # Get latest prices
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
                    prev_price = df.iloc[1]['close_price']
                    change = ((price - prev_price) / prev_price) * 100
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
                    'volume': '-',
                    'signal': '-'
                })
            except:
                stocks_data.append({
                    'code': code,
                    'price': '-',
                    'change': 0,
                    'volume': '-',
                    'signal': '-'
                })
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', STOCKS_TEMPLATE),
            pool_name='watchlist',
            stock_count=len(stocks_list),
            stocks=stocks_data,
            page='stocks'
        )
        
    @app.route('/query', methods=['GET', 'POST'])
    def query():
        """Data query interface."""
        from src.data.database import get_db_engine
        import pandas as pd
        
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
                        change = row.get('change_pct', 0)
                        data.append({
                            'date': str(row.get('date', ''))[:10],
                            'open': f"{row.get('open_price', 0):.2f}",
                            'high': f"{row.get('high_price', 0):.2f}",
                            'low': f"{row.get('low_price', 0):.2f}",
                            'close': f"{row.get('close_price', 0):.2f}",
                            'volume': f"{row.get('volume', 0):,.0f}",
                            'change': round(change, 2) if change else 0
                        })
            except Exception as e:
                data = [{'error': str(e)}]
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', QUERY_TEMPLATE),
            data=data,
            page='query'
        )
        
    @app.route('/charts', methods=['GET', 'POST'])
    def charts():
        """Interactive charts."""
        from src.monitor.interactive_charts import InteractiveCharts
        
        chart_html = None
        if request.method == 'POST' or request.args:
            code = request.form.get('code') or request.args.get('code', 'SH.600519')
            days = int(request.form.get('days') or request.args.get('days', 60))
            
            charts = InteractiveCharts()
            chart_html = charts.generate_kline_chart(code, days)
        
        return render_template_string(
            BASE_TEMPLATE.replace('{% block content %}{% endblock %}', CHARTS_TEMPLATE),
            chart_html=chart_html,
            page='charts'
        )
        
    @app.route('/report')
    def report():
        """Reports page."""
        from src.monitor.report_generator import PerformanceReporter
        
        reporter = PerformanceReporter()
        report_content = reporter.daily_report()
        
        return render_template_string(
            BASE_TEMPLATE,
            report_content=report_content,
            page='report'
        )
        
    @app.route('/api/status')
    def api_status():
        """API status endpoint."""
        from src.monitor.system_monitor import SystemMonitor
        monitor = SystemMonitor()
        return jsonify(monitor.generate_health_report())
        
    @app.route('/api/stocks')
    def api_stocks():
        """API stocks endpoint."""
        import yaml
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
        return jsonify(cfg.get('pools', {}))
        
    return app


if __name__ == "__main__":
    app = create_enhanced_app()
    if app:
        print("🌐 启动增强版 Web 看板: http://localhost:5000")
        print("📊 功能: 仪表板 | 股票管理 | 数据查询 | 图表分析")
        app.run(host='0.0.0.0', port=5000, debug=True)
