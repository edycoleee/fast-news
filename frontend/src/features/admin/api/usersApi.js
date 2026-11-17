import { apiClient, buildCsrfHeaders } from '../../../shared/api/client'

export async function listUsers({ page = 1, pageSize = 10, search = '' } = {}) {
  const response = await apiClient.get('/api/users/query', {
    params: {
      page,
      page_size: pageSize,
      search: search || undefined,
    },
  })
  return response.data
}

export async function createUser(payload) {
  const response = await apiClient.post('/api/users', payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function updateUser(userId, payload) {
  const response = await apiClient.put(`/api/users/${userId}`, payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function deleteUser(userId) {
  const response = await apiClient.delete(`/api/users/${userId}`, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}
