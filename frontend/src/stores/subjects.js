import { defineStore } from 'pinia'
import { getSubjects, getSubject } from '@/api/subjects'

export const useSubjectStore = defineStore('subjects', {
  state: () => ({
    items: [],
    total: 0,
    loading: false,
    error: null,
    // 筛选参数
    filters: {
      type: undefined,
      search: '',
      date_from: undefined,
      date_to: undefined,
      score_from: undefined,
      score_to: undefined,
      nsfw: undefined,
      series: undefined,
    },
    // 分页
    page: 1,
    limit: 20,
    sort: 'score',
    order: 'desc',
    // 视图模式
    viewMode: 'grid',
    // 详情
    currentDetail: null,
    detailLoading: false,
  }),

  getters: {
    hasMore(state) {
      return state.page * state.limit < state.total
    },
  },

  actions: {
    async fetch(params = {}) {
      this.loading = true
      this.error = null
      try {
        const merged = {
          page: this.page,
          limit: this.limit,
          sort: this.sort,
          order: this.order,
          ...this.filters,
          ...params,
        }
        // 清理 undefined 值
        Object.keys(merged).forEach((k) => {
          if (merged[k] === undefined || merged[k] === '') delete merged[k]
        })
        const data = await getSubjects(merged)
        this.items = data.items
        this.total = data.total
        if (params.page !== undefined) this.page = params.page
      } catch (e) {
        this.error = e.message || '获取条目列表失败'
        this.items = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },

    async fetchById(bangumiId) {
      this.detailLoading = true
      try {
        this.currentDetail = await getSubject(bangumiId)
      } catch (e) {
        this.currentDetail = null
        throw e
      } finally {
        this.detailLoading = false
      }
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.page = 1
    },

    setPage(page) {
      this.page = page
    },

    setSort(sort, order = 'desc') {
      this.sort = sort
      this.order = order
      this.page = 1
    },

    setViewMode(mode) {
      this.viewMode = mode
    },
  },
})
