<template>
  <el-card
    :class="['subject-card', viewMode]"
    :body-style="viewMode === 'list' ? { padding: '10px 16px' } : { padding: '12px' }"
    shadow="hover"
    @click="goDetail"
  >
    <!-- Grid 模式 -->
    <template v-if="viewMode === 'grid'">
      <div class="card-type-badge">
        <StatusBadge type="subject_type" :value="subject.type" size="small" />
      </div>
      <div class="card-name">{{ subject.name_cn || subject.name }}</div>
      <div class="card-name-sub" v-if="subject.name_cn && subject.name">
        {{ subject.name }}
      </div>
      <div class="card-meta">
        <ScoreDisplay :score="subject.score" :rank="subject.rank" size="small" />
      </div>
      <div class="card-footer">
        <span class="card-date" v-if="subject.date">{{ formatDate(subject.date) }}</span>
        <span class="card-stats">
          <el-icon><Star /></el-icon>{{ favCount }}
        </span>
      </div>
      <!-- 悬停时显示的快速收藏按钮 -->
      <div class="card-quick-actions" @click.stop>
        <el-button size="small" circle @click="quickCollect(1)" title="想看">
          <span class="quick-icon">想</span>
        </el-button>
        <el-button size="small" circle @click="quickCollect(3)" title="看过">
          <span class="quick-icon">✓</span>
        </el-button>
        <el-button size="small" circle type="primary" @click="emit('add-record', subject)" title="添加记录">
          <span class="quick-icon">+</span>
        </el-button>
      </div>
    </template>

    <!-- List 模式 -->
    <template v-else>
      <div class="list-row">
        <StatusBadge type="subject_type" :value="subject.type" size="small" />
        <span class="list-name">{{ subject.name_cn || subject.name }}</span>
        <span class="list-name-original" v-if="subject.name_cn && subject.name">
          {{ subject.name }}
        </span>
        <span class="list-spacer" />
        <ScoreDisplay :score="subject.score" :rank="subject.rank" size="small" />
        <span class="list-date" v-if="subject.date">{{ formatDate(subject.date) }}</span>
        <el-button size="small" text type="primary" @click.stop="quickCollect(1)" title="想看">想</el-button>
        <el-button size="small" text type="success" @click.stop="quickCollect(3)" title="看过">✓</el-button>
        <el-button size="small" text type="warning" @click.stop="emit('add-record', subject)" title="添加记录">+记录</el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { createRecord } from '@/api/records'
import { ElMessage } from 'element-plus'
import StatusBadge from './StatusBadge.vue'
import ScoreDisplay from './ScoreDisplay.vue'

const props = defineProps({
  subject: { type: Object, required: true },
  viewMode: { type: String, default: 'grid', validator: (v) => ['grid', 'list'].includes(v) },
})

const emit = defineEmits(['quick-record', 'add-record'])

const router = useRouter()

const favCount = computed(() => {
  const s = props.subject
  return (s.wish_count || 0) + (s.doing_count || 0) + (s.done_count || 0) +
    (s.on_hold_count || 0) + (s.dropped_count || 0)
})

function goDetail() {
  router.push(`/subjects/${props.subject.bangumi_id}`)
}

async function quickCollect(status) {
  try {
    await createRecord({
      subject_id: props.subject.bangumi_id,
      status,
    })
    const statusNames = { 1: '想看', 2: '在看', 3: '看过', 4: '搁置', 5: '抛弃' }
    ElMessage.success(`已标记为「${statusNames[status]}」`)
  } catch {
    emit('quick-record', props.subject)
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  if (dateStr.length > 10) return dateStr.slice(0, 10)
  return dateStr
}
</script>

<style scoped>
.subject-card {
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  border-radius: 12px;
  overflow: hidden;
}
.subject-card:hover {
  transform: translateY(-2px);
}

/* Grid 模式 */
.subject-card.grid {
  display: flex;
  flex-direction: column;
  height: 190px;
  position: relative;
}
.card-type-badge {
  margin-bottom: 6px;
}
.card-name {
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.6em;
  flex-shrink: 0;
}
.card-name-sub {
  font-size: 0.75rem;
  color: #999;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}
.card-meta {
  margin-top: auto;
  padding-top: 6px;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  font-size: 0.78rem;
  color: #999;
}
.card-stats {
  display: flex;
  align-items: center;
  gap: 2px;
}
.card-quick-actions {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
}
.subject-card.grid:hover .card-quick-actions {
  opacity: 1;
}
.card-quick-actions .el-button {
  width: 28px;
  height: 28px;
  min-width: 0;
  padding: 0;
}
.quick-icon {
  font-size: 11px;
  font-weight: 700;
}

/* List 模式 */
.subject-card.list {
  margin-bottom: 4px;
  border-radius: 10px;
}
.list-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.list-name {
  font-weight: 600;
  font-size: 0.95rem;
}
.list-name-original {
  color: #999;
  font-size: 0.78rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}
.list-spacer {
  flex: 1;
}
.list-date {
  color: #999;
  font-size: 0.78rem;
}
</style>
