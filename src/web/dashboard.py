"""
Web Dashboard
Simple Flask-based web interface for monitoring.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

def create_app():
    """Create Flask application."""
    try:
        from flask import Flask, jsonify, render_template_string
    except ImportError:
        print("⚠️ Flask not installed. Run: pip install flask")
        return None
        
    app = Flask(__name__)
    
    # Template
    DASHBOARD_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>翠花量化 - 监控看板</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #1a73e8; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .header h1 { margin: 0; font-size: 24px; }
            .header p { margin: 5px 0 0; opacity: 0.9; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .card h2 { margin: 0 0 15px; font-size: 18px; color: #333; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }
            .metric { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
            .metric:last-child { border-bottom: none; }
            .metric-label { color: #666; }
            .metric-value { font-weight: bold; color: #333; }
            .positive { color: #0d904f; }
            .negative { color: #d93025; }
            .status { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .status-ok { background: #e6f4ea; color: #0d904f; }
            .status-warn { background: #fef7e0; color: #f9ab00; }
            .status-error { background: #fce8e6; color: #d93025; }
            .refresh { text-align: center; margin-top: 20px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🦜 翠花量化 - 监控看板</h1>
                <p>最后更新: {{ update_time }}</p>
            </div>
            <div class="grid">
                <div class="card">
                    <h2>📊 系统状态</h2>
                    {% for item in system_status %}
                    <div class="metric">
                        <span class="metric-label">{{ item.name }}</span>
                        <span class="metric-value status {{ item.status_class }}">{{ item.value }}</span>
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
            <div class="refresh">
                <p>自动刷新: 每 60 秒 | <a href="javascript:location.reload()">立即刷新</a></p>
            </div>
        </div>
        <script>
            setTimeout(() => location.reload(), 60000);
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def dashboard():
        """Main dashboard."""
        from src.monitor.system_monitor import SystemMonitor
        from src.data.trade_logger import TradeLogger
        from src.data.database import get_db_engine
        import pandas as pd
        
        monitor = SystemMonitor()
        logger = TradeLogger()
        
        # System status
        futu = monitor.check_futu_connection()
        data = monitor.check_data_freshness()
        disk = monitor.check_disk_space()
        
        system_status = [
            {'name': 'Futu 连接', 'value': '✅ 正常' if futu['status'] == 'OK' else '❌ 异常', 'status_class': 'status-ok' if futu['status'] == 'OK' else 'status-error'},
            {'name': '数据新鲜度', 'value': data.get('message', ''), 'status_class': 'status-ok' if data['status'] == 'OK' else 'status-warn'},
            {'name': '磁盘空间', 'value': disk.get('message', ''), 'status_class': 'status-ok' if disk['status'] == 'OK' else 'status-warn'},
        ]
        
        # Portfolio
        summary = logger.get_summary()
        portfolio = [
            {'name': '总信号数', 'value': str(summary['total_signals']), 'class': ''},
            {'name': '总订单数', 'value': str(summary['total_orders']), 'class': ''},
            {'name': '胜率', 'value': f"{summary['win_rate']:.1%}", 'class': 'positive' if summary['win_rate'] > 0.5 else 'negative'},
            {'name': '总盈亏', 'value': f"¥{summary['total_pnl']:,.2f}", 'class': 'positive' if summary['total_pnl'] > 0 else 'negative'},
        ]
        
        # Trade stats
        trade_stats = [
            {'name': '已平仓', 'value': str(summary['closed_trades'])},
            {'name': '平均盈亏', 'value': f"¥{summary['total_pnl']/max(summary['closed_trades'],1):,.2f}"},
        ]
        
        # Data coverage
        try:
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
            DASHBOARD_TEMPLATE,
            update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            system_status=system_status,
            portfolio=portfolio,
            trade_stats=trade_stats,
            data_coverage=data_coverage
        )
        
    @app.route('/api/status')
    def api_status():
        """API endpoint for status."""
        from src.monitor.system_monitor import SystemMonitor
        monitor = SystemMonitor()
        return jsonify(monitor.generate_health_report())
        
    return app


if __name__ == "__main__":
    app = create_app()
    if app:
        print("🌐 启动 Web 看板: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
