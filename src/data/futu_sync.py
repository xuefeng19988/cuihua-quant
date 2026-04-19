"""
Futu Data Sync Module
Fetches data from Futu OpenAPI and syncs to local database.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime, timedelta
from futu import OpenQuoteContext, RET_OK, KLType, SysNotifyHandlerBase
from dotenv import load_dotenv

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import StockDaily, get_db_engine, init_db
from sqlalchemy.orm import sessionmaker

class FutuSync:
    def __init__(self, config_path=None):
        # Load Env
        load_dotenv(os.path.join(project_root, '.env'))
        
        # Load Config
        if not config_path:
            config_path = os.path.join(project_root, 'config', 'stocks.yaml')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        # Futu Connection
        self.host = os.getenv('FUTU_HOST', '127.0.0.1')
        self.port = int(os.getenv('FUTU_PORT', '11112'))
        self.ctx = None
        
        # DB Setup
        init_db()
        self.engine = get_db_engine()
        self.Session = sessionmaker(bind=self.engine)

    def connect(self):
        """Connect to Futu OpenD"""
        print(f"🔌 Connecting to Futu OpenD at {self.host}:{self.port}...")
        self.ctx = OpenQuoteContext(host=self.host, port=self.port)
        # Check connection
        ret, data = self.ctx.get_global_state()
        if ret != RET_OK:
            print(f"❌ Connection failed: {data}")
            return False
        print("✅ Connected.")
        return True

    def close(self):
        if self.ctx:
            self.ctx.close()
            print("🔌 Disconnected from Futu.")

    def get_stock_list(self, pool_name='watchlist'):
        """Get list of stocks from config pool"""
        pools = self.config.get('pools', {})
        pool = pools.get(pool_name, {})
        return pool.get('stocks', [])

    def get_last_synced_date(self, code):
        """Check the latest date in local DB for a stock"""
        try:
            session = self.Session()
            # Query max date for this code
            res = session.query(StockDaily.date).filter(StockDaily.code == code).order_by(StockDaily.date.desc()).first()
            session.close()
            if res and res[0]:
                return res[0]
        except Exception:
            pass
        return None

    def sync_stock(self, code, days_back=10):
        """Sync single stock history - INCREMENTAL mode to save API quota"""
        if not self.ctx:
            return

        # 1. Check local DB for last synced date
        last_date = self.get_last_synced_date(code)
        
        # 2. Determine start date
        end_date_obj = datetime.now()
        end_date = end_date_obj.strftime('%Y-%m-%d')
        
        # Check if today's data is already present (assuming market is open or just closed)
        if last_date and last_date == end_date_obj.date():
            # print(f"✅ {code} is up to date ({last_date}). Skipped.")
            return # Skip if already synced today
        
        if last_date:
            # Incremental: Start from day after last sync
            start_date_obj = last_date + timedelta(days=1)
            start_date = start_date_obj.strftime('%Y-%m-%d')
            # If start_date > end_date (e.g. weekend), skip
            if start_date_obj > end_date_obj:
                return
        else:
            # Initial sync: Go back `days_back` days
            start_date = (end_date_obj - timedelta(days=days_back)).strftime('%Y-%m-%d')

        # Fetch K-Line
        # KLType.K_DAY = Daily
        # AuType.QFQ = Forward Adjusted
        ret, df, _ = self.ctx.request_history_kline(
            code, 
            start=start_date, 
            end=end_date, 
            ktype=KLType.K_DAY, 
            autype='qfq'
        )

        if ret != RET_OK or df is None or df.empty:
            print(f"⚠️  Failed to fetch {code} ({start_date} to {end_date})")
            return

        # Process Data
        rows_to_insert = []
        for _, row in df.iterrows():
            time_str = str(row['time_key'])[:10] # YYYY-MM-DD
            try:
                trade_date = datetime.strptime(time_str, '%Y-%m-%d').date()
            except Exception as e:
                continue

            rows_to_insert.append(StockDaily(
                code=code,
                date=trade_date,
                open_price=row.get('open'),
                high_price=row.get('high'),
                low_price=row.get('low'),
                close_price=row.get('close'),
                volume=row.get('volume'),
                turnover=row.get('turnover'),
                change_pct=row.get('change_rate'), # Percent
                pe_ratio=row.get('pe_ratio'),
                turnover_rate=row.get('turnover_rate')
            ))

        # Upsert into DB
        try:
            session = self.Session()
            # Check existing
            for item in rows_to_insert:
                # Check if exists
                exists = session.query(StockDaily).filter_by(code=item.code, date=item.date).first()
                if exists:
                    # Update
                    exists.open_price = item.open_price
                    exists.high_price = item.high_price
                    exists.low_price = item.low_price
                    exists.close_price = item.close_price
                    exists.volume = item.volume
                    exists.turnover = item.turnover
                    exists.change_pct = item.change_pct
                else:
                    session.add(item)
            session.commit()
            print(f"✅ Synced {code}: {len(rows_to_insert)} records upserted.")
        except Exception as e:
            session.rollback()
            print(f"❌ DB Error for {code}: {e}")
        finally:
            session.close()

    def run(self, pool_name='watchlist', days_back=10):
        """Run Sync Process"""
        stocks = self.get_stock_list(pool_name)
        if not stocks:
            print(f"⚠️  Pool '{pool_name}' is empty.")
            return

        print(f"🚀 Starting sync for pool: {pool_name} ({len(stocks)} stocks)")
        print(f"📅 Range: Last {days_back} days.")

        for i, code in enumerate(stocks):
            self.sync_stock(code, days_back)
            # Rate limiting / Polite delay
            if i < len(stocks) - 1:
                import time
                time.sleep(0.2)
        
        print("🎉 All sync tasks finished.")

if __name__ == "__main__":
    syncer = FutuSync()
    if syncer.connect():
        syncer.run(pool_name='watchlist', days_back=5)
        syncer.close()
