<template>
  <div class="app-container">
    <el-row :gutter="20">
      <el-col :span="8" v-for="tool in tools" :key="tool.name">
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <div style="font-size: 24px;margin-bottom: 8px;">{{ tool.icon }}</div>
          <div style="font-size: 16px;font-weight: 600;margin-bottom: 4px;">{{ tool.name }}</div>
          <div style="color: #909399;font-size: 13px;">{{ tool.desc }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
export default {
  name: 'Research',
  data() {
    return {
      tools: [
        { name: '因子研究', icon: '🧮', desc: '因子挖掘与测试' },
        { name: 'ML 流水线', icon: '🤖', desc: '机器学习模型训练' },
        { name: '市场状态', icon: '📊', desc: '市场状态检测' },
        { name: '行业热力图', icon: '🔥', desc: '行业表现热力图' },
        { name: '特征工程', icon: '🔧', desc: '特征提取与选择' },
        { name: 'LSTM 模型', icon: '🧠', desc: '深度学习预测' }
      ]
    }
  }
}
</script>
