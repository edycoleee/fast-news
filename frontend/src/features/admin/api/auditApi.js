import { apiClient } from '../../../shared/api/client'

export async function listAuditLogs({
  page = 1,
  pageSize = 25,
  action = '',
  userId = '',
  dateFrom = '',
  dateTo = '',
} = {}) {
  const response = await apiClient.get('/api/audit/logs', {
    params: {
      page,
      page_size: pageSize,
      action: action || undefined,
      user_id: userId || undefined,
      date_from: dateFrom ? `${dateFrom}T00:00:00` : undefined,
      date_to: dateTo ? `${dateTo}T23:59:59` : undefined,
    },
  })
  return response.data
}

export async function exportAuditLogs(filters) {
  const response = await apiClient.get('/api/audit/logs/export', {
    params: {
      action: filters.action || undefined,
      user_id: filters.userId || undefined,
      date_from: filters.dateFrom ? `${filters.dateFrom}T00:00:00` : undefined,
      date_to: filters.dateTo ? `${filters.dateTo}T23:59:59` : undefined,
    },
    responseType: 'blob',
  })
  return response.data
}
