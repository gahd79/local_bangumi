import apiClient from './request'

export function getPersons(params) {
  return apiClient.get('/persons', { params })
}

export function getPerson(bangumiId) {
  return apiClient.get(`/persons/${bangumiId}`)
}
