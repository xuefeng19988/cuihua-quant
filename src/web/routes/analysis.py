"""
Phase 269: 分析路由模块
图表、热力图、筛选器、资金流向、板块轮动、市场情绪
"""

def register_analysis_routes(app, helpers):
    """注册分析相关路由"""
    from flask import request, jsonify
    import pandas as pd

    @app.route('/api/charts', methods=['GET'])
    @helpers['token_required']
    def api_charts():
        """K线数据 + 技术指标"""
        code = request.args.get('code', 'SH.600519')
        days = int(request.args.get('days', 90))
        indicators = request.args.get('indicators', 'ma,macd,rsi,bb')

        engine = helpers['get_db_engine']()
        if not engine:
            return jsonify({'code': 200, 'data': {}})

        try:
            from sqlalchemy import text
            query = f"SELECT date, open_price, high_price, low_price, close_price, volume FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT {days}"
            df = pd.read_sql(text(query), engine)
            if df.empty:
                return jsonify({'code': 404, 'message': '无数据'})

            df = df.iloc[::-1].reset_index(drop=True)
            from src.analysis.technical import calculate_indicators
            df_for_indicators = df[['open_price', 'high_price', 'low_price', 'close_price', 'volume']].copy()
            df_for_indicators.columns = ['open', 'high', 'low', 'close', 'volume']
            df_with_indicators = calculate_indicators(df_for_indicators)

            result = {
                'code': code, 'dates': df['date'].tolist(),
                'open': df['open_price'].tolist(), 'high': df['high_price'].tolist(),
                'low': df['low_price'].tolist(), 'close': df['close_price'].tolist(),
                'volume': df['volume'].tolist(), 'indicators': {}
            }
            if 'ma' in indicators:
                result['indicators']['ma5'] = df_with_indicators['ma5'].round(2).tolist()
                result['indicators']['ma10'] = df_with_indicators['ma10'].round(2).tolist()
                result['indicators']['ma20'] = df_with_indicators['ma20'].round(2).tolist()
            if 'macd' in indicators:
                result['indicators']['macd'] = df_with_indicators['macd'].round(4).tolist()
                result['indicators']['macd_signal'] = df_with_indicators['macd_signal'].round(4).tolist()
                result['indicators']['macd_hist'] = df_with_indicators['macd_hist'].round(4).tolist()
            if 'rsi' in indicators:
                result['indicators']['rsi'] = df_with_indicators['rsi'].round(2).tolist()
            if 'bb' in indicators:
                result['indicators']['bb_upper'] = df_with_indicators['bb_upper'].round(2).tolist()
                result['indicators']['bb_middle'] = df_with_indicators['bb_middle'].round(2).tolist()
                result['indicators']['bb_lower'] = df_with_indicators['bb_lower'].round(2).tolist()

            return jsonify({'code': 200, 'data': result})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/heatmap', methods=['GET'])
    @helpers['token_required']
    def api_heatmap():
        """板块热力图"""
        try:
            from sqlalchemy import text
            engine = helpers['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            result = pd.read_sql(text("SELECT industry, AVG(change_pct) as avg_change, COUNT(*) as stock_count FROM stock_daily WHERE date = (SELECT MAX(date) FROM stock_daily) GROUP BY industry ORDER BY avg_change DESC"), engine)
            return jsonify({'code': 200, 'data': {'sectors': result.to_dict('records')}})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/fund-flow', methods=['GET'])
    @helpers['token_required']
    def api_fund_flow():
        """资金流向"""
        try:
            from sqlalchemy import text
            engine = helpers['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            result = pd.read_sql(text("SELECT code, name, change_pct, volume, turnover FROM stock_daily WHERE date = (SELECT MAX(date) FROM stock_daily) ORDER BY turnover DESC LIMIT 30"), engine)
            return jsonify({'code': 200, 'data': {'flows': result.to_dict('records')}})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/sector-rotation', methods=['GET'])
    @helpers['token_required']
    def api_sector_rotation():
        """板块轮动"""
        try:
            from sqlalchemy import text
            engine = helpers['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            result = pd.read_sql(text("SELECT industry, AVG(change_pct) as change_5d FROM stock_daily WHERE date >= (SELECT MAX(date) FROM stock_daily) - INTERVAL 5 DAY GROUP BY industry ORDER BY change_5d DESC LIMIT 20"), engine)
            return jsonify({'code': 200, 'data': {'rotations': result.to_dict('records')}})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/market-sentiment', methods=['GET'])
    @helpers['token_required']
    def api_market_sentiment():
        """市场情绪"""
        try:
            from sqlalchemy import text
            engine = helpers['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            result = pd.read_sql(text("SELECT COUNT(*) as total, SUM(CASE WHEN change_pct > 0 THEN 1 ELSE 0 END) as up, SUM(CASE WHEN change_pct < 0 THEN 1 ELSE 0 END) as down, AVG(change_pct) as avg_change, AVG(volume) as avg_volume FROM stock_daily WHERE date = (SELECT MAX(date) FROM stock_daily)"), engine)
            row = result.iloc[0]
            sentiment = 'bullish' if row['up'] > row['down'] else 'bearish'
            return jsonify({'code': 200, 'data': {'sentiment': sentiment, 'up': int(row['up']), 'down': int(row['down']), 'avg_change': round(float(row['avg_change']), 2)}})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/screener', methods=['POST'])
    @helpers['token_required']
    def api_screener():
        """智能选股器"""
        try:
            from sqlalchemy import text
            data = request.get_json() or {}
            engine = helpers['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            
            conditions = []
            if 'min_price' in data: conditions.append(f"close_price >= {data['min_price']}")
            if 'max_price' in data: conditions.append(f"close_price <= {data['max_price']}")
            if 'min_change' in data: conditions.append(f"change_pct >= {data['min_change']}")
            if 'max_change' in data: conditions.append(f"change_pct <= {data['max_change']}")
            if 'min_volume' in data: conditions.append(f"volume >= {data['min_volume']}")
            
            where = ' AND '.join(conditions) if conditions else '1=1'
            query = f"SELECT code, close_price, change_pct, volume FROM stock_daily WHERE date = (SELECT MAX(date) FROM stock_daily) AND {where} ORDER BY change_pct DESC LIMIT 100"
            result = pd.read_sql(text(query), engine)
            return jsonify({'code': 200, 'data': {'results': result.to_dict('records'), 'total': len(result)}})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})
