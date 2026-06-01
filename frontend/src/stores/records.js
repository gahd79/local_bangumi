import { defineStore } from 'pinia'
import {
  getRecords,
  createRecord,
  updateRecord,
  deleteRecord,
} from '@/api/records'
import apiClient from '@/api/request'

export const useRecordStore = defineStore('records', {
  state: () => ({
    records: [],
    loading: false,
    error: null,
    stats: null,
    statsLoading: false,
    activeStatus: undefined,
  }),

  actions: {
    async fetch(params = {}) {
      this.loading = true
      this.error = null
      try {
        const merged = {}
        if (this.activeStatus !== undefined) merged.status = this.activeStatus
        Object.assign(merged, params)
        const data = await getRecords(merged)
        this.records = Array.isArray(data) ? data : data.items || []
      } catch (e) {
        this.error = e.message || '获取记录失败'
        this.records = []
      } finally {
        this.loading = false
      }
    },

    async create(data) {
      const record = await createRecord(data)
      this.records.unshift(record)
      await this.fetchStats()
      return record
    },

    async update(id, data) {
      const record = await updateRecord(id, data)
      const idx = this.records.findIndex((r) => r.id === id)
      if (idx >= 0) this.records[idx] = record
      await this.fetchStats()
      return record
    },

    async remove(id) {
      await deleteRecord(id)
      this.records = this.records.filter((r) => r.id !== id)
      await this.fetchStats()
    },

    async fetchStats() {
      this.statsLoading = true
      try {
        this.stats = await apiClient.get('/records/stats')
      } catch (e) {
        this.stats = null
      } finally {
        this.statsLoading = false
      }
    },

    setActiveStatus(status) {
      this.activeStatus = status
    },
  },
})
