import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import { SessionManager } from './SessionManager'
import { listAllSessions } from '../../auth/api/authApi'

vi.mock('../../auth/api/authApi', () => ({
  listAllSessions: vi.fn(),
  listMySessions: vi.fn(),
  revokeOtherSessions: vi.fn(),
  revokeSession: vi.fn(),
}))

test('renders the current active session without exposing tokens', async () => {
  listAllSessions.mockResolvedValue({
    items: [
      {
        id: 4,
        user_id: 1,
        username: 'admin',
        user_agent: 'Browser test',
        ip_address: '127.0.0.1',
        created_at: '2026-11-18T04:00:00Z',
        last_seen_at: '2026-11-18T04:10:00Z',
        expires_at: '2026-11-18T12:00:00Z',
        is_current: true,
      },
    ],
  })
  const queryClient = new QueryClient()

  render(
    <QueryClientProvider client={queryClient}>
      <SessionManager />
    </QueryClientProvider>,
  )

  expect(await screen.findByText('Session #4')).toBeInTheDocument()
  expect(screen.getByText('Current')).toBeInTheDocument()
  expect(screen.queryByText(/session_token/i)).not.toBeInTheDocument()
})
