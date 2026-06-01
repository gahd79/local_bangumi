<template>
  <div class="infobox-display" v-if="infobox && infobox.fields && Object.keys(infobox.fields).length">
    <div class="infobox-type" v-if="infobox.type">
      <el-tag type="info" size="small">{{ infobox.type }}</el-tag>
    </div>
    <el-descriptions :column="2" border size="small">
      <el-descriptions-item
        v-for="(value, key) in infobox.fields"
        :key="key"
        :label="String(key)"
      >
        <!-- 数组类型：标签列表 -->
        <template v-if="Array.isArray(value)">
          <el-tag v-for="(item, idx) in value" :key="idx" size="small" class="infobox-tag">
            {{ item }}
          </el-tag>
        </template>
        <!-- 对象类型：尝试提取有意义的展示 -->
        <template v-else-if="typeof value === 'object' && value !== null">
          <!-- 情况1: {"k": "", "v": "叛逆的鲁路修R2"} 形式的别名 → 只展示 v 的值 -->
          <template v-if="isKVObject(value)">
            <span>{{ extractV(value) }}</span>
          </template>
          <!-- 情况2: 嵌套对象的多个 k:v 对 -->
          <template v-else>
            <template v-for="(v, k) in value" :key="k">
              <span class="infobox-nested-key">{{ k }}:</span>
              <span class="infobox-nested-value">{{ formatValue(v) }}</span>
            </template>
          </template>
        </template>
        <!-- 普通值 -->
        <template v-else>
          {{ formatValue(value) }}
        </template>
      </el-descriptions-item>
    </el-descriptions>
  </div>
  <el-empty v-else description="暂无 Infobox 数据" :image-size="60" />
</template>

<script setup>
defineProps({
  infobox: { type: Object, default: null },
})

/** 判断是否为 {"k": "...", "v": "..."} 形式的 kv 对象 */
function isKVObject(obj) {
  const keys = Object.keys(obj)
  return keys.length === 2 && 'k' in obj && 'v' in obj
}

/** 从 kv 对象中提取 v 值 */
function extractV(obj) {
  return obj.v || obj.k || ''
}

/** 递归格式化值 */
function formatValue(v) {
  if (v === null || v === undefined) return ''
  if (typeof v === 'object') {
    if (Array.isArray(v)) return v.map(formatValue).join(', ')
    if (isKVObject(v)) return extractV(v)
    return JSON.stringify(v)
  }
  return String(v)
}
</script>

<style scoped>
.infobox-display {
  margin: 8px 0;
}
.infobox-type {
  margin-bottom: 8px;
}
.infobox-tag {
  margin-right: 4px;
  margin-bottom: 2px;
}
.infobox-nested-key {
  font-weight: 600;
  margin-right: 4px;
  color: #606266;
}
.infobox-nested-value {
  margin-right: 12px;
}
</style>
