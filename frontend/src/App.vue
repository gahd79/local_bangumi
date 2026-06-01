<template>
  <el-container style="min-height: 100vh">
    <!-- 移动端汉堡菜单按钮 -->
    <div class="mobile-toggle" v-if="isMobile" @click="sidebarCollapsed = !sidebarCollapsed">
      <el-icon :size="24"><Expand v-if="sidebarCollapsed" /><Fold v-else /></el-icon>
    </div>

    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="app-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header" v-show="!sidebarCollapsed">
        <span class="sidebar-logo">LB</span>
        <span class="sidebar-title">local_bangumi</span>
      </div>

      <el-menu
        router
        :default-active="$route.path"
        :collapse="sidebarCollapsed"
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/subjects">
          <el-icon><Collection /></el-icon>
          <span>条目浏览</span>
        </el-menu-item>
        <el-menu-item index="/search">
          <el-icon><Search /></el-icon>
          <span>搜索</span>
        </el-menu-item>
        <el-menu-item index="/records">
          <el-icon><Notebook /></el-icon>
          <span>我的记录</span>
        </el-menu-item>
      </el-menu>

      <!-- 同步状态 -->
      <div class="sidebar-footer" v-if="!sidebarCollapsed && syncInfo">
        <el-divider />
        <div class="sync-info">
          <span class="sync-label">数据库</span>
          <span class="sync-value">{{ syncInfo.table_counts?.subjects?.toLocaleString() || '-' }} 条目</span>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <keep-alive :include="cachedViews">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiClient from '@/api/request'

const router = useRouter()
const route = useRoute()

const sidebarCollapsed = ref(false)
const windowWidth = ref(window.innerWidth)
const syncInfo = ref(null)

// KeepAlive 缓存：列表页组件返回时不重新加载
const cachedViews = ['Home', 'SubjectList', 'Search', 'MyRecords']

const isMobile = computed(() => windowWidth.value < 768)
const sidebarWidth = computed(() => {
  if (isMobile.value && sidebarCollapsed.value) return '0px'
  if (sidebarCollapsed.value) return '64px'
  if (isMobile.value) return '200px'
  return '200px'
})

function onResize() {
  windowWidth.value = window.innerWidth
  if (windowWidth.value < 768) {
    sidebarCollapsed.value = true
  }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  window.addEventListener('keydown', onKeydown)
  onResize()
  // 获取同步状态
  apiClient.get('/sync/status').then((json) => {
    syncInfo.value = json
  }).catch(() => {})
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('keydown', onKeydown)
})

// 全局键盘快捷键
function onKeydown(e) {
  // 忽略输入框内的按键
  const tag = e.target.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.target.isContentEditable) {
    return
  }
  // / — 跳转搜索页并聚焦
  if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
    e.preventDefault()
    if (route.path !== '/search') {
      router.push('/search')
    }
    // 聚焦搜索框（等 nextTick）
    setTimeout(() => {
      const input = document.querySelector('.search-page .search-bar input')
      if (input) input.focus()
    }, 200)
  }
}
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, sans-serif;
}

/* 全局圆角 — Element Plus 组件 */
.el-card {
  border-radius: 12px !important;
}
.el-button {
  border-radius: 8px !important;
}
.el-input .el-input__wrapper {
  border-radius: 8px !important;
}
.el-select .el-select__wrapper {
  border-radius: 8px !important;
}
.el-dialog {
  border-radius: 14px !important;
}
.el-tag {
  border-radius: 6px !important;
}
.el-pagination .el-pager li {
  border-radius: 6px !important;
}
.el-table {
  border-radius: 10px;
}
.el-tabs__nav-wrap {
  border-radius: 8px;
}
</style>

<style scoped>
.app-sidebar {
  background: #fff;
  border-right: 1px solid #ebeef5;
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.app-sidebar.collapsed {
  width: 64px !important;
}

.sidebar-header {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sidebar-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #409eff;
  color: #fff;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.85rem;
}
.sidebar-title {
  font-weight: 600;
  font-size: 1rem;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.sidebar-footer {
  padding: 0 12px 12px;
}
.sync-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
}
.sync-label {
  color: #909399;
}
.sync-value {
  color: #606266;
}

.mobile-toggle {
  position: fixed;
  top: 8px;
  left: 8px;
  z-index: 1000;
  background: #fff;
  border-radius: 6px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.app-main {
  background: #f5f7fa;
}
</style>
