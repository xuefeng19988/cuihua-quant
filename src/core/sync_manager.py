"""
翠花量化系统 - 数据同步管理器
通过系统配置模型管理股票数据同步。
支持多数据源 (Futu/AKShare)、定时同步、批量同步。
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.core.config import config_manager
from src.data.database import get_db_engine, init_db

logger = logging.getLogger(__name__)


class SyncManager:
    """
    数据同步管理器 - 通过系统配置驱动数据同步。
    
    支持功能:
    - 多数据源切换 (futu / akshare / both)
    - 股票池选择 (watchlist / all / custom)
    - 批量同步 (batch_size 控制)
    - 定时同步 (cron 表达式)
    - 自动同步 (启动时)
    """
    
    def __init__(self):
        self.config = config_manager.load()
        self.sync_config = self.config.datasync
        init_db()
        self.engine = get_db_engine()
        self._syncer = None
        self.stats = {
            'total_synced': 0,
            'success_count': 0,
            'fail_count': 0,
            'last_sync_time': None,
            'last_sync_duration': 0,
        }
        
    def _get_syncer(self):
        """获取同步器实例"""
        source = self.sync_config.source
        if source == 'futu':
            from src.data.futu_sync import FutuSync
            return FutuSync()
        elif source == 'akshare':
            from src.data.akshare_sync import AKShareSync
            return AKShareSync()
        elif source == 'both':
            # 优先使用 primary_source
            primary = self.sync_config.primary_source
            if primary == 'futu':
                from src.data.futu_sync import FutuSync
                return FutuSync()
            else:
                from src.data.akshare_sync import AKShareSync
                return AKShareSync()
        else:
            from src.data.akshare_sync import AKShareSync
            return AKShareSync()
    
    def get_stock_codes(self) -> List[str]:
        """根据配置获取需要同步的股票代码列表"""
        pool = self.sync_config.pool
        
        if pool == 'custom':
            return self.sync_config.custom_codes
            
        # 从 stocks.yaml 读取
        import yaml
        stocks_path = os.path.join(project_root, 'config', 'stocks.yaml')
        with open(stocks_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
            
        if pool == 'watchlist':
            pool_data = cfg.get('pools', {}).get('watchlist', {})
        elif pool == 'all':
            # 合并所有池
            all_codes = []
            for p in cfg.get('pools', {}).values():
                for s in p.get('stocks', []):
                    if isinstance(s, dict):
                        all_codes.append(s['code'])
                    else:
                        all_codes.append(s)
            return list(set(all_codes))
        else:
            pool_data = cfg.get('pools', {}).get('watchlist', {})
            
        codes = []
        for s in pool_data.get('stocks', []):
            if isinstance(s, dict):
                codes.append(s['code'])
            else:
                codes.append(s)
        return codes
    
    def sync_all(self, progress_callback=None) -> Dict:
        """
        同步所有股票数据
        
        Args:
            progress_callback: 进度回调函数 (current, total, code, status)
            
        Returns:
            同步统计信息
        """
        start_time = time.time()
        codes = self.get_stock_codes()
        total = len(codes)
        
        logger.info(f"🔄 开始同步 {total} 只股票 (数据源: {self.sync_config.source})")
        
        self.stats = {
            'total_synced': total,
            'success_count': 0,
            'fail_count': 0,
            'last_sync_time': datetime.now().isoformat(),
            'last_sync_duration': 0,
            'details': []
        }
        
        syncer = self._get_syncer()
        batch_size = self.sync_config.batch_size
        
        # 分批同步
        for i in range(0, total, batch_size):
            batch = codes[i:i+batch_size]
            for code in batch:
                try:
                    if hasattr(syncer, 'sync_single'):
                        result = syncer.sync_single(code, days=self.sync_config.days_back)
                    elif hasattr(syncer, 'sync_stock'):
                        result = syncer.sync_stock(code, days=self.sync_config.days_back)
                    else:
                        # Fallback: 尝试调用 sync 方法
                        result = syncer.sync(code, days=self.sync_config.days_back)
                        
                    self.stats['success_count'] += 1
                    status = 'success'
                except Exception as e:
                    self.stats['fail_count'] += 1
                    status = f'failed: {str(e)[:50]}'
                    logger.warning(f"❌ 同步失败 {code}: {e}")
                
                if progress_callback:
                    progress_callback(i + batch.index(code) + 1, total, code, status)
                    
                self.stats['details'].append({
                    'code': code,
                    'status': status
                })
                
                # 间隔防限流
                if self.sync_config.interval_seconds > 0:
                    time.sleep(self.sync_config.interval_seconds)
        
        self.stats['last_sync_duration'] = round(time.time() - start_time, 2)
        logger.info(f"✅ 同步完成: {self.stats['success_count']} 成功, {self.stats['fail_count']} 失败, 耗时 {self.stats['last_sync_duration']}s")
        
        return self.stats
    
    def sync_single(self, code: str) -> Dict:
        """同步单只股票"""
        syncer = self._get_syncer()
        try:
            if hasattr(syncer, 'sync_single'):
                result = syncer.sync_single(code, days=self.sync_config.days_back)
            elif hasattr(syncer, 'sync_stock'):
                result = syncer.sync_stock(code, days=self.sync_config.days_back)
            else:
                result = syncer.sync(code, days=self.sync_config.days_back)
            return {'code': code, 'status': 'success'}
        except Exception as e:
            return {'code': code, 'status': f'failed: {str(e)}'}
    
    def get_status(self) -> Dict:
        """获取同步状态"""
        return {
            'config': {
                'source': self.sync_config.source,
                'pool': self.sync_config.pool,
                'days_back': self.sync_config.days_back,
                'batch_size': self.sync_config.batch_size,
                'interval_seconds': self.sync_config.interval_seconds,
                'auto_sync_on_start': self.sync_config.auto_sync_on_start,
                'schedule_cron': self.sync_config.schedule_cron,
            },
            'stats': self.stats,
            'stock_count': len(self.get_stock_codes()),
        }
    
    def update_config(self, **kwargs) -> bool:
        """更新同步配置"""
        valid_keys = [
            'source', 'pool', 'custom_codes', 'days_back',
            'interval_seconds', 'batch_size', 'auto_sync_on_start',
            'schedule_cron', 'primary_source', 'fallback_source',
            'max_retries', 'log_level'
        ]
        for key, value in kwargs.items():
            if key in valid_keys and hasattr(self.sync_config, key):
                setattr(self.sync_config, key, value)
        logger.info(f"📝 同步配置已更新: {kwargs}")
        return True


# Global instance
sync_manager = SyncManager()
