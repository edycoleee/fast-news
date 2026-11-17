import { apiClient, buildCsrfHeaders } from '../../../shared/api/client'

export async function listRoles({ page = 1, pageSize = 20, search = '' } = {}) {
  const response = await apiClient.get('/api/rbac/roles/query', {
    params: {
      page,
      page_size: pageSize,
      search: search || undefined,
    },
  })
  return response.data
}

export async function createRole(payload) {
  const response = await apiClient.post('/api/rbac/roles', payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function deleteRole(roleId) {
  const response = await apiClient.delete(`/api/rbac/roles/${roleId}`, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function listPermissions({ page = 1, pageSize = 20, search = '' } = {}) {
  const response = await apiClient.get('/api/rbac/permissions/query', {
    params: {
      page,
      page_size: pageSize,
      search: search || undefined,
    },
  })
  return response.data
}

export async function createPermission(payload) {
  const response = await apiClient.post('/api/rbac/permissions', payload, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function deletePermission(permissionId) {
  const response = await apiClient.delete(`/api/rbac/permissions/${permissionId}`, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function assignPermissionToRole(roleId, permissionId) {
  const response = await apiClient.post(`/api/rbac/roles/${roleId}/permissions/${permissionId}`, {}, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function assignRoleToUser(userId, roleId) {
  const response = await apiClient.post(`/api/rbac/users/${userId}/roles/${roleId}`, {}, {
    headers: buildCsrfHeaders(),
  })
  return response.data
}

export async function getUserRoles(userId) {
  const response = await apiClient.get(`/api/rbac/users/${userId}/roles`)
  return response.data
}

export async function getRolePermissions(roleId) {
  const response = await apiClient.get(`/api/rbac/roles/${roleId}/permissions`)
  return response.data
}
