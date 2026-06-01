<template>
  <div class="staff-list">
    <div class="section-header">
      <h4>STAFF（{{ persons.length }} 人）</h4>
    </div>

    <el-empty v-if="!persons.length" description="暂无 STAFF 信息" :image-size="40" />

    <div v-for="group in positionGroups" :key="group.label" class="staff-group">
      <h5 class="position-label">{{ group.label }}（{{ group.members.length }}）</h5>
      <div class="staff-members">
        <el-tag
          v-for="p in group.members"
          :key="`${p.person_id}-${p.position}`"
          class="staff-tag"
          size="default"
          effect="plain"
        >
          {{ p.person_name }}
          <span v-if="p.appear_eps" class="staff-eps">（{{ p.appear_eps }}）</span>
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  persons: { type: Array, default: () => [] },
})

const POSITION_NAMES = {
  1: '原作',
  2: '导演',
  3: '脚本',
  4: '分镜',
  5: '演出',
  6: '音乐',
  7: '人物设定',
  8: '美术监督',
  9: '音响监督',
  10: '系列构成',
  11: '作画监督',
  12: '原画',
  13: '动画制作',
  14: '制作',
  99: '其他',
}

const positionGroups = computed(() => {
  const groups = new Map()
  for (const p of props.persons) {
    const key = p.position ?? 99
    const label = POSITION_NAMES[key] || `职位${key}`
    if (!groups.has(key)) {
      groups.set(key, { key, label, members: [] })
    }
    groups.get(key).members.push(p)
  }
  // 按 position 编号排序
  return [...groups.values()].sort((a, b) => a.key - b.key)
})
</script>

<style scoped>
.section-header {
  margin-bottom: 12px;
}
.section-header h4 {
  margin: 0;
  font-size: 1.1rem;
}
.staff-group {
  margin-bottom: 12px;
}
.position-label {
  margin: 0 0 6px;
  font-size: 0.9rem;
  color: #606266;
}
.staff-members {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.staff-tag {
  cursor: default;
}
.staff-eps {
  color: #909399;
  font-size: 0.75rem;
}
</style>
