"""
股票评分系统 v2 - Phase 267
综合评分算法，8维度评估 + 百分位排名 + 同行对比
"""

import math


class StockScorer:
    """股票综合评分器 v2"""

    # 8维度权重
    WEIGHTS = {
        'trend': 0.18,       # 趋势
        'momentum': 0.15,    # 动量
        'volatility': 0.10,  # 波动率
        'volume': 0.10,      # 成交量
        'valuation': 0.18,   # 估值
        'quality': 0.14,     # 质量
        'growth': 0.10,      # 成长
        'sentiment': 0.05    # 情绪
    }

    @staticmethod
    def calculate_score(stock_data):
        """
        计算股票综合评分 (8维度)
        :param stock_data: 股票数据字典
        :return: 评分结果字典
        """
        # 提取数据
        price = stock_data.get('price', 0)
        change = stock_data.get('change', 0)
        volume = stock_data.get('volume', 0)
        turnover = stock_data.get('turnover_rate', 0)
        pe = stock_data.get('pe', 0)
        pb = stock_data.get('pb', 0)
        roe = stock_data.get('roe', 0)
        rsi = stock_data.get('rsi', 50)
        macd = stock_data.get('macd', 0)
        ma5 = stock_data.get('ma5', 0)
        ma20 = stock_data.get('ma20', 0)
        ma60 = stock_data.get('ma60', ma20)
        week52_high = stock_data.get('week52_high', price)
        week52_low = stock_data.get('week52_low', price)
        revenue_growth = stock_data.get('revenue_growth', 0)
        profit_growth = stock_data.get('profit_growth', 0)
        net_margin = stock_data.get('net_margin', 0)
        debt_ratio = stock_data.get('debt_ratio', 0)
        dividend_yield = stock_data.get('dividend_yield', 0)
        northbound = stock_data.get('northbound_net', 0)
        main_flow = stock_data.get('main_net_inflow', 0)
        sector_avg_pe = stock_data.get('sector_avg_pe', pe)

        # 8维度评分
        scores = {
            'trend': StockScorer.calculate_trend_score(price, ma5, ma20, ma60, week52_high, week52_low),
            'momentum': StockScorer.calculate_momentum_score(change, rsi, macd),
            'volatility': StockScorer.calculate_volatility_score(week52_high, week52_low, price),
            'volume': StockScorer.calculate_volume_score(volume, turnover),
            'valuation': StockScorer.calculate_valuation_score(pe, pb, roe, sector_avg_pe),
            'quality': StockScorer.calculate_quality_score(roe, net_margin, debt_ratio, dividend_yield),
            'growth': StockScorer.calculate_growth_score(revenue_growth, profit_growth, roe),
            'sentiment': StockScorer.calculate_sentiment_score(northbound, main_flow, turnover, change)
        }

        # 加权总分
        total_score = sum(scores[k] * StockScorer.WEIGHTS[k] for k in scores)
        total_score = round(total_score)

        # 百分位等级
        percentile = StockScorer.score_to_percentile(total_score)

        # 综合评级
        grade = StockScorer.get_grade(total_score)
        recommendation = StockScorer.get_recommendation(total_score)

        # 强项/弱项
        sorted_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        strengths = [{'dim': d, 'score': s, 'label': StockScorer.dim_label(d)} for d, s in sorted_dims[:3]]
        weaknesses = [{'dim': d, 'score': s, 'label': StockScorer.dim_label(d)} for d, s in sorted_dims[-2:]]

        return {
            'total': total_score,
            'percentile': percentile,
            'grade': grade,
            'recommendation': recommendation,
            'scores': scores,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'weights': {k: int(v * 100) for k, v in StockScorer.WEIGHTS.items()}
        }

    @staticmethod
    def calculate_trend_score(price, ma5, ma20, ma60, week52_high, week52_low):
        """趋势评分 (0-100)"""
        score = 50

        # 多头排列 (price > MA5 > MA20 > MA60)
        if ma5 > ma20 > ma60 and price > ma5:
            score += 30
        elif price > ma5 > ma20:
            score += 20
        elif price > ma20:
            score += 10
        elif price < ma60:
            score -= 20
        elif price < ma20:
            score -= 10

        # 52周位置
        range_ = week52_high - week52_low
        if range_ > 0:
            position = (price - week52_low) / range_
            score += (position - 0.5) * 20

        return max(0, min(100, round(score)))

    @staticmethod
    def calculate_momentum_score(change, rsi, macd):
        """动量评分 (0-100)"""
        score = 50

        # 涨跌幅 (±5%范围内线性映射)
        score += max(-15, min(15, change * 3))

        # RSI
        if rsi < 20:
            score += 20  # 极度超卖，可能反弹
        elif rsi < 30:
            score += 12
        elif rsi < 40:
            score += 5
        elif rsi > 80:
            score -= 15  # 极度超买
        elif rsi > 70:
            score -= 8
        else:
            score += 3

        # MACD
        if macd > 0:
            score += 8
        else:
            score -= 5

        return max(0, min(100, round(score)))

    @staticmethod
    def calculate_volatility_score(week52_high, week52_low, price):
        """波动率评分 (0-100)，适度波动最佳"""
        range_pct = (week52_high - week52_low) / week52_low * 100 if week52_low > 0 else 0

        # 正态分布风格评分，30-50%波动率区间最佳
        if 25 <= range_pct <= 50:
            return 85
        elif 15 <= range_pct < 25:
            return 75
        elif 50 < range_pct <= 70:
            return 65
        elif 10 <= range_pct < 15:
            return 60
        elif 70 < range_pct <= 90:
            return 50
        elif range_pct > 90:
            return 35
        return 50

    @staticmethod
    def calculate_volume_score(volume, turnover):
        """成交量评分 (0-100)"""
        score = 50

        # 换手率评分 - 3-7%最佳
        if 3 <= turnover <= 7:
            score += 25
        elif 2 <= turnover < 3:
            score += 15
        elif 7 < turnover <= 10:
            score += 10
        elif 10 < turnover <= 15:
            score += 0
        elif turnover > 15:
            score -= 10
        elif turnover < 1:
            score -= 15

        # 量比 (需要额外数据，这里简化)
        if turnover > 5:
            score += 5  # 活跃

        return max(0, min(100, round(score)))

    @staticmethod
    def calculate_valuation_score(pe, pb, roe, sector_avg_pe=0):
        """估值评分 (0-100)，相对行业估值"""
        score = 50

        # PE相对行业估值
        if sector_avg_pe > 0 and pe > 0:
            pe_ratio = pe / sector_avg_pe
            if pe_ratio < 0.7:
                score += 20  # 显著低估
            elif pe_ratio < 0.9:
                score += 12
            elif pe_ratio < 1.1:
                score += 5   # 合理
            elif pe_ratio < 1.5:
                score -= 5
            else:
                score -= 15  # 显著高估
        elif pe > 0:
            # 无行业对比，绝对估值
            if 8 <= pe <= 20:
                score += 15
            elif 20 < pe <= 30:
                score += 5
            elif pe > 40:
                score -= 10

        # PB
        if 0.5 <= pb <= 2:
            score += 10
        elif 2 < pb <= 4:
            score += 3
        elif pb > 6:
            score -= 8

        # ROE
        if roe >= 20:
            score += 15
        elif roe >= 15:
            score += 10
        elif roe >= 10:
            score += 5
        elif roe < 5:
            score -= 5

        return max(0, min(100, round(score)))

    @staticmethod
    def calculate_quality_score(roe, net_margin, debt_ratio, dividend_yield):
        """质量评分 (0-100)"""
        score = 50

        # ROE质量
        if roe >= 20:
            score += 18
        elif roe >= 15:
            score += 12
        elif roe >= 10:
            score += 6
        elif roe < 5:
            score -= 10

        # 净利率
        if net_margin >= 20:
            score += 12
        elif net_margin >= 10:
            score += 8
        elif net_margin >= 5:
            score += 4
        elif net_margin < 0:
            score -= 10

        # 负债率 (越低越好，但适度负债正常)
        if 30 <= debt_ratio <= 50:
            score += 8
        elif debt_ratio < 30:
            score += 5
        elif 50 < debt_ratio <= 60:
            score += 0
        elif debt_ratio > 60:
            score -= 10

        # 股息率
        if dividend_yield >= 4:
            score += 10
        elif dividend_yield >= 2:
            score += 6
        elif dividend_yield >= 1:
            score += 3

        return max(0, min(100, round(score)))

    @staticmethod
    def calculate_growth_score(revenue_growth, profit_growth, roe):
        """成长评分 (0-100)"""
        score = 50

        # 营收增长
        if revenue_growth >= 30:
            score += 20
        elif revenue_growth >= 20:
            score += 14
        elif revenue_growth >= 10:
            score += 8
        elif revenue_growth >= 0:
            score += 2
        else:
            score -= 10

        # 利润增长
        if profit_growth >= 30:
            score += 20
        elif profit_growth >= 20:
            score += 14
        elif profit_growth >= 10:
            score += 8
        elif profit_growth >= 0:
            score += 2
        else:
            score -= 10

        # ROE趋势 (高ROE隐含成长质量)
        if roe >= 20:
            score += 8
        elif roe >= 15:
            score += 5

        return max(0, min(100, round(score)))

    @staticmethod
    def calculate_sentiment_score(northbound, main_flow, turnover, change):
        """情绪评分 (0-100)"""
        score = 50

        # 北向资金
        if northbound > 50000000:
            score += 15
        elif northbound > 10000000:
            score += 8
        elif northbound < -50000000:
            score -= 15
        elif northbound < -10000000:
            score -= 8

        # 主力净流入
        if main_flow > 100000000:
            score += 12
        elif main_flow > 20000000:
            score += 6
        elif main_flow < -100000000:
            score -= 12
        elif main_flow < -20000000:
            score -= 6

        # 换手率情绪
        if turnover > 10:
            score += 5  # 高关注度
        elif turnover < 1:
            score -= 3  # 低关注度

        # 涨跌幅情绪
        if change > 5:
            score += 5
        elif change < -5:
            score -= 5

        return max(0, min(100, round(score)))

    @staticmethod
    def compare_stocks(stock_scores_list):
        """
        多股票对比分析
        :param stock_scores_list: [{'code': '', 'name': '', 'score_result': {...}}, ...]
        :return: 对比结果
        """
        if not stock_scores_list:
            return {'rankings': [], 'summary': {}}

        # 按总分排序
        rankings = sorted(
            stock_scores_list,
            key=lambda x: x['score_result']['total'],
            reverse=True
        )

        # 添加排名
        for i, item in enumerate(rankings):
            item['rank'] = i + 1

        # 计算各维度最高/最低
        dimensions = ['trend', 'momentum', 'volatility', 'volume', 'valuation', 'quality', 'growth', 'sentiment']
        dim_stats = {}
        for dim in dimensions:
            values = [(item['code'], item['score_result']['scores'].get(dim, 0)) for item in rankings]
            best = max(values, key=lambda x: x[1])
            worst = min(values, key=lambda x: x[1])
            dim_stats[dim] = {
                'label': StockScorer.dim_label(dim),
                'best': {'code': best[0], 'score': best[1]},
                'worst': {'code': worst[0], 'score': worst[1]}
            }

        # 百分位计算
        total_scores = [item['score_result']['total'] for item in rankings]
        for item in rankings:
            score = item['score_result']['total']
            better_count = sum(1 for s in total_scores if s > score)
            item['percentile'] = round((1 - better_count / len(total_scores)) * 100)

        return {
            'rankings': rankings,
            'dim_stats': dim_stats,
            'summary': {
                'total_stocks': len(rankings),
                'avg_score': round(sum(total_scores) / len(total_scores)),
                'max_score': max(total_scores),
                'min_score': min(total_scores)
            }
        }

    @staticmethod
    def get_sector_ranking(stocks_in_sector, target_code):
        """
        计算股票在行业中的排名百分位
        :param stocks_in_sector: 同行业所有股票评分列表
        :param target_code: 目标股票代码
        :return: 排名信息
        """
        sorted_stocks = sorted(stocks_in_sector, key=lambda x: x['total'], reverse=True)
        for i, stock in enumerate(sorted_stocks):
            if stock['code'] == target_code:
                percentile = round((1 - i / len(sorted_stocks)) * 100) if len(sorted_stocks) > 1 else 100
                return {
                    'rank': i + 1,
                    'total': len(sorted_stocks),
                    'percentile': percentile,
                    'top_n': i + 1
                }
        return None

    @staticmethod
    def score_to_percentile(score):
        """将评分转换为市场百分位（基于正态分布近似）"""
        # 假设市场平均60，标准差15
        z = (score - 60) / 15
        # 简单近似
        percentile = 50 * (1 + math.erf(z / math.sqrt(2)))
        return round(percentile)

    @staticmethod
    def get_grade(score):
        """获取评级"""
        if score >= 85: return 'A+'
        elif score >= 75: return 'A'
        elif score >= 65: return 'B+'
        elif score >= 55: return 'B'
        elif score >= 45: return 'C+'
        elif score >= 35: return 'C'
        return 'D'

    @staticmethod
    def get_recommendation(score):
        """获取投资建议"""
        if score >= 80: return '强烈推荐'
        elif score >= 70: return '推荐'
        elif score >= 60: return '关注'
        elif score >= 50: return '观望'
        elif score >= 40: return '谨慎'
        return '回避'

    @staticmethod
    def dim_label(dim):
        """维度中文标签"""
        labels = {
            'trend': '趋势',
            'momentum': '动量',
            'volatility': '波动',
            'volume': '成交量',
            'valuation': '估值',
            'quality': '质量',
            'growth': '成长',
            'sentiment': '情绪'
        }
        return labels.get(dim, dim)
