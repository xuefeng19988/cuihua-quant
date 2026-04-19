"""
Phase 269: 系统路由模块
系统统计、缓存管理、健康检查
"""

def register_system_routes(app, helpers):
    """注册系统相关路由"""
    from flask import request, jsonify

    @app.route('/api/cache/stats', methods=['GET'])
    @helpers['token_required']
    def api_cache_stats():
        """缓存统计 (Phase 268)"""
        stats = {
            'simple_cache': {
                'entries': len(helpers.get('_api_cache', {})),
                'ttl_entries': len(helpers.get('_api_cache_ttl', {}))
            }
        }
        if helpers.get('advanced_cache'):
            stats['advanced_cache'] = helpers['advanced_cache'].to_dict()
        return jsonify({'code': 200, 'data': stats})

    @app.route('/api/cache/clear', methods=['POST'])
    @helpers['token_required']
    def api_cache_clear():
        """清空缓存 (Phase 268)"""
        if helpers.get('advanced_cache'):
            helpers['advanced_cache'].clear()
        if '_api_cache' in helpers:
            helpers['_api_cache'].clear()
        if '_api_cache_ttl' in helpers:
            helpers['_api_cache_ttl'].clear()
        return jsonify({'code': 200, 'message': '缓存已清空'})

    @app.route('/api/system/stats', methods=['GET'])
    @helpers['token_required']
    def api_system_stats():
        """系统统计"""
        request_times = helpers.get('_request_times', {})
        stats = {}
        for endpoint, data in request_times.items():
            stats[endpoint] = {
                **data,
                'avg': round(data['total'] / data['count'], 2) if data['count'] > 0 else 0
            }
        return jsonify({
            'code': 200,
            'data': {
                'api_performance': stats,
                'uptime': '运行中'
            }
        })

    @app.route('/api/health', methods=['GET'])
    def api_health():
        """健康检查"""
        try:
            engine = helpers['get_db_engine']()
            db_ok = False
            if engine:
                from sqlalchemy import text
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    db_ok = True
            return jsonify({
                'code': 200,
                'data': {
                    'status': 'healthy' if db_ok else 'degraded',
                    'database': 'connected' if db_ok else 'disconnected',
                    'api_version': '5.1.0'
                }
            })
        except Exception as e:
            return jsonify({'code': 500, 'data': {'status': 'unhealthy', 'error': str(e)}})

    @app.route('/api/docs', methods=['GET'])
    def api_docs():
        """API 文档"""
        rules = []
        for rule in app.url_map.iter_rules():
            if '/api/' in rule.rule:
                rules.append({
                    'endpoint': rule.rule,
                    'methods': sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]),
                    'description': rule.endpoint
                })
        return jsonify({
            'code': 200,
            'data': {
                'name': '翠花量化系统 API',
                'version': '5.1.0',
                'total_endpoints': len(rules),
                'endpoints': rules
            }
        })
