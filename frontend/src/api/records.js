import apiClient from './request'

export function getRecords(params) {
  return apiClient.get('/records', { params })
}

export function createRecord(data) {
  return apiClient.post('/records', data)
}

export function updateRecord(id, data) {
  return apiClient.put(`/records/${id}`, data)
}

export function deleteRecord(id) {
  return apiClient.delete(`/records/${id}`)
}

export function getWatching() {
  return apiClient.get('/records/watching')
}

export function importRecords(data) {
  return apiClient.post('/records/import', data)
}
