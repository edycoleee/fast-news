import { apiClient, buildCsrfHeaders } from '../../../shared/api/client'

export async function listFiles({ page = 1, pageSize = 10, search = '' } = {}) {
  const response = await apiClient.get('/api/files/query', {
    params: {
      page,
      page_size: pageSize,
      search: search || undefined,
    },
  })
  return response.data
}

export async function uploadFile(file) {
  const formData = new FormData()
  formData.append('upload_file', file)

  const response = await apiClient.post('/api/files/upload', formData, {
    headers: {
      ...buildCsrfHeaders(),
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export async function deleteFile(fileId) {
  const response = await apiClient.delete(`/api/files/${fileId}`, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}
