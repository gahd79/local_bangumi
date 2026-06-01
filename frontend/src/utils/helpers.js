// 工具函数（后续阶段扩展）

/**
 * 条目类型映射
 */
export const TYPE_MAP = {
  1: '漫画',
  2: '动画',
  3: '音乐',
  4: '游戏',
  6: '三次元',
}

/**
 * 观看状态映射
 */
export const STATUS_MAP = {
  1: '想看',
  2: '在看',
  3: '看过',
  4: '搁置',
  5: '抛弃',
}

/**
 * 根据类型编号获取中文名称
 */
export function getTypeName(type) {
  return TYPE_MAP[type] || '未知'
}

/**
 * 根据状态编号获取中文名称
 */
export function getStatusName(status) {
  return STATUS_MAP[status] || '未知'
}
