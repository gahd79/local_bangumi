import apiClient from './request'

export function getSyncStatus() {
  return apiClient.get('/sync/status')
}

export function getLatestVersion() {
  return apiClient.get('/sync/latest-version')
}

export function triggerLocalSync(dumpDir) {
  return apiClient.post('/sync/trigger/local', null, {
    params: { dump_dir: dumpDir },
  })
}

export function triggerGithubSync() {
  return apiClient.post('/sync/trigger/github')
}
