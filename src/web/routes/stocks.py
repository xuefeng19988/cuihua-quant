"""
Phase 269: 股票路由模块
从 api_server.py 拆分: 股票CRUD + 评分 + 排行 + 对比
"""
from flask import Blueprint, jsonify, request

stocks_bp = Blueprint('stocks', __name__, url_prefix='/api')


def register_stock_routes(app, helpers):
    """注册股票相关路由"""
    _h = helpers  # token_required, get_stock_codes, get_stock_names, get_db_engine, _build_stock_score_data

    @app.route('/api/stocks', methods=['GET'])
    @_h['token_required']
    def api_stocks():
        """获取股票列表"""
        try:
            from src.data.database import get_db_engine
            engine = get_db_engine()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            
            from sqlalchemy import text
            import pandas as pd
            result = pd.read_sql(text("SELECT code, name, market, industry FROM stock_info ORDER BY code"), engine)
            stocks = result.to_dict('records')
            
            return jsonify({'code': 200, 'data': {'stocks': stocks, 'total': len(stocks)}})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/stock-detail/<code>', methods=['GET'])
    @_h['token_required']
    def api_stock_detail(code):
        """获取股票详情"""
        try:
            from src.data.database import get_db_engine
            from sqlalchemy import text
            import pandas as pd
            
            engine = get_db_engine()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            
            # 基本信息
            info = pd.read_sql(text(f"SELECT * FROM stock_info WHERE code='{code}'"), engine)
            if info.empty:
                return jsonify({'code': 404, 'message': '股票不存在'})
            
            # 最新行情
            latest = pd.read_sql(text(f"SELECT * FROM stock_daily WHERE code='{code}' ORDER BY date DESC LIMIT 1"), engine)
            
            return jsonify({
                'code': 200,
                'data': {
                    'info': info.iloc[0].to_dict(),
                    'latest': latest.iloc[0].to_dict() if not latest.empty else None
                }
            })
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/stock-score/<code>', methods=['GET'])
    @_h['token_required']
    def api_stock_score(code):
        """获取股票综合评分"""
        try:
            from src.web.modules.stock_scorer import StockScorer
            engine = _h['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            
            stock_data = _h['_build_stock_score_data'](code, engine)
            if not stock_data:
                return jsonify({'code': 404, 'message': '股票数据不存在'})
            
            score_result = StockScorer.calculate_score(stock_data)
            return jsonify({
                'code': 200,
                'data': {
                    'code': code,
                    'score': score_result['total'],
                    'percentile': score_result['percentile'],
                    'grade': score_result['grade'],
                    'recommendation': score_result['recommendation'],
                    'scores': score_result['scores'],
                    'strengths': score_result['strengths'],
                    'weaknesses': score_result['weaknesses'],
                    'weights': score_result['weights']
                }
            })
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/stock-ranking', methods=['GET'])
    @_h['token_required']
    def api_stock_ranking():
        """获取股票排名 (Phase 268 优化: 批量查询)"""
        try:
            from src.web.modules.stock_scorer import StockScorer
            from src.web.modules.batch_scorer import batch_build_score_data
            engine = _h['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            
            limit = int(request.args.get('limit', 50))
            market = request.args.get('market', '')
            min_score = int(request.args.get('min_score', 0))
            sort_by = request.args.get('sort_by', 'score')
            
            stocks = _h['get_stock_codes']()
            sn = _h['get_stock_names']()
            
            if market == 'A':
                filtered = [c for c in stocks if c.startswith(('SH.', 'SZ.'))]
            elif market == 'HK':
                filtered = [c for c in stocks if c.startswith('HK.')]
            else:
                filtered = stocks
            
            batch_data = batch_build_score_data(filtered, engine)
            
            rankings = []
            for code in filtered:
                stock_data = batch_data.get(code)
                if not stock_data:
                    continue
                score_result = StockScorer.calculate_score(stock_data)
                if score_result['total'] < min_score:
                    continue
                rankings.append({
                    'code': code, 'name': sn.get(code, ''),
                    'score': score_result['total'],
                    'percentile': score_result['percentile'],
                    'grade': score_result['grade'],
                    'recommendation': score_result['recommendation'],
                    'scores': score_result['scores'],
                    'price': stock_data['price'],
                    'change': stock_data['change']
                })
            
            if sort_by in ('trend', 'momentum', 'valuation', 'quality', 'growth'):
                rankings.sort(key=lambda x: x['scores'].get(sort_by, 0), reverse=True)
            else:
                rankings.sort(key=lambda x: x['score'], reverse=True)
            rankings = rankings[:limit]
            
            for i, r in enumerate(rankings):
                r['rank'] = i + 1
            
            all_scores = [r['score'] for r in rankings]
            return jsonify({
                'code': 200,
                'data': {
                    'rankings': rankings,
                    'total': len(rankings),
                    'avg_score': round(sum(all_scores) / len(all_scores)) if all_scores else 0,
                    'max_score': max(all_scores) if all_scores else 0,
                    'min_score': min(all_scores) if all_scores else 0
                }
            })
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/stock-compare', methods=['POST'])
    @_h['token_required']
    def api_stock_compare():
        """股票对比评分分析"""
        try:
            from src.web.modules.stock_scorer import StockScorer
            from src.web.modules.batch_scorer import batch_build_score_data
            engine = _h['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            
            data = request.get_json() or {}
            codes = data.get('codes', [])
            if not codes or len(codes) < 2:
                return jsonify({'code': 400, 'message': '请至少选择2只股票'})
            if len(codes) > 10:
                return jsonify({'code': 400, 'message': '最多对比10只股票'})
            
            sn = _h['get_stock_names']()
            batch_data = batch_build_score_data(codes, engine)
            
            stock_list = []
            for code in codes:
                stock_data = batch_data.get(code)
                if not stock_data:
                    continue
                score_result = StockScorer.calculate_score(stock_data)
                stock_list.append({
                    'code': code, 'name': sn.get(code, ''),
                    'price': stock_data['price'],
                    'change': stock_data['change'],
                    'score_result': score_result
                })
            
            compare_result = StockScorer.compare_stocks(stock_list)
            return jsonify({'code': 200, 'data': compare_result})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})

    @app.route('/api/stock-score-batch', methods=['POST'])
    @_h['token_required']
    def api_stock_score_batch():
        """批量评分 (Phase 268: 仅2条SQL)"""
        try:
            from src.web.modules.stock_scorer import StockScorer
            from src.web.modules.batch_scorer import batch_build_score_data
            engine = _h['get_db_engine']()
            if not engine:
                return jsonify({'code': 500, 'message': '数据库未连接'})
            
            data = request.get_json() or {}
            codes = data.get('codes', [])
            if not codes:
                codes = _h['get_stock_codes']()
            
            sn = _h['get_stock_names']()
            batch_data = batch_build_score_data(codes, engine)
            
            results = []
            for code in codes:
                stock_data = batch_data.get(code)
                if not stock_data:
                    continue
                score_result = StockScorer.calculate_score(stock_data)
                results.append({
                    'code': code, 'name': sn.get(code, ''),
                    'score': score_result['total'],
                    'grade': score_result['grade'],
                    'percentile': score_result['percentile'],
                    'recommendation': score_result['recommendation'],
                    'scores': score_result['scores'],
                    'price': stock_data['price'],
                    'change': stock_data['change']
                })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return jsonify({
                'code': 200,
                'data': {'results': results, 'total': len(results), 'sql_queries': 2}
            })
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)})
