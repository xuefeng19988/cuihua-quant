"""
Phase 9.3: Cryptocurrency Support
Integrates crypto data via CoinGecko/Binance APIs.
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import StockDaily, get_db_engine, init_db
from sqlalchemy.orm import sessionmaker

class CryptoFetcher:
    """
    Fetches cryptocurrency data from CoinGecko API (free tier).
    Supports: BTC, ETH, and other major cryptos.
    """
    
    def __init__(self):
        self.base_url = 'https://api.coingecko.com/api/v3'
        self.engine = get_db_engine()
        self.Session = sessionmaker(bind=self.engine)
        
        # Common crypto IDs
        self.crypto_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'DOGE': 'dogecoin',
            'DOT': 'polkadot',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network'
        }
        
    def fetch_ohlcv(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        Fetch OHLCV data for crypto.
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            days: Number of days of data
            
        Returns:
            DataFrame with OHLCV data
        """
        crypto_id = self.crypto_ids.get(symbol.upper())
        if not crypto_id:
            print(f"⚠️ Unknown crypto symbol: {symbol}")
            return pd.DataFrame()
            
        url = f'{self.base_url}/coins/{crypto_id}/market_chart'
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if 'prices' not in data:
                print(f"⚠️ API error: {data.get('error', 'Unknown')}")
                return pd.DataFrame()
                
            # Convert to DataFrame
            prices = data['prices']
            volumes = data.get('total_volumes', [])
            
            df = pd.DataFrame(prices, columns=['timestamp', 'close'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
            df['close_price'] = df['close']
            
            if volumes:
                vol_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
                df['volume'] = vol_df['volume']
            else:
                df['volume'] = 0
                
            # Simplified OHLC (using close as OHLC for free API)
            df['open_price'] = df['close_price']
            df['high_price'] = df['close_price']
            df['low_price'] = df['close_price']
            
            df = df[['date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
            return df
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return pd.DataFrame()
            
    def save_to_db(self, symbol: str, df: pd.DataFrame) -> int:
        """Save crypto data to database with CRYPTO. prefix."""
        if df.empty:
            return 0
            
        code = f"CRYPTO.{symbol}"
        count = 0
        
        try:
            session = self.Session()
            for _, row in df.iterrows():
                exists = session.query(StockDaily).filter_by(code=code, date=row['date']).first()
                if exists:
                    exists.close_price = row['close_price']
                    exists.volume = row['volume']
                else:
                    session.add(StockDaily(
                        code=code,
                        date=row['date'],
                        open_price=row['open_price'],
                        high_price=row['high_price'],
                        low_price=row['low_price'],
                        close_price=row['close_price'],
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
            
    def fetch_and_save(self, symbols: List[str], days: int = 30) -> Dict[str, int]:
        """Fetch and save multiple cryptos."""
        results = {}
        for symbol in symbols:
            df = self.fetch_ohlcv(symbol, days)
            count = self.save_to_db(symbol, df)
            results[symbol] = count
            import time
            time.sleep(1)  # Rate limiting
            
        return results
        
    def get_crypto_report(self) -> str:
        """Generate report of crypto data in database."""
        try:
            import pandas as pd
            df = pd.read_sql(
                "SELECT code, COUNT(*) as cnt, MAX(date) as last FROM stock_daily WHERE code LIKE 'CRYPTO.%' GROUP BY code",
                self.engine
            )
            
            if df.empty:
                return "⚠️ No crypto data in database"
                
            lines = ["📊 Cryptocurrency Data Coverage", "=" * 40]
            for _, row in df.iterrows():
                lines.append(f"  {row['code']}: {row['cnt']} records (last: {row['last']})")
                
            return "\n".join(lines)
        except Exception as e:
            return f"⚠️ Error: {e}"


if __name__ == "__main__":
    fetcher = CryptoFetcher()
    # Test with BTC
    df = fetcher.fetch_ohlcv('BTC', days=7)
    if not df.empty:
        print(f"Fetched {len(df)} records for BTC")
        print(df.tail())
        fetcher.save_to_db('BTC', df)
