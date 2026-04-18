/**
 * 快捷键系统 - Phase 223
 * 全局快捷键支持
 */
import Vue from 'vue'

const shortcutStore = {
  shortcuts: [
    { key: 'ctrl+k', action: 'globalSearch', desc: '全局搜索', enabled: true },
    { key: 'ctrl+n', action: 'newNote', desc: '新建笔记', enabled: true },
    { key: 'ctrl+s', action: 'save', desc: '保存', enabled: true },
    { key: 'ctrl+b', action: 'toggleSidebar', desc: '切换侧边栏', enabled: true },
    { key: 'f5', action: 'refresh', desc: '刷新数据', enabled: true },
    { key: 'escape', action: 'closeDialog', desc: '关闭弹窗', enabled: true },
    { key: 'ctrl+d', action: 'toggleTheme', desc: '切换主题', enabled: true },
    { key: 'ctrl+/', action: 'showShortcuts', desc: '显示快捷键', enabled: true }
  ],
  handlers: {}
}

// 注册快捷键
export function registerShortcut(key, handler) {
  shortcutStore.handlers[key] = handler
}

// 移除快捷键
export function unregisterShortcut(key) {
  delete shortcutStore.handlers[key]
}

// 快捷键指令
const ShortcutDirective = {
  bind(el, binding) {
    const key = binding.value.key
    const handler = binding.value.handler
    
    const onKeyDown = (e) => {
      const combo = []
      if (e.ctrlKey || e.metaKey) combo.push('ctrl')
      if (e.shiftKey) combo.push('shift')
      if (e.altKey) combo.push('alt')
      combo.push(e.key.toLowerCase())
      
      const keyCombo = combo.join('+')
      if (keyCombo === key && handler) {
        e.preventDefault()
        handler(e)
      }
    }
    
    el._shortcutHandler = onKeyDown
    document.addEventListener('keydown', onKeyDown)
  },
  unbind(el) {
    if (el._shortcutHandler) {
      document.removeEventListener('keydown', el._shortcutHandler)
    }
  }
}

Vue.directive('shortcut', ShortcutDirective)

// 获取快捷键列表
export function getShortcuts() {
  return shortcutStore.shortcuts
}

// 更新快捷键状态
export function updateShortcut(key, enabled) {
  const shortcut = shortcutStore.shortcuts.find(s => s.key === key)
  if (shortcut) {
    shortcut.enabled = enabled
  }
}

export default {
  registerShortcut,
  unregisterShortcut,
  getShortcuts,
  updateShortcut
}
