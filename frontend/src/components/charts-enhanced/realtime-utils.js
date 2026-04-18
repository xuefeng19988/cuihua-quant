/**
 * 实时行情推送工具 - Phase 253
 * WebSocket 实时数据推送
 */

export class RealtimeQuoteUtils {
  constructor(url, options = {}) {
    this.url = url
    this.ws = null
    this.connected = false
    this.reconnectInterval = options.reconnectInterval || 3000
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10
    this.reconnectAttempts = 0
    this.subscribers = []
    this.autoReconnect = options.autoReconnect !== false
  }
  
  /**
   * 连接 WebSocket
   */
  connect() {
    try {
      this.ws = new WebSocket(this.url)
      
      this.ws.onopen = () => {
        this.connected = true
        this.reconnectAttempts = 0
        this._notifySubscribers('connected', null)
        console.log('[RealtimeQuote] 已连接')
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this._notifySubscribers('quote', data)
        } catch (e) {
          console.error('[RealtimeQuote] 数据解析失败:', e)
        }
      }
      
      this.ws.onclose = () => {
        this.connected = false
        this._notifySubscribers('disconnected', null)
        console.log('[RealtimeQuote] 已断开')
        
        if (this.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          setTimeout(() => this.connect(), this.reconnectInterval)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('[RealtimeQuote] 错误:', error)
        this._notifySubscribers('error', error)
      }
    } catch (e) {
      console.error('[RealtimeQuote] 连接失败:', e)
    }
  }
  
  /**
   * 断开连接
   */
  disconnect() {
    this.autoReconnect = false
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
  
  /**
   * 订阅行情数据
   * @param {Function} callback - 回调函数
   * @returns {Function} 取消订阅函数
   */
  subscribe(callback) {
    this.subscribers.push(callback)
    
    // 返回取消订阅函数
    return () => {
      this.subscribers = this.subscribers.filter(cb => cb !== callback)
    }
  }
  
  /**
   * 通知所有订阅者
   * @param {string} type - 事件类型
   * @param {*} data - 数据
   */
  _notifySubscribers(type, data) {
    this.subscribers.forEach(callback => {
      try {
        callback(type, data)
      } catch (e) {
        console.error('[RealtimeQuote] 回调错误:', e)
      }
    })
  }
  
  /**
   * 发送消息
   * @param {Object} message - 消息内容
   */
  send(message) {
    if (this.ws && this.connected) {
      this.ws.send(JSON.stringify(message))
    }
  }
  
  /**
   * 订阅特定股票
   * @param {string} code - 股票代码
   */
  subscribeStock(code) {
    this.send({
      action: 'subscribe',
      code
    })
  }
  
  /**
   * 取消订阅特定股票
   * @param {string} code - 股票代码
   */
  unsubscribeStock(code) {
    this.send({
      action: 'unsubscribe',
      code
    })
  }
}

/**
 * 创建实时行情工具实例
 * @param {string} url - WebSocket URL
 * @param {Object} options - 配置选项
 * @returns {RealtimeQuoteUtils} 实例
 */
export function createRealtimeQuote(url, options = {}) {
  return new RealtimeQuoteUtils(url, options)
}
