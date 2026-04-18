"""
数据可视化模块 - Phase 222
提供动态数据刷新和高级图表数据
"""
from flask import Blueprint, request, jsonify
import random
from datetime import datetime, timedelta

viz_bp = Blueprint('visualization', __name__)

@viz_bp.route('/api/viz/realtime-data', methods=['GET'])
def get_realtime_data():
    """获取实时数据（模拟）"""
    code = request.args.get('code', 'SH.600519')
    interval = request.args.get('interval', '1m')
    
    # 模拟实时数据
    now = datetime.now()
    data_points = []
    
    for i in range(60):
        timestamp = now - timedelta(minutes=60-i)
        data_points.append({
            'time': timestamp.strftime('%H:%M'),
            'price': round(random.uniform(1700, 1750), 2),
            'volume': random.randint(100, 1000)
        })
    
    return jsonify({
        'code': 200,
        'data': {
            'code': code,
            'interval': interval,
            'data': data_points,
            'last_update': now.isoformat()
        }
    })

@viz_bp.route('/api/viz/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """获取仪表板数据"""
    return jsonify({
        'code': 200,
        'data': {
            'market_overview': {
                'sh_index': round(random.uniform(3200, 3400), 2),
                'sz_index': round(random.uniform(11000, 11500), 2),
                'cy_index': round(random.uniform(2200, 2400), 2),
                'up_count': random.randint(1500, 2500),
                'down_count': random.randint(1500, 2500),
                'flat_count': random.randint(100, 300)
            },
            'portfolio_summary': {
                'total_value': round(random.uniform(900000, 1100000), 2),
                'daily_pnl': round(random.uniform(-10000, 15000), 2),
                'total_pnl': round(random.uniform(50000, 150000), 2),
                'position_ratio': round(random.uniform(60, 90), 2)
            },
            'top_gainers': [
                {'code': 'SH.600519', 'name': '贵州茅台', 'change': round(random.uniform(3, 8), 2)},
                {'code': 'SZ.300750', 'name': '宁德时代', 'change': round(random.uniform(3, 8), 2)},
                {'code': 'SZ.002594', 'name': '比亚迪', 'change': round(random.uniform(3, 8), 2)}
            ],
            'top_losers': [
                {'code': 'SH.601318', 'name': '中国平安', 'change': round(random.uniform(-8, -3), 2)},
                {'code': 'SH.600036', 'name': '招商银行', 'change': round(random.uniform(-8, -3), 2)}
            ]
        }
    })

@viz_bp.route('/api/viz/heatmap-data', methods=['GET'])
def get_heatmap_data():
    """获取热力图数据"""
    sectors = ['白酒', '新能源', '金融', '科技', '医药', '消费', '地产', '军工']
    stocks = {
        '白酒': ['贵州茅台', '五粮液', '泸州老窖'],
        '新能源': ['宁德时代', '比亚迪', '隆基绿能'],
        '金融': ['中国平安', '招商银行', '兴业银行'],
        '科技': ['海康威视', '科大讯飞', '中兴通讯'],
        '医药': ['恒瑞医药', '药明康德', '迈瑞医疗'],
        '消费': ['美的集团', '格力电器', '海尔智家'],
        '地产': ['万科A', '保利地产', '招商蛇口'],
        '军工': ['中航沈飞', '航发动力', '中国卫星']
    }
    
    heatmap_data = []
    for sector in sectors:
        for stock in stocks[sector]:
            heatmap_data.append({
                'sector': sector,
                'name': stock,
                'change': round(random.uniform(-10, 10), 2),
                'volume': random.randint(10000, 100000)
            })
    
    return jsonify({
        'code': 200,
        'data': {
            'sectors': sectors,
            'stocks': heatmap_data
        }
    })
