"""
Phase 111: 文章信息管理
- TrendRadar 新闻数据库查询
- 文章与股票相关性匹配
- 按日期分类、分页查询
"""

import os
import sys
import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# TrendRadar 新闻数据库目录
TRENDRADAR_NEWS_DIR = os.path.join(project_root, '../TrendRadar/output/news')

# 平台中文映射
PLATFORM_NAMES = {
    'toutiao': '今日头条',
    'weibo': '微博',
    'baidu': '百度',
    'bilibili-hot-search': 'B站',
    'zhihu': '知乎',
    'douyin': '抖音',
    'wallstreetcn-hot': '华尔街见闻',
    'thepaper': '澎湃新闻',
    '36kr': '36氪',
    'cls-hot': '财联社',
    'ifeng': '凤凰新闻',
    'tieba': '百度贴吧',
    'github-trending': 'GitHub',
}

# 财经/科技类平台（优先展示）
FINANCE_PLATFORMS = {'wallstreetcn-hot', 'cls-hot', '36kr', 'baidu', 'toutiao'}


class ArticleManager:
    """文章信息管理"""

    def __init__(self, news_dir: str = None):
        self.news_dir = news_dir or TRENDRADAR_NEWS_DIR
        if not os.path.exists(self.news_dir):
            os.makedirs(self.news_dir, exist_ok=True)

        # 股票名称和关键词映射
        self.stock_keywords = self._build_stock_keywords()

    def _build_stock_keywords(self) -> Dict[str, List[str]]:
        """构建股票-关键词映射"""
        cfg_path = os.path.join(project_root, 'config', 'stocks.yaml')
        import yaml
        try:
            with open(cfg_path, 'r') as f:
                cfg = yaml.safe_load(f)
        except Exception as e:
            cfg = {}

        keywords = {}
        stock_names = {}
        for pool_data in cfg.get('pools', {}).values():
            for item in pool_data.get('stocks', []):
                if isinstance(item, dict):
                    code = item.get('code', '')
                    name = item.get('name', '')
                else:
                    code = item
                    name = ''
                if not code:
                    continue
                stock_names[code] = name
                # 提取关键词：中文名、简称、英文名
                kws = set()
                if name:
                    kws.add(name)
                    # 提取简称（取前2-4个汉字）
                    clean_name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', '', name)
                    if len(clean_name) >= 2:
                        kws.add(clean_name[:2])
                        kws.add(clean_name[:3])
                        kws.add(clean_name[:4])
                keywords[code] = list(kws)

        # 添加额外行业关键词
        industry_kws = {
            '白酒': ['茅台', '五粮液', '白酒', '泸州'],
            '新能源': ['宁德时代', '比亚迪', '锂电池', '光伏', '储能', '隆基', '亿纬'],
            '科技': ['腾讯', '科大讯飞', '海康威视', '芯片', '半导体', '中芯国际'],
            '金融': ['平安', '招商', '中行', '银行', '保险', '券商', '东方财富'],
            '消费': ['美团', '海底捞', '泡泡玛特', '名创优品', '中国中免'],
            '家电': ['美的', '格力', '海尔'],
            '汽车': ['小米汽车', '比亚迪', '蔚来', '理想', '小鹏', '特斯拉'],
            '医药': ['恒瑞医药', '创新药', 'CRO'],
            '公用事业': ['长江电力', '核电', '华能国际'],
            '能源': ['中国神华', '煤炭', '原油'],
            '港股': ['阿里', '小米', '美团', '快手', '京东', '百度', '网易', '舜宇'],
        }
        for sector, kws in industry_kws.items():
            keywords[sector] = kws

        return keywords

    def get_available_dates(self) -> List[str]:
        """获取所有可用日期"""
        dates = []
        if not os.path.exists(self.news_dir):
            return dates
        for f in sorted(os.listdir(self.news_dir)):
            if f.endswith('.db'):
                date_str = f.replace('.db', '')
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append(date_str)
                except Exception as e:
                    continue
        return dates

    def get_db_path(self, date: str) -> Optional[str]:
        """获取指定日期的数据库路径"""
        db_path = os.path.join(self.news_dir, f'{date}.db')
        if os.path.exists(db_path):
            return db_path
        return None

    def get_articles_by_date(self, date: str, limit: int = 100,
                             platforms: List[str] = None) -> List[Dict]:
        """获取指定日期的文章列表"""
        db_path = self.get_db_path(date)
        if not db_path:
            return []

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT ni.id, ni.title, ni.platform_id, ni.rank, ni.url, ni.first_crawl_time FROM news_items ni"
            conditions = []
            params = []

            if platforms:
                placeholders = ','.join(['?' for _ in platforms])
                conditions.append(f"ni.platform_id IN ({placeholders})")
                params.extend(platforms)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY ni.rank ASC"
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            articles = []
            for row in rows:
                articles.append({
                    'id': row['id'],
                    'title': row['title'],
                    'platform': row['platform_id'],
                    'platform_name': PLATFORM_NAMES.get(row['platform_id'], row['platform_id']),
                    'rank': row['rank'],
                    'url': row['url'],
                    'time': row['first_crawl_time'],
                    'date': date,
                })

            conn.close()
            return articles
        except Exception as e:
            print(f"⚠️ 获取文章失败: {e}")
            return []

    def match_articles_with_stocks(self, articles: List[Dict]) -> List[Dict]:
        """匹配文章与相关股票"""
        for article in articles:
            title = article.get('title', '').lower()
            matched_stocks = []

            for code, kws in self.stock_keywords.items():
                for kw in kws:
                    if kw.lower() in title:
                        if code not in [s['code'] for s in matched_stocks]:
                            matched_stocks.append({
                                'code': code,
                                'keyword': kw,
                            })
                        break

            article['matched_stocks'] = matched_stocks
            article['has_stock'] = len(matched_stocks) > 0
            article['relevance'] = 'high' if len(matched_stocks) >= 2 else ('medium' if matched_stocks else 'low')

        return articles

    def get_date_range_articles(self, start_date: str, end_date: str,
                                page: int = 1, per_page: int = 20,
                                stock_only: bool = False) -> Tuple[List[Dict], int]:
        """获取日期范围内的文章，支持分页"""
        all_articles = []

        # 获取日期范围内所有可用日期
        available = set(self.get_available_dates())
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except Exception as e:
            return [], 0

        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            if date_str in available:
                articles = self.get_articles_by_date(date_str, limit=200)
                articles = self.match_articles_with_stocks(articles)
                if stock_only:
                    articles = [a for a in articles if a['has_stock']]
                all_articles.extend(articles)
            current += timedelta(days=1)

        # 按日期分组排序（最新的在前）
        all_articles.sort(key=lambda x: (x['date'], x['rank']), reverse=True)

        total = len(all_articles)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        return all_articles[start_idx:end_idx], total

    def get_daily_summary(self, date: str) -> Dict:
        """获取指定日期的文章摘要"""
        articles = self.get_articles_by_date(date, limit=500)
        if not articles:
            return {'date': date, 'total': 0, 'platforms': {}, 'top_articles': []}

        # 按平台统计
        platform_counts = defaultdict(int)
        for a in articles:
            platform_counts[a['platform']] += 1

        # 匹配股票
        articles = self.match_articles_with_stocks(articles)
        stock_articles = [a for a in articles if a['has_stock']]

        return {
            'date': date,
            'total': len(articles),
            'stock_related': len(stock_articles),
            'platforms': dict(platform_counts),
            'top_articles': articles[:10],
            'stock_articles': stock_articles[:20],
        }

    def get_articles_by_stock(self, date: str, stock_code: str = None,
                              stock_name: str = None) -> List[Dict]:
        """获取与某只股票相关的文章"""
        articles = self.get_articles_by_date(date, limit=500)
        articles = self.match_articles_with_stocks(articles)

        if stock_code:
            articles = [a for a in articles if any(s['code'] == stock_code for s in a['matched_stocks'])]
        elif stock_name:
            articles = [a for a in articles if any(s['code'] == stock_name for s in a['matched_stocks'])]

        return articles


if __name__ == "__main__":
    mgr = ArticleManager()
    dates = mgr.get_available_dates()
    print(f"可用日期: {len(dates)} 天")
    print(f"最近日期: {dates[-5:]}")

    if dates:
        latest = dates[-1]
        summary = mgr.get_daily_summary(latest)
        print(f"\n📅 {latest} 摘要:")
        print(f"  文章总数: {summary['total']}")
        print(f"  股票相关: {summary['stock_related']}")
        print(f"  平台分布: {summary['platforms']}")

        if summary['stock_articles']:
            print(f"\n🔥 股票相关文章:")
            for a in summary['stock_articles'][:10]:
                stocks = ', '.join([s['code'] for s in a['matched_stocks']])
                print(f"  [{a['platform_name']}] {a['title'][:40]}... → {stocks}")
