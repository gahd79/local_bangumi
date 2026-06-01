<template>
  <div class="records-page">
    <div class="page-header">
      <h2>我的记录</h2>
      <div class="header-actions">
        <el-button @click="openImport">
          <el-icon><Upload /></el-icon>
          导入
        </el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加记录
        </el-button>
      </div>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="16" class="stats-row" v-if="stats">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总记录" :value="stats.total_records" />
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" v-for="(count, label) in stats.status_distribution" :key="label">
        <el-card shadow="hover" class="stat-card" v-if="count > 0">
          <el-statistic :title="label" :value="count" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Tab 筛选 -->
    <el-tabs v-model="activeStatus" @tab-change="onStatusChange" class="status-tabs">
      <el-tab-pane label="全部" name="" />
      <el-tab-pane label="想看" name="1" />
      <el-tab-pane label="在看" name="2" />
      <el-tab-pane label="看过" name="3" />
      <el-tab-pane label="搁置" name="4" />
      <el-tab-pane label="抛弃" name="5" />
    </el-tabs>

    <!-- 记录列表 -->
    <el-table
      :data="records"
      v-loading="loading"
      stripe
      style="width: 100%"
      empty-text="暂无记录"
      @row-click="onRowClick"
    >
      <el-table-column label="条目" min-width="200">
        <template #default="{ row }">
          <router-link :to="`/subjects/${row.subject_id}`" class="subject-link">
            {{ row.subject_name_cn || row.subject_name || `#${row.subject_id}` }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <StatusBadge type="record_status" :value="row.status" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="进度" width="100">
        <template #default="{ row }">
          <span>{{ row.progress }}</span>
        </template>
      </el-table-column>
      <el-table-column label="评分" width="130">
        <template #default="{ row }">
          <ScoreDisplay :score="row.rating" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="评论" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="comment-preview">{{ row.comment || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" width="140">
        <template #default="{ row }">
          <span class="time-text">{{ formatDate(row.updated_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click.stop="openEdit(row)">
            编辑
          </el-button>
          <el-popconfirm title="确定删除此记录？" @confirm="doDelete(row.id)">
            <template #reference>
              <el-button text type="danger" size="small" @click.stop>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editVisible"
      :title="editingRecord?.id ? '编辑记录' : '添加记录'"
      width="480px"
      @close="resetEdit"
    >
      <el-form :model="editForm" label-position="top">
        <el-form-item label="条目 ID（Bangumi ID）" v-if="!editingRecord?.id">
          <el-input v-model.number="editForm.subject_id" placeholder="输入条目 Bangumi ID" type="number" />
        </el-form-item>
        <el-form-item label="观看状态">
          <el-select v-model.number="editForm.status" style="width: 100%">
            <el-option :value="1" label="想看" />
            <el-option :value="2" label="在看" />
            <el-option :value="3" label="看过" />
            <el-option :value="4" label="搁置" />
            <el-option :value="5" label="抛弃" />
          </el-select>
        </el-form-item>
        <el-form-item label="进度">
          <el-input-number v-model="editForm.progress" :min="0" :max="editMaxProgress" style="width: 100%" />
          <span class="progress-hint" v-if="editMaxProgress < 9999">
            共 {{ editMaxProgress }} 集/章
          </span>
        </el-form-item>
        <el-form-item label="评分">
          <RatingInput v-model="editForm.rating" />
        </el-form-item>
        <el-form-item label="评论">
          <el-input
            v-model="editForm.comment"
            type="textarea"
            :rows="3"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="doSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 导入弹窗 -->
    <el-dialog
      v-model="importVisible"
      title="导入 Bangumi 记录"
      width="500px"
    >
      <el-alert
        title="支持 Bangumi 导出的 collections JSON 文件"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :on-change="onFileChange"
        accept=".json"
        :limit="1"
        :file-list="importFileList"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            请选择 bgm_collections.json 文件
          </div>
        </template>
      </el-upload>
      <div v-if="importResult" class="import-result">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="总数">{{ importResult.total }}</el-descriptions-item>
          <el-descriptions-item label="新增">{{ importResult.created }}</el-descriptions-item>
          <el-descriptions-item label="更新">{{ importResult.updated }}</el-descriptions-item>
          <el-descriptions-item label="跳过">{{ importResult.skipped }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="importVisible = false">关闭</el-button>
        <el-button type="primary" @click="doImport" :loading="importing" :disabled="!importFileData">
          开始导入
        </el-button>
      </template>
    </el-dialog>
    <el-dialog
      v-model="showAddDialog"
      title="添加观看记录"
      width="480px"
      @close="resetEdit"
    >
      <el-form :model="editForm" label-position="top">
        <el-form-item label="条目 Bangumi ID">
          <el-input
            v-model.number="editForm.subject_id"
            placeholder="输入要收藏的条目 ID（可在条目详情页找到）"
            type="number"
          />
        </el-form-item>
        <el-form-item label="观看状态">
          <el-select v-model.number="editForm.status" style="width: 100%">
            <el-option :value="1" label="想看" />
            <el-option :value="2" label="在看" />
            <el-option :value="3" label="看过" />
            <el-option :value="4" label="搁置" />
            <el-option :value="5" label="抛弃" />
          </el-select>
        </el-form-item>
        <el-form-item label="进度">
          <el-input-number v-model="editForm.progress" :min="0" :max="editMaxProgress" style="width: 100%" />
          <span class="progress-hint" v-if="editMaxProgress < 9999">
            共 {{ editMaxProgress }} 集/章
          </span>
        </el-form-item>
        <el-form-item label="评分">
          <RatingInput v-model="editForm.rating" />
        </el-form-item>
        <el-form-item label="评论">
          <el-input
            v-model="editForm.comment"
            type="textarea"
            :rows="3"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="doSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getRecords,
  createRecord,
  updateRecord,
  deleteRecord,
  importRecords,
} from '@/api/records'
import { ElMessage } from 'element-plus'
import apiClient from '@/api/request'
import StatusBadge from '@/components/StatusBadge.vue'
import ScoreDisplay from '@/components/ScoreDisplay.vue'
import RatingInput from '@/components/RatingInput.vue'

const records = ref([])
const loading = ref(false)
const saving = ref(false)
const stats = ref(null)
const activeStatus = ref('')
const editVisible = ref(false)
const showAddDialog = ref(false)
const editingRecord = ref(null)

// 导入相关
const importVisible = ref(false)
const importFileList = ref([])
const importFileData = ref(null)
const importing = ref(false)
const importResult = ref(null)

const editForm = reactive({
  subject_id: null,
  status: 1,
  progress: 0,
  rating: null,
  comment: '',
})

// 当前编辑记录的剧集总数（用于限制进度最大值）
const editMaxProgress = computed(() => {
  const cnt = editingRecord.value?.episode_count
  return cnt && cnt > 0 ? cnt : 9999
})

onMounted(() => {
  fetchRecords()
  fetchStats()
})

async function fetchRecords() {
  loading.value = true
  try {
    const params = {}
    if (activeStatus.value) params.status = Number(activeStatus.value)
    const data = await getRecords(params)
    records.value = Array.isArray(data) ? data : []
  } catch {
    records.value = []
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const statsData = await apiClient.get('/records/stats')
    stats.value = statsData
  } catch {
    stats.value = null
  }
}

function onStatusChange() {
  fetchRecords()
}

function openEdit(record) {
  editingRecord.value = record
  editForm.subject_id = record.subject_id
  editForm.status = record.status
  editForm.progress = record.progress
  editForm.rating = record.rating
  editForm.comment = record.comment || ''
  editVisible.value = true
}

function resetEdit() {
  editingRecord.value = null
  editForm.subject_id = null
  editForm.status = 1
  editForm.progress = 0
  editForm.rating = null
  editForm.comment = ''
}

async function doSave() {
  if (!editForm.subject_id && !editingRecord.value?.id) {
    ElMessage.warning('请输入条目 ID')
    return
  }
  saving.value = true
  try {
    if (editingRecord.value?.id) {
      await updateRecord(editingRecord.value.id, { ...editForm })
      ElMessage.success('记录已更新')
    } else {
      await createRecord({ ...editForm })
      ElMessage.success('记录已添加')
    }
    editVisible.value = false
    showAddDialog.value = false
    resetEdit()
    await fetchRecords()
    await fetchStats()
  } catch {
    // 错误提示由 API 拦截器统一处理
  } finally {
    saving.value = false
  }
}

async function doDelete(id) {
  try {
    await deleteRecord(id)
    ElMessage.success('记录已删除')
    await fetchRecords()
    await fetchStats()
  } catch {
    // 错误提示由 API 拦截器统一处理
  }
}

function onRowClick(row) {
  // 点击行不做跳转，使用操作列的按钮
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// ─── 导入功能 ───
function openImport() {
  importFileList.value = []
  importFileData.value = null
  importResult.value = null
  importVisible.value = true
}

function onFileChange(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)
      importFileData.value = Array.isArray(data) ? data : null
      if (!importFileData.value) {
        ElMessage.warning('文件内容不是有效的 JSON 数组')
      }
    } catch {
      ElMessage.error('文件解析失败，请检查 JSON 格式')
      importFileData.value = null
    }
  }
  reader.readAsText(file.raw)
}

async function doImport() {
  if (!importFileData.value || !importFileData.value.length) {
    ElMessage.warning('请先选择有效的 JSON 文件')
    return
  }
  importing.value = true
  try {
    const res = await importRecords(importFileData.value)
    importResult.value = res
    ElMessage.success(`导入完成：新增 ${res.created} 条，更新 ${res.updated} 条，跳过 ${res.skipped} 条`)
    await fetchRecords()
    await fetchStats()
  } catch {
    // 错误由拦截器处理
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.records-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 1.3rem;
}
.header-actions {
  display: flex;
  gap: 8px;
}

.stats-row {
  margin-bottom: 16px;
}
.stat-card {
  margin-bottom: 12px;
  border-radius: 12px;
}

.status-tabs {
  margin-bottom: 8px;
}

.subject-link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.15s;
}
.subject-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.comment-preview {
  color: #909399;
  font-size: 0.85rem;
}
.time-text {
  color: #909399;
  font-size: 0.85rem;
}

/* 圆角 */
:deep(.el-table) {
  border-radius: 10px;
  overflow: hidden;
}
:deep(.el-tabs__nav-wrap) {
  border-radius: 8px;
}

.progress-hint {
  display: block;
  font-size: 0.75rem;
  color: #909399;
  margin-top: 4px;
}
.import-result {
  margin-top: 16px;
}
</style>
