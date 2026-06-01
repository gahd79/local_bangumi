<template>
  <el-tag :type="tagType" :size="size" :effect="effect">
    {{ label }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (v) =>
      ['subject_type', 'record_status', 'episode_type', 'role', 'person_type'].includes(v),
  },
  value: {
    type: Number,
    required: true,
  },
  size: {
    type: String,
    default: 'default',
  },
  effect: {
    type: String,
    default: 'light',
  },
})

const LABELS = {
  subject_type: { 1: '漫画', 2: '动画', 3: '音乐', 4: '游戏', 6: '三次元' },
  record_status: { 1: '想看', 2: '在看', 3: '看过', 4: '搁置', 5: '抛弃' },
  episode_type: { 0: '正篇', 1: 'SP', 2: 'OP', 3: 'ED', 4: '预告', 5: 'MAD', 6: '其他' },
  role: { 1: '角色', 2: '机体', 3: '组织' },
  person_type: { 1: '个人', 2: '公司', 3: '组合' },
}

const TYPE_COLORS = {
  subject_type: { 1: '', 2: 'success', 3: 'warning', 4: 'danger', 6: 'info' },
  record_status: { 1: 'info', 2: '', 3: 'success', 4: 'warning', 5: 'danger' },
  episode_type: { 0: '', 1: 'info', 2: 'warning', 3: 'warning', 4: 'info', 5: 'info', 6: 'info' },
  role: { 1: '', 2: 'danger', 3: 'warning' },
  person_type: { 1: '', 2: 'success', 3: 'warning' },
}

const label = computed(() => {
  return LABELS[props.type]?.[props.value] || `#${props.value}`
})

const tagType = computed(() => {
  return TYPE_COLORS[props.type]?.[props.value] || ''
})
</script>
