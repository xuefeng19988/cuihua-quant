"""
Phase 27: PDF Report Generator
Generate professional PDF reports.
"""

import os
import sys
import yaml
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

from src.core.utils import load_stock_names  # 统一入口

class PDFReportGenerator:
    """
    Generate professional PDF reports.
    """
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(project_root, 'data', 'reports')
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        
    def generate_daily_report(self, report_data: Dict, filename: str = None) -> str:
        """Generate daily performance report as PDF."""
        if filename is None:
            filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        html = self._create_report_html("每日绩效报告", report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return filepath
        
    def generate_portfolio_report(self, portfolio_data: Dict, filename: str = None) -> str:
        """Generate portfolio analysis report."""
        if filename is None:
            filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        html = self._create_portfolio_html(portfolio_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return filepath
        
    def generate_stock_report(self, stock_data: Dict, filename: str = None) -> str:
        """Generate individual stock report."""
        if filename is None:
            code = stock_data.get('code', 'unknown')
            filename = f"stock_report_{code}_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        html = self._create_stock_html(stock_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return filepath
    
    def _get_stock_label(self, code: str) -> str:
        """获取股票标签 (代码 + 名称)"""
        names = _load_stock_names()
        name = names.get(code, '')
        return f"{code} {name}".strip() if name else code
        
    def _create_report_html(self, title: str, data: Dict) -> str:
        """Create HTML for general report."""
        return f"""
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .header h1 {{ color: white; border: none; margin: 0; }}
                .metric {{ display: inline-block; width: 200px; margin: 10px; padding: 15px; background: #ecf0f1; border-radius: 8px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .metric-label {{ font-size: 14px; color: #7f8c8d; }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #3498db; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .footer {{ margin-top: 50px; text-align: center; color: #95a5a6; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🦜 {title}</h1>
                <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h2>📊 核心指标</h2>
            <div>
                {self._render_metrics(data.get('metrics', {}))}
            </div>
            
            <h2>📈 持仓明细</h2>
            {self._render_table(data.get('positions', []))}
            
            <h2>📋 交易记录</h2>
            {self._render_table(data.get('trades', []))}
            
            <div class="footer">
                <p>翠花量化系统 - 自动生成报告</p>
                <p>https://github.com/xuefeng19988/cuihua-quant</p>
            </div>
        </body>
        </html>
        """
        
    def _create_portfolio_html(self, data: Dict) -> str:
        """Create HTML for portfolio report."""
        return self._create_report_html("投资组合分析报告", data)
        
    def _create_stock_html(self, data: Dict) -> str:
        """Create HTML for stock report."""
        code = data.get('code', '')
        label = self._get_stock_label(code)
        return self._create_report_html(f"股票分析报告 - {label}", data)
        
    def _render_metrics(self, metrics: Dict) -> str:
        """Render metrics cards."""
        html = ""
        for label, value in metrics.items():
            css_class = ""
            if isinstance(value, str):
                if '+' in value:
                    css_class = "positive"
                elif '-' in value:
                    css_class = "negative"
            html += f"""
            <div class="metric">
                <div class="metric-value {css_class}">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """
        return html
        
    def _render_table(self, rows: List[Dict]) -> str:
        """Render HTML table."""
        if not rows:
            return "<p>无数据</p>"
            
        html = "<table><thead><tr>"
        for key in rows[0].keys():
            html += f"<th>{key}</th>"
        html += "</tr></thead><tbody>"
        
        for row in rows:
            html += "<tr>"
            for value in row.values():
                html += f"<td>{value}</td>"
            html += "</tr>"
            
        html += "</tbody></table>"
        return html
