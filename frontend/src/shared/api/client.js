import axios from 'axios'

function resolveApiBaseUrl() {
  const envApiUrl = import.meta.env.VITE_API_URL?.trim()
  const browserHostApiUrl = `${window.location.protocol}//${window.location.hostname}:8000`
  const browserHost = window.location.hostname
  const browserIsLocalHost = browserHost === 'localhost' || browserHost === '127.0.0.1'

  if (!envApiUrl) {
    return browserHostApiUrl
  }

  try {
    const parsedUrl = new URL(envApiUrl)
    const envIsLocalHost = parsedUrl.hostname === 'localhost' || parsedUrl.hostname === '127.0.0.1'

    if (!browserIsLocalHost && envIsLocalHost) {
      return browserHostApiUrl
    }
  } catch {
    return envApiUrl
  }

  return envApiUrl
}

export const API_BASE_URL = resolveApiBaseUrl()

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})

export function getCsrfTokenFromCookie(cookieName = 'newshub_csrf') {
  const cookies = document.cookie.split(';').map((item) => item.trim())
  const tokenCookie = cookies.find((entry) => entry.startsWith(`${cookieName}=`))
  if (!tokenCookie) {
    return null
  }

  const [, rawValue] = tokenCookie.split('=')
  return decodeURIComponent(rawValue)
}

export function buildCsrfHeaders(headerName = 'X-CSRF-Token') {
  const csrfToken = getCsrfTokenFromCookie()
  return csrfToken ? { [headerName]: csrfToken } : {}
}
