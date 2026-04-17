"""
翠花量化系统 - 公共工具模块
统一封装常用的重复代码，减少冗余。
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# 项目根目录（所有模块统一使用）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ensure_project_path():
    """确保项目根目录在 sys.path 中"""
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    return PROJECT_ROOT


# 自动初始化
ensure_project_path()


# ==================== 股票名称映射 ====================

def load_stock_names() -> dict:
    """
    加载股票代码到名称的映射（统一入口）
    从 config/stocks.yaml 读取，支持结构化 {code, name} 格式。
    
    Returns:
        {code: name} 字典，无名称的股票映射为空字符串
    """
    names = {}
    cfg_path = os.path.join(PROJECT_ROOT, 'config', 'stocks.yaml')
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        for pool_data in cfg.get('pools', {}).values():
            for item in pool_data.get('stocks', []):
                if isinstance(item, dict):
                    code = item.get('code', '')
                    name = item.get('name', '')
                    if code and code not in names:
                        names[code] = name
                elif isinstance(item, str) and item not in names:
                    names[item] = ''
    except Exception:
        pass
    return names


def get_stock_label(code: str, names: dict = None) -> str:
    """
    获取股票标签（代码 + 名称）
    
    Args:
        code: 股票代码
        names: 名称映射字典（可选，不传则自动加载）
    
    Returns:
        如 "SZ.002594 比亚迪"
    """
    if names is None:
        names = load_stock_names()
    name = names.get(code, '')
    return f"{code} {name}".strip() if name else code


# ==================== YAML 配置加载 ====================

def load_yaml_config(filename: str) -> dict:
    """
    加载 YAML 配置文件
    
    Args:
        filename: 配置文件路径（相对于项目根目录或绝对路径）
    
    Returns:
        配置字典，文件不存在返回空字典
    """
    if not os.path.isabs(filename):
        filename = os.path.join(PROJECT_ROOT, filename)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_stocks_config(pool_name: str = 'watchlist') -> tuple:
    """
    加载股票池配置
    
    Args:
        pool_name: 股票池名称
    
    Returns:
        (codes_list, names_dict) 代码列表和名称映射
    """
    cfg = load_yaml_config('config/stocks.yaml')
    pool = cfg.get('pools', {}).get(pool_name, {})
    raw_stocks = pool.get('stocks', [])
    
    codes = []
    names = {}
    for item in raw_stocks:
        if isinstance(item, dict):
            code = item.get('code', '')
            name = item.get('name', '')
            codes.append(code)
            names[code] = name
        else:
            codes.append(item)
            names[item] = ''
    
    return codes, names


# ==================== 日期工具 ====================

def format_date_cn(dt) -> str:
    """
    将日期格式化为中文格式
    
    Args:
        dt: datetime 对象或日期字符串
    
    Returns:
        "2026年04月17日"
    """
    if isinstance(dt, str):
        dt = pd.to_datetime(dt)
    return dt.strftime('%Y年%m月%d日')


def format_dates_cn(dates) -> List[str]:
    """
    批量格式化日期为中文
    
    Args:
        dates: 日期列表或 Series
    
    Returns:
        中文日期列表
    """
    if isinstance(dates, pd.Series):
        return dates.dt.strftime('%Y年%m月%d日').tolist()
    return [format_date_cn(d) for d in dates]


def now_str(fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """当前时间格式化字符串"""
    return datetime.now().strftime(fmt)


def today_str() -> str:
    """今天日期字符串 YYYY-MM-DD"""
    return datetime.now().strftime('%Y-%m-%d')


# ==================== 数据库工具 ====================

def get_db_engine():
    """获取数据库引擎"""
    from src.data.database import get_db_engine
    return get_db_engine()


def query_stock_latest(code: str, days: int = 1, columns: str = '*'):
    """
    查询股票最新数据
    
    Args:
        code: 股票代码
        days: 最近天数
        columns: 查询列
    
    Returns:
        DataFrame
    """
    engine = get_db_engine()
    query = f"SELECT {columns} FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT {days}"
    return pd.read_sql(query, engine)


# ==================== 数据验证 ====================

def validate_date(date_str: str) -> bool:
    """验证日期格式 YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def validate_stock_code(code: str) -> bool:
    """验证股票代码格式 (SH/SZ/HK.XXXXXX)"""
    if not code or '.' not in code:
        return False
    parts = code.split('.')
    if len(parts) != 2:
        return False
    return parts[0] in ('SH', 'SZ', 'HK') and len(parts[1]) == 6


# ==================== 指标计算 ====================

def calc_sharpe(returns: pd.Series, risk_free: float = 0.03) -> float:
    """
    计算夏普比率
    
    Args:
        returns: 收益率序列
        risk_free: 无风险利率（年化）
    
    Returns:
        夏普比率
    """
    if returns.empty or returns.std() == 0:
        return 0.0
    excess = returns - risk_free / 252
    return (excess.mean() / excess.std()) * (252 ** 0.5)


def calc_max_drawdown(equity: pd.Series) -> float:
    """
    计算最大回撤
    
    Args:
        equity: 净值序列
    
    Returns:
        最大回撤（负值）
    """
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    return drawdown.min()


def calc_win_rate(pnls: pd.Series) -> float:
    """
    计算胜率
    
    Args:
        pnls: 盈亏序列
    
    Returns:
        胜率 (0-1)
    """
    if pnls.empty:
        return 0.0
    return (pnls > 0).sum() / len(pnls)


def calc_profit_factor(pnls: pd.Series) -> float:
    """
    计算盈亏比
    
    Args:
        pnls: 盈亏序列
    
    Returns:
        盈亏比
    """
    if pnls.empty:
        return 0.0
    total_profit = pnls[pnls > 0].sum()
    total_loss = abs(pnls[pnls < 0].sum())
    if total_loss == 0:
        return float('inf') if total_profit > 0 else 0.0
    return total_profit / total_loss
