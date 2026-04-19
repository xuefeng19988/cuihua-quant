"""
US Stock Market Support
Integrates US stock data via Alpha Vantage / Polygon APIs.
"""

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import StockDaily, get_db_engine, init_db
from sqlalchemy.orm import sessionmaker

class USStockFetcher:
    """
    Fetches US stock data from free APIs.
    Supports: Alpha Vantage, Finnhub (free tiers).
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_KEY', 'demo')
        self.base_url = 'https://www.alphavantage.co/query'
        self.engine = get_db_engine()
        self.Session = sessionmaker(bind=self.engine)
        
    def fetch_daily(self, symbol: str, outputsize: str = 'compact') -> pd.DataFrame:
        """
        Fetch daily OHLCV data for US stock.
        
        Args:
            symbol: US stock ticker (e.g., 'AAPL', 'MSFT')
            outputsize: 'compact' (100 days) or 'full' (20+ years)
            
        Returns:
            DataFrame with OHLCV data
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                print(f"⚠️ API error for {symbol}: {data.get('Information', data.get('Note', ''))}")
                return pd.DataFrame()
                
            ts = data['Time Series (Daily)']
            rows = []
            for date, values in ts.items():
                rows.append({
                    'date': date,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
                
            df = pd.DataFrame(rows)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return pd.DataFrame()
            
    def save_to_db(self, symbol: str, df: pd.DataFrame) -> int:
        """Save US stock data to database with US. prefix."""
        if df.empty:
            return 0
            
        code = f"US.{symbol}"
        count = 0
        
        try:
            session = self.Session()
            for _, row in df.iterrows():
                exists = session.query(StockDaily).filter_by(code=code, date=row['date'].date()).first()
                if exists:
                    exists.open_price = row['open']
                    exists.high_price = row['high']
                    exists.low_price = row['low']
                    exists.close_price = row['close']
                    exists.volume = row['volume']
                else:
                    session.add(StockDaily(
                        code=code,
                        date=row['date'].date(),
                        open_price=row['open'],
                        high_price=row['high'],
                        low_price=row['low'],
                        close_price=row['close'],
                        volume=row['volume']
                    ))
                count += 1
                
            session.commit()
            print(f"✅ Saved {count} records for {code}")
            return count
            
        except Exception as e:
            session.rollback()
            print(f"❌ DB error for {code}: {e}")
            return 0
        finally:
            session.close()
            
    def fetch_and_save(self, symbols: List[str]) -> Dict[str, int]:
        """Fetch and save multiple US stocks."""
        results = {}
        for symbol in symbols:
            df = self.fetch_daily(symbol)
            count = self.save_to_db(symbol, df)
            results[symbol] = count
            import time
            time.sleep(12)  # Alpha Vantage free tier: 5 calls/min
            
        return results
        
    def get_us_stocks_report(self) -> str:
        """Generate report of US stocks in database."""
        try:
            df = pd.read_sql(
                "SELECT code, COUNT(*) as cnt, MAX(date) as last FROM stock_daily WHERE code LIKE 'US.%' GROUP BY code",
                self.engine
            )
            
            if df.empty:
                return "⚠️ No US stock data in database"
                
            lines = ["📊 US Stock Data Coverage", "=" * 40]
            for _, row in df.iterrows():
                lines.append(f"  {row['code']}: {row['cnt']} records (last: {row['last']})")
                
            return "\n".join(lines)
        except Exception as e:
            return f"⚠️ Error: {e}"


if __name__ == "__main__":
    fetcher = USStockFetcher()
    # Test with demo API (limited)
    df = fetcher.fetch_daily('AAPL', outputsize='compact')
    if not df.empty:
        print(f"Fetched {len(df)} records for AAPL")
        print(df.tail())
        fetcher.save_to_db('AAPL', df)
