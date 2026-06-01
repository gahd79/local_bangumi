import apiClient from './request'

export function search(params) {
  return apiClient.get('/search', { params })
}
