"""
Phase 26: Data Export Module
Export data to CSV, Excel, PDF formats.
"""

import os
import sys
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class DataExporter:
    """
    Export data to various formats.
    """
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(project_root, 'data', 'exports')
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        
    def export_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export DataFrame to CSV."""
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        return filepath
        
    def export_to_excel(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export DataFrame to Excel."""
        try:
            import openpyxl
        except ImportError:
            os.system('pip install openpyxl')
            import openpyxl
            
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        df.to_excel(filepath, index=False, engine='openpyxl')
        return filepath
        
    def export_to_pdf(self, df: pd.DataFrame, title: str = "Data Export", filename: str = None) -> str:
        """Export DataFrame to PDF using simple HTML conversion."""
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create simple HTML table
        html = f"""
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            {df.to_html(index=False, border=0)}
        </body>
        </html>
        """
        
        # Try to use weasyprint if available
        try:
            from weasyprint import HTML
            HTML(string=html).write_pdf(filepath)
        except ImportError:
            # Fallback: save as HTML
            filepath = filepath.replace('.pdf', '.html')
            with open(filepath, 'w') as f:
                f.write(html)
                
        return filepath
        
    def export_stock_data(self, code: str, engine, start_date: str = None, end_date: str = None, format: str = 'csv') -> str:
        """Export stock data to specified format."""
        query = f"SELECT * FROM stock_daily WHERE code='{code}'"
        if start_date:
            query += f" AND date >= '{start_date}'"
        if end_date:
            query += f" AND date <= '{end_date}'"
        query += " ORDER BY date"
        
        df = pd.read_sql(query, engine)
        if df.empty:
            return ""
            
        filename = f"{code.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}"
        
        if format == 'csv':
            return self.export_to_csv(df, f"{filename}.csv")
        elif format == 'excel':
            return self.export_to_excel(df, f"{filename}.xlsx")
        elif format == 'pdf':
            return self.export_to_pdf(df, f"Stock Data: {code}", f"{filename}.pdf")
        else:
            return ""
            
    def export_portfolio(self, portfolio_data: Dict, engine, format: str = 'csv') -> str:
        """Export portfolio summary."""
        # This would export positions, P&L, etc.
        # Placeholder for now
        return ""
        
    def list_exports(self) -> List[Dict]:
        """List all exported files."""
        files = []
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'path': filepath
                })
        return sorted(files, key=lambda x: x['created'], reverse=True)
