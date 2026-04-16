"""
Enhanced CLI v2 - All commands
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
    from src.data.futu_sync import FutuSync
    from src.data.akshare_sync import AKShareSync
    
    syncer = FutuSync()
    if syncer.connect():
        syncer.run(pool_name=args.pool, days_back=args.days)
        syncer.close()
    else:
        print("🔄 Falling back to AKShare...")
        AKShareSync().run(pool_name=args.pool, days_back=args.days)

def cmd_analyze(args):
    from src.analysis.signal_gen import SignalGenerator
    
    with open(os.path.join(project_root, 'config', 'stocks.yaml'), 'r') as f:
        cfg = yaml.safe_load(f)
    codes = cfg.get('pools', {}).get(args.pool, {}).get('stocks', [])
    if not codes:
        print(f"⚠️ Pool '{args.pool}' is empty.")
        return
        
    gen = SignalGenerator()
    df = gen.generate_combined_signal(codes)
    if df is not None and not df.empty:
        print(f"\n📈 Top {args.top} Signals:")
        for _, row in df.head(args.top).iterrows():
            sigs = ', '.join(row['signals']) if row['signals'] else 'None'
            print(f"#{row['rank']} {row['code']}: Score {row['combined_score']:.3f} | Close {row['close']:.2f}")
            print(f"    Signals: {sigs}")

def cmd_backtest(args):
    from src.backtest.backtest_runner import BacktestRunner
    from src.strategy.sma_cross import SmaCross
    
    with open(os.path.join(project_root, 'config', 'stocks.yaml'), 'r') as f:
        cfg = yaml.safe_load(f)
    codes = cfg.get('pools', {}).get(args.pool, {}).get('stocks', [])
    if not codes:
        print(f"⚠️ Pool '{args.pool}' is empty.")
        return
        
    runner = BacktestRunner()
    df = runner.run_batch(codes[:10], SmaCross, cash=args.capital, start_date=args.start_date)
    print(runner.generate_report(df))

def cmd_pipeline(args):
    from src.execution.pipeline_v2 import TradingPipelineV2
    pipeline = TradingPipelineV2()
    pipeline.run_full_pipeline(execute_trades=args.execute, include_ml=args.ml)

def cmd_rebalance(args):
    from src.strategy.rebalancer import PortfolioRebalancer
    
    with open(os.path.join(project_root, 'config', 'stocks.yaml'), 'r') as f:
        cfg = yaml.safe_load(f)
    codes = cfg.get('pools', {}).get(args.pool, {}).get('stocks', [])
    if not codes:
        print(f"⚠️ Pool '{args.pool}' is empty.")
        return
        
    rebalancer = PortfolioRebalancer()
    if args.method == 'equal':
        alloc = rebalancer.equal_weight(codes)
    elif args.method == 'risk_parity':
        alloc = rebalancer.risk_parity(codes)
    else:
        print(f"⚠️ Unknown method: {args.method}")
        return
        
    print(f"\n💼 Portfolio Allocation ({args.method})")
    for code, weight in sorted(alloc.items(), key=lambda x: x[1], reverse=True):
        print(f"  {code}: {weight:.1%}")

def cmd_report(args):
    from src.monitor.report_generator import PerformanceReporter
    reporter = PerformanceReporter()
    if args.weekly:
        print(reporter.weekly_report())
    else:
        print(reporter.daily_report(args.date))

def cmd_status(args):
    from src.data.database import get_db_engine
    from sqlalchemy import text
    
    print("=" * 50)
    print("📊 Cuihua Quant System Status")
    print("=" * 50)
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM stock_daily")).scalar()
            print(f"✅ Database: {count} records")
    except Exception as e:
        print(f"❌ Database: {e}")
        
    from futu import OpenQuoteContext, RET_OK
    try:
        ctx = OpenQuoteContext(host='127.0.0.1', port=11112)
        ret, _ = ctx.get_global_state()
        print("✅ Futu OpenD: Connected" if ret == RET_OK else "⚠️ Futu OpenD: Not connected")
        ctx.close()
    except Exception as e:
        print(f"⚠️ Futu OpenD: {e}")
        
    for fname in ['app.yaml', 'stocks.yaml', 'strategies.yaml', 'risk.yaml']:
        fpath = os.path.join(project_root, 'config', fname)
        print(f"{'✅' if os.path.exists(fpath) else '⚠️'} Config: {fname}")

def main():
    parser = argparse.ArgumentParser(description="Cuihua Quant System CLI v2")
    sub = parser.add_subparsers(dest='command', help='Commands')
    
    p = sub.add_parser('sync'); p.add_argument('--pool', default='watchlist'); p.add_argument('--days', type=int, default=5)
    p = sub.add_parser('analyze'); p.add_argument('--pool', default='watchlist'); p.add_argument('--top', type=int, default=5)
    p = sub.add_parser('backtest'); p.add_argument('--pool', default='watchlist'); p.add_argument('--capital', type=float, default=100000); p.add_argument('--start-date', default='2025-01-01')
    p = sub.add_parser('pipeline'); p.add_argument('--execute', action='store_true'); p.add_argument('--ml', action='store_true')
    p = sub.add_parser('rebalance'); p.add_argument('--pool', default='watchlist'); p.add_argument('--capital', type=float, default=100000); p.add_argument('--method', default='equal', choices=['equal', 'risk_parity'])
    p = sub.add_parser('report'); p.add_argument('--date', default=None); p.add_argument('--weekly', action='store_true')
    sub.add_parser('status')
    
    args = parser.parse_args()
    cmds = {'sync': cmd_sync, 'analyze': cmd_analyze, 'backtest': cmd_backtest, 
            'pipeline': cmd_pipeline, 'rebalance': cmd_rebalance, 'report': cmd_report, 'status': cmd_status}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
