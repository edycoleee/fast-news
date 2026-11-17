import { apiClient, buildCsrfHeaders } from '../../../shared/api/client'

export async function listCategories({ page = 1, pageSize = 10, search = '' } = {}) {
  const response = await apiClient.get('/api/categories/query', {
    params: {
      page,
      page_size: pageSize,
      search: search || undefined,
    },
  })
  return response.data
}

export async function createCategory(payload) {
  const response = await apiClient.post('/api/categories', payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function updateCategory(categoryId, payload) {
  const response = await apiClient.put(`/api/categories/${categoryId}`, payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function deleteCategory(categoryId) {
  const response = await apiClient.delete(`/api/categories/${categoryId}`, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}
