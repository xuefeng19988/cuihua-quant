<template>
  <div class="note-templates">
    <el-card>
      <div slot="header">📝 笔记模板</div>
      <el-row :gutter="16">
        <el-col :span="8" v-for="tpl in templates" :key="tpl.name" style="margin-bottom:12px;">
          <el-card shadow="hover" style="cursor:pointer;" @click.native="useTemplate(tpl)">
            <div style="font-size:16px;font-weight:bold;margin-bottom:8px;">{{ tpl.icon }} {{ tpl.name }}</div>
            <div style="font-size:12px;color:#909399;">{{ tpl.desc }}</div>
            <div style="margin-top:8px;">
              <el-tag v-for="tag in tpl.tags" :key="tag" size="mini" style="margin-right:4px;">{{ tag }}</el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 模板预览/使用对话框 -->
    <el-dialog :title="`使用模板: ${selectedTemplate?.name || ''}`" :visible.sync="dialogVisible" width="700px">
      <el-form v-if="selectedTemplate" label-width="80px">
        <el-form-item label="股票">
          <el-select v-model="form.code" filterable placeholder="选择关联股票" style="width:100%;">
            <el-option v-for="s in stockList" :key="s.code" :label="`${s.name} (${s.code})`" :value="s.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板内容">
          <el-input type="textarea" :rows="15" v-model="form.content" />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createNote">创建笔记</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'NoteTemplates',
  data() {
    return {
      dialogVisible: false,
      selectedTemplate: null,
      stockList: [],
      form: { code: '', content: '' },
      templates: [
        { name: '个股分析', icon: '📊', desc: '全面分析个股基本面和技术面', tags: ['股票', '分析'], content: `# 个股分析报告\n\n## 基本信息\n- 股票代码: \n- 股票名称: \n- 所属行业: \n\n## 基本面分析\n### 财务数据\n- 营收增长:\n- 净利润:\n- ROE:\n- 负债率:\n\n## 技术面分析\n### 均线系统\n- MA5:\n- MA20:\n- MA60:\n\n### 技术指标\n- MACD:\n- RSI:\n- KDJ:\n\n## 投资建议\n### 目标价\n- 保守: \n- 中性: \n- 乐观: \n\n### 风险提示\n- \n- \n\n## 结论\n\n` },
        { name: '复盘笔记', icon: '📝', desc: '每日交易复盘与反思', tags: ['复盘', '日志'], content: `# 每日复盘\n\n## 日期: \n\n## 今日操作\n| 时间 | 股票 | 操作 | 价格 | 数量 | 盈亏 |\n|------|------|------|------|------|------|\n| | | | | | |\n\n## 市场回顾\n- 大盘走势:\n- 板块表现:\n- 资金流向:\n\n## 操作反思\n### 做对的\n1. \n2. \n\n### 做错的\n1. \n2. \n\n## 明日计划\n- \n- \n\n## 心得感悟\n\n` },
        { name: '策略模板', icon: '🎯', desc: '交易策略设计与回测记录', tags: ['策略', '回测'], content: `# 交易策略\n\n## 策略名称\n\n## 策略逻辑\n### 入场条件\n1. \n2. \n\n### 出场条件\n1. \n2. \n\n### 仓位管理\n- 单票最大仓位:\n- 总仓位控制:\n\n## 回测参数\n- 回测区间: 至\n- 初始资金:\n- 手续费:\n\n## 预期结果\n- 年化收益:\n- 最大回撤:\n- 夏普比率:\n\n## 风险评估\n- 主要风险:\n- 应对措施:\n\n` },
        { name: '行业研究', icon: '🏢', desc: '行业深度研究报告', tags: ['行业', '研究'], content: `# 行业研究报告\n\n## 行业: \n\n## 行业概况\n- 市场规模:\n- 增速:\n- 集中度:\n\n## 产业链分析\n### 上游\n\n### 中游\n\n### 下游\n\n## 竞争格局\n| 公司 | 市场份额 | 优势 | 劣势 |\n|------|----------|------|------|\n| | | | |\n\n## 发展趋势\n1. \n2. \n3. \n\n## 投资建议\n### 重点关注\n- \n- \n\n### 风险提示\n- \n- \n\n` },
        { name: '市场周报', icon: '📰', desc: '每周市场总结与展望', tags: ['周报', '总结'], content: `# 市场周报\n\n## 日期: 第 周\n\n## 一周回顾\n### 主要指数表现\n| 指数 | 周涨跌 | 成交额 |\n|------|--------|--------|\n| 上证指数 | | |\n| 深证成指 | | |\n| 创业板指 | | |\n\n## 板块表现\n### 领涨板块\n1. \n2. \n\n### 领跌板块\n1. \n2. \n\n## 资金面\n- 北向资金:\n- 南向资金:\n- 融资余额:\n\n## 下周展望\n\n## 操作建议\n\n` },
        { name: '风险提示', icon: '⚠️', desc: '风险识别与应对方案', tags: ['风控', '风险'], content: `# 风险提示报告\n\n## 识别日期: \n\n## 风险等级: □低 □中 □高 □极高\n\n## 风险描述\n### 风险1: \n- 来源:\n- 影响:\n- 概率:\n\n### 风险2: \n- 来源:\n- 影响:\n- 概率:\n\n## 应对措施\n### 风险1应对\n- \n\n### 风险2应对\n- \n\n## 监控指标\n| 指标 | 当前值 | 预警值 | 状态 |\n|------|--------|--------|------|\n| | | | |\n\n` },
      ]
    }
  },
  mounted() { this.loadStocks() },
  methods: {
    async loadStocks() {
      try {
        const { data } = await request.get('/stocks?limit=100')
        if (data.code === 200) this.stockList = data.data.stocks || []
      } catch (e) { /* ignore */ }
    },
    useTemplate(tpl) {
      this.selectedTemplate = tpl
      this.form = { code: '', content: tpl.content }
      this.dialogVisible = true
    },
    async createNote() {
      try {
        const { data } = await request.post('/notes', {
          title: `${this.selectedTemplate.name}: ${this.form.code || ''}`,
          content: this.form.content,
          tags: this.selectedTemplate.tags,
          status: 'draft'
        })
        if (data.code === 200) {
          this.$message.success('笔记已创建')
          this.dialogVisible = false
          this.$router.push('/ai-center/note')
        }
      } catch (e) { this.$message.error('创建失败') }
    }
  }
}
</script>

<style scoped>
.note-templates { padding: 20px; }
</style>
