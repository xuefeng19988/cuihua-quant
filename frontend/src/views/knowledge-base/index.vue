<template>
  <div class="app-container">
    <el-card style="margin-bottom:20px;">
      <div slot="header">
        <span>📚 知识库管理</span>
        <el-button size="mini" type="primary" style="float:right;" @click="createKnowledgeBase">➕ 新建知识库</el-button>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧：知识库树 -->
      <el-col :span="8">
        <el-card>
          <div slot="header"><span>📂 知识库列表</span></div>
          <el-tree :data="knowledgeBases" :props="treeProps" node-key="id" default-expand-all @node-click="handleNodeClick">
            <span class="custom-tree-node" slot-scope="{ node, data }">
              <span><i :class="data.icon"></i> {{ node.label }}</span>
              <span>
                <el-button size="mini" type="text" icon="el-icon-edit" @click.stop="editNode(data)"></el-button>
                <el-button size="mini" type="text" icon="el-icon-plus" @click.stop="addChild(data)"></el-button>
              </span>
            </span>
          </el-tree>
        </el-card>
      </el-col>

      <!-- 右侧：笔记列表 -->
      <el-col :span="16">
        <el-card>
          <div slot="header">
            <span>📝 {{ currentKB ? currentKB.name : '全部笔记' }}</span>
            <el-button size="mini" type="primary" style="float:right;" @click="createNote">➕ 新建笔记</el-button>
          </div>
          
          <el-table :data="kbNotes" style="width:100%" stripe>
            <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column label="标签" width="150"><template slot-scope="{ row }"><el-tag v-for="t in row.tags" :key="t" size="mini" style="margin:2px;">{{ t }}</el-tag></template></el-table-column>
            <el-table-column label="状态" width="80"><template slot-scope="{ row }"><el-tag :type="row.status === 'published' ? 'success' : 'info'" size="mini">{{ row.status === 'published' ? '已发布' : '草稿' }}</el-tag></template></el-table-column>
            <el-table-column prop="updated_at" label="更新时间" width="160" />
            <el-table-column label="操作" width="100">
              <template slot-scope="{ row }">
                <el-button size="mini" @click="editNote(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'KnowledgeBase',
  data() {
    return {
      knowledgeBases: [
        {
          id: 1,
          label: '量化研究',
          icon: 'el-icon-data-analysis',
          children: [
            { id: 11, label: '策略开发', icon: 'el-icon-cpu', children: [] },
            { id: 12, label: '因子研究', icon: 'el-icon-s-grid', children: [] }
          ]
        },
        {
          id: 2,
          label: '市场分析',
          icon: 'el-icon-trend-charts',
          children: [
            { id: 21, label: 'A股分析', icon: 'el-icon-document', children: [] },
            { id: 22, label: '港股分析', icon: 'el-icon-document', children: [] }
          ]
        },
        {
          id: 3,
          label: '学习笔记',
          icon: 'el-icon-reading',
          children: []
        }
      ],
      treeProps: { children: 'children', label: 'label' },
      currentKB: null,
      kbNotes: []
    }
  },
  created() { this.loadNotes() },
  methods: {
    loadNotes() {
      // 模拟数据
      this.kbNotes = [
        { id: 1, title: 'MACD策略优化笔记', category: '策略开发', tags: ['量化', '策略'], status: 'published', updated_at: '2026-04-18' },
        { id: 2, title: 'A股市场分析2026Q1', category: 'A股分析', tags: ['A股', '分析'], status: 'published', updated_at: '2026-04-17' },
        { id: 3, title: 'Python量化学习笔记', category: '学习笔记', tags: ['Python', '学习'], status: 'draft', updated_at: '2026-04-16' }
      ]
    },
    handleNodeClick(data) {
      this.currentKB = data
      this.$message.info(`选择了：${data.label}`)
    },
    createKnowledgeBase() { this.$message.info('新建知识库') },
    createNote() { this.$router.push('/note-editor') },
    editNote(note) { this.$router.push(`/note-editor/${note.id}`) },
    editNode(data) { this.$message.info(`编辑：${data.label}`) },
    addChild(data) { this.$message.info(`添加子节点到：${data.label}`) }
  }
}
</script>

<style scoped>
.app-container { background: #0f0f1a; min-height: 100vh; padding: 16px; }
.el-card { background: #1a1a2e !important; border: 1px solid #2a2a3e !important; }
.el-card__header { border-bottom: 1px solid #2a2a3e !important; }
.custom-tree-node { flex: 1; display: flex; align-items: center; justify-content: space-between; font-size: 14px; padding-right: 8px; }
</style>
