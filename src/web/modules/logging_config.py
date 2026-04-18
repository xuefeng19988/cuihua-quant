"""
日志配置模块 - Phase 230
结构化日志，分级输出
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app, log_dir=None, max_bytes=10*1024*1024, backup_count=5):
    """配置应用日志"""
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'logs')
    
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器 (轮转)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'cuihua_quant.log'),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 错误文件处理器
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Flask 日志
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
    
    return root_logger

class APILogger:
    """API请求日志"""
    @staticmethod
    def log_request(method, endpoint, status_code, duration_ms, client_ip):
        logging.info(f"{method} {endpoint} {status_code} {duration_ms:.2f}ms {client_ip}")
    
    @staticmethod
    def log_error(endpoint, error, client_ip):
        logging.error(f"ERROR {endpoint} {error} {client_ip}")
