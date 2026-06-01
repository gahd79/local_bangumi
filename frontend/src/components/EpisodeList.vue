<template>
  <div class="episode-list">
    <div class="episode-header">
      <h4>剧集列表（{{ episodes.length }} 集）</h4>
      <el-button
        v-if="showViewAll"
        text
        type="primary"
        @click="$router.push(`/episodes?subject=${subjectId}`)"
      >
        查看全部
      </el-button>
    </div>

    <el-empty v-if="!episodes.length" description="暂无剧集信息" :image-size="40" />

    <!-- 按 disc 分组 — 点格子模式 -->
    <template v-for="group in discGroups" :key="group.disc">
      <div class="disc-group">
        <h5 v-if="group.disc > 0" class="disc-label">Disc {{ group.disc }}</h5>
        <div class="episode-grid">
          <div
            v-for="ep in group.episodes"
            :key="ep.bangumi_id"
            :class="['episode-cell', epCellClass(ep)]"
            @click="toggleEpisode(ep)"
            :title="epTooltip(ep)"
          >
            <span class="ep-cell-num">{{ formatSort(ep.sort) }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- 剧集详情展开 -->
    <el-collapse v-if="episodes.length > 0" style="margin-top: 16px">
      <el-collapse-item title="剧集详情列表" name="detail">
        <template v-for="group in discGroups" :key="'d-' + group.disc">
          <div class="disc-group">
            <h5 v-if="group.disc > 0" class="disc-label">Disc {{ group.disc }}</h5>
            <div
              v-for="ep in group.episodes"
              :key="'d-' + ep.bangumi_id"
              class="episode-item"
              :class="{ 'ep-watched': epCellClass(ep) === 'watched' }"
              @click="toggleEpisode(ep)"
            >
              <div class="ep-main">
                <span class="ep-sort">{{ formatSort(ep.sort) }}</span>
                <StatusBadge type="episode_type" :value="ep.type" size="small" />
                <span class="ep-name">{{ ep.name_cn || ep.name }}</span>
                <span class="ep-name-original" v-if="ep.name_cn && ep.name">
                  {{ ep.name }}
                </span>
                <span class="ep-spacer" />
                <span class="ep-duration" v-if="ep.duration">{{ ep.duration }}</span>
                <span class="ep-airdate" v-if="ep.airdate">{{ ep.airdate }}</span>
                <el-icon v-if="epCellClass(ep) === 'watched'" class="ep-check"><Check /></el-icon>
              </div>
            </div>
          </div>
        </template>
      </el-collapse-item>
    </el-collapse>

    <div class="episode-hint" v-if="episodes.length > 0">
      💡 点击剧集格子标记/取消已看 ｜ 绿色=已看
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StatusBadge from './StatusBadge.vue'

const props = defineProps({
  episodes: { type: Array, default: () => [] },
  subjectId: { type: Number, required: true },
  showViewAll: { type: Boolean, default: false },
  /** 用户的逐集状态，如 {"1": "看过", "2": "看过", ...} */
  epStatus: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['toggle-ep'])

const discGroups = computed(() => {
  const groups = new Map()
  for (const ep of props.episodes) {
    const disc = ep.disc ?? 0
    if (!groups.has(disc)) {
      groups.set(disc, { disc, episodes: [] })
    }
    groups.get(disc).episodes.push(ep)
  }
  return [...groups.values()].sort((a, b) => a.disc - b.disc)
})

function epKey(ep) {
  return String(ep.sort)
}

function epCellClass(ep) {
  const key = epKey(ep)
  const status = props.epStatus && props.epStatus[key]
  if (status === '看过') return 'watched'
  if (status === '抛弃') return 'dropped'
  return ''
}

function epTooltip(ep) {
  const name = ep.name_cn || ep.name
  const mark = epCellClass(ep) === 'watched' ? ' ✅' : ''
  return `${formatSort(ep.sort)}. ${name}${mark}`
}

function toggleEpisode(ep) {
  emit('toggle-ep', ep)
}

function formatSort(sort) {
  if (sort === undefined || sort === null) return '?'
  return String(sort)
}
</script>

<style scoped>
.episode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.episode-header h4 {
  margin: 0;
  font-size: 1.1rem;
}
.disc-group {
  margin-bottom: 12px;
}
.disc-label {
  color: #909399;
  font-size: 0.85rem;
  margin: 8px 0 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid #ebeef5;
}

/* 点格子 */
.episode-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.episode-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: #f0f2f5;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}
.episode-cell:hover {
  background: #d9ecff;
  transform: scale(1.1);
}
.episode-cell.watched {
  background: #67c23a;
  color: #fff;
}
.episode-cell.watched:hover {
  background: #5daf34;
}
.episode-cell.dropped {
  background: #f56c6c;
  color: #fff;
  opacity: 0.7;
}
.ep-cell-num {
  font-size: 0.78rem;
  font-weight: 600;
}

.episode-hint {
  margin-top: 8px;
  font-size: 0.78rem;
  color: #909399;
}

/* 详情列表 */
.episode-item {
  padding: 5px 8px;
  border-radius: 8px;
  transition: background 0.15s;
  cursor: pointer;
}
.episode-item:hover {
  background: #f5f7fa;
}
.episode-item.ep-watched {
  background: #f0f9eb;
}
.ep-main {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ep-sort {
  color: #909399;
  font-size: 0.8rem;
  min-width: 24px;
  text-align: right;
}
.ep-name {
  font-weight: 500;
}
.ep-name-original {
  color: #c0c4cc;
  font-size: 0.8rem;
}
.ep-spacer {
  flex: 1;
}
.ep-duration {
  color: #909399;
  font-size: 0.8rem;
}
.ep-airdate {
  color: #909399;
  font-size: 0.8rem;
}
.ep-check {
  color: #67c23a;
}
</style>
