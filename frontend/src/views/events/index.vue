<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>📅 事件研究配置</span></div>
      <el-form :inline="true">
        <el-form-item label="事件类型"><el-select v-model="form.type" style="width: 150px;">
          <el-option label="财报发布" value="earnings" /><el-option label="分红派息" value="dividend" />
          <el-option label="重大公告" value="announcement" /><el-option label="政策发布" value="policy" />
        </el-select></el-form-item>
        <el-form-item label="事件窗口"><el-input v-model="form.window" style="width: 120px;" placeholder="-5, +5" /></el-form-item>
        <el-form-item><el-button type="primary" @click="$message.info('分析功能开发中')">🔍 分析</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card>
      <div slot="header"><span>📊 分析结果</span></div>
      <el-empty description="暂无事件分析数据" />
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Events',
  data() { return { form: { type: 'earnings', window: '-5, +5' } } }
}
</script>
