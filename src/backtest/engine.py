"""
Backtest Engine Module
Wraps Backtrader to run strategies on data from our local DB.
"""

import os
import sys
import backtrader as bt
import pandas as pd
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.database import get_db_engine

class SQLDataFeed(bt.feeds.PandasData):
    """
    Custom Data Feed to load data from our SQL DataFrame.
    """
    params = (
        ('datetime', 'date'),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', None),
    )

def prepare_data(engine, code, start_date, end_date):
    """
    Query DB and format for Backtrader.
    """
    query = f"""
        SELECT date, open_price as open, high_price as high, low_price as low, 
               close_price as close, volume 
        FROM stock_daily 
        WHERE code = '{code}' AND date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date ASC
    """
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df['date'])
    return df

def run_backtest(code, strategy_cls, cash=100000, start_date='2025-01-01'):
    """
    Run a single strategy backtest on a specific stock.
    """
    engine = get_db_engine()
    df = prepare_data(engine, code, start_date, datetime.now().strftime('%Y-%m-%d'))
    
    if df.empty:
        print(f"⚠️  No data for {code} in range.")
        return

    cerebro = bt.Cerebro()
    
    # Add Data
    data = SQLDataFeed(dataname=df)
    cerebro.adddata(data)
    
    # Add Strategy
    cerebro.addstrategy(strategy_cls)
    
    # Settings
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001) # 0.1% Commission
    
    # Run
    print(f"🚀 Backtesting {code} | Start Cash: {cerebro.broker.getvalue():.2f}")
    cerebro.run()
    final_val = cerebro.broker.getvalue()
    print(f"🏁 End Cash: {final_val:.2f} | PnL: {final_val - cash:.2f}")
