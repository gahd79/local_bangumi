<template>
  <div class="subject-filters">
    <div class="filters-header">
      <h3>筛选条件</h3>
    </div>
    <el-form :model="localFilters" label-position="top" size="default">
      <el-row :gutter="16">
        <!-- 类型筛选 -->
        <el-col :xs="12" :sm="8" :md="4">
          <el-form-item label="条目类型">
            <el-select
              v-model="localFilters.type"
              placeholder="全部"
              clearable
              style="width: 100%"
            >
              <el-option :value="1" label="漫画" />
              <el-option :value="2" label="动画" />
              <el-option :value="3" label="音乐" />
              <el-option :value="4" label="游戏" />
              <el-option :value="6" label="三次元" />
            </el-select>
          </el-form-item>
        </el-col>

        <!-- 关键词搜索 -->
        <el-col :xs="12" :sm="8" :md="4">
          <el-form-item label="关键词">
            <el-input v-model="localFilters.search" placeholder="搜索名称..." clearable />
          </el-form-item>
        </el-col>

        <!-- 年份筛选 -->
        <el-col :xs="12" :sm="8" :md="3">
          <el-form-item label="年份">
            <el-select
              v-model="localFilters.year"
              placeholder="全部"
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="y in yearOptions"
                :key="y"
                :value="y"
                :label="String(y)"
              />
            </el-select>
          </el-form-item>
        </el-col>

        <!-- 季度筛选 -->
        <el-col :xs="12" :sm="8" :md="3">
          <el-form-item label="季度">
            <el-select
              v-model="localFilters.season"
              placeholder="全部"
              clearable
              style="width: 100%"
              :disabled="!localFilters.year"
            >
              <el-option :value="1" label="🌨 冬季 (1-3月)" />
              <el-option :value="2" label="🌸 春季 (4-6月)" />
              <el-option :value="3" label="☀ 夏季 (7-9月)" />
              <el-option :value="4" label="🍂 秋季 (10-12月)" />
            </el-select>
          </el-form-item>
        </el-col>

        <!-- 评分范围 -->
        <el-col :xs="12" :sm="8" :md="4">
          <el-form-item label="评分范围">
            <el-slider
              v-model="scoreRange"
              range
              :min="0"
              :max="10"
              :step="0.5"
              :marks="{ 0: '0', 5: '5', 10: '10' }"
            />
          </el-form-item>
        </el-col>

        <!-- 热度筛选 -->
        <el-col :xs="12" :sm="8" :md="3">
          <el-form-item label="最低收藏人数">
            <el-select
              v-model="localFilters.popularity_from"
              placeholder="不限"
              clearable
              style="width: 100%"
            >
              <el-option :value="100" label="≥100" />
              <el-option :value="500" label="≥500" />
              <el-option :value="1000" label="≥1,000" />
              <el-option :value="5000" label="≥5,000" />
              <el-option :value="10000" label="≥10,000" />
            </el-select>
          </el-form-item>
        </el-col>

        <!-- 高级选项 -->
        <el-col :xs="12" :sm="8" :md="3">
          <el-form-item label="成人内容">
            <el-switch v-model="localFilters.nsfw" active-text="仅NSFW" />
          </el-form-item>
        </el-col>
        <el-col :xs="12" :sm="8" :md="3">
          <el-form-item label="系列作品">
            <el-switch v-model="localFilters.series" active-text="仅系列" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row justify="end" style="margin-top: 8px">
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="applyFilters">应用筛选</el-button>
      </el-row>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue', 'apply', 'reset'])

// 年份选项：从当前年份往回 30 年
const currentYear = new Date().getFullYear()
const yearOptions = Array.from({ length: 40 }, (_, i) => currentYear - i)

const localFilters = reactive({
  type: props.modelValue.type ?? undefined,
  search: props.modelValue.search ?? '',
  year: props.modelValue.year ?? undefined,
  season: props.modelValue.season ?? undefined,
  score_from: props.modelValue.score_from ?? undefined,
  score_to: props.modelValue.score_to ?? undefined,
  popularity_from: props.modelValue.popularity_from ?? undefined,
  nsfw: props.modelValue.nsfw ?? undefined,
  series: props.modelValue.series ?? undefined,
})

const scoreRange = ref([
  props.modelValue.score_from ?? 0,
  props.modelValue.score_to ?? 10,
])

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      Object.assign(localFilters, {
        type: val.type ?? undefined,
        search: val.search ?? '',
        year: val.year ?? undefined,
        season: val.season ?? undefined,
        score_from: val.score_from ?? undefined,
        score_to: val.score_to ?? undefined,
        popularity_from: val.popularity_from ?? undefined,
        nsfw: val.nsfw ?? undefined,
        series: val.series ?? undefined,
      })
    }
  },
  { deep: true }
)

// 当年份变化时，如果没有选择季度则不自动应用
watch(
  () => localFilters.year,
  (newYear) => {
    if (!newYear) {
      localFilters.season = undefined
    }
  }
)

function applyFilters() {
  const filters = {
    type: localFilters.type,
    search: localFilters.search || undefined,
    year: localFilters.year,
    season: localFilters.season,
    score_from: scoreRange.value[0] !== 0 ? scoreRange.value[0] : undefined,
    score_to: scoreRange.value[1] !== 10 ? scoreRange.value[1] : undefined,
    popularity_from: localFilters.popularity_from,
    nsfw: localFilters.nsfw,
    series: localFilters.series,
  }
  // 清理 undefined 值
  Object.keys(filters).forEach((k) => {
    if (filters[k] === undefined || filters[k] === '' || filters[k] === null)
      delete filters[k]
  })
  emit('update:modelValue', filters)
  emit('apply', filters)
}

function resetFilters() {
  localFilters.type = undefined
  localFilters.search = ''
  localFilters.year = undefined
  localFilters.season = undefined
  localFilters.nsfw = undefined
  localFilters.series = undefined
  localFilters.popularity_from = undefined
  scoreRange.value = [0, 10]
  emit('update:modelValue', {})
  emit('reset')
}
</script>

<style scoped>
.subject-filters {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px 4px;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.filters-header {
  margin-bottom: 12px;
}
.filters-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #303133;
}
</style>
