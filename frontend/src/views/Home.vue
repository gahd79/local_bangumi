<template>
  <div class="home-page">
    <!-- Hero 区 -->
    <div class="hero">
      <h1 class="hero-title">local_bangumi</h1>
      <p class="hero-desc">本地 ACGN 数据库 — 基于 Bangumi Archive 数据的离线浏览与收藏管理</p>

      <!-- 快速搜索 -->
      <div class="quick-search">
        <el-input
          v-model="searchKeyword"
          size="large"
          placeholder="搜索条目 / 人物 / 角色..."
          clearable
          @keyup.enter="goSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" @click="goSearch" style="margin-left: 8px">
          搜索
        </el-button>
      </div>
    </div>

    <!-- 数据统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-statistic title="条目总数" :value="syncStatus?.table_counts?.subjects || 0" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-statistic title="人物总数" :value="syncStatus?.table_counts?.persons || 0" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-statistic title="角色总数" :value="syncStatus?.table_counts?.characters || 0" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-statistic title="数据更新时间">
          <template #suffix>
            <span class="stat-suffix">{{ lastSyncText }}</span>
          </template>
        </el-statistic>
      </el-col>
    </el-row>

    <!-- 在看在追 — 点格子 -->
    <el-card class="section-card" v-if="watchingItems.length > 0" v-loading="watchingLoading">
      <template #header>
        <span>在看在追（{{ watchingItems.length }} 部）</span>
        <el-button text type="primary" @click="$router.push('/records')" style="float: right">
          查看全部
        </el-button>
      </template>
      <div class="watching-list">
        <div
          v-for="item in watchingItems"
          :key="item.record.subject_id"
          class="watching-item"
        >
          <div class="watching-item-header">
            <router-link
              :to="`/subjects/${item.record.subject_id}`"
              class="watching-subject-link"
            >
              {{ item.subject.name_cn || item.subject.name || `#${item.record.subject_id}` }}
            </router-link>
            <span class="watching-progress">
              {{ watchedCount(item) }} / {{ item.episode_count || item.episodes.length }}
            </span>
          </div>
          <div class="watching-ep-grid">
            <div
              v-for="ep in item.episodes.slice(0, 48)"
              :key="ep.bangumi_id"
              :class="['watching-ep-cell', epCellClass(item, ep)]"
              @click="toggleWatchingEp(item, ep)"
              :title="epTooltip(item, ep)"
            >
              <span class="watching-ep-num">{{ formatEpSort(ep.sort) }}</span>
            </div>
            <div
              v-if="item.episodes.length > 48"
              class="watching-ep-cell watching-ep-more"
              @click="$router.push(`/subjects/${item.record.subject_id}`)"
              title="点击查看全部剧集"
            >
              <span class="watching-ep-num">···</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 个人统计 -->
    <el-card class="section-card" v-if="recordStats">
      <template #header>
        <span>我的观看记录</span>
        <el-button text type="primary" @click="$router.push('/records')" style="float: right">
          查看全部
        </el-button>
      </template>
      <el-row :gutter="16" v-if="recordStats.total_records > 0">
        <el-col :xs="12" :sm="6">
          <div class="stat-item">
            <span class="stat-num">{{ recordStats.total_records }}</span>
            <span class="stat-label">总记录</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" v-for="(count, label) in recordStats.status_distribution" :key="label">
          <div class="stat-item" v-if="count > 0">
            <span class="stat-num">{{ count }}</span>
            <span class="stat-label">{{ label }}</span>
          </div>
        </el-col>
      </el-row>
      <el-empty v-else description="暂无观看记录，去浏览条目吧" :image-size="60" />
    </el-card>

    <!-- 高分推荐 -->
    <el-card class="section-card" v-loading="topLoading">
      <template #header>
        <span>高分推荐</span>
        <el-button text type="primary" @click="$router.push('/subjects?sort=score&order=desc')" style="float: right">
          更多
        </el-button>
      </template>
      <el-row :gutter="12">
        <el-col v-for="s in topSubjects" :key="s.bangumi_id" :xs="12" :sm="8" :md="6" :lg="4">
          <SubjectCard :subject="s" view-mode="grid" @add-record="openHomeAddRecord" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 最新更新 -->
    <el-card class="section-card" v-loading="latestLoading">
      <template #header>
        <span>最新更新</span>
      </template>
      <el-row :gutter="12">
        <el-col v-for="s in latestSubjects" :key="s.bangumi_id" :xs="12" :sm="8" :md="6" :lg="4">
          <SubjectCard :subject="s" view-mode="grid" @add-record="openHomeAddRecord" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 快速收藏弹窗 -->
    <el-dialog v-model="homeRecordVisible" title="添加记录" width="440px">
      <el-form :model="homeRecordForm" label-position="top">
        <el-form-item label="条目">
          <span class="quick-subject-name">{{ homeRecordSubject?.name_cn || homeRecordSubject?.name }}</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model.number="homeRecordForm.status" style="width: 100%">
            <el-option :value="1" label="想看" />
            <el-option :value="2" label="在看" />
            <el-option :value="3" label="看过" />
            <el-option :value="4" label="搁置" />
            <el-option :value="5" label="抛弃" />
          </el-select>
        </el-form-item>
        <el-form-item label="进度">
          <el-input-number v-model="homeRecordForm.progress" :min="0" :max="9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="评分">
          <RatingInput v-model="homeRecordForm.rating" />
        </el-form-item>
        <el-form-item label="评论">
          <el-input
            v-model="homeRecordForm.comment"
            type="textarea"
            :rows="2"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="homeRecordVisible = false">取消</el-button>
        <el-button type="primary" @click="doHomeRecord" :loading="homeRecordSaving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSubjects } from '@/api/subjects'
import { getWatching, updateRecord, createRecord } from '@/api/records'
import apiClient from '@/api/request'
import SubjectCard from '@/components/SubjectCard.vue'
import RatingInput from '@/components/RatingInput.vue'
import { ElMessage } from 'element-plus'

// ─── 模块级缓存 ───
const _topSubjects = ref([])
const _latestSubjects = ref([])
const _syncStatus = ref(null)
const _recordStats = ref(null)
const _watchingItems = ref([])
const _loaded = ref(false)

const router = useRouter()
const searchKeyword = ref('')
const topSubjects = _topSubjects
const latestSubjects = _latestSubjects
const topLoading = ref(!_loaded.value)
const latestLoading = ref(!_loaded.value)
const syncStatus = _syncStatus
const recordStats = _recordStats
const watchingItems = _watchingItems
const watchingLoading = ref(!_loaded.value)

// 首页快速收藏弹窗
const homeRecordVisible = ref(false)
const homeRecordSubject = ref(null)
const homeRecordSaving = ref(false)
const homeRecordForm = reactive({ status: 2, progress: 0, rating: null, comment: '' })

const lastSyncText = computed(() => {
  if (!syncStatus.value?.last_sync) return '未知'
  return new Date(syncStatus.value.last_sync).toLocaleDateString('zh-CN')
})

onMounted(async () => {
  if (_loaded.value) {
    // 返回首页直接恢复缓存，不重查
    return
  }
  // 并行加载
  try {
    const [topRes, latestRes, syncRes, statsRes, watchingRes] = await Promise.all([
      getSubjects({ sort: 'score', order: 'desc', score_from: 7, limit: 10, type: 2 }),
      getSubjects({ sort: 'updated_at', order: 'desc', limit: 10 }),
      apiClient.get('/sync/status'),
      apiClient.get('/records/stats').catch(() => ({ data: null })),
      getWatching().catch(() => []),
    ])
    topSubjects.value = topRes.items || []
    latestSubjects.value = latestRes.items || []
    syncStatus.value = syncRes.data || syncRes
    recordStats.value = statsRes.data || statsRes
    watchingItems.value = Array.isArray(watchingRes) ? watchingRes : []
    _loaded.value = true
  } catch (e) {
    console.error('Home page load error:', e)
  } finally {
    topLoading.value = false
    latestLoading.value = false
    watchingLoading.value = false
  }
})

function goSearch() {
  if (searchKeyword.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchKeyword.value.trim())}`)
  }
}

// ─── 点格子逻辑 ───

function epCellClass(item, ep) {
  const key = String(ep.sort)
  const epStatus = item.record.ep_status || {}
  if (epStatus[key] === '看过') return 'watched'
  return ''
}

function epTooltip(item, ep) {
  const name = ep.name_cn || ep.name
  const mark = epCellClass(item, ep) === 'watched' ? ' ✅' : ''
  return `${formatEpSort(ep.sort)}. ${name}${mark}`
}

function formatEpSort(sort) {
  if (sort === undefined || sort === null) return '?'
  return String(sort)
}

function watchedCount(item) {
  const epStatus = item.record.ep_status || {}
  return Object.values(epStatus).filter(s => s === '看过').length
}

async function toggleWatchingEp(item, ep) {
  const record = item.record
  const clickedSort = Math.floor(ep.sort)
  const oldProgress = record.progress
  const oldEpStatus = { ...(record.ep_status || {}) }

  // 点击当前进度格 → 取消全部进度；否则设置进度为该格 sort
  const newProgress = (oldProgress === clickedSort) ? 0 : clickedSort

  // 乐观更新：本地计算 ep_status
  const newEpStatus = {}
  for (const epItem of item.episodes) {
    if (epItem.sort <= newProgress) {
      newEpStatus[String(epItem.sort)] = '看过'
    }
  }
  // 保留超出进度的非「看过」状态（如 抛弃）
  for (const [k, v] of Object.entries(oldEpStatus)) {
    if (parseFloat(k) > newProgress && v !== '看过') {
      newEpStatus[k] = v
    }
  }
  record.ep_status = newEpStatus
  record.progress = newProgress

  try {
    if (record.id) {
      // 只发 progress，让后端生成 ep_status，保证双向统一
      const res = await updateRecord(record.id, {
        progress: newProgress,
        status: newProgress > 0 ? 2 : record.status,
      })
      // 用服务端返回值校准本地状态
      record.ep_status = res.ep_status || {}
      record.progress = res.progress
    } else {
      // 自动创建记录 — 只发 progress
      const newRec = await createRecord({
        subject_id: record.subject_id,
        status: 2,
        progress: newProgress,
      })
      record.id = newRec.id
      record.ep_status = newRec.ep_status || {}
      record.progress = newRec.progress
    }
  } catch {
    // 回滚
    record.ep_status = oldEpStatus
    record.progress = oldProgress
  }
}

// ─── 首页快速收藏弹窗 ───
function openHomeAddRecord(subject) {
  homeRecordSubject.value = subject
  homeRecordForm.status = 2
  homeRecordForm.progress = 0
  homeRecordForm.rating = null
  homeRecordForm.comment = ''
  homeRecordVisible.value = true
}

async function doHomeRecord() {
  if (!homeRecordSubject.value) return
  homeRecordSaving.value = true
  try {
    await createRecord({
      subject_id: homeRecordSubject.value.bangumi_id,
      status: homeRecordForm.status,
      progress: homeRecordForm.progress,
      rating: homeRecordForm.rating,
      comment: homeRecordForm.comment || undefined,
    })
    ElMessage.success(`已收藏「${homeRecordSubject.value.name_cn || homeRecordSubject.value.name}」`)
    homeRecordVisible.value = false
  } catch {
    // 错误由拦截器处理
  } finally {
    homeRecordSaving.value = false
  }
}
</script>

<style scoped>
.home-page {
  max-width: 1400px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 40px 0 30px;
}
.hero-title {
  font-size: 2.4rem;
  color: #409eff;
  margin: 0 0 12px;
}
.hero-desc {
  color: #909399;
  font-size: 1rem;
  margin-bottom: 24px;
}
.quick-search {
  display: flex;
  justify-content: center;
  max-width: 500px;
  margin: 0 auto;
}

.stats-row {
  margin-bottom: 24px;
}

.section-card {
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
  padding: 12px 0;
}
.stat-num {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: #409eff;
}
.stat-label {
  display: block;
  font-size: 0.85rem;
  color: #909399;
  margin-top: 4px;
}
.stat-suffix {
  font-size: 0.75rem;
  color: #909399;
}

/* 在看在追 — 点格子 */
.watching-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.watching-item {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 12px 16px;
}
.watching-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.watching-subject-link {
  font-weight: 600;
  font-size: 1rem;
  color: #409eff;
  text-decoration: none;
  transition: color 0.15s;
}
.watching-subject-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}
.watching-progress {
  font-size: 0.85rem;
  color: #909399;
  font-weight: 500;
}
.watching-ep-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.watching-ep-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 7px;
  background: #f0f2f5;
  cursor: pointer;
  transition: all 0.12s;
  user-select: none;
}
.watching-ep-cell:hover {
  background: #d9ecff;
  transform: scale(1.12);
}
.watching-ep-cell.watched {
  background: #67c23a;
  color: #fff;
}
.watching-ep-cell.watched:hover {
  background: #5daf34;
}
.watching-ep-cell.watching-ep-more {
  background: transparent;
  border: 1px dashed #dcdfe6;
  cursor: pointer;
  color: #909399;
}
.watching-ep-num {
  font-size: 0.72rem;
  font-weight: 600;
}

.quick-subject-name {
  font-weight: 600;
  font-size: 1.05rem;
}
</style>
