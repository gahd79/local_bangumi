import apiClient from './request'

export function getCharacters(params) {
  return apiClient.get('/characters', { params })
}

export function getCharacter(bangumiId) {
  return apiClient.get(`/characters/${bangumiId}`)
}
