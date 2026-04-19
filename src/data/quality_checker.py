"""
Phase 43: Data Quality Manager
Data validation, cleaning, and quality monitoring.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class DataQualityChecker:
    """
    Data quality checking and validation.
    """
    
    def __init__(self):
        self.quality_reports: List[Dict] = []
        
    def check_completeness(self, df: pd.DataFrame, required_columns: List[str] = None) -> Dict:
        """Check data completeness."""
        results = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': {},
            'completeness_score': 0
        }
        
        # Check required columns
        if required_columns:
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                results['missing_columns'] = list(missing_cols)
                
        # Check missing values
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                results['missing_values'][col] = {
                    'count': int(missing),
                    'percentage': round(missing / len(df) * 100, 2)
                }
                
        # Calculate completeness score
        total_cells = len(df) * len(df.columns)
        missing_cells = sum(df.isna().sum())
        results['completeness_score'] = round((1 - missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0
        
        return results
        
    def check_consistency(self, df: pd.DataFrame, rules: Dict[str, Callable] = None) -> Dict:
        """Check data consistency."""
        results = {
            'violations': [],
            'consistency_score': 100
        }
        
        if rules is None:
            # Default rules for stock data
            rules = {
                'high_ge_low': lambda df: (df.get('high', pd.Series()) >= df.get('low', pd.Series())).all(),
                'volume_positive': lambda df: (df.get('volume', pd.Series()) >= 0).all(),
                'price_positive': lambda df: (df.get('close', pd.Series()) > 0).all(),
            }
            
        violations = 0
        for rule_name, rule_func in rules.items():
            try:
                if not rule_func(df):
                    results['violations'].append(rule_name)
                    violations += 1
            except Exception as e:
                results['violations'].append(f"{rule_name}_error")
                violations += 1
                
        results['consistency_score'] = round((1 - violations / max(len(rules), 1)) * 100, 2)
        
        return results
        
    def check_timeliness(self, df: pd.DataFrame, date_column: str = 'date',
                        expected_frequency: str = 'B') -> Dict:
        """Check data timeliness and gaps."""
        results = {
            'has_gaps': False,
            'gap_count': 0,
            'latest_date': None,
            'days_since_latest': None
        }
        
        if date_column not in df.columns:
            results['error'] = f"Date column '{date_column}' not found"
            return results
            
        dates = pd.to_datetime(df[date_column]).sort_values()
        results['latest_date'] = dates.iloc[-1].strftime('%Y-%m-%d') if len(dates) > 0 else None
        results['days_since_latest'] = (datetime.now() - dates.iloc[-1]).days if len(dates) > 0 else None
        
        # Check for gaps
        if expected_frequency == 'B':  # Business days
            expected_dates = pd.bdate_range(dates.iloc[0], dates.iloc[-1])
            missing_dates = expected_dates.difference(dates)
            results['gap_count'] = len(missing_dates)
            results['has_gaps'] = len(missing_dates) > 0
            if missing_dates.any():
                results['missing_dates'] = [d.strftime('%Y-%m-%d') for d in missing_dates[:10]]
                
        return results
        
    def check_outliers(self, df: pd.DataFrame, columns: List[str] = None,
                      method: str = 'iqr') -> Dict:
        """Detect outliers in numeric columns."""
        results = {'outliers': {}}
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
        for col in columns:
            if col not in df.columns:
                continue
                
            series = df[col].dropna()
            if len(series) < 4:
                continue
                
            if method == 'iqr':
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = series[(series < lower) | (series > upper)]
            else:  # z-score
                mean = series.mean()
                std = series.std()
                if std > 0:
                    z_scores = (series - mean) / std
                    outliers = series[abs(z_scores) > 3]
                else:
                    outliers = pd.Series(dtype=float)
                    
            if len(outliers) > 0:
                results['outliers'][col] = {
                    'count': len(outliers),
                    'percentage': round(len(outliers) / len(series) * 100, 2),
                    'values': outliers.tolist()[:5]
                }
                
        return results
        
    def run_full_check(self, df: pd.DataFrame, required_columns: List[str] = None) -> Dict:
        """Run complete data quality check."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'rows': len(df),
            'columns': len(df.columns),
            'completeness': self.check_completeness(df, required_columns),
            'consistency': self.check_consistency(df),
            'timeliness': self.check_timeliness(df),
            'outliers': self.check_outliers(df)
        }
        
        # Overall quality score
        scores = [
            report['completeness']['completeness_score'],
            report['consistency']['consistency_score'],
        ]
        report['overall_score'] = round(np.mean(scores), 2)
        
        self.quality_reports.append(report)
        
        return report
        
    def generate_report(self, report: Dict = None) -> str:
        """Generate data quality report."""
        if report is None:
            if not self.quality_reports:
                return "⚠️ 无质量报告"
            report = self.quality_reports[-1]
            
        lines = []
        lines.append("=" * 60)
        lines.append("🔍 数据质量报告")
        lines.append("=" * 60)
        lines.append(f"\n📊 数据规模: {report['rows']} 行 × {report['columns']} 列")
        lines.append(f"🎯 总体质量分: {report['overall_score']:.1f}%")
        
        comp = report['completeness']
        lines.append(f"\n✅ 完整性: {comp['completeness_score']:.1f}%")
        if comp['missing_values']:
            lines.append(f"  缺失列:")
            for col, info in comp['missing_values'].items():
                lines.append(f"    - {col}: {info['count']} ({info['percentage']}%)")
                
        cons = report['consistency']
        lines.append(f"\n🔄 一致性: {cons['consistency_score']:.1f}%")
        if cons['violations']:
            lines.append(f"  违规: {', '.join(cons['violations'])}")
            
        time = report['timeliness']
        lines.append(f"\n⏰ 时效性")
        lines.append(f"  最新数据: {time.get('latest_date', 'N/A')}")
        lines.append(f"  距今天数: {time.get('days_since_latest', 'N/A')}")
        gap_status = '✅' if not time.get('has_gaps') else f"❌ {time['gap_count']} 个"
        lines.append(f"  数据缺口: {gap_status}")
            
        out = report['outliers']
        if out['outliers']:
            lines.append(f"\n📈 异常值")
            for col, info in out['outliers'].items():
                lines.append(f"  {col}: {info['count']} 个 ({info['percentage']}%)")
                
        return "\n".join(lines)


if __name__ == "__main__":
    # Test with mock data
    np.random.seed(42)
    dates = pd.bdate_range('2024-01-01', periods=100)
    df = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(100, 200, 100),
        'high': np.random.uniform(100, 200, 100),
        'low': np.random.uniform(100, 200, 100),
        'close': np.random.uniform(100, 200, 100),
        'volume': np.random.uniform(1e6, 1e8, 100)
    })
    # Ensure high >= low
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    checker = DataQualityChecker()
    report = checker.run_full_check(df)
    print(checker.generate_report(report))
