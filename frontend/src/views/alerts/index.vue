<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>🔔 告警规则</span>
        <el-button size="mini" style="float:right;" type="primary" @click="showAdd = true">➕ 添加规则</el-button>
      </div>
      <el-table :data="rules" style="width: 100%">
        <el-table-column prop="name" label="规则名称" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column label="状态" width="80">
          <template slot-scope="{ row }"><el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '启用' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template slot-scope="{ row }">
            <el-switch v-model="row.enabled" @change="$message.success('状态已更新')" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card>
      <div slot="header"><span>📋 告警记录</span></div>
      <el-empty description="暂无告警记录" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Alerts',
  data() {
    return {
      showAdd: false,
      rules: [
        { name: '价格异动', type: '价格', threshold: '±3%', enabled: true },
        { name: '成交量异常', type: '成交量', threshold: '>2倍均值', enabled: true },
        { name: '系统异常', type: '系统', threshold: '服务宕机', enabled: true },
        { name: '数据延迟', type: '数据', threshold: '>30分钟', enabled: true },
        { name: '风险超标', type: '风险', threshold: 'VaR>阈值', enabled: false }
      ]
    }
  }
}
</script>
