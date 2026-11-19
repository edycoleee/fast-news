import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { deleteComment, listComments, moderateComment } from '../api/commentsApi'
import { formatLocalDateTime } from '../../../shared/utils/dateTime'

const STATUS_STYLES = {
  pending: 'bg-warning/15 text-amber-700',
  approved: 'bg-success/15 text-success',
  rejected: 'bg-danger/10 text-danger',
}

export function AdminCommentsPage() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('pending')
  const [page, setPage] = useState(1)
  const [moderationTarget, setModerationTarget] = useState(null)
  const [moderationNote, setModerationNote] = useState('')
  const pageSize = 10

  const commentsQuery = useQuery({
    queryKey: ['admin-comments', { page, pageSize, statusFilter }],
    queryFn: () => listComments({ page, pageSize, status: statusFilter }),
    retry: false,
  })

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ['admin-comments'] })
  }
  const moderateMutation = useMutation({
    mutationFn: moderateComment,
    onSuccess: async () => {
      setModerationTarget(null)
      setModerationNote('')
      await refresh()
    },
  })
  const deleteMutation = useMutation({
    mutationFn: deleteComment,
    onSuccess: refresh,
  })

  const openModeration = (commentId, status) => {
    setModerationNote('')
    setModerationTarget({ commentId, status })
  }

  const submitModeration = () => {
    if (!moderationTarget) {
      return
    }
    moderateMutation.mutate({
      commentId: moderationTarget.commentId,
      status: moderationTarget.status,
      note: moderationNote,
    })
  }

  const totalPages = commentsQuery.data
    ? Math.max(1, Math.ceil(commentsQuery.data.total / commentsQuery.data.page_size))
    : 1

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Moderasi Komentar</h2>
            <p className="text-sm text-slate-600">Tinjau komentar publik sebelum ditampilkan.</p>
          </div>
          <select
            data-testid="comment-status-filter"
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value)
              setPage(1)
            }}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="">Semua status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div className="p-5">
          {commentsQuery.isLoading && <p className="text-sm text-slate-500">Memuat komentar...</p>}
          {commentsQuery.isError && (
            <p className="text-sm text-danger">
              {commentsQuery.error?.response?.data?.detail || 'Gagal memuat komentar.'}
            </p>
          )}
          {commentsQuery.isSuccess && commentsQuery.data.items.length === 0 && (
            <p className="text-sm text-slate-500">Tidak ada komentar pada filter ini.</p>
          )}
          {commentsQuery.isSuccess && (
            <div className="space-y-3">
              {commentsQuery.data.items.map((comment) => (
                <article
                  key={comment.id}
                  data-testid={`admin-comment-${comment.id}`}
                  className="rounded-lg border border-slate-200 p-4"
                >
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-semibold text-slate-900">{comment.author_name}</p>
                        <span className={`rounded-full px-2 py-1 text-xs font-semibold ${STATUS_STYLES[comment.status]}`}>
                          {comment.status}
                        </span>
                        <span className="text-xs text-slate-500">News #{comment.news_id}</span>
                      </div>
                      <p className="mt-2 whitespace-pre-wrap text-sm text-slate-700">{comment.content}</p>
                      <p className="mt-2 text-xs text-slate-500">
                        Dikirim {formatLocalDateTime(comment.created_at)}
                      </p>
                      {comment.moderation_note && (
                        <p className="mt-2 text-xs text-slate-600">
                          Catatan moderasi: {comment.moderation_note}
                        </p>
                      )}
                      {comment.moderated_at && (
                        <p className="mt-1 text-xs text-slate-500">
                          Dimoderasi {formatLocalDateTime(comment.moderated_at)}
                          {comment.moderated_by_id ? ` oleh user #${comment.moderated_by_id}` : ''}
                        </p>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {comment.status === 'pending' && (
                        <>
                          <button
                            data-testid={`comment-approve-${comment.id}`}
                            type="button"
                            onClick={() => openModeration(comment.id, 'approved')}
                            disabled={moderateMutation.isPending}
                            className="rounded border border-success/30 px-3 py-2 text-xs font-semibold text-success disabled:opacity-50"
                          >
                            Approve
                          </button>
                          <button
                            data-testid={`comment-reject-${comment.id}`}
                            type="button"
                            onClick={() => openModeration(comment.id, 'rejected')}
                            disabled={moderateMutation.isPending}
                            className="rounded border border-danger/30 px-3 py-2 text-xs font-semibold text-danger disabled:opacity-50"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      <button
                        data-testid={`comment-delete-${comment.id}`}
                        type="button"
                        onClick={() => {
                          if (window.confirm('Hapus komentar ini?')) {
                            deleteMutation.mutate(comment.id)
                          }
                        }}
                        disabled={deleteMutation.isPending}
                        className="rounded border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 disabled:opacity-50"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
          {moderateMutation.isError && (
            <p className="mt-3 text-sm text-danger">
              {moderateMutation.error?.response?.data?.detail || 'Moderasi gagal.'}
            </p>
          )}
          {deleteMutation.isError && (
            <p className="mt-3 text-sm text-danger">
              {deleteMutation.error?.response?.data?.detail || 'Penghapusan gagal.'}
            </p>
          )}
          {commentsQuery.isSuccess && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Page {commentsQuery.data.page} of {totalPages} · Total {commentsQuery.data.total}
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  disabled={page <= 1}
                  className="rounded border border-slate-300 px-3 py-1 text-xs disabled:opacity-50"
                >
                  Prev
                </button>
                <button
                  type="button"
                  onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
                  disabled={page >= totalPages}
                  className="rounded border border-slate-300 px-3 py-1 text-xs disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </section>
      {moderationTarget && (
        <div
          data-testid="comment-moderation-dialog"
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="comment-moderation-title"
        >
          <div className="w-full max-w-md rounded-xl bg-white p-5 shadow-2xl">
            <h3 id="comment-moderation-title" className="text-lg font-semibold text-slate-900">
              {moderationTarget.status === 'approved' ? 'Approve komentar' : 'Reject komentar'}
            </h3>
            <p className="mt-1 text-sm text-slate-600">
              Catatan moderasi bersifat opsional dan akan tersimpan dalam audit trail.
            </p>
            <label htmlFor="comment-moderation-note" className="mt-4 block text-sm font-medium text-slate-700">
              Catatan
            </label>
            <textarea
              id="comment-moderation-note"
              data-testid="comment-moderation-note"
              value={moderationNote}
              onChange={(event) => setModerationNote(event.target.value)}
              maxLength={500}
              className="mt-1 min-h-28 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder={
                moderationTarget.status === 'approved'
                  ? 'Catatan persetujuan...'
                  : 'Alasan penolakan...'
              }
              autoFocus
            />
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setModerationTarget(null)}
                disabled={moderateMutation.isPending}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 disabled:opacity-50"
              >
                Batal
              </button>
              <button
                data-testid="comment-moderation-confirm"
                type="button"
                onClick={submitModeration}
                disabled={moderateMutation.isPending}
                className={`rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:opacity-50 ${
                  moderationTarget.status === 'approved' ? 'bg-success' : 'bg-danger'
                }`}
              >
                {moderateMutation.isPending
                  ? 'Memproses...'
                  : moderationTarget.status === 'approved'
                    ? 'Approve'
                    : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
