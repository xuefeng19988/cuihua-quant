/**
 * 股票评分系统 - Phase 250
 * 综合评分算法，多维度评估股票
 */

export class StockScorer {
  /**
   * 计算股票综合评分
   * @param {Object} stockData - 股票数据
   * @returns {Object} 评分结果
   */
  static calculateScore(stockData) {
    const {
      price,
      change,
      volume,
      turnover,
      pe,
      pb,
      roe,
      rsi,
      macd,
      ma5,
      ma20,
      week52High,
      week52Low
    } = stockData

    // 各维度评分 (0-100)
    const scores = {
      trend: this.calculateTrendScore(price, ma5, ma20, week52High, week52Low),
      momentum: this.calculateMomentumScore(change, rsi, macd),
      volatility: this.calculateVolatilityScore(week52High, week52Low, price),
      volume: this.calculateVolumeScore(volume, turnover),
      valuation: this.calculateValuationScore(pe, pb, roe)
    }

    // 权重计算综合评分
    const weights = {
      trend: 0.25,
      momentum: 0.20,
      volatility: 0.15,
      volume: 0.15,
      valuation: 0.25
    }

    const totalScore = Object.entries(scores).reduce((sum, [key, score]) => {
      return sum + score * weights[key]
    }, 0)

    return {
      total: Math.round(totalScore),
      scores,
      grade: this.getGrade(totalScore),
      recommendation: this.getRecommendation(totalScore)
    }
  }

  /**
   * 趋势评分
   */
  static calculateTrendScore(price, ma5, ma20, week52High, week52Low) {
    let score = 50
    
    // 均线趋势
    if (price > ma5 && ma5 > ma20) score += 20
    else if (price > ma5) score += 10
    else if (price < ma20) score -= 15
    
    // 52周位置
    const range = week52High - week52Low
    if (range > 0) {
      const position = (price - week52Low) / range
      score += (position - 0.5) * 30
    }
    
    return Math.max(0, Math.min(100, score))
  }

  /**
   * 动量评分
   */
  static calculateMomentumScore(change, rsi, macd) {
    let score = 50
    
    // 涨跌幅
    score += change * 2
    
    // RSI
    if (rsi < 30) score += 15 // 超卖
    else if (rsi > 70) score -= 10 // 超买
    else score += 5
    
    // MACD
    if (macd > 0) score += 10
    else score -= 5
    
    return Math.max(0, Math.min(100, score))
  }

  /**
   * 波动率评分
   */
  static calculateVolatilityScore(week52High, week52Low, price) {
    const range = (week52High - week52Low) / week52Low * 100
    
    // 适度波动最佳
    if (range >= 20 && range <= 60) return 80
    if (range >= 10 && range < 20) return 70
    if (range > 60 && range <= 80) return 60
    if (range > 80) return 40
    return 50
  }

  /**
   * 成交量评分
   */
  static calculateVolumeScore(volume, turnover) {
    // 换手率适中最佳
    if (turnover >= 2 && turnover <= 8) return 80
    if (turnover >= 1 && turnover < 2) return 70
    if (turnover > 8 && turnover <= 15) return 60
    if (turnover > 15) return 40
    return 50
  }

  /**
   * 估值评分
   */
  static calculateValuationScore(pe, pb, roe) {
    let score = 50
    
    // PE估值
    if (pe >= 10 && pe <= 25) score += 15
    else if (pe < 10) score += 10
    else if (pe > 40) score -= 10
    
    // PB估值
    if (pb >= 1 && pb <= 3) score += 10
    else if (pb > 5) score -= 5
    
    // ROE
    if (roe >= 15) score += 15
    else if (roe >= 10) score += 10
    else if (roe < 5) score -= 5
    
    return Math.max(0, Math.min(100, score))
  }

  /**
   * 获取评级
   */
  static getGrade(score) {
    if (score >= 85) return 'A+'
    if (score >= 75) return 'A'
    if (score >= 65) return 'B+'
    if (score >= 55) return 'B'
    if (score >= 45) return 'C+'
    if (score >= 35) return 'C'
    return 'D'
  }

  /**
   * 获取投资建议
   */
  static getRecommendation(score) {
    if (score >= 80) return '强烈推荐'
    if (score >= 70) return '推荐'
    if (score >= 60) return '关注'
    if (score >= 50) return '观望'
    if (score >= 40) return '谨慎'
    return '回避'
  }
}
