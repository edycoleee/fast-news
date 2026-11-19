import { apiClient, buildCsrfHeaders } from '../../../shared/api/client'

export async function listSettings() {
  const response = await apiClient.get('/api/settings')
  return response.data
}

export async function updateSettings(settings) {
  const response = await apiClient.put(
    '/api/settings',
    { settings },
    { headers: buildCsrfHeaders() },
  )
  return response.data
}

export async function runRetentionCleanup({ dry_run, batch_size = 1000 }) {
  const response = await apiClient.post(
    '/api/settings/retention/cleanup',
    { dry_run, batch_size },
    { headers: buildCsrfHeaders() },
  )
  return response.data
}
