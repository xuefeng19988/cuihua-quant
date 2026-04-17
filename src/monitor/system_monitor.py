"""
System Monitor
Monitors system health, data freshness, and pipeline status.
"""

import os
import sys
import time
import yaml
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine
from src.data.futu_sync import FutuSync

class SystemMonitor:
    """
    Monitors system health and data freshness.
    """
    
    def __init__(self):
        self.engine = get_db_engine()
        
    def check_futu_connection(self) -> Dict:
        """Check Futu OpenD connection."""
        from futu import OpenQuoteContext, RET_OK
        try:
            ctx = OpenQuoteContext(host='127.0.0.1', port=11112)
            ret, data = ctx.get_global_state()
            ctx.close()
            
            if ret == RET_OK:
                return {'status': 'OK', 'message': 'Futu OpenD connected'}
            return {'status': 'ERROR', 'message': f'Futu connection failed: {data}'}
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
            
    def check_data_freshness(self) -> Dict:
        """Check if data is up-to-date."""
        import pandas as pd
        
        try:
            df = pd.read_sql(
                "SELECT code, MAX(date) as last_date, COUNT(*) as cnt FROM stock_daily GROUP BY code",
                self.engine
            )
            
            if df.empty:
                return {'status': 'WARN', 'message': 'No data in database'}
                
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Count stocks with recent data
            recent_count = 0
            stale_count = 0
            for _, row in df.iterrows():
                last_date = pd.to_datetime(row['last_date']).date()
                if last_date >= yesterday:
                    recent_count += 1
                else:
                    stale_count += 1
                    
            return {
                'status': 'OK' if stale_count == 0 else 'WARN',
                'total_stocks': len(df),
                'recent_stocks': recent_count,
                'stale_stocks': stale_count,
                'message': f'{recent_count}/{len(df)} stocks with recent data'
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
            
    def check_disk_space(self) -> Dict:
        """Check disk space usage."""
        import shutil
        
        total, used, free = shutil.disk_usage(project_root)
        used_pct = used / total * 100
        
        return {
            'status': 'OK' if used_pct < 80 else 'WARN',
            'total_gb': total / 1e9,
            'used_gb': used / 1e9,
            'free_gb': free / 1e9,
            'used_pct': used_pct,
            'message': f'Disk: {used_pct:.1f}% used ({free/1e9:.1f}GB free)'
        }
        
    def check_process_status(self) -> Dict:
        """Check if required processes are running."""
        processes = {
            'openclaw': False,
            'Futu': False,
            'python3': False
        }
        
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            output = result.stdout
            
            for proc in processes:
                if proc.lower() in output.lower():
                    processes[proc] = True
                    
            return {
                'status': 'OK' if all(processes.values()) else 'WARN',
                'processes': processes,
                'message': f'Processes: {sum(processes.values())}/{len(processes)} running'
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
            
    def generate_health_report(self) -> str:
        """Generate comprehensive health report."""
        lines = []
        lines.append("=" * 50)
        lines.append("🏥 系统健康报告")
        lines.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 50)
        
        # Check all
        checks = {
            'Futu 连接': self.check_futu_connection(),
            '数据新鲜度': self.check_data_freshness(),
            '磁盘空间': self.check_disk_space(),
            '进程状态': self.check_process_status()
        }
        
        all_ok = True
        for name, result in checks.items():
            status = result.get('status', 'UNKNOWN')
            icon = "✅" if status == 'OK' else ("⚠️" if status == 'WARN' else "❌")
            if status != 'OK':
                all_ok = False
            lines.append(f"  {icon} {name}: {result.get('message', '')}")
            
        lines.append(f"\n{'✅ 系统正常' if all_ok else '⚠️ 存在问题需要关注'}")
        lines.append("=" * 50)
        
        return "\n".join(lines)
        
    def run_periodic_check(self, interval_minutes: int = 30):
        """Run periodic health checks."""
        while True:
            report = self.generate_health_report()
            print(report)
            print(f"\n⏰ Next check in {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    monitor = SystemMonitor()
    print(monitor.generate_health_report())
