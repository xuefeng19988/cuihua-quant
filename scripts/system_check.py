#!/usr/bin/env python3
"""
系统健康检查脚本 - Phase 232
检查系统各项指标
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def check_database():
    """检查数据库"""
    try:
        from src.data.database import get_db_engine
        from sqlalchemy import inspect, text
        engine = get_db_engine()
        if not engine:
            return False, "数据库连接失败"
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # 检查索引
        total_indexes = 0
        for table in tables:
            total_indexes += len(inspector.get_indexes(table))
        
        return True, f"表: {len(tables)}, 索引: {total_indexes}"
    except Exception as e:
        return False, str(e)

def check_modules():
    """检查模块"""
    modules_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'web', 'modules')
    if not os.path.exists(modules_dir):
        return False, "模块目录不存在"
    
    modules = [f for f in os.listdir(modules_dir) if f.endswith('.py') and f != '__init__.py']
    return True, f"模块: {len(modules)} 个"

def check_frontend():
    """检查前端构建"""
    dist_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
    if not os.path.exists(dist_dir):
        return False, "前端未构建"
    
    files = os.listdir(dist_dir)
    return True, f"构建文件: {len(files)} 个"

def check_api():
    """检查API"""
    try:
        from src.web.api_server import app
        rules = [r for r in app.url_map.iter_rules() if '/api/' in r.rule]
        return True, f"API端点: {len(rules)} 个"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("🔍 翠花量化系统 - 健康检查报告")
    print(f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    checks = [
        ("数据库", check_database),
        ("模块", check_modules),
        ("前端", check_frontend),
        ("API", check_api),
    ]
    
    all_passed = True
    for name, check_func in checks:
        passed, message = check_func()
        status = "✅" if passed else "❌"
        print(f"\n{name}: {status}")
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 系统健康检查通过")
    else:
        print("⚠️ 部分检查未通过，请查看上方详情")
    print("=" * 60)

if __name__ == '__main__':
    main()
