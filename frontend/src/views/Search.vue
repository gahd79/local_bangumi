<template>
  <div class="search-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="query"
        size="large"
        placeholder="搜索条目 / 人物 / 角色..."
        clearable
        @keyup.enter="doSearch"
        @clear="doSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="scope" style="width: 120px; margin-left: 8px" @change="doSearch">
        <el-option label="条目" value="subjects" />
        <el-option label="人物" value="persons" />
        <el-option label="角色" value="characters" />
        <el-option label="全部" value="all" />
      </el-select>
      <el-button type="primary" size="large" @click="doSearch" :loading="loading" style="margin-left: 8px">
        搜索
      </el-button>
    </div>

    <!-- 加载 -->
    <div v-if="loading" style="text-align: center; padding: 40px">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 结果 -->
    <template v-if="!loading && hasSearched">
      <!-- 范围 Tab -->
      <el-tabs v-model="activeTab" @tab-change="onTabChange" v-if="scope === 'all'">
        <el-tab-pane label="条目" name="subjects" />
        <el-tab-pane label="人物" name="persons" />
        <el-tab-pane label="角色" name="characters" />
      </el-tabs>

      <!-- 条目结果 -->
      <template v-if="showTab('subjects')">
        <div class="result-header">
          <span>找到 {{ totals.subjects || 0 }} 个条目</span>
        </div>
        <el-empty v-if="!results.subjects?.length" description="未找到匹配的条目" :image-size="60" />
        <SubjectCard
          v-for="s in results.subjects"
          :key="s.bangumi_id"
          :subject="s"
          view-mode="list"
        />
        <el-pagination
          v-if="(totals.subjects || 0) > limit"
          v-model:current-page="page"
          :page-size="limit"
          :total="totals.subjects"
          layout="prev, pager, next"
          @current-change="doSearch"
          style="justify-content: center; margin-top: 16px"
        />
      </template>

      <!-- 人物结果 -->
      <template v-if="showTab('persons')">
        <div class="result-header">
          <span>找到 {{ totals.persons || 0 }} 个人物</span>
        </div>
        <el-empty v-if="!results.persons?.length" description="未找到匹配的人物" :image-size="60" />
        <el-card
          v-for="p in results.persons"
          :key="p.bangumi_id"
          class="result-card"
          shadow="hover"
          :body-style="{ padding: '10px 16px' }"
        >
          <div class="person-row">
            <StatusBadge type="person_type" :value="p.type" size="small" />
            <span class="person-name" v-html="highlight(p.name)"></span>
          </div>
        </el-card>
      </template>

      <!-- 角色结果 -->
      <template v-if="showTab('characters')">
        <div class="result-header">
          <span>找到 {{ totals.characters || 0 }} 个角色</span>
        </div>
        <el-empty v-if="!results.characters?.length" description="未找到匹配的角色" :image-size="60" />
        <el-card
          v-for="c in results.characters"
          :key="c.bangumi_id"
          class="result-card"
          shadow="hover"
          :body-style="{ padding: '10px 16px' }"
        >
          <div class="person-row">
            <StatusBadge type="role" :value="c.role" size="small" />
            <span class="person-name" v-html="highlight(c.name)"></span>
          </div>
        </el-card>
      </template>
    </template>

    <!-- 初始状态 -->
    <el-empty
      v-if="!loading && !hasSearched"
      description="输入关键词开始搜索"
      :image-size="100"
      style="margin-top: 60px"
    />
  </div>
</template>

<script setup>
defineOptions({ name: 'Search' })

import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import apiClient from '@/api/request'
import SubjectCard from '@/components/SubjectCard.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const route = useRoute()
const router = useRouter()

const query = ref('')
const scope = ref('subjects')
const results = ref({})
const totals = ref({})
const loading = ref(false)
const hasSearched = ref(false)
const page = ref(1)
const limit = 20
const activeTab = ref('subjects')

onMounted(() => {
  if (route.query.q) {
    query.value = route.query.q
    scope.value = route.query.scope || 'subjects'
    doSearch()
  }
})

function showTab(key) {
  if (scope.value !== 'all') return scope.value === key
  return activeTab.value === key
}

function onTabChange() {
  page.value = 1
  doSearch()
}

async function doSearch() {
  if (!query.value.trim()) {
    results.value = {}
    totals.value = {}
    hasSearched.value = false
    return
  }
  loading.value = true
  hasSearched.value = true
  try {
    const searchScope = scope.value === 'all' ? activeTab.value : scope.value
    const data = await apiClient.get('/search', {
      params: {
        q: query.value.trim(),
        scope: searchScope,
        page: page.value,
        limit,
      },
    })
    results.value = data.results || {}
    totals.value = data.totals || {}
  } catch (e) {
    ElMessage.warning('搜索失败，请重试')
  } finally {
    loading.value = false
  }
}

function highlight(text) {
  if (!query.value || !text) return text
  const escaped = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const re = new RegExp(`(${escaped})`, 'gi')
  return text.replace(re, '<mark>$1</mark>')
}
</script>

<style scoped>
.search-page {
  max-width: 1000px;
  margin: 0 auto;
}

.search-bar {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.result-header {
  margin-bottom: 12px;
  color: #909399;
  font-size: 0.9rem;
}

.result-card {
  margin-bottom: 4px;
  cursor: default;
}

.person-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.person-name {
  font-weight: 500;
}
</style>
