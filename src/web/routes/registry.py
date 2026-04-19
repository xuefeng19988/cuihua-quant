"""
Phase 269: 路由注册表
集中管理所有路由模块的注册
"""

from typing import Any
from flask import Flask


def register_all_routes(app: Flask, helpers: dict[str, Any]) -> dict[str, str]:
    """
    注册所有路由模块
    helpers: dict with token_required, get_stock_codes, get_stock_names, get_db_engine, etc.
    """
    from src.web.routes.stocks import register_stock_routes
    from src.web.routes.analysis import register_analysis_routes
    from src.web.routes.system import register_system_routes
    
    register_stock_routes(app, helpers)
    register_analysis_routes(app, helpers)
    register_system_routes(app, helpers)
    
    return {
        'stocks': 'registered',
        'analysis': 'registered',
        'system': 'registered'
    }
