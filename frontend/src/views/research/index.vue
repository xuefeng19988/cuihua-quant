<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>📓 研究笔记本</span><el-button size="mini" style="float:right;" type="primary" @click="newNote">➕ 新建</el-button></div></el-card>
    <el-row :gutter="20">
      <el-col :span="8" v-for="note in notes" :key="note.title">
        <el-card shadow="hover" style="margin-bottom:16px;cursor:pointer;" @click="$message.info('打开: ' + note.title)">
          <div style="font-weight:600;margin-bottom:8px;">{{ note.title }}</div>
          <div style="color:#909399;font-size:12px;margin-bottom:8px;">{{ note.date }}</div>
          <el-tag v-for="t in note.tags" :key="t" size="mini" style="margin-right:4px;">{{ t }}</el-tag>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
export default { name: 'Research', data() { return {
  notes: [
    { title: '多因子选股模型优化', date: '2026-04-15', tags: ['因子', '多因子'] },
    { title: 'A股动量效应研究', date: '2026-04-10', tags: ['动量', '实证'] },
    { title: '机器学习在量化选股中的应用', date: '2026-04-05', tags: ['ML', '选股'] },
    { title: '市场微观结构分析', date: '2026-03-28', tags: ['微观结构'] },
    { title: '行业轮动策略回测', date: '2026-03-20', tags: ['轮动', '行业'] },
    { title: '波动率预测模型对比', date: '2026-03-15', tags: ['波动率', 'ML'] }
  ]
}}, methods: { newNote() { this.$message.info('创建新研究笔记') } } }
</script>
