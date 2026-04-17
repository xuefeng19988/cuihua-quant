<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header">
        <span>⭐ 自选股</span>
        <el-button size="mini" style="float:right;" type="primary" @click="showAdd = true">➕ 添加</el-button>
      </div>
      <el-dialog title="添加自选股" :visible.sync="showAdd" width="400px">
        <el-form :model="addForm" label-width="60px">
          <el-form-item label="股票"><el-select v-model="addForm.code" filterable placeholder="选择" style="width:100%;">
            <el-option v-for="s in allStocks" :key="s.value" :label="s.label" :value="s.value" />
          </el-select></el-form-item>
        </el-form>
        <span slot="footer"><el-button @click="showAdd = false">取消</el-button><el-button type="primary" @click="addStock">确定</el-button></span>
      </el-dialog>
      <el-table :data="watchlist" style="width: 100%">
        <el-table-column prop="code" label="代码" width="110"><template slot-scope="{ row }"><el-tag size="small">{{ row.code }}</el-tag></template></el-table-column>
        <el-table-column prop="name" label="名称" width="80" />
        <el-table-column prop="price" label="最新价" width="80" />
        <el-table-column prop="change" label="涨跌幅" width="80">
          <template slot-scope="{ row }"><span :style="{ color: row.change > 0 ? '#67C23A' : row.change < 0 ? '#F56C6C' : '#909399' }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}%</span></template>
        </el-table-column>
        <el-table-column label="操作" width="80"><template slot-scope="{ row }"><el-button size="mini" type="danger" @click="removeStock(row.code)">删除</el-button></template></el-table-column>
      </el-table>
      <el-empty v-if="watchlist.length === 0" description="暂无自选股，点击上方添加" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Watchlist',
  data() {
    return { watchlist: [], allStocks: [], showAdd: false, addForm: { code: '' } }
  },
  created() { this.fetchWatchlist(); this.fetchStocks() },
  methods: {
    fetchWatchlist() {
      fetch('/api/watchlist').then(r => r.json()).then(d => {
        if (d.code === 200) this.watchlist = d.data.stocks || []
      })
    },
    fetchStocks() {
      fetch('/api/stocks?page=1').then(r => r.json()).then(d => {
        if (d.code === 200) this.allStocks = (d.data.list || []).map(s => ({ value: s.code, label: s.code + ' ' + s.name }))
      })
    },
    addStock() {
      if (!this.addForm.code) return
      fetch('/api/watchlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: this.addForm.code })
      }).then(() => {
        this.showAdd = false
        this.addForm = { code: '' }
        this.fetchWatchlist()
      })
    },
    removeStock(code) {
      fetch('/api/watchlist', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code })
      }).then(() => this.fetchWatchlist())
    }
  }
}
</script>
