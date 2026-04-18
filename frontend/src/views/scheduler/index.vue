<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>⏰ 定时任务调度</span></div></el-card>
    <el-card><el-table :data="data.tasks" stripe><el-table-column prop="name" label="任务名称" /><el-table-column prop="schedule" label="执行计划" /><el-table-column prop="status" label="状态"><template slot-scope="{ row }"><el-tag size="mini" :type="row.status==='active'?'success':'info'">{{ row.status }}</el-tag></template></el-table-column><el-table-column prop="last_run" label="上次执行" /></el-table></el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'Scheduler', data() { return { data: { tasks: [] } } },
  created() { this.fetchData() },
  methods: {
    async fetchData() { try { const { data } = await request.get('/api/scheduler'); if (data.code === 200) this.data = data.data } catch (e) {} }
  }
}
</script>
