import { apiClient, buildCsrfHeaders } from '../../../shared/api/client'

export async function listComments({ page = 1, pageSize = 10, status = '' } = {}) {
  const response = await apiClient.get('/api/comments/query', {
    params: {
      page,
      page_size: pageSize,
      status_filter: status || undefined,
    },
  })
  return response.data
}

export async function moderateComment({ commentId, status, note }) {
  const response = await apiClient.post(
    `/api/comments/${commentId}/moderate`,
    { status, note: note || null },
    { headers: buildCsrfHeaders() },
  )
  return response.data
}

export async function deleteComment(commentId) {
  const response = await apiClient.delete(`/api/comments/${commentId}`, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}
