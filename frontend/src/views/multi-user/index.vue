<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;"><div slot="header"><span>👥 多用户管理</span><el-button size="mini" type="primary" style="float:right;" @click="showAddUser">➕ 添加用户</el-button></div></el-card>
    <el-card><el-table :data="users" stripe><el-table-column prop="id" label="ID" width="60" /><el-table-column prop="username" label="用户名" /><el-table-column prop="role" label="角色"><template slot-scope="{ row }"><el-tag size="mini" :type="row.role==='admin'?'danger':row.role==='trader'?'success':'info'">{{ row.role }}</el-tag></template></el-table-column><el-table-column prop="status" label="状态" /><el-table-column prop="created_at" label="创建时间" /></el-table></el-card>
  </div>
</template>

<script>
import request from '@/utils/request'
export default {
  name: 'MultiUser', data() { return { users: [] } },
  created() { this.fetchUsers() },
  methods: {
    async fetchUsers() { try { const { data } = await request.get('/api/users'); if (data.code === 200) this.users = data.data.users || [] } catch (e) {} },
    showAddUser() { this.$message.info('添加用户功能') }
  }
}
</script>
