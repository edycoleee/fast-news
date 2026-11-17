import { apiClient } from '../../../shared/api/client'

export async function listPublicNews({ search = '' } = {}) {
  const response = await apiClient.get('/api/public/news', {
    params: {
      search: search || undefined,
    },
  })
  return response.data
}

export async function getPublicNewsDetail(slug) {
  const response = await apiClient.get(`/api/public/news/${slug}`)
  return response.data
}
