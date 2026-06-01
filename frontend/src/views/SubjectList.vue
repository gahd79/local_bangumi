<template>
  <div class="subject-list-page">
    <!-- 筛选面板 — 默认展开 -->
    <SubjectFilters
      v-model="filters"
      @apply="onFilterApply"
      @reset="onFilterReset"
    />

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <span class="result-count">共 {{ total }} 条结果</span>
      </div>
      <div class="toolbar-right">
        <el-radio-group v-model="sortKey" size="small" @change="onSortChange">
          <el-radio-button value="score">评分</el-radio-button>
          <el-radio-button value="popularity">热度</el-radio-button>
          <el-radio-button value="date">日期</el-radio-button>
          <el-radio-button value="rank">排名</el-radio-button>
          <el-radio-button value="name_cn">名称</el-radio-button>
          <el-radio-button value="updated_at">更新</el-radio-button>
        </el-radio-group>
        <el-switch
          v-model="sortOrder"
          inline-prompt
          active-text="↓"
          inactive-text="↑"
          :active-value="'desc'"
          :inactive-value="'asc'"
          @change="onSortChange"
          style="margin-left: 8px"
        />
        <el-divider direction="vertical" />
        <el-button-group size="small">
          <el-button
            :type="viewMode === 'grid' ? 'primary' : ''"
            @click="viewMode = 'grid'"
          >
            <el-icon><Grid /></el-icon>
          </el-button>
          <el-button
            :type="viewMode === 'list' ? 'primary' : ''"
            @click="viewMode = 'list'"
          >
            <el-icon><List /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 加载 -->
    <el-skeleton v-if="loading" :rows="8" animated />

    <!-- 内容区 -->
    <template v-if="!loading">
      <el-empty v-if="!items.length" description="没有找到匹配的条目" :image-size="80" />

      <!-- Grid 模式 -->
      <el-row v-if="viewMode === 'grid'" :gutter="12">
        <el-col
          v-for="s in items"
          :key="s.bangumi_id"
          :xs="12"
          :sm="8"
          :md="6"
          :lg="4"
          style="margin-bottom: 12px"
        >
          <SubjectCard :subject="s" view-mode="grid" @quick-record="onQuickRecord(s)" @add-record="onAddRecord(s)" />
        </el-col>
      </el-row>

      <!-- List 模式 -->
      <template v-if="viewMode === 'list'">
        <SubjectCard
          v-for="s in items"
          :key="s.bangumi_id"
          :subject="s"
          view-mode="list"
          @quick-record="onQuickRecord(s)"
          @add-record="onAddRecord(s)"
        />
      </template>
    </template>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > limit">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="limit"
        :total="total"
        layout="prev, pager, next, jumper"
        @current-change="onPageChange"
      />
    </div>

    <!-- 快速收藏 / 添加记录弹窗 -->
    <el-dialog v-model="quickRecordVisible" :title="quickDialogTitle" width="440px">
      <el-form :model="quickForm" label-position="top">
        <el-form-item label="条目">
          <span class="quick-subject-name">{{ quickSubject?.name_cn || quickSubject?.name }}</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model.number="quickForm.status" style="width: 100%">
            <el-option :value="1" label="想看" />
            <el-option :value="2" label="在看" />
            <el-option :value="3" label="看过" />
            <el-option :value="4" label="搁置" />
            <el-option :value="5" label="抛弃" />
          </el-select>
        </el-form-item>
        <el-form-item label="进度">
          <el-input-number v-model="quickForm.progress" :min="0" :max="9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="评分">
          <RatingInput v-model="quickForm.rating" />
        </el-form-item>
        <el-form-item label="评论">
          <el-input
            v-model="quickForm.comment"
            type="textarea"
            :rows="2"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="quickRecordVisible = false">取消</el-button>
        <el-button type="primary" @click="doQuickRecord" :loading="quickSaving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
defineOptions({ name: 'SubjectList' })

import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSubjects } from '@/api/subjects'
import { createRecord } from '@/api/records'
import { ElMessage } from 'element-plus'
import SubjectCard from '@/components/SubjectCard.vue'
import SubjectFilters from '@/components/SubjectFilters.vue'
import RatingInput from '@/components/RatingInput.vue'

const route = useRoute()
const router = useRouter()

const items = ref([])
const total = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const limit = 25
const viewMode = ref('grid')
const sortKey = ref('score')
const sortOrder = ref('desc')

const filters = reactive({
  type: undefined,
  search: '',
  year: undefined,
  season: undefined,
  score_from: undefined,
  score_to: undefined,
  popularity_from: undefined,
  nsfw: undefined,
  series: undefined,
})

// 快速收藏
const quickRecordVisible = ref(false)
const quickSubject = ref(null)
const quickSaving = ref(false)
const quickIsFullEdit = ref(false)  // 是否为完整编辑模式
const quickForm = reactive({ status: 1, progress: 0, rating: null, comment: '' })

const quickDialogTitle = computed(() => {
  return quickIsFullEdit.value ? '添加记录' : '快速收藏'
})

// 从 URL 恢复状态
function loadFromURL() {
  const q = route.query
  if (q.type) filters.type = Number(q.type)
  if (q.search) filters.search = q.search
  if (q.year) filters.year = Number(q.year)
  if (q.season) filters.season = Number(q.season)
  if (q.score_from) filters.score_from = Number(q.score_from)
  if (q.score_to) filters.score_to = Number(q.score_to)
  if (q.popularity_from) filters.popularity_from = Number(q.popularity_from)
  if (q.nsfw) filters.nsfw = q.nsfw === 'true'
  if (q.series) filters.series = q.series === 'true'
  if (q.sort) sortKey.value = q.sort
  if (q.order) sortOrder.value = q.order
  if (q.page) currentPage.value = Number(q.page)
  if (q.view) viewMode.value = q.view
}

// 将状态持久化到 URL
function saveToURL() {
  const q = { ...route.query }
  // 筛选参数
  const allFilters = {
    type: filters.type,
    search: filters.search || undefined,
    year: filters.year,
    season: filters.season,
    score_from: filters.score_from,
    score_to: filters.score_to,
    popularity_from: filters.popularity_from,
    nsfw: filters.nsfw,
    series: filters.series,
    sort: sortKey.value !== 'score' ? sortKey.value : undefined,
    order: sortOrder.value !== 'desc' ? sortOrder.value : undefined,
    page: currentPage.value > 1 ? currentPage.value : undefined,
    view: viewMode.value !== 'grid' ? viewMode.value : undefined,
  }
  // 清理
  Object.keys(allFilters).forEach((k) => {
    if (allFilters[k] !== undefined && allFilters[k] !== '' && allFilters[k] !== null) {
      q[k] = String(allFilters[k])
    } else {
      delete q[k]
    }
  })
  router.replace({ query: q })
}

onMounted(() => {
  loadFromURL()
  fetchData()
})

// 当路由 query 变化时（如浏览器前进/后退）
watch(() => route.query, () => {
  loadFromURL()
  fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit,
      sort: sortKey.value,
      order: sortOrder.value,
    }
    // 筛选参数
    const filterKeys = ['type', 'search', 'year', 'season', 'score_from', 'score_to', 'popularity_from', 'nsfw', 'series']
    filterKeys.forEach((k) => {
      if (filters[k] !== undefined && filters[k] !== '' && filters[k] !== null) params[k] = filters[k]
    })
    const data = await getSubjects(params)
    items.value = data.items
    total.value = data.total
  } catch (e) {
    console.error('Failed to load subjects:', e)
  } finally {
    loading.value = false
  }
}

function onFilterApply(newFilters) {
  Object.assign(filters, newFilters)
  currentPage.value = 1
  saveToURL()
  fetchData()
}

function onFilterReset() {
  Object.keys(filters).forEach((k) => (filters[k] = undefined))
  filters.search = ''
  currentPage.value = 1
  sortKey.value = 'score'
  sortOrder.value = 'desc'
  router.replace({ query: {} })
  fetchData()
}

function onSortChange() {
  currentPage.value = 1
  saveToURL()
  fetchData()
}

function onPageChange(page) {
  currentPage.value = page
  saveToURL()
  fetchData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function onQuickRecord(subject) {
  quickSubject.value = subject
  quickIsFullEdit.value = false
  quickForm.status = 1
  quickForm.progress = 0
  quickForm.rating = null
  quickForm.comment = ''
  quickRecordVisible.value = true
}

function onAddRecord(subject) {
  quickSubject.value = subject
  quickIsFullEdit.value = true
  quickForm.status = 2  // 默认"在看"
  quickForm.progress = 0
  quickForm.rating = null
  quickForm.comment = ''
  quickRecordVisible.value = true
}

async function doQuickRecord() {
  if (!quickSubject.value) return
  quickSaving.value = true
  try {
    await createRecord({
      subject_id: quickSubject.value.bangumi_id,
      status: quickForm.status,
      progress: quickForm.progress,
      rating: quickForm.rating,
      comment: quickForm.comment || undefined,
    })
    ElMessage.success(`已收藏「${quickSubject.value.name_cn || quickSubject.value.name}」`)
    quickRecordVisible.value = false
  } catch {
    // 错误由拦截器处理
  } finally {
    quickSaving.value = false
  }
}
</script>

<style scoped>
.subject-list-page {
  max-width: 1600px;
  margin: 0 auto;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}
.toolbar-right {
  display: flex;
  align-items: center;
}
.result-count {
  font-size: 0.9rem;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.quick-subject-name {
  font-weight: 600;
  font-size: 1.05rem;
}
</style>
