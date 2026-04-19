<template>
  <div class="ai-chat-panel">
    <div class="chat-status">
      <el-tag :type="status.available ? 'success' : 'warning'" size="mini">
        {{ status.available ? '🟢 在线' : '🔴 离线' }}
      </el-tag>
      <span v-if="status.model" style="margin-left:8px;color:#909399;font-size:12px;">{{ status.model }}</span>
    </div>

    <div class="chat-messages" ref="messagesRef">
      <div v-for="(msg, idx) in messages" :key="idx" class="chat-msg" :class="msg.role">
        <div class="msg-bubble">
          <span class="msg-role">{{ msg.role === 'user' ? '🧑' : '🤖' }}</span>
          <div class="msg-content" v-html="sanitizeHTML(formatContent(msg.content))" />
        </div>
      </div>
      <div v-if="loading" class="chat-msg ai">
        <div class="msg-bubble">
          <span class="msg-role">🤖</span>
          <div class="msg-content">思考中...</div>
        </div>
      </div>
    </div>

    <div class="chat-input">
      <el-input v-model="input" type="textarea" :rows="2" placeholder="输入问题，如：今天大盘走势如何？"
        @keyup.enter.native="sendMessage" :disabled="loading" />
      <el-button type="primary" @click="sendMessage" :loading="loading" style="margin-top:8px;">发送</el-button>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'
import sanitizeMixin from '@/mixins/sanitize'

export default {
  mixins: [sanitizeMixin],
  name: 'AIChat',
  data() {
    return {
      messages: [],
      input: '',
      loading: false,
      status: { available: false, model: '' },
      history: []
    }
  },
  mounted() { this.checkStatus() },
  methods: {
    async checkStatus() {
      try {
        const { data } = await request.get('/api/ai/status')
        if (data.code === 200) {
          this.status = { available: data.data.available, model: data.data.model }
        }
      } catch (e) { /* ignore */ }
    },
    async sendMessage() {
      const q = this.input.trim()
      if (!q || this.loading) return
      this.messages.push({ role: 'user', content: q })
      this.input = ''
      this.loading = true

      try {
        const { data } = await request.post('/api/ai/chat', {
          question: q,
          history: this.history
        })
        if (data.code === 200) {
          const reply = data.data.content
          this.messages.push({ role: 'ai', content: reply })
          this.history.push({ role: 'user', content: q })
          this.history.push({ role: 'assistant', content: reply })
          this.$nextTick(() => this.scrollToBottom())
        } else {
          this.messages.push({ role: 'ai', content: `❌ ${data.message}` })
        }
      } catch (e) {
        this.messages.push({ role: 'ai', content: `❌ 请求失败: ${e.message}` })
      } finally {
        this.loading = false
      }
    },
    scrollToBottom() {
      const el = this.$refs.messagesRef
      if (el) el.scrollTop = el.scrollHeight
    },
    formatContent(text) {
      return text.replace(/\n/g, '<br/>')
    }
  }
}
</script>

<style scoped>
.ai-chat-panel { display:flex; flex-direction:column; height:600px; }
.chat-status { padding:8px 0; border-bottom:1px solid #ebeef5; margin-bottom:12px; }
.chat-messages { flex:1; overflow-y:auto; padding:12px 0; }
.chat-msg { margin-bottom:12px; display:flex; }
.chat-msg.user { justify-content:flex-end; }
.chat-msg.ai { justify-content:flex-start; }
.msg-bubble { max-width:70%; padding:10px 14px; border-radius:12px; background:#f5f7fa; }
.chat-msg.user .msg-bubble { background:#e6f7ff; }
.msg-role { margin-right:6px; }
.msg-content { font-size:14px; line-height:1.6; white-space:pre-wrap; }
.chat-input { border-top:1px solid #ebeef5; padding-top:12px; }
</style>
