#!/usr/bin/env python3
"""
Cuihua Quant CLI
Command-line interface for the Cuihua Quant System.
"""

import os
import sys
import yaml
import argparse
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def cmd_sync(args):
    """Sync market data."""
    from src.data.futu_sync import FutuSync
    from src.data.akshare_sync import AKShareSync
    
    print("🔄 Syncing market data...")
    
    # Try Futu first
    syncer = FutuSync()
    if syncer.connect():
        syncer.run(pool_name=args.pool, days_back=args.days)
        syncer.close()
    else:
        print("🔄 Falling back to AKShare...")
        ak_syncer = AKShareSync()
        ak_syncer.run(pool_name=args.pool, days_back=args.days)

def cmd_analyze(args):
    """Run analysis and generate signals."""
    from src.analysis.signal_gen import SignalGenerator
    from src.data.database import get_db_engine
    
    print("🧠 Analyzing market data...")
    
    # Load stock codes
    cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)
        
    codes = cfg.get('pools', {}).get(args.pool, {}).get('stocks', [])
    if not codes:
        print(f"⚠️ Pool '{args.pool}' is empty.")
        return
        
    gen = SignalGenerator()
    df = gen.generate_combined_signal(codes)
    
    if df is not None and not df.empty:
        print(f"\n📈 Top {args.top} Signals:")
        print("-" * 60)
        for _, row in df.head(args.top).iterrows():
            signals_str = ', '.join(row['signals']) if row['signals'] else 'None'
            print(f"#{row['rank']} {row['code']}: Score {row['combined_score']:.3f} | Close {row['close']:.2f}")
            print(f"    Signals: {signals_str}")
    else:
        print("⚠️ No signals generated.")

def cmd_backtest(args):
    """Run backtest."""
    from src.backtest.engine import run_backtest
    from src.strategy.sma_cross import SmaCross
    
    # Load stock codes
    cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)
        
    codes = cfg.get('pools', {}).get(args.pool, {}).get('stocks', [])
    if not codes:
        print(f"⚠️ Pool '{args.pool}' is empty.")
        return
        
    target = codes[0]  # Backtest first stock in pool
    print(f"📉 Backtesting {target} with SmaCross strategy...")
    run_backtest(target, SmaCross, cash=args.capital, start_date=args.start_date)

def cmd_pipeline(args):
    """Run full trading pipeline."""
    from src.execution.pipeline import TradingPipeline
    
    print("🚀 Running Trading Pipeline...")
    pipeline = TradingPipeline()
    pipeline.run(execute=args.execute)

def cmd_status(args):
    """Show system status."""
    from src.data.database import get_db_engine
    from sqlalchemy import text
    
    print("=" * 50)
    print("📊 Cuihua Quant System Status")
    print("=" * 50)
    
    # Check DB
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM stock_daily"))
            count = result.scalar()
            print(f"✅ Database: {count} records")
    except Exception as e:
        print(f"❌ Database: {e}")
        
    # Check Futu
    from futu import OpenQuoteContext, RET_OK
    try:
        ctx = OpenQuoteContext(host='127.0.0.1', port=11112)
        ret, _ = ctx.get_global_state()
        if ret == RET_OK:
            print("✅ Futu OpenD: Connected")
        ctx.close()
    except Exception as e:
        print(f"⚠️ Futu OpenD: Not connected ({e})")
        
    # Check config
    config_files = ['app.yaml', 'stocks.yaml', 'schedule.yaml']
    config_dir = os.path.join(project_root, 'config')
    for fname in config_files:
        fpath = os.path.join(config_dir, fname)
        if os.path.exists(fpath):
            print(f"✅ Config: {fname}")
        else:
            print(f"⚠️ Config: {fname} (missing)")

def main():
    parser = argparse.ArgumentParser(description="Cuihua Quant System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command
    parser_sync = subparsers.add_parser('sync', help='Sync market data')
    parser_sync.add_argument('--pool', default='watchlist', help='Stock pool name')
    parser_sync.add_argument('--days', type=int, default=5, help='Days back to fetch')
    
    # Analyze command
    parser_analyze = subparsers.add_parser('analyze', help='Generate trading signals')
    parser_analyze.add_argument('--pool', default='watchlist', help='Stock pool name')
    parser_analyze.add_argument('--top', type=int, default=5, help='Number of top signals to show')
    
    # Backtest command
    parser_backtest = subparsers.add_parser('backtest', help='Run backtest')
    parser_backtest.add_argument('--pool', default='watchlist', help='Stock pool name')
    parser_backtest.add_argument('--capital', type=float, default=100000, help='Starting capital')
    parser_backtest.add_argument('--start-date', default='2025-01-01', help='Backtest start date')
    
    # Pipeline command
    parser_pipeline = subparsers.add_parser('pipeline', help='Run full trading pipeline')
    parser_pipeline.add_argument('--execute', action='store_true', help='Execute trades (paper trading)')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if args.command == 'sync':
        cmd_sync(args)
    elif args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'backtest':
        cmd_backtest(args)
    elif args.command == 'pipeline':
        cmd_pipeline(args)
    elif args.command == 'status':
        cmd_status(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
