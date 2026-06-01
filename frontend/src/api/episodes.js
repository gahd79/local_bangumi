import apiClient from './request'

export function getEpisodes(params) {
  return apiClient.get('/episodes', { params })
}

export function getEpisode(bangumiId) {
  return apiClient.get(`/episodes/${bangumiId}`)
}
