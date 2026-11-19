import { apiClient, buildCsrfHeaders, getCsrfTokenFromCookie } from '../../../shared/api/client'

export async function login(payload) {
  const response = await apiClient.post('/api/auth/login', payload)
  return response.data
}

export async function getMe() {
  const response = await apiClient.get('/api/auth/me')
  return response.data
}

export async function logout() {
  const csrfToken = getCsrfTokenFromCookie()
  const response = await apiClient.post(
    '/api/auth/logout',
    {},
    csrfToken ? { headers: { 'X-CSRF-Token': csrfToken } } : undefined,
  )
  return response.data
}

export async function listMySessions() {
  const response = await apiClient.get('/api/auth/sessions')
  return response.data
}

export async function listAllSessions() {
  const response = await apiClient.get('/api/auth/sessions/all')
  return response.data
}

export async function revokeSession(sessionId) {
  const response = await apiClient.delete(`/api/auth/sessions/${sessionId}`, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function revokeOtherSessions() {
  const response = await apiClient.delete('/api/auth/sessions', {
    headers: buildCsrfHeaders(),
  })
  return response.data
}
