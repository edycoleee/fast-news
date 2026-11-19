import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import { AdminAuditPage } from './AdminAuditPage'
import { listAuditLogs } from '../api/auditApi'

vi.mock('../api/auditApi', () => ({
  listAuditLogs: vi.fn(),
  exportAuditLogs: vi.fn(),
}))

test('renders security audit events', async () => {
  listAuditLogs.mockResolvedValue({
    items: [
      {
        id: 1,
        user_id: 1,
        action: 'auth.login.success',
        entity_type: 'auth',
        entity_id: 1,
        details: { ip_address: '127.0.0.1' },
        created_at: '2026-11-18T04:10:00Z',
      },
    ],
    total: 1,
    page: 1,
    page_size: 25,
  })
  const queryClient = new QueryClient()

  render(
    <QueryClientProvider client={queryClient}>
      <AdminAuditPage />
    </QueryClientProvider>,
  )

  expect(await screen.findByText('auth.login.success')).toBeInTheDocument()
  expect(screen.getByText('Actor user #1')).toBeInTheDocument()
})
