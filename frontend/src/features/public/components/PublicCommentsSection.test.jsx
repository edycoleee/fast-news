import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import { PublicCommentsSection } from './PublicCommentsSection'
import { listPublicComments, submitPublicComment } from '../api/commentsApi'
import { getPublicSettings } from '../api/publicSettingsApi'

vi.mock('../api/commentsApi', () => ({
  listPublicComments: vi.fn(),
  submitPublicComment: vi.fn(),
}))
vi.mock('../api/publicSettingsApi', () => ({
  getPublicSettings: vi.fn(),
}))

function renderSection() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <PublicCommentsSection slug="published-news" />
    </QueryClientProvider>,
  )
}

test('shows approved comments and submits a pending comment', async () => {
  getPublicSettings.mockResolvedValue({
    comment_max_length: 2000,
    upload_max_size_bytes: 5242880,
    signature_max_size_bytes: 524288,
  })
  listPublicComments.mockResolvedValue([
    {
      id: 1,
      author_name: 'Approved Reader',
      content: 'Komentar tersetujui',
      parent_id: null,
      created_at: '2026-11-18T02:00:00Z',
    },
  ])
  submitPublicComment.mockResolvedValue({
    id: 2,
    message: 'Komentar diterima dan menunggu moderasi.',
  })
  renderSection()

  expect(await screen.findByText('Komentar tersetujui')).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Nama'), {
    target: { value: 'New Reader' },
  })
  fireEvent.change(screen.getByLabelText('Komentar'), {
    target: { value: 'Komentar pengujian frontend' },
  })
  fireEvent.click(screen.getByTestId('comment-submit-button'))

  expect(await screen.findByText('Komentar diterima dan menunggu moderasi.')).toBeInTheDocument()
  expect(submitPublicComment.mock.calls[0][0]).toEqual({
    slug: 'published-news',
    payload: {
      author_name: 'New Reader',
      content: 'Komentar pengujian frontend',
      parent_id: null,
    },
  })
})
