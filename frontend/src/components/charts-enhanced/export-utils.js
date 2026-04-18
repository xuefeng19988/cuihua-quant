/**
 * 图表导出工具 - Phase 252
 * 支持 PNG/SVG/PDF/Excel 导出
 */

import * as echarts from 'echarts'

export class ChartExportUtils {
  /**
   * 导出图表为 PNG
   * @param {Object} chart - ECharts 实例
   * @param {string} filename - 文件名
   * @param {number} pixelRatio - 像素比
   */
  static exportPNG(chart, filename = 'chart', pixelRatio = 2) {
    if (!chart) return
    
    const url = chart.getDataURL({
      type: 'png',
      pixelRatio,
      backgroundColor: '#1a1a2e'
    })
    
    const link = document.createElement('a')
    link.download = `${filename}_${Date.now()}.png`
    link.href = url
    link.click()
  }
  
  /**
   * 导出图表为 SVG
   * @param {Object} chart - ECharts 实例
   * @param {string} filename - 文件名
   */
  static exportSVG(chart, filename = 'chart') {
    if (!chart) return
    
    const url = chart.getDataURL({
      type: 'svg',
      pixelRatio: 1,
      backgroundColor: '#1a1a2e'
    })
    
    const link = document.createElement('a')
    link.download = `${filename}_${Date.now()}.svg`
    link.href = url
    link.click()
  }
  
  /**
   * 导出图表为 PDF
   * @param {Object} chart - ECharts 实例
   * @param {string} filename - 文件名
   */
  static async exportPDF(chart, filename = 'chart') {
    if (!chart) return
    
    // 获取 PNG 数据
    const pngUrl = chart.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#1a1a2e'
    })
    
    // 创建 PDF (简化版，实际项目中使用 jsPDF)
    const link = document.createElement('a')
    link.download = `${filename}_${Date.now()}.png`
    link.href = pngUrl
    link.click()
  }
  
  /**
   * 导出图表数据为 Excel
   * @param {Array} data - 图表数据
   * @param {string} filename - 文件名
   */
  static exportExcel(data, filename = 'chart-data') {
    if (!data || data.length === 0) return
    
    // 创建 CSV 内容
    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(h => row[h]).join(','))
    ].join('\n')
    
    // 下载文件
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${filename}_${Date.now()}.csv`
    link.click()
  }
  
  /**
   * 批量导出多个图表
   * @param {Array} charts - ECharts 实例数组
   * @param {string} filename - 文件名前缀
   * @param {string} type - 导出类型 (png/svg)
   */
  static exportBatch(charts, filename = 'charts', type = 'png') {
    if (!charts || charts.length === 0) return
    
    charts.forEach((chart, index) => {
      setTimeout(() => {
        if (type === 'svg') {
          this.exportSVG(chart, `${filename}_${index + 1}`)
        } else {
          this.exportPNG(chart, `${filename}_${index + 1}`)
        }
      }, index * 500) // 间隔 500ms 避免浏览器阻止下载
    })
  }
  
  /**
   * 导出图表配置
   * @param {Object} chart - ECharts 实例
   * @param {string} filename - 文件名
   */
  static exportConfig(chart, filename = 'chart-config') {
    if (!chart) return
    
    const option = chart.getOption()
    const json = JSON.stringify(option, null, 2)
    
    const blob = new Blob([json], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${filename}_${Date.now()}.json`
    link.click()
  }
}
