"""
股票评分系统 - Phase 250
综合评分算法，多维度评估股票
"""

class StockScorer:
    """股票综合评分器"""
    
    @staticmethod
    def calculate_score(stock_data):
        """
        计算股票综合评分
        :param stock_data: 股票数据字典
        :return: 评分结果字典
        """
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
        week52_high = stock_data.get('week52_high', price)
        week52_low = stock_data.get('week52_low', price)
        
        # 各维度评分 (0-100)
        scores = {
            'trend': StockScorer.calculate_trend_score(price, ma5, ma20, week52_high, week52_low),
            'momentum': StockScorer.calculate_momentum_score(change, rsi, macd),
            'volatility': StockScorer.calculate_volatility_score(week52_high, week52_low, price),
            'volume': StockScorer.calculate_volume_score(volume, turnover),
            'valuation': StockScorer.calculate_valuation_score(pe, pb, roe)
        }
        
        # 权重计算综合评分
        weights = {
            'trend': 0.25,
            'momentum': 0.20,
            'volatility': 0.15,
            'volume': 0.15,
            'valuation': 0.25
        }
        
        total_score = sum(score * weights[key] for key, score in scores.items())
        
        return {
            'total': round(total_score),
            'scores': scores,
            'grade': StockScorer.get_grade(total_score),
            'recommendation': StockScorer.get_recommendation(total_score)
        }
    
    @staticmethod
    def calculate_trend_score(price, ma5, ma20, week52_high, week52_low):
        """趋势评分"""
        score = 50
        
        # 均线趋势
        if price > ma5 and ma5 > ma20:
            score += 20
        elif price > ma5:
            score += 10
        elif price < ma20:
            score -= 15
        
        # 52周位置
        range_ = week52_high - week52_low
        if range_ > 0:
            position = (price - week52_low) / range_
            score += (position - 0.5) * 30
        
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_momentum_score(change, rsi, macd):
        """动量评分"""
        score = 50
        
        # 涨跌幅
        score += change * 2
        
        # RSI
        if rsi < 30:
            score += 15  # 超卖
        elif rsi > 70:
            score -= 10  # 超买
        else:
            score += 5
        
        # MACD
        if macd > 0:
            score += 10
        else:
            score -= 5
        
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_volatility_score(week52_high, week52_low, price):
        """波动率评分"""
        range_ = (week52_high - week52_low) / week52_low * 100 if week52_low > 0 else 0
        
        # 适度波动最佳
        if 20 <= range_ <= 60:
            return 80
        elif 10 <= range_ < 20:
            return 70
        elif 60 < range_ <= 80:
            return 60
        elif range_ > 80:
            return 40
        return 50
    
    @staticmethod
    def calculate_volume_score(volume, turnover):
        """成交量评分"""
        # 换手率适中最佳
        if 2 <= turnover <= 8:
            return 80
        elif 1 <= turnover < 2:
            return 70
        elif 8 < turnover <= 15:
            return 60
        elif turnover > 15:
            return 40
        return 50
    
    @staticmethod
    def calculate_valuation_score(pe, pb, roe):
        """估值评分"""
        score = 50
        
        # PE估值
        if 10 <= pe <= 25:
            score += 15
        elif pe < 10:
            score += 10
        elif pe > 40:
            score -= 10
        
        # PB估值
        if 1 <= pb <= 3:
            score += 10
        elif pb > 5:
            score -= 5
        
        # ROE
        if roe >= 15:
            score += 15
        elif roe >= 10:
            score += 10
        elif roe < 5:
            score -= 5
        
        return max(0, min(100, score))
    
    @staticmethod
    def get_grade(score):
        """获取评级"""
        if score >= 85:
            return 'A+'
        elif score >= 75:
            return 'A'
        elif score >= 65:
            return 'B+'
        elif score >= 55:
            return 'B'
        elif score >= 45:
            return 'C+'
        elif score >= 35:
            return 'C'
        return 'D'
    
    @staticmethod
    def get_recommendation(score):
        """获取投资建议"""
        if score >= 80:
            return '强烈推荐'
        elif score >= 70:
            return '推荐'
        elif score >= 60:
            return '关注'
        elif score >= 50:
            return '观望'
        elif score >= 40:
            return '谨慎'
        return '回避'
