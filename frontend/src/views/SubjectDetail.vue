<template>
  <div class="subject-detail-page" v-loading="loading">
    <!-- 骨架屏 -->
    <template v-if="loading">
      <el-skeleton :rows="4" animated />
      <el-skeleton :rows="6" animated style="margin-top: 24px" />
    </template>

    <!-- 内容 -->
    <template v-if="!loading && subject">
      <!-- 返回按钮 -->
      <el-button text @click="$router.back()" style="margin-bottom: 16px">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>

      <!-- Hero 区 -->
      <div class="detail-hero">
        <div class="hero-main">
          <h1 class="hero-title">
            {{ subject.name_cn || subject.name }}
          </h1>
          <div class="hero-sub-names" v-if="subject.name_cn && subject.name">
            <span class="sub-name">{{ subject.name }}</span>
            <span class="sub-name" v-if="subject.name_en">{{ subject.name_en }}</span>
          </div>
          <div class="hero-tags">
            <StatusBadge type="subject_type" :value="subject.type" />
            <el-tag v-if="subject.nsfw" type="danger" size="small">NSFW</el-tag>
            <el-tag v-if="subject.series" type="info" size="small">系列作品</el-tag>
            <el-tag v-if="subject.platform" type="info" size="small">
              平台: {{ subject.platform }}
            </el-tag>
          </div>
          <div class="hero-meta">
            <ScoreDisplay :score="subject.score" :rank="subject.rank" />
            <span class="hero-date" v-if="subject.date">{{ subject.date }}</span>
          </div>
          <!-- 收藏统计 -->
          <div class="fav-stats">
            <span v-if="subject.wish_count" class="fav-item">
              <el-icon><Star /></el-icon> 想看 {{ subject.wish_count }}
            </span>
            <span v-if="subject.doing_count" class="fav-item">
              在看 {{ subject.doing_count }}
            </span>
            <span v-if="subject.done_count" class="fav-item">
              看过 {{ subject.done_count }}
            </span>
            <span v-if="subject.on_hold_count" class="fav-item">
              搁置 {{ subject.on_hold_count }}
            </span>
            <span v-if="subject.dropped_count" class="fav-item">
              抛弃 {{ subject.dropped_count }}
            </span>
          </div>
        </div>
      </div>

      <!-- 概要 -->
      <el-card class="detail-section" v-if="subject.summary">
        <template #header><span>概要</span></template>
        <p class="summary-text">{{ subject.summary }}</p>
      </el-card>

      <!-- Infobox -->
      <el-card class="detail-section">
        <template #header><span>详细信息</span></template>
        <InfoboxDisplay :infobox="subject.infobox_parsed" />
      </el-card>

      <!-- 标签 -->
      <el-card class="detail-section" v-if="subject.tags && subject.tags.length">
        <template #header><span>标签</span></template>
        <div class="tag-list">
          <el-tag
            v-for="tag in subject.tags.slice(0, 30)"
            :key="tag.name"
            type="info"
            effect="plain"
            size="default"
            class="tag-item"
          >
            {{ tag.name }}
            <span v-if="tag.count" class="tag-count">{{ tag.count }}</span>
          </el-tag>
        </div>
      </el-card>

      <!-- 剧集列表（点格子） -->
      <el-card class="detail-section">
        <EpisodeList
          :episodes="subject.episodes || []"
          :subject-id="subject.bangumi_id"
          :ep-status="recordEpStatus"
          :show-view-all="(subject.episodes || []).length >= 200"
          @toggle-ep="onToggleEpisode"
        />
      </el-card>

      <!-- 角色 -->
      <el-card class="detail-section">
        <CharacterGrid :characters="subject.characters || []" />
      </el-card>

      <!-- STAFF -->
      <el-card class="detail-section">
        <StaffList :persons="subject.persons || []" />
      </el-card>

      <!-- 关联条目 -->
      <el-card class="detail-section" v-if="subject.relations && subject.relations.length">
        <template #header><span>关联条目（{{ subject.relations.length }}）</span></template>
        <div class="relation-list">
          <el-card
            v-for="r in subject.relations"
            :key="`${r.relation_type}-${r.related_subject_id}`"
            shadow="hover"
            class="relation-card"
            @click="$router.push(`/subjects/${r.related_subject_id}`)"
          >
            <div class="relation-row">
              <span class="relation-name">
                {{ r.related_subject_name_cn || r.related_subject_name || `#${r.related_subject_id}` }}
              </span>
              <span class="relation-type-tag">{{ RELATION_NAMES[r.relation_type] || `类型${r.relation_type}` }}</span>
            </div>
          </el-card>
        </div>
      </el-card>

      <!-- 收藏操作栏（底部悬浮） -->
      <div class="action-bar">
        <el-select v-model="recordForm.status" placeholder="状态" style="width: 120px">
          <el-option :value="1" label="想看" />
          <el-option :value="2" label="在看" />
          <el-option :value="3" label="看过" />
          <el-option :value="4" label="搁置" />
          <el-option :value="5" label="抛弃" />
        </el-select>
        <el-input-number
          v-model="recordForm.progress"
          :min="0"
          :max="maxProgress"
          placeholder="进度"
          style="width: 120px"
        />
        <RatingInput v-model="recordForm.rating" />
        <el-button type="primary" @click="saveRecord" :loading="recordSaving">
          {{ existingRecord ? '更新记录' : '添加收藏' }}
        </el-button>
        <el-button v-if="existingRecord" type="danger" @click="delRecord" :loading="recordSaving">
          删除
        </el-button>
      </div>

      <el-backtop />
    </template>

    <!-- 错误 -->
    <el-result v-if="!loading && !subject && error" icon="error" title="加载失败" :sub-title="error">
      <template #extra>
        <el-button @click="$router.back()">返回</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSubject } from '@/api/subjects'
import { getRecords, createRecord, updateRecord, deleteRecord } from '@/api/records'
import { ElMessage } from 'element-plus'
import StatusBadge from '@/components/StatusBadge.vue'
import ScoreDisplay from '@/components/ScoreDisplay.vue'
import RatingInput from '@/components/RatingInput.vue'
import InfoboxDisplay from '@/components/InfoboxDisplay.vue'
import EpisodeList from '@/components/EpisodeList.vue'
import CharacterGrid from '@/components/CharacterGrid.vue'
import StaffList from '@/components/StaffList.vue'

const route = useRoute()

const subject = ref(null)
const loading = ref(true)
const error = ref(null)
const existingRecord = ref(null)
const recordSaving = ref(false)
const recordEpStatus = ref({})

const recordForm = reactive({
  status: 1,
  progress: 0,
  rating: null,
})

const RELATION_NAMES = {
  1: '续作',
  2: '前传',
  3: '同系列',
  1001: '改编',
  1002: '衍生',
  3003: '角色出演',
  3005: '番外篇',
  3099: '其他',
}

// 根据剧集数量计算进度最大值
const maxProgress = computed(() => {
  const eps = subject.value?.episodes
  if (!eps || !eps.length) return 9999
  // 取 max sort 值（floor），至少为剧集数量
  const maxSort = Math.max(...eps.map(e => Math.floor(e.sort)).filter(s => s > 0), 0)
  return maxSort || eps.length || 9999
})

onMounted(async () => {
  const bangumiId = Number(route.params.bangumiId)
  if (!bangumiId) {
    error.value = '无效的条目 ID'
    loading.value = false
    return
  }

  try {
    const [detail, records] = await Promise.all([
      getSubject(bangumiId),
      getRecords({ subject_id: bangumiId }).catch(() => []),
    ])
    subject.value = detail

    // 检查是否已有记录
    const recs = Array.isArray(records) ? records : []
    if (recs.length > 0) {
      existingRecord.value = recs[0]
      recordForm.status = recs[0].status
      recordForm.progress = recs[0].progress
      recordForm.rating = recs[0].rating
      recordEpStatus.value = recs[0].ep_status || {}
    }
  } catch (e) {
    error.value = e.response?.data?.detail || '加载条目失败'
  } finally {
    loading.value = false
  }
})

async function saveRecord() {
  recordSaving.value = true
  try {
    if (existingRecord.value) {
      await updateRecord(existingRecord.value.id, {
        status: recordForm.status,
        progress: recordForm.progress,
        rating: recordForm.rating,
      })
      ElMessage.success('收藏记录已更新')
    } else {
      await createRecord({
        subject_id: subject.value.bangumi_id,
        status: recordForm.status,
        progress: recordForm.progress,
        rating: recordForm.rating,
      })
      ElMessage.success('已添加收藏')
    }
    // 刷新记录状态
    const records = await getRecords({ limit: 100 })
    const recs = Array.isArray(records) ? records : []
    const match = recs.find((r) => r.subject_id === subject.value.bangumi_id)
    existingRecord.value = match || null
    // 同步更新网格状态
    if (match) {
      recordEpStatus.value = match.ep_status || {}
      recordForm.progress = match.progress
    }
  } catch {
    // 错误提示由 API 拦截器统一处理
  } finally {
    recordSaving.value = false
  }
}

async function onToggleEpisode(ep) {
  // 点击格子 → 设置进度为该格 sort（floor），由后端生成 ep_status，保证双向统一
  const clickedSort = Math.floor(ep.sort)
  const oldProgress = recordForm.progress
  const oldEpStatus = { ...recordEpStatus.value }

  // 点击当前进度格 → 取消全部进度；否则设置进度为该格 sort
  const newProgress = (oldProgress === clickedSort) ? 0 : clickedSort

  // 乐观更新：本地计算 ep_status
  const episodes = subject.value?.episodes || []
  const newEpStatus = {}
  for (const epItem of episodes) {
    if (epItem.sort <= newProgress) {
      newEpStatus[String(epItem.sort)] = '看过'
    }
  }
  for (const [k, v] of Object.entries(oldEpStatus)) {
    if (parseFloat(k) > newProgress && v !== '看过') {
      newEpStatus[k] = v
    }
  }
  recordEpStatus.value = newEpStatus
  recordForm.progress = newProgress

  try {
    if (existingRecord.value) {
      // 只发 progress，让后端生成 ep_status
      const res = await updateRecord(existingRecord.value.id, {
        progress: newProgress,
        status: newProgress > 0 ? existingRecord.value.status : existingRecord.value.status,
      })
      recordEpStatus.value = res.ep_status || {}
      existingRecord.value = { ...existingRecord.value, ep_status: res.ep_status, progress: res.progress }
      recordForm.progress = res.progress
    } else {
      // 自动创建记录 — 只发 progress
      const newRec = await createRecord({
        subject_id: subject.value.bangumi_id,
        status: 2,
        progress: newProgress,
      })
      existingRecord.value = newRec
      recordEpStatus.value = newRec.ep_status || {}
      recordForm.status = 2
      recordForm.progress = newRec.progress
    }
  } catch {
    // 回滚
    recordEpStatus.value = oldEpStatus
    recordForm.progress = oldProgress
  }
}

async function delRecord() {
  if (!existingRecord.value) return
  recordSaving.value = true
  try {
    await deleteRecord(existingRecord.value.id)
    ElMessage.success('收藏记录已删除')
    existingRecord.value = null
    recordEpStatus.value = {}
    recordForm.status = 1
    recordForm.progress = 0
    recordForm.rating = null
  } catch {
    // 错误提示由 API 拦截器统一处理
  } finally {
    recordSaving.value = false
  }
}
</script>

<style scoped>
.subject-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.detail-hero {
  margin-bottom: 24px;
}
.hero-title {
  font-size: 1.8rem;
  margin: 0 0 8px;
  color: #303133;
}
.hero-sub-names {
  margin-bottom: 12px;
}
.sub-name {
  display: inline-block;
  color: #909399;
  font-size: 0.9rem;
  margin-right: 16px;
}
.hero-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.hero-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}
.hero-date {
  color: #909399;
  font-size: 0.9rem;
}
.fav-stats {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: #909399;
}
.fav-item {
  display: flex;
  align-items: center;
  gap: 2px;
}

.detail-section {
  margin-bottom: 16px;
  border-radius: 12px;
}

.summary-text {
  line-height: 1.8;
  white-space: pre-wrap;
  color: #606266;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tag-item {
  cursor: default;
}
.tag-count {
  color: #c0c4cc;
  margin-left: 2px;
  font-size: 0.75rem;
}

.relation-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.relation-card {
  cursor: pointer;
  flex: 0 0 auto;
  min-width: 200px;
}
.relation-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.relation-name {
  font-weight: 500;
  font-size: 0.9rem;
}
.relation-type-tag {
  font-size: 0.75rem;
  color: #909399;
}

/* 底部操作栏 */
.action-bar {
  position: sticky;
  bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
  flex-wrap: wrap;
  justify-content: center;
}
</style>
