"""
Phase 26: Stock Group Manager
Manage stock groups and advanced filtering.
"""

import os
import sys
import yaml
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class StockGroupManager:
    """
    Manage stock groups and advanced filtering.
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(project_root, 'config', 'stock_groups.yaml')
        self.config_path = config_path
        self.groups: Dict[str, Dict] = {}
        self._load_groups()
        
    def _load_groups(self):
        """Load stock groups from config."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.groups = yaml.safe_load(f) or {}
        else:
            # Create default groups
            self.groups = {
                "核心观察": {
                    "description": "核心观察股票池",
                    "stocks": ["SH.600519", "SZ.002594", "HK.00700", "SZ.300750"]
                },
                "A 股": {
                    "description": "A 股市场",
                    "stocks": []
                },
                "港股": {
                    "description": "港股市场",
                    "stocks": []
                },
                "科技": {
                    "description": "科技行业",
                    "stocks": ["SZ.002415", "SZ.002230", "HK.00700"]
                },
                "消费": {
                    "description": "消费行业",
                    "stocks": ["SH.600519", "SZ.000858", "SZ.000333"]
                },
                "金融": {
                    "description": "金融行业",
                    "stocks": ["SH.601318", "SH.600036", "SZ.300059"]
                }
            }
            self._save_groups()
            
    def _save_groups(self):
        """Save stock groups to config."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.groups, f, allow_unicode=True, default_flow_style=False)
            
    def get_groups(self) -> Dict:
        """Get all groups."""
        return self.groups
        
    def get_group(self, name: str) -> Optional[Dict]:
        """Get specific group."""
        return self.groups.get(name)
        
    def add_group(self, name: str, description: str = "", stocks: List[str] = None) -> bool:
        """Add a new group."""
        if name in self.groups:
            return False
        self.groups[name] = {
            "description": description,
            "stocks": stocks or []
        }
        self._save_groups()
        return True
        
    def remove_group(self, name: str) -> bool:
        """Remove a group."""
        if name not in self.groups:
            return False
        del self.groups[name]
        self._save_groups()
        return True
        
    def add_stock_to_group(self, group_name: str, stock_code: str) -> bool:
        """Add stock to a group."""
        if group_name not in self.groups:
            return False
        if stock_code not in self.groups[group_name]['stocks']:
            self.groups[group_name]['stocks'].append(stock_code)
            self._save_groups()
        return True
        
    def remove_stock_from_group(self, group_name: str, stock_code: str) -> bool:
        """Remove stock from a group."""
        if group_name not in self.groups:
            return False
        if stock_code in self.groups[group_name]['stocks']:
            self.groups[group_name]['stocks'].remove(stock_code)
            self._save_groups()
        return True
        
    def filter_stocks(self, criteria: Dict, engine) -> pd.DataFrame:
        """
        Filter stocks based on criteria.
        
        Args:
            criteria: Dict with filter criteria
                - min_price: Minimum price
                - max_price: Maximum price
                - min_change: Minimum change %
                - max_change: Maximum change %
                - min_volume: Minimum volume
                - industry: Industry filter
                - group: Filter by group
                
        Returns:
            Filtered DataFrame
        """
        from src.data.database import get_db_engine
        
        if engine is None:
            engine = get_db_engine()
            
        # Get all stocks
        df = pd.read_sql(
            "SELECT code, date, close_price, volume, change_pct FROM stock_daily "
            "WHERE date = (SELECT MAX(date) FROM stock_daily s2 WHERE s1.code = s2.code)",
            engine
        )
        
        if df.empty:
            return df
            
        # Apply filters
        if 'min_price' in criteria:
            df = df[df['close_price'] >= criteria['min_price']]
        if 'max_price' in criteria:
            df = df[df['close_price'] <= criteria['max_price']]
        if 'min_change' in criteria:
            df = df[df['change_pct'] >= criteria['min_change']]
        if 'max_change' in criteria:
            df = df[df['change_pct'] <= criteria['max_change']]
        if 'min_volume' in criteria:
            df = df[df['volume'] >= criteria['min_volume']]
        if 'group' in criteria:
            group = self.get_group(criteria['group'])
            if group:
                df = df[df['code'].isin(group['stocks'])]
                
        return df
        
    def generate_report(self) -> str:
        """Generate stock groups report."""
        lines = []
        lines.append("=" * 60)
        lines.append("📊 股票分组报告")
        lines.append("=" * 60)
        
        for name, group in self.groups.items():
            stocks = group.get('stocks', [])
            desc = group.get('description', '')
            lines.append(f"\n📁 {name} ({len(stocks)} 只)")
            lines.append(f"   {desc}")
            for code in stocks[:10]:
                lines.append(f"   - {code}")
            if len(stocks) > 10:
                lines.append(f"   ... 还有 {len(stocks) - 10} 只")
                
        return "\n".join(lines)
