<template>
  <div class="score-display" :class="{ 'score-empty': score == null && rank == null }">
    <template v-if="score != null">
      <el-rate
        :model-value="normalizedScore"
        :max="5"
        disabled
        show-score
        :score-template="`${score.toFixed(1)}`"
        :size="rateSize"
      />
    </template>
    <template v-if="rank != null">
      <span class="rank-tag">
        <el-icon><Trophy /></el-icon>
        #{{ rank }}
      </span>
    </template>
    <template v-if="score == null && rank == null">
      <span class="no-score">暂无评分</span>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: null },
  rank: { type: Number, default: null },
  size: { type: String, default: 'default' },
})

const normalizedScore = computed(() => {
  if (props.score == null) return 0
  return props.score / 2 // 10分制 → 5星制
})

const rateSize = computed(() => {
  return props.size === 'small' ? 'small' : 'default'
})
</script>

<style scoped>
.score-display {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.rank-tag {
  color: #e6a23c;
  font-size: 0.85rem;
  font-weight: 600;
}
.no-score {
  color: #999;
  font-size: 0.85rem;
}
.score-empty {
  min-height: unset;
}
</style>
