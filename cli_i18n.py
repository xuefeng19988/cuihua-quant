"""
Phase 25: Multi-language CLI
Supports both Chinese and English output.
"""

import os
import sys
import argparse
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.core.i18n import i18n

def cmd_sync(args):
    from src.data.futu_sync import FutuSync
    from src.data.akshare_sync import AKShareSync
    
    print(i18n.t("sync_data"))
    syncer = FutuSync()
    if syncer.connect():
        syncer.run(pool_name=args.pool, days_back=args.days)
        syncer.close()
    else:
        print("🔄 Falling back to AKShare...")
        AKShareSync().run(pool_name=args.pool, days_back=args.days)

def cmd_analyze(args):
    from src.analysis.signal_gen import SignalGenerator
    import yaml
    
    cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)
    codes = cfg.get('pools', {}).get(args.pool, {}).get('stocks', [])
    if not codes:
        print(f"⚠️ Pool '{args.pool}' is empty.")
        return
        
    print(i18n.t("analyze_stocks", count=len(codes)))
    gen = SignalGenerator()
    df = gen.generate_combined_signal(codes)
    if df is not None and not df.empty:
        print(f"\n📈 Top {args.top} Signals:")
        for _, row in df.head(args.top).iterrows():
            sigs = ', '.join(row['signals']) if row['signals'] else 'None'
            print(f"#{row['rank']} {row['code']}: Score {row['combined_score']:.3f} | Close {row['close']:.2f}")
            print(f"    Signals: {sigs}")

def cmd_status(args):
    from src.data.database import get_db_engine
    from sqlalchemy import text
    
    print("=" * 50)
    print(i18n.t("system_status"))
    print("=" * 50)
    
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM stock_daily")).scalar()
            print(f"✅ {i18n.t('database')}: {count} {i18n.t('records')}")
    except Exception as e:
        print(f"❌ Database: {e}")
        
    from futu import OpenQuoteContext, RET_OK
    try:
        ctx = OpenQuoteContext(host='127.0.0.1', port=11112)
        ret, _ = ctx.get_global_state()
        print(i18n.t("futu_connected") if ret == RET_OK else i18n.t("futu_disconnected"))
        ctx.close()
    except Exception as e:
        print(f"⚠️ Futu OpenD: {e}")
        
    for fname in ['app.yaml', 'stocks.yaml', 'strategies.yaml', 'risk.yaml']:
        fpath = os.path.join(project_root, 'config', fname)
        icon = "✅" if os.path.exists(fpath) else "⚠️"
        print(f"{icon} {i18n.t('config')}: {fname}")

def main():
    parser = argparse.ArgumentParser(description="Cuihua Quant System CLI")
    parser.add_argument('--lang', choices=['zh', 'en'], default='zh', help='Language')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    p = subparsers.add_parser('sync')
    p.add_argument('--pool', default='watchlist')
    p.add_argument('--days', type=int, default=5)
    
    p = subparsers.add_parser('analyze')
    p.add_argument('--pool', default='watchlist')
    p.add_argument('--top', type=int, default=5)
    
    subparsers.add_parser('status')
    
    args = parser.parse_args()
    
    # Set language
    i18n.set_language(args.lang)
    
    cmds = {'sync': cmd_sync, 'analyze': cmd_analyze, 'status': cmd_status}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
