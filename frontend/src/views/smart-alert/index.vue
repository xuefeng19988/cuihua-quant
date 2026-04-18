<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>⚠️ 智能预警</span></div></el-card>
    <el-card><el-table :data="data.alerts" stripe><el-table-column prop="type" label="类型" /><el-table-column prop="condition" label="条件" /><el-table-column prop="status" label="状态"><template slot-scope="{ row }"><el-tag size="mini" :type="row.status==='active'?'success':'info'">{{ row.status }}</el-tag></template></el-table-column><el-table-column label="触发"><template slot-scope="{ row }"><el-tag size="mini" :type="row.triggered?'danger':'info'">{{ row.triggered?'已触发':'未触发' }}</el-tag></template></el-table-column></el-table></el-card>
    <el-card style="margin-top:20px;"><div slot="header"><span>🤖 ML异常检测</span></div>
      <p>状态: <el-tag type="success">已启用</el-tag> | 检测时间: {{ data.ml_anomaly.last_check }}</p>
      <p>发现异常: <strong>{{ data.ml_anomaly.anomalies_detected }}</strong> 个</p>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'SmartAlert', data() { return { data: { alerts: [], ml_anomaly: {} } } },
  created() { this.fetchData() },
  methods: {
    async fetchData() { try { const { data } = await request.get('/api/smart-alert'); if (data.code === 200) this.data = data.data } catch (e) {} }
  }
}
</script>
