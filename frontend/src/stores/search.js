import { defineStore } from 'pinia'
import apiClient from '@/api/request'

export const useSearchStore = defineStore('search', {
  state: () => ({
    query: '',
    scope: 'subjects',
    results: {},
    totals: {},
    loading: false,
    error: null,
    page: 1,
    limit: 20,
  }),

  actions: {
    async search(params = {}) {
      this.loading = true
      this.error = null
      try {
        const merged = {
          q: this.query,
          scope: this.scope,
          page: this.page,
          limit: this.limit,
          ...params,
        }
        const data = await apiClient.get('/search', { params: merged })
        this.results = data.results || {}
        this.totals = data.totals || {}
        this.query = merged.q
        this.scope = merged.scope
      } catch (e) {
        this.error = e.message || '搜索失败'
        this.results = {}
      } finally {
        this.loading = false
      }
    },

    setQuery(q) {
      this.query = q
    },

    setScope(scope) {
      this.scope = scope
    },

    setPage(page) {
      this.page = page
    },

    clear() {
      this.query = ''
      this.results = {}
      this.totals = {}
      this.page = 1
    },
  },
})
