"""
系统优化模块 - Phase 227
数据库索引、查询优化、缓存、性能监控
"""
from flask import Blueprint, request, jsonify
import time
import functools
from datetime import datetime

optimizer_bp = Blueprint('optimizer', __name__)

# 查询性能监控
_query_stats = {}

def monitor_query(func):
    """查询性能监控装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000
        
        func_name = func.__name__
        if func_name not in _query_stats:
            _query_stats[func_name] = {'count': 0, 'total_ms': 0, 'max_ms': 0, 'min_ms': float('inf')}
        
        _query_stats[func_name]['count'] += 1
        _query_stats[func_name]['total_ms'] += elapsed
        _query_stats[func_name]['max_ms'] = max(_query_stats[func_name]['max_ms'], elapsed)
        _query_stats[func_name]['min_ms'] = min(_query_stats[func_name]['min_ms'], elapsed)
        
        return result
    return wrapper

# 简单内存缓存
_cache = {}
_cache_ttl = {}

def cache_result(ttl=300):
    """查询结果缓存装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if key in _cache and key in _cache_ttl:
                if time.time() < _cache_ttl[key]:
                    return _cache[key]
            
            result = func(*args, **kwargs)
            _cache[key] = result
            _cache_ttl[key] = time.time() + ttl
            return result
        return wrapper
    return decorator

@optimizer_bp.route('/api/system/optimize', methods=['POST'])
def optimize_system():
    """系统优化执行"""
    from src.data.database import get_db_engine
    from sqlalchemy import text
    import os
    
    results = {'success': 0, 'failed': 0, 'details': []}
    engine = get_db_engine()
    
    if engine:
        with engine.connect() as conn:
            # 1. 创建数据库索引
            indexes = [
                ("notes_title_idx", "CREATE INDEX IF NOT EXISTS notes_title_idx ON notes(title)"),
                ("notes_created_idx", "CREATE INDEX IF NOT EXISTS notes_created_idx ON notes(created_at)"),
                ("notes_status_idx", "CREATE INDEX IF NOT EXISTS notes_status_idx ON note_articles(status)"),
                ("notes_category_idx", "CREATE INDEX IF NOT EXISTS notes_category_idx ON note_articles(category)"),
                ("articles_published_idx", "CREATE INDEX IF NOT EXISTS articles_published_idx ON note_articles(published_at)"),
                ("stock_daily_code_idx", "CREATE INDEX IF NOT EXISTS stock_daily_code_idx ON stock_daily(code)"),
                ("stock_daily_date_idx", "CREATE INDEX IF NOT EXISTS stock_daily_date_idx ON stock_daily(date)"),
                ("stock_daily_code_date_idx", "CREATE INDEX IF NOT EXISTS stock_daily_code_date_idx ON stock_daily(code, date)"),
            ]
            
            for name, sql in indexes:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    results['success'] += 1
                    results['details'].append({'action': f'创建索引: {name}', 'status': 'success'})
                except Exception as e:
                    results['failed'] += 1
                    results['details'].append({'action': f'创建索引: {name}', 'status': 'failed', 'error': str(e)})
        
        # 2. 清理过期缓存
        now = time.time()
        expired_keys = [k for k, v in _cache_ttl.items() if now > v]
        for key in expired_keys:
            _cache.pop(key, None)
            _cache_ttl.pop(key, None)
        results['details'].append({'action': f'清理缓存: {len(expired_keys)} 个过期键', 'status': 'success'})
        
        # 3. 数据库VACUUM (SQLite优化)
        try:
            with engine.connect() as conn:
                conn.execute(text('VACUUM'))
                conn.execute(text('ANALYZE'))
            results['details'].append({'action': '数据库VACUUM+ANALYZE', 'status': 'success'})
        except Exception as e:
            results['details'].append({'action': '数据库VACUUM', 'status': 'failed', 'error': str(e)})
    
    # 4. 清理临时文件
    temp_dirs = ['backups', 'public/notes']
    for temp_dir in temp_dirs:
        dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), temp_dir)
        if os.path.exists(dir_path):
            try:
                files = os.listdir(dir_path)
                # 保留最近10个备份
                if 'backups' in temp_dir and len(files) > 10:
                    files.sort()
                    for old_file in files[:-10]:
                        os.remove(os.path.join(dir_path, old_file))
                results['details'].append({'action': f'清理目录: {temp_dir}', 'status': 'success'})
            except Exception as e:
                results['details'].append({'action': f'清理目录: {temp_dir}', 'status': 'failed', 'error': str(e)})
    
    return jsonify({'code': 200, 'data': results})


@optimizer_bp.route('/api/system/performance', methods=['GET'])
def get_performance():
    """获取性能统计"""
    stats = {}
    for func_name, data in _query_stats.items():
        stats[func_name] = {
            **data,
            'avg_ms': round(data['total_ms'] / data['count'], 2) if data['count'] > 0 else 0
        }
    
    return jsonify({
        'code': 200,
        'data': {
            'query_stats': stats,
            'cache_size': len(_cache),
            'uptime': '运行中'
        }
    })


@optimizer_bp.route('/api/system/cache/clear', methods=['POST'])
def clear_cache():
    """清空缓存"""
    _cache.clear()
    _cache_ttl.clear()
    return jsonify({'code': 200, 'message': '缓存已清空'})
