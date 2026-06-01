<template>
  <div class="character-grid">
    <div class="section-header">
      <h4>角色列表（{{ characters.length }}）</h4>
    </div>

    <el-empty v-if="!characters.length" description="暂无角色信息" :image-size="40" />

    <el-row :gutter="12">
      <el-col
        v-for="char in characters"
        :key="char.character_id"
        :xs="12"
        :sm="8"
        :md="6"
        :lg="4"
        style="margin-bottom: 12px"
      >
        <el-card shadow="hover" class="char-card" :body-style="{ padding: '10px' }">
          <div class="char-name">{{ char.character_name }}</div>
          <div class="char-meta">
            <StatusBadge type="role" :value="char.role" size="small" />
            <span class="char-type-tag" v-if="char.type > 0">
              {{ ['', '主角', '配角', '客串'][char.type] || '' }}
            </span>
          </div>
          <div class="char-cv" v-if="char.cv_persons && char.cv_persons.length">
            <span class="cv-label">CV:</span>
            <span
              v-for="(cv, i) in char.cv_persons.slice(0, 3)"
              :key="cv.bangumi_id"
              class="cv-name"
            >
              {{ cv.name }}<template v-if="i < Math.min(char.cv_persons.length, 3) - 1">, </template>
            </span>
            <span v-if="char.cv_persons.length > 3" class="cv-more">
              +{{ char.cv_persons.length - 3 }}
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import StatusBadge from './StatusBadge.vue'

defineProps({
  characters: { type: Array, default: () => [] },
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
.char-card {
  cursor: default;
}
.char-name {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 6px;
}
.char-meta {
  display: flex;
  gap: 4px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}
.char-type-tag {
  font-size: 0.75rem;
  color: #909399;
}
.char-cv {
  font-size: 0.8rem;
  color: #606266;
  line-height: 1.4;
}
.cv-label {
  color: #909399;
  margin-right: 4px;
}
.cv-name {
  color: #409eff;
}
.cv-more {
  color: #909399;
}
</style>
