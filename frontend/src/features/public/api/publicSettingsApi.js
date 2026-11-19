import { apiClient } from '../../../shared/api/client'

export async function getPublicSettings() {
  const response = await apiClient.get('/api/settings/public')
  return response.data
}
