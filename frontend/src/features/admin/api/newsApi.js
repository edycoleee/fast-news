import { apiClient, buildCsrfHeaders } from '../../../shared/api/client'

export async function listNews({ page = 1, pageSize = 10, search = '', statusFilter = '' } = {}) {
  const response = await apiClient.get('/api/news/query', {
    params: {
      page,
      page_size: pageSize,
      search: search || undefined,
      status_filter: statusFilter || undefined,
    },
  })
  return response.data
}

export async function createNews(payload) {
  const response = await apiClient.post('/api/news', payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function updateNews(newsId, payload) {
  const response = await apiClient.put(`/api/news/${newsId}`, payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function deleteNews(newsId) {
  const response = await apiClient.delete(`/api/news/${newsId}`, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}
