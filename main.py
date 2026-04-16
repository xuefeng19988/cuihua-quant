#!/usr/bin/env python3
"""
Cuihua Quant System - Main Entry Point

Usage:
    python main.py --mode sync       # Run data sync
    python main.py --mode analyze    # Run analysis
    python main.py --mode list-tasks # List configured tasks
"""

import os
import sys
import yaml
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Setup paths to load local modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load Env
load_dotenv()

def load_config():
    """Load all YAML configurations"""
    configs = {}
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    
    # Load YAML files
    for fname in ['app.yaml', 'stocks.yaml', 'schedule.yaml']:
        fpath = os.path.join(config_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                configs[fname.replace('.yaml', '')] = yaml.safe_load(f) or {}
    
    return configs

def main():
    parser = argparse.ArgumentParser(description="Cuihua Quant System")
    parser.add_argument("--mode", type=str, help="Execution mode: sync, analyze, list-tasks")
    parser.add_argument("--days", type=int, default=5, help="Days back to fetch data (default: 5)")
    parser.add_argument("--pool", type=str, default="watchlist", help="Stock pool name (default: watchlist)")
    
    args = parser.parse_args()
    
    # Load configs
    cfg = load_config()
    
    print(f"🚀 Cuihua Quant System v{cfg.get('app', {}).get('app', {}).get('version', '0.1.0')}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📂 Project Root: {os.path.dirname(__file__)}")

    if args.mode == 'sync':
        from src.data.futu_sync import FutuSync
        from src.data.akshare_sync import AKShareSync
        
        # 1. Try Futu first
        print("🔄 Trying Futu OpenD...")
        syncer = FutuSync()
        success = False
        if syncer.connect():
            syncer.run(pool_name=args.pool, days_back=args.days)
            syncer.close()
            success = True
        
        # 2. Fallback to AKShare if Futu fails
        if not success:
            print("🔄 Futu failed, falling back to AKShare...")
            ak_syncer = AKShareSync()
            ak_syncer.run(pool_name=args.pool, days_back=args.days)
            print("✅ AKShare fallback completed.")
            
    elif args.mode == 'analyze':
        from src.analysis.signal_gen import SignalGenerator
        from src.data.futu_sync import FutuSync
        
        # Ensure data is reasonably fresh? 
        # For now just run analysis
        cfg_stocks = cfg.get('stocks', {}).get('pools', {}).get(args.pool, {}).get('stocks', [])
        if not cfg_stocks:
            print(f"⚠️  Pool '{args.pool}' is empty.")
            return
            
        print(f"🔍 Analyzing {len(cfg_stocks)} stocks in pool '{args.pool}'...")
        gen = SignalGenerator()
        results = gen.run_analysis(cfg_stocks)
        gen.generate_report(results)
            
    elif args.mode == 'backtest':
        from src.backtest.engine import run_backtest
        from src.strategy.sma_cross import SmaCross
        
        # Run backtest on a single stock for demo
        target = cfg.get('stocks', {}).get('pools', {}).get(args.pool, {}).get('stocks', ['SH.600519'])[0]
        print(f"\n📉 Starting Backtest on {target} using SmaCross...")
        run_backtest(target, SmaCross, cash=100000, start_date='2025-01-01')
        
    elif args.mode == 'report':
        from src.analysis.signal_gen import SignalGenerator
        from src.monitor.reporter import DailyReporter
        
        cfg_stocks = cfg.get('stocks', {}).get('pools', {}).get(args.pool, {}).get('stocks', [])
        if not cfg_stocks:
            print(f"⚠️  Pool '{args.pool}' is empty.")
            return
            
        print("🔍 Generating Daily Report...")
        gen = SignalGenerator()
        signals = gen.run_analysis(cfg_stocks)
        
        reporter = DailyReporter()
        content = reporter.generate_content(signals)
        reporter.send_wecom(content)
        
    elif args.mode == 'list-tasks':
        # Print Schedule
        print(f"\n📅 Configured Schedule:")
        schedule = cfg.get('schedule', {}).get('schedule', [])
        for task in schedule:
            print(f"   - {task.get('name', 'Unknown')}: {task.get('cron', 'N/A')}")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
