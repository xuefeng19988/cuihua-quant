<template>
  <div class="data-wizard">
    <el-steps :active="currentStep" finish-status="success" style="margin-bottom:20px;">
      <el-step title="选择文件" icon="el-icon-upload2"></el-step>
      <el-step title="数据预览" icon="el-icon-view"></el-step>
      <el-step title="字段映射" icon="el-icon-setting"></el-step>
      <el-step title="导入完成" icon="el-icon-check"></el-step>
    </el-steps>

    <!-- 步骤1: 选择文件 -->
    <div v-show="currentStep === 0" class="step-content">
      <el-upload
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".csv,.xlsx,.xls"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip" slot="tip">支持 CSV/Excel 文件，不超过 10MB</div>
      </el-upload>

      <div style="margin-top:20px;">
        <h4>📋 快速模板</h4>
        <el-button size="mini" @click="downloadTemplate('stocks')">📈 股票列表模板</el-button>
        <el-button size="mini" @click="downloadTemplate('notes')">📝 笔记模板</el-button>
        <el-button size="mini" @click="downloadTemplate('trades')">💼 交易记录模板</el-button>
      </div>
    </div>

    <!-- 步骤2: 数据预览 -->
    <div v-show="currentStep === 1" class="step-content">
      <h4>👀 数据预览 (前10行)</h4>
      <el-table :data="previewData" stripe style="width:100%;max-height:400px;overflow:auto;">
        <el-table-column v-for="col in columns" :key="col" :prop="col" :label="col" />
      </el-table>
      <p style="color:#909399;margin-top:12px;">共 {{ totalRows }} 行数据</p>
    </div>

    <!-- 步骤3: 字段映射 -->
    <div v-show="currentStep === 2" class="step-content">
      <h4>🔗 字段映射</h4>
      <el-form label-width="120px">
        <el-form-item v-for="(target, index) in targetFields" :key="index" :label="target.label">
          <el-select v-model="fieldMapping[target.key]" placeholder="选择对应字段" style="width:100%;">
            <el-option v-for="col in columns" :key="col" :label="col" :value="col" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 步骤4: 导入完成 -->
    <div v-show="currentStep === 3" class="step-content">
      <el-result icon="success" title="导入成功" :sub-title="`成功导入 ${importedRows} 行数据`">
        <template slot="extra">
          <el-button type="primary" @click="$emit('complete')">完成</el-button>
          <el-button @click="resetWizard">继续导入</el-button>
        </template>
      </el-result>
    </div>

    <!-- 操作按钮 -->
    <div class="wizard-actions" v-if="currentStep < 3">
      <el-button @click="prevStep" :disabled="currentStep === 0">上一步</el-button>
      <el-button type="primary" @click="nextStep" :disabled="!canNext">
        {{ currentStep === 2 ? '开始导入' : '下一步' }}
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataWizard',
  props: {
    targetFields: {
      type: Array,
      default: () => []
    },
    importType: {
      type: String,
      default: 'stocks'
    }
  },
  data() {
    return {
      currentStep: 0,
      file: null,
      rawData: [],
      previewData: [],
      columns: [],
      totalRows: 0,
      fieldMapping: {},
      importedRows: 0
    }
  },
  computed: {
    canNext() {
      if (this.currentStep === 0) return this.file !== null
      if (this.currentStep === 1) return true
      if (this.currentStep === 2) return Object.keys(this.fieldMapping).length > 0
      return false
    }
  },
  methods: {
    handleFileChange(file) {
      this.file = file.raw
      this.parseFile(file.raw)
    },
    async parseFile(file) {
      const Papa = await import('papaparse')
      Papa.default.parse(file, {
        header: true,
        complete: (results) => {
          this.rawData = results.data
          this.columns = results.meta.fields || []
          this.totalRows = results.data.length
          this.previewData = results.data.slice(0, 10)
          this.currentStep = 1
        },
        error: (error) => {
          this.$message.error('文件解析失败: ' + error.message)
        }
      })
    },
    nextStep() {
      if (this.currentStep === 2) {
        this.startImport()
      } else {
        this.currentStep++
      }
    },
    prevStep() {
      if (this.currentStep > 0) this.currentStep--
    },
    async startImport() {
      this.$emit('import', {
        data: this.rawData,
        mapping: this.fieldMapping,
        type: this.importType
      })
    },
    downloadTemplate(type) {
      const templates = {
        stocks: 'code,name,industry\nSH.600519,贵州茅台,白酒',
        notes: 'title,content,tags\n标题,内容,标签1,标签2',
        trades: 'code,action,price,qty,date\nSH.600519,买入,1700.00,100,2026-04-18'
      }
      const blob = new Blob([templates[type]], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `template_${type}.csv`
      link.click()
    },
    resetWizard() {
      this.currentStep = 0
      this.file = null
      this.rawData = []
      this.previewData = []
      this.columns = []
      this.fieldMapping = {}
    }
  }
}
</script>

<style scoped>
.data-wizard {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.step-content {
  min-height: 300px;
  padding: 20px 0;
}

.upload-area {
  text-align: center;
}

.wizard-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e6e6e6;
}
</style>
