import { apiClient, buildCsrfHeaders } from '../../../shared/api/client'

export async function listSignatures({ page = 1, pageSize = 10, status = '' } = {}) {
  const response = await apiClient.get('/api/signatures/query', {
    params: {
      page,
      page_size: pageSize,
      status_filter: status || undefined,
    },
  })
  return response.data
}

export async function createSignature(payload) {
  const response = await apiClient.post('/api/signatures', payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function revokeSignature({ signatureId, reason }) {
  const response = await apiClient.post(
    `/api/signatures/${signatureId}/revoke`,
    { reason },
    { headers: buildCsrfHeaders() },
  )
  return response.data
}
