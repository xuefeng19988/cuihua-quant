"""
AKShare Data Sync Module
Backup data source when Futu is unavailable.
Uses open-source AKShare library to fetch data via HTTP.
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import StockDaily, get_db_engine, init_db
from sqlalchemy.orm import sessionmaker

class AKShareSync:
    def __init__(self, config_path=None):
        # Load Env
        load_dotenv(os.path.join(project_root, '.env'))
        
        # Load Config
        if not config_path:
            config_path = os.path.join(project_root, 'config', 'stocks.yaml')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        # DB Setup
        init_db()
        self.engine = get_db_engine()
        self.Session = sessionmaker(bind=self.engine)

    def convert_code(self, code: str) -> str:
        """
        Convert Futu code format to AKShare format.
        Futu: "SH.600519" -> AKShare: "600519"
        Futu: "HK.00700"  -> AKShare: "00700" (Note: HK stocks support varies by API)
        """
        parts = code.split('.')
        if len(parts) == 2:
            return parts[1]
        return code

    def fetch_akshare_daily(self, code: str, days_back: int = 10) -> pd.DataFrame:
        """
        Fetch daily K-line data via AKShare.
        Returns DataFrame with columns: date, open, high, low, close, volume
        """
        import akshare as ak
        import time
        
        symbol = self.convert_code(code)
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%d')
        
        try:
            # A-Shares: Use "stock_zh_a_hist" (with retries)
            if code.startswith(('SH.', 'SZ.')):
                # Retry up to 3 times
                for attempt in range(3):
                    try:
                        df = ak.stock_zh_a_hist(
                            symbol=symbol,
                            period="daily",
                            start_date=start_date,
                            end_date=end_date,
                            adjust="qfq"  # Forward adjusted
                        )
                        if not df.empty:
                            break
                    except Exception as e:
                        if attempt == 2:
                            raise e
                        time.sleep(2 ** attempt)
                
                # Standardize columns
                df = df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '最高': 'high',
                    '最低': 'low',
                    '收盘': 'close',
                    '成交量': 'volume',
                    '成交额': 'turnover',
                    '涨跌幅': 'change_pct',
                    '换手率': 'turnover_rate'
                })
                
            # HK-Shares: Use "stock_hk_hist" (fallback to East Money)
            elif code.startswith('HK.'):
                for attempt in range(3):
                    try:
                        df = ak.stock_hk_hist(
                            symbol=symbol,
                            period="daily",
                            start_date=start_date,
                            end_date=end_date,
                            adjust="qfq"
                        )
                        if not df.empty:
                            break
                    except Exception as e:
                        if attempt == 2:
                            raise e
                        time.sleep(2 ** attempt)
                
                df = df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '最高': 'high',
                    '最低': 'low',
                    '收盘': 'close',
                    '成交量': 'volume',
                    '成交额': 'turnover',
                    '涨跌幅': 'change_pct',
                    '换手率': 'turnover_rate'
                })
            else:
                print(f"⚠️  Unsupported code format: {code}")
                return pd.DataFrame()
                
            if df.empty:
                print(f"⚠️  AKShare returned no data for {code}")
                return pd.DataFrame()
                
            return df
            
        except Exception as e:
            print(f"❌ AKShare Error for {code}: {e}")
            return pd.DataFrame()

    def sync_stock(self, code: str, days_back: int = 10):
        """Sync single stock via AKShare to DB"""
        
        df = self.fetch_akshare_daily(code, days_back)
        if df.empty:
            return

        rows_to_insert = []
        for _, row in df.iterrows():
            try:
                # Handle date format
                date_str = str(row['date'])[:10]
                trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
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
                change_pct=row.get('change_pct'),
                turnover_rate=row.get('turnover_rate')
            ))

        # Upsert into DB
        try:
            session = self.Session()
            for item in rows_to_insert:
                exists = session.query(StockDaily).filter_by(code=item.code, date=item.date).first()
                if exists:
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
            print(f"✅ [AKShare] Synced {code}: {len(rows_to_insert)} records upserted.")
        except Exception as e:
            session.rollback()
            print(f"❌ DB Error for {code}: {e}")
        finally:
            session.close()

    def run(self, pool_name='watchlist', days_back=10):
        """Run Sync Process using AKShare"""
        stocks = self.get_stock_list(pool_name)
        if not stocks:
            print(f"⚠️  Pool '{pool_name}' is empty.")
            return

        print(f"🚀 [AKShare] Starting sync for pool: {pool_name} ({len(stocks)} stocks)")
        print(f"📅 Range: Last {days_back} days.")

        for i, code in enumerate(stocks):
            self.sync_stock(code, days_back)
            # Rate limiting (AKShare has no strict limits, but be polite)
            if i < len(stocks) - 1:
                import time
                time.sleep(0.5)
        
        print("🎉 [AKShare] All sync tasks finished.")

    def get_stock_list(self, pool_name='watchlist'):
        """Get list of stocks from config pool"""
        pools = self.config.get('pools', {})
        pool = pools.get(pool_name, {})
        return pool.get('stocks', [])


if __name__ == "__main__":
    # Test AKShare sync
    syncer = AKShareSync()
    syncer.run(pool_name='csi300_top', days_back=5)
