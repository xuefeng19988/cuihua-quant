<template>
  <div class="ai-extended-features">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Phase 301: AI 回测 -->
      <el-tab-pane label="🎯 AI 回测" name="backtest">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-card>
              <div slot="header">🎯 AI 策略回测</div>
              <el-input type="textarea" v-model="backtestDesc" :rows="3" placeholder="描述你的交易策略，如：当5日均线上穿20日均线时买入，下穿时卖出，初始资金100万" />
              <el-button type="primary" @click="runBacktest" :loading="backtestLoading" style="margin-top:8px;">🚀 AI 回测</el-button>
              <div v-if="backtestResult" style="margin-top:16px;">
                <el-row :gutter="12">
                  <el-col :span="6"><el-statistic title="年化收益" :value="backtestResult.annual_return" suffix="%" /></el-col>
                  <el-col :span="6"><el-statistic title="最大回撤" :value="backtestResult.max_drawdown" suffix="%" /></el-col>
                  <el-col :span="6"><el-statistic title="夏普比率" :value="backtestResult.sharpe_ratio" /></el-col>
                  <el-col :span="6"><el-statistic title="胜率" :value="backtestResult.win_rate" suffix="%" /></el-col>
                </el-row>
                <div id="backtest-chart" style="width:100%;height:250px;margin-top:16px;"></div>
                <div v-if="backtestResult.ai_analysis" style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:8px;" v-html="formatText(backtestResult.ai_analysis)" />
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div slot="header">📋 策略模板</div>
              <div v-for="s in strategyTemplates" :key="s.name" class="strategy-item" @click="useStrategy(s)">
                <div class="strategy-name">{{ s.name }}</div>
                <div class="strategy-desc">{{ s.description }}</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Phase 302: AI 实时盯盘 -->
      <el-tab-pane label="📡 实时盯盘" name="monitor">
        <el-card>
          <div slot="header">
            <span>📡 AI 实时盯盘</span>
            <el-button size="mini" :type="monitorRunning ? 'danger' : 'success'" @click="toggleMonitor">
              {{ monitorRunning ? '⏹ 停止' : '▶ 启动' }}
            </el-button>
          </div>
          <el-alert v-if="monitorAlerts.length" :title="`发现 ${monitorAlerts.length} 条异动`" type="warning" show-icon style="margin-bottom:12px;" />
          <el-timeline>
            <el-timeline-item v-for="(a, i) in monitorAlerts" :key="i" :timestamp="a.timestamp" placement="top">
              <el-card>
                <h4>{{ a.name }} ({{ a.code }})</h4>
                <el-tag v-for="al in a.alerts" :key="al.type" :type="al.level === 'high' ? 'danger' : 'warning'" size="mini" style="margin-right:4px;">
                  {{ al.type }}: {{ al.message }}
                </el-tag>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-if="!monitorAlerts.length" description="暂无异动" />
        </el-card>
      </el-tab-pane>

      <!-- Phase 303: AI 知识库 -->
      <el-tab-pane label="🧠 知识库" name="knowledge">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-card>
              <div slot="header">🧠 AI 知识问答</div>
              <el-input v-model="kbQuery" placeholder="输入问题，如：贵州茅台的投资逻辑是什么？" @keyup.enter.native="askKnowledge" />
              <el-button type="primary" @click="askKnowledge" :loading="kbLoading" style="margin-top:8px;">🔍 搜索</el-button>
              <div v-if="kbAnswer" style="margin-top:16px;">
                <el-card><div slot="header">回答</div><div v-html="formatText(kbAnswer)" /></el-card>
                <div v-if="kbSources.length" style="margin-top:8px;">
                  <div style="font-size:12px;color:#909399;margin-bottom:4px;">来源:</div>
                  <el-tag v-for="s in kbSources" :key="s.id" size="mini" style="margin-right:4px;">{{ s.title }} ({{ s.score }})</el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div slot="header">📚 添加知识</div>
              <el-input v-model="kbDocTitle" placeholder="标题" style="margin-bottom:8px;" />
              <el-select v-model="kbDocCategory" style="width:100%;margin-bottom:8px;">
                <el-option label="股票分析" value="stock" />
                <el-option label="研报" value="research" />
                <el-option label="笔记" value="note" />
                <el-option label="决策记录" value="decision" />
              </el-select>
              <el-input type="textarea" v-model="kbDocContent" :rows="6" placeholder="内容" />
              <el-button type="primary" @click="addKnowledge" :loading="kbDocLoading" style="margin-top:8px;width:100%;">添加</el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Phase 307: Prompt 模板 -->
      <el-tab-pane label="📝 Prompt 模板" name="prompts">
        <el-card>
          <div slot="header">
            <span>📝 Prompt 模板管理</span>
            <el-button size="mini" type="primary" @click="showAddPrompt">➕ 新建</el-button>
          </div>
          <el-table :data="promptTemplates" stripe border>
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="version" label="版本" width="80" />
            <el-table-column prop="system" label="系统提示" show-overflow-tooltip />
            <el-table-column label="操作" width="120">
              <template slot-scope="{row}">
                <el-button size="mini" type="text" @click="editPrompt(row)">编辑</el-button>
                <el-button size="mini" type="text" style="color:#f56c6c;" @click="deletePrompt(row.name)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Phase 306: 多模型代理 -->
      <el-tab-pane label="🔄 多模型代理" name="proxy">
        <el-card>
          <div slot="header">🔄 多模型并发 + 自动降级</div>
          <el-form label-width="100px">
            <el-form-item label="百炼 Key"><el-input v-model="apiKeys.bailian" type="password" placeholder="sk-..." /></el-form-item>
            <el-form-item label="OpenAI Key"><el-input v-model="apiKeys.openai" type="password" placeholder="sk-..." /></el-form-item>
            <el-form-item label="DeepSeek Key"><el-input v-model="apiKeys.deepseek" type="password" placeholder="sk-..." /></el-form-item>
          </el-form>
          <el-input v-model="proxyQuestion" type="textarea" :rows="2" placeholder="输入问题..." style="margin-bottom:8px;" />
          <el-button type="primary" @click="askProxy" :loading="proxyLoading">🚀 发送 (自动降级)</el-button>
          <div v-if="proxyAnswer" style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:8px;">
            <div style="font-size:12px;color:#909399;">使用: {{ proxyProvider }}</div>
            <div v-html="formatText(proxyAnswer)" />
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 新增 Prompt 对话框 -->
    <el-dialog :title="promptDialogTitle" :visible.sync="promptDialogVisible" width="600px">
      <el-form :model="promptForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="promptForm.name" /></el-form-item>
        <el-form-item label="系统提示"><el-input type="textarea" v-model="promptForm.system" :rows="3" /></el-form-item>
        <el-form-item label="用户提示"><el-input type="textarea" v-model="promptForm.user" :rows="4" /></el-form-item>
        <el-form-item label="温度"><el-slider v-model="promptForm.temperature" :min="0" :max="1" :step="0.1" /></el-form-item>
        <el-form-item label="最大 Token"><el-input-number v-model="promptForm.max_tokens" :min="100" :max="4000" /></el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="promptDialogVisible=false">取消</el-button>
        <el-button type="primary" @click="savePrompt">保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import request from '@/utils/request'

export default {
  name: 'AIExtendedFeatures',
  data() {
    return {
      activeTab: 'backtest',
      // 301 回测
      backtestDesc: '', backtestLoading: false, backtestResult: null,
      strategyTemplates: [],
      // 302 盯盘
      monitorRunning: false, monitorAlerts: [], monitorTimer: null,
      // 303 知识库
      kbQuery: '', kbLoading: false, kbAnswer: '', kbSources: [],
      kbDocTitle: '', kbDocContent: '', kbDocCategory: 'stock', kbDocLoading: false,
      // 307 Prompt 模板
      promptTemplates: [], promptDialogVisible: false, promptForm: {}, promptDialogTitle: '新建模板',
      // 306 多模型代理
      apiKeys: { bailian: '', openai: '', deepseek: '' },
      proxyQuestion: '', proxyLoading: false, proxyAnswer: '', proxyProvider: '',
    }
  },
  mounted() { this.loadStrategies(); this.loadPrompts() },
  methods: {
    formatText(t) { return (t || '').replace(/\n/g, '<br/>') },

    // Phase 301: AI 回测
    async loadStrategies() {
      try { const { data } = await request.get('/api/ai/backtest-strategies'); if (data.code === 200) this.strategyTemplates = data.data.strategies } catch (e) {}
    },
    useStrategy(s) { this.backtestDesc = s.description },
    async runBacktest() {
      if (!this.backtestDesc) return this.$message.warning('请描述策略')
      this.backtestLoading = true
      try {
        const { data } = await request.post('/api/ai/backtest-gen', { description: this.backtestDesc })
        if (data.code === 200) {
          this.backtestResult = data.data.result
          this.$nextTick(() => this.renderBacktestChart())
        }
      } catch (e) { this.$message.error('回测失败') }
      finally { this.backtestLoading = false }
    },
    renderBacktestChart() {
      const el = document.getElementById('backtest-chart')
      if (!el || !this.backtestResult) return
      const chart = echarts.init(el)
      const mr = this.backtestResult.monthly_returns
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: mr.map((_, i) => `M${i + 1}`) },
        yAxis: { type: 'value', name: '净值' },
        series: [{ type: 'line', data: mr.map(m => m.value), smooth: true, areaStyle: { color: 'rgba(64,158,255,0.2)' } }]
      })
    },

    // Phase 302: 实时盯盘
    async toggleMonitor() {
      if (this.monitorRunning) {
        await request.post('/api/ai/monitor/stop')
        this.monitorRunning = false
        clearInterval(this.monitorTimer)
      } else {
        await request.post('/api/ai/monitor/start')
        this.monitorRunning = true
        this.monitorTimer = setInterval(() => this.checkMonitor(), 5000)
      }
    },
    async checkMonitor() {
      try {
        const { data } = await request.post('/api/ai/monitor/check')
        if (data.code === 200 && data.data.alerts.length) {
          this.monitorAlerts = [...data.data.alerts, ...this.monitorAlerts].slice(0, 50)
        }
      } catch (e) {}
    },

    // Phase 303: 知识库
    async askKnowledge() {
      if (!this.kbQuery) return
      this.kbLoading = true
      try {
        const { data } = await request.post('/api/ai/knowledge/qa', { question: this.kbQuery })
        if (data.code === 200) { this.kbAnswer = data.data.answer; this.kbSources = data.data.sources || [] }
      } catch (e) { this.$message.error('查询失败') }
      finally { this.kbLoading = false }
    },
    async addKnowledge() {
      if (!this.kbDocContent) return this.$message.warning('请输入内容')
      this.kbDocLoading = true
      try {
        const { data } = await request.post('/api/ai/knowledge/add', {
          title: this.kbDocTitle || '未命名', content: this.kbDocContent, category: this.kbDocCategory
        })
        if (data.code === 200) { this.$message.success('已添加'); this.kbDocTitle = ''; this.kbDocContent = '' }
      } catch (e) { this.$message.error('添加失败') }
      finally { this.kbDocLoading = false }
    },

    // Phase 307: Prompt 模板
    async loadPrompts() {
      try { const { data } = await request.get('/api/prompt-templates'); if (data.code === 200) this.promptTemplates = Object.values(data.data.templates) } catch (e) {}
    },
    showAddPrompt() { this.promptDialogTitle = '新建模板'; this.promptForm = { name: '', system: '', user: '', temperature: 0.7, max_tokens: 1000, version: '1.0' }; this.promptDialogVisible = true },
    editPrompt(row) { this.promptDialogTitle = '编辑模板'; this.promptForm = { ...row }; this.promptDialogVisible = true },
    async savePrompt() {
      try {
        const method = this.promptTemplates.find(t => t.name === this.promptForm.name) ? 'put' : 'post'
        const { data } = await request[method](`/api/prompt-templates/${this.promptForm.name}`, this.promptForm)
        if (data.code === 200) { this.$message.success('已保存'); this.promptDialogVisible = false; this.loadPrompts() }
      } catch (e) { this.$message.error('保存失败') }
    },
    async deletePrompt(name) {
      try { await request.delete(`/api/prompt-templates/${name}`); this.$message.success('已删除'); this.loadPrompts() } catch (e) {}
    },

    // Phase 306: 多模型代理
    async askProxy() {
      if (!this.proxyQuestion) return
      this.proxyLoading = true
      try {
        const { data } = await request.post('/api/ai/proxy/chat', { question: this.proxyQuestion, api_keys: this.apiKeys })
        if (data.code === 200) { this.proxyAnswer = data.data.content; this.proxyProvider = data.data.used_provider }
      } catch (e) { this.$message.error('请求失败') }
      finally { this.proxyLoading = false }
    },
  }
}
</script>

<style scoped>
.ai-extended-features { padding: 20px; }
.strategy-item { padding: 10px; border-bottom: 1px solid #ebeef5; cursor: pointer; }
.strategy-item:hover { background: #f5f7fa; }
.strategy-name { font-weight: bold; font-size: 14px; }
.strategy-desc { font-size: 12px; color: #909399; margin-top: 4px; }
</style>
