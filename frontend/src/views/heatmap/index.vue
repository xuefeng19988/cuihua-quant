<template>
  <div class="app-container">
    <el-card style="margin-bottom: 20px;">
      <div slot="header"><span>🔥 板块热力图</span></div>
      <el-row :gutter="20">
        <el-col :span="12" v-for="sector in sectors" :key="sector.name">
          <div style="display:flex;align-items:center;margin-bottom:12px;">
            <span style="width:80px;font-size:14px;">{{ sector.name }}</span>
            <div style="flex:1;height:24px;background:#f5f7fa;border-radius:4px;overflow:hidden;">
              <div :style="{width:Math.min(Math.abs(sector.change)/0.2*100,100)+'%',height:'100%',background:sector.change>=0?'rgba(103,194,58,0.7)':'rgba(245,108,108,0.7)',borderRadius:'4px'}"></div>
            </div>
            <span :style="{color:sector.change>=0?'#67C23A':'#F56C6C',fontWeight:600,width:70,textAlign:'right'}">{{ sector.change>=0?'+':'' }}{{ (sector.change*100).toFixed(2) }}%</span>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>
<script>
export default {
  name: 'Heatmap',
  data() {
    return {
      sectors: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      var self = this
      fetch('/api/heatmap').then(function(r) { return r.json() }).then(function(d) {
        if (d.code === 200 && d.data && d.data.sectors) {
          self.sectors = d.data.sectors
        } else {
          self.sectors = [
            { name: '新能源', change: 0.164 },
            { name: '新能源车', change: 0.066 },
            { name: '金融', change: 0.024 },
            { name: '家电', change: 0.018 },
            { name: '公用事业', change: 0.006 },
            { name: '白酒', change: 0.005 }
          ]
        }
      }).catch(function() {
        self.sectors = [
          { name: '新能源', change: 0.164 },
          { name: '新能源车', change: 0.066 },
          { name: '金融', change: 0.024 },
          { name: '家电', change: 0.018 },
          { name: '公用事业', change: 0.006 },
          { name: '白酒', change: 0.005 }
        ]
      })
    }
  }
}
</script>
