#!/usr/bin/env python3
"""
性能监控脚本
检查系统关键指标
"""
import os
import sys
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def check_api_response_time():
    """检查API响应时间"""
    from src.web.api_server import app
    times = []
    endpoints = ['/api/health', '/api/stats']
    
    with app.test_client() as client:
        for ep in endpoints:
            start = time.time()
            resp = client.get(ep)
            elapsed = (time.time() - start) * 1000
            times.append({'endpoint': ep, 'time_ms': round(elapsed, 2), 'status': resp.status_code})
    
    return times

def check_db_health():
    """检查数据库健康"""
    from src.data.database import get_db_engine
    from sqlalchemy import text
    engine = get_db_engine()
    if not engine:
        return {'status': 'error', 'message': '数据库连接失败'}
    
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        return {'status': 'ok', 'message': '数据库连接正常'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_config():
    """检查配置文件"""
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
    required = ['stocks.yaml', 'auth.yaml']
    missing = [f for f in required if not os.path.exists(os.path.join(config_dir, f))]
    return {'status': 'ok' if not missing else 'warning', 'missing': missing}

def main():
    print("=" * 50)
    print("🔍 翠花量化系统 - 性能监控报告")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 数据库健康
    print("\n📊 数据库健康检查:")
    db_health = check_db_health()
    print(f"   状态: {db_health['status']}")
    if db_health.get('message'):
        print(f"   详情: {db_health['message']}")
    
    # API响应时间
    print("\n⚡ API响应时间:")
    api_times = check_api_response_time()
    for t in api_times:
        status = "✅" if t['time_ms'] < 100 else "⚠️" if t['time_ms'] < 500 else "🔴"
        print(f"   {status} {t['endpoint']}: {t['time_ms']}ms ({t['status']})")
    
    # 配置检查
    print("\n⚙️ 配置文件检查:")
    config_status = check_config()
    print(f"   状态: {config_status['status']}")
    if config_status.get('missing'):
        print(f"   缺失: {', '.join(config_status['missing'])}")
    else:
        print("   所有配置文件齐全")
    
    # 系统资源
    print("\n💻 系统资源:")
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        print(f"   CPU: {cpu}%")
        print(f"   内存: {mem}%")
        print(f"   磁盘: {disk}%")
    except ImportError:
        print("   ⚠️ 安装psutil以获取系统资源信息")
    
    print("\n" + "=" * 50)
    print("✅ 监控完成")
    print("=" * 50)

if __name__ == '__main__':
    main()
