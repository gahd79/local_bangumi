<template>
  <div class="rating-input">
    <el-rate
      :model-value="modelValue ? modelValue / 2 : 0"
      :max="5"
      :size="size"
      :disabled="disabled"
      :allow-half="true"
      show-score
      :score-template="scoreText"
      @update:model-value="onRateChange"
      @clear="onClear"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: null },
  disabled: { type: Boolean, default: false },
  size: { type: String, default: 'default' },
})

const emit = defineEmits(['update:modelValue'])

const scoreText = computed(() => {
  if (props.modelValue == null) return '未评分'
  return `${props.modelValue}/10`
})

function onRateChange(val) {
  if (val === 0) {
    emit('update:modelValue', null)
  } else {
    emit('update:modelValue', Math.round(val * 2))
  }
}

function onClear() {
  emit('update:modelValue', null)
}
</script>
