import { apiClient, getCsrfTokenFromCookie } from '../../../shared/api/client'

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
