import apiClient from './request'

export function getSubjects(params) {
  return apiClient.get('/subjects', { params })
}

export function getSubject(bangumiId) {
  return apiClient.get(`/subjects/${bangumiId}`)
}
