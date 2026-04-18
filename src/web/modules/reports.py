"""
报表导出模块 - Phase 221
支持 PDF/Excel/Word 多格式导出
"""
from flask import Blueprint, request, jsonify, send_file
import io
import os
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/api/export/report', methods=['POST'])
def export_report():
    """导出报表"""
    data = request.get_json() or {}
    report_type = data.get('type', 'excel')
    report_data = data.get('data', {})
    
    if report_type == 'excel':
        return _export_excel(report_data)
    elif report_type == 'csv':
        return _export_csv(report_data)
    elif report_type == 'json':
        return _export_json(report_data)
    else:
        return jsonify({'code': 400, 'message': '不支持的格式'})

def _export_excel(data):
    """导出Excel"""
    try:
        import pandas as pd
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, sheet_data in data.items():
                if isinstance(sheet_data, list) and len(sheet_data) > 0:
                    df = pd.DataFrame(sheet_data)
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        
        output.seek(0)
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'code': 500, 'message': f'导出失败: {str(e)}'})

def _export_csv(data):
    """导出CSV"""
    try:
        import pandas as pd
        output = io.StringIO()
        
        for sheet_name, sheet_data in data.items():
            if isinstance(sheet_data, list) and len(sheet_data) > 0:
                df = pd.DataFrame(sheet_data)
                df.to_csv(output, index=False)
        
        output.seek(0)
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'code': 500, 'message': f'导出失败: {str(e)}'})

def _export_json(data):
    """导出JSON"""
    import json
    output = io.BytesIO()
    output.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    output.seek(0)
    
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

@reports_bp.route('/api/export/templates', methods=['GET'])
def get_report_templates():
    """获取报表模板"""
    return jsonify({
        'code': 200,
        'data': {
            'templates': [
                {'id': 'stock_list', 'name': '股票列表', 'type': 'excel'},
                {'id': 'portfolio_summary', 'name': '投资组合摘要', 'type': 'excel'},
                {'id': 'performance_report', 'name': '绩效报告', 'type': 'excel'},
                {'id': 'trade_history', 'name': '交易历史', 'type': 'csv'},
                {'id': 'notes_export', 'name': '笔记导出', 'type': 'json'}
            ]
        }
    })
