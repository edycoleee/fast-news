import { apiClient } from '../../../shared/api/client'

export async function getMyPermissions() {
  const response = await apiClient.get('/api/rbac/me/permissions')
  return response.data
}
