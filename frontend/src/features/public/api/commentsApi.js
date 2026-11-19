import { apiClient } from '../../../shared/api/client'

export async function listPublicComments(slug) {
  const response = await apiClient.get(`/api/public/news/${slug}/comments`)
  return response.data
}

export async function submitPublicComment({ slug, payload }) {
  const response = await apiClient.post(`/api/public/news/${slug}/comments`, payload)
  return response.data
}
