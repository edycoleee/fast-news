import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { AdminCommentsPage } from './AdminCommentsPage'
import { listComments, moderateComment } from '../api/commentsApi'

vi.mock('../api/commentsApi', () => ({
  listComments: vi.fn(),
  moderateComment: vi.fn(),
  deleteComment: vi.fn(),
}))

test('approves a comment through the moderation dialog', async () => {
  listComments.mockResolvedValue({
    items: [
      {
        id: 7,
        news_id: 1,
        author_name: 'Reader',
        content: 'Pending comment',
        status: 'pending',
        moderation_note: null,
        created_at: '2026-11-18T02:00:00Z',
      },
    ],
    total: 1,
    page: 1,
    page_size: 10,
  })
  moderateComment.mockResolvedValue({ id: 7, status: 'approved' })
  const queryClient = new QueryClient()

  render(
    <QueryClientProvider client={queryClient}>
      <AdminCommentsPage />
    </QueryClientProvider>,
  )

  fireEvent.click(await screen.findByTestId('comment-approve-7'))
  fireEvent.change(screen.getByTestId('comment-moderation-note'), {
    target: { value: 'Sesuai kebijakan' },
  })
  fireEvent.click(screen.getByTestId('comment-moderation-confirm'))

  await waitFor(() => expect(moderateComment).toHaveBeenCalled())
  expect(moderateComment.mock.calls[0][0]).toEqual({
    commentId: 7,
    status: 'approved',
    note: 'Sesuai kebijakan',
  })
})
