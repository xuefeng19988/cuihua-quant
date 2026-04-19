"""
Phase 23.4: Sector Heatmap
Generates sector/industry rotation heatmaps.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class SectorHeatmap:
    """
    Generates sector/industry rotation heatmaps.
    """
    
    def __init__(self):
        # Sector mapping for A-shares
        self.sector_mapping = {
            'SH.600519': '白酒', 'SZ.000858': '白酒', 'SZ.002594': '新能源车',
            'SZ.300750': '新能源', 'SH.601318': '金融', 'SH.600036': '金融',
            'SZ.300059': '金融', 'SZ.000333': '家电', 'SZ.000651': '家电',
            'SZ.002415': '科技', 'SZ.002230': '科技', 'SH.600276': '医药',
            'SH.601888': '消费', 'SH.601012': '新能源', 'SZ.300014': '新能源',
            'SH.600900': '公用事业', 'SH.601985': '能源', 'SH.600011': '能源',
            'SH.601088': '能源',
        }
        
    def get_sector_returns(self, codes: List[str], period: int = 5) -> pd.DataFrame:
        """
        Calculate sector returns over a period.
        
        Returns:
            DataFrame with sector and return columns
        """
        from src.data.database import get_db_engine
        engine = get_db_engine()
        
        results = []
        for code in codes:
            df = pd.read_sql(
f"SELECT close_price FROM stock_daily WHERE code=:code "
                f"ORDER BY date DESC LIMIT {period + 1}",
                engine
            )
            if len(df) > 1:
                ret = (df.iloc[0]['close_price'] / df.iloc[-1]['close_price']) - 1
                sector = self.sector_mapping.get(code, '其他')
                results.append({'code': code, 'sector': sector, 'return': ret})
                
        df_results = pd.DataFrame(results)
        if df_results.empty:
            return df_results
            
        # Aggregate by sector
        sector_returns = df_results.groupby('sector')['return'].mean().reset_index()
        sector_returns = sector_returns.sort_values('return', ascending=False)
        return sector_returns
        
    def generate_ascii_heatmap(self, sector_returns: pd.DataFrame) -> str:
        """Generate ASCII heatmap for console output."""
        if sector_returns.empty:
            return "⚠️ 无板块数据"
            
        lines = []
        lines.append("=" * 50)
        lines.append("📊 板块热力图")
        lines.append("=" * 50)
        
        max_ret = sector_returns['return'].abs().max()
        if max_ret == 0:
            max_ret = 0.01
            
        for _, row in sector_returns.iterrows():
            ret = row['return']
            # Color intensity based on return
            bar_len = int(abs(ret) / max_ret * 20)
            if ret > 0:
                bar = "🟢" * bar_len
            else:
                bar = "🔴" * bar_len
                
            lines.append(f"{row['sector']:<10} {bar} {ret:+.2%}")
            
        return "\n".join(lines)
        
    def generate_html_heatmap(self, sector_returns: pd.DataFrame) -> Optional[str]:
        """Generate HTML heatmap using Plotly."""
        if sector_returns.empty:
            return None
            
        try:
            import plotly.express as px
        except ImportError:
            return None
            
        # Create a simple heatmap
        fig = px.imshow(
            [sector_returns['return'].values],
            labels=dict(x="板块", y="", color="涨跌幅"),
            x=sector_returns['sector'].tolist(),
            color_continuous_scale='RdYlGn',
            aspect='auto'
        )
        
        fig.update_layout(
            title='板块热力图',
            template='plotly_dark',
            height=300
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')


if __name__ == "__main__":
    heatmap = SectorHeatmap()
    codes = list(heatmap.sector_mapping.keys())
    df = heatmap.get_sector_returns(codes)
    if not df.empty:
        print(heatmap.generate_ascii_heatmap(df))
