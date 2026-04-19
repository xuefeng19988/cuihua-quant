"""
Phase 31: Advanced Visualization
Additional chart types: scatter, radar, tree map, etc.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class AdvancedVisualization:
    """
    Advanced chart types for data analysis.
    """
    
    def __init__(self):
        self.engine = None
        try:
            from src.data.database import get_db_engine
            self.engine = get_db_engine()
        except Exception as e:
            pass
            
    def generate_scatter_plot(self, x_data: List, y_data: List, 
                               labels: List[str] = None, title: str = "散点图") -> Optional[str]:
        """
        Generate scatter plot.
        
        Args:
            x_data: X axis data
            y_data: Y axis data
            labels: Point labels
            title: Chart title
            
        Returns:
            HTML string with chart
        """
        try:
            import plotly.express as px
        except ImportError:
            return None
            
        df = pd.DataFrame({
            'x': x_data,
            'y': y_data,
            'label': labels or [str(i) for i in range(len(x_data))]
        })
        
        fig = px.scatter(
            df, x='x', y='y', text='label',
            title=title,
            labels={'x': 'X', 'y': 'Y'}
        )
        
        fig.update_traces(textposition='top center')
        fig.update_layout(
            template='plotly_dark',
            height=500
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_radar_chart(self, categories: List[str], values: List[float], 
                              title: str = "雷达图") -> Optional[str]:
        """
        Generate radar/spider chart.
        
        Args:
            categories: Category names
            values: Category values
            title: Chart title
            
        Returns:
            HTML string with chart
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            return None
            
        # Close the radar chart
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            name='Values'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2]
                )
            ),
            title=title,
            template='plotly_dark',
            height=500
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_tree_map(self, labels: List[str], values: List[float], 
                           parents: List[str] = None, title: str = "树图") -> Optional[str]:
        """
        Generate tree map chart.
        
        Args:
            labels: Node labels
            values: Node values
            parents: Parent node labels
            title: Chart title
            
        Returns:
            HTML string with chart
        """
        try:
            import plotly.express as px
        except ImportError:
            return None
            
        df = pd.DataFrame({
            'labels': labels,
            'values': values,
            'parents': parents or [''] * len(labels)
        })
        
        fig = px.treemap(
            df,
            names='labels',
            values='values',
            parents='parents',
            title=title
        )
        
        fig.update_layout(
            template='plotly_dark',
            height=600
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_correlation_matrix(self, data: pd.DataFrame, title: str = "相关性矩阵") -> Optional[str]:
        """
        Generate correlation matrix heatmap.
        
        Args:
            data: DataFrame with numeric columns
            title: Chart title
            
        Returns:
            HTML string with chart
        """
        try:
            import plotly.express as px
        except ImportError:
            return None
            
        corr = data.corr()
        
        fig = px.imshow(
            corr,
            labels=dict(x="变量", y="变量", color="相关性"),
            color_continuous_scale='RdBu_r',
            title=title
        )
        
        fig.update_layout(
            template='plotly_dark',
            height=600
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    def generate_stock_scatter(self, codes: List[str] = None) -> Optional[str]:
        """
        Generate risk-return scatter plot for stocks.
        X: Volatility, Y: Return
        """
        if self.engine is None:
            return None
            
        if codes is None:
            from src.data.database import get_db_engine
            engine = get_db_engine()
            df_codes = pd.read_sql("SELECT DISTINCT code FROM stock_daily LIMIT 20", engine)
            codes = df_codes['code'].tolist()
            
        x_data = []
        y_data = []
        
        for code in codes:
            try:
                df = pd.read_sql(
                    f"SELECT close_price FROM stock_daily WHERE code='{code}' ORDER BY date",
                    self.engine
                )
                if len(df) >= 30:
                    returns = df['close_price'].pct_change().dropna()
                    x_data.append(returns.std() * np.sqrt(252) * 100)  # Annualized vol
                    y_data.append(((df.iloc[-1]['close_price'] / df.iloc[0]['close_price']) - 1) * 100)  # Total return
            except Exception as e:
                pass
                
        if not x_data:
            return None
            
        return self.generate_scatter_plot(
            x_data, y_data,
            labels=codes[:len(x_data)],
            title="风险收益散点图 (波动率 vs 收益率)"
        )


if __name__ == "__main__":
    viz = AdvancedVisualization()
    
    # Test radar chart
    categories = ['动量', '价值', '质量', '波动率', '成长', '情绪']
    values = [0.8, 0.6, 0.7, 0.5, 0.9, 0.4]
    html = viz.generate_radar_chart(categories, values, "股票评分雷达图")
    if html:
        print("✅ Radar chart generated")
