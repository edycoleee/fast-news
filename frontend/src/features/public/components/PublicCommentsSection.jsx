import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { listPublicComments, submitPublicComment } from '../api/commentsApi'
import { publicCommentSchema } from '../schemas/commentSchema'
import { formatLocalDateTime } from '../../../shared/utils/dateTime'
import { getPublicSettings } from '../api/publicSettingsApi'

export function PublicCommentsSection({ slug }) {
  const queryClient = useQueryClient()
  const [validationError, setValidationError] = useState('')
  const { register, handleSubmit, reset } = useForm({
    defaultValues: { author_name: '', content: '' },
  })
  const commentsQuery = useQuery({
    queryKey: ['public-comments', slug],
    queryFn: () => listPublicComments(slug),
    enabled: Boolean(slug),
    retry: false,
  })
  const limitsQuery = useQuery({
    queryKey: ['public-settings'],
    queryFn: getPublicSettings,
    retry: false,
    staleTime: 15_000,
  })
  const submitMutation = useMutation({
    mutationFn: submitPublicComment,
    onSuccess: async () => {
      reset()
      setValidationError('')
      await queryClient.invalidateQueries({ queryKey: ['public-comments', slug] })
    },
  })

  const onSubmit = (values) => {
    const parsed = publicCommentSchema.safeParse({
      ...values,
      parent_id: null,
    })
    if (!parsed.success) {
      setValidationError(parsed.error.issues[0]?.message || 'Komentar tidak valid.')
      return
    }
    setValidationError('')
    submitMutation.mutate({ slug, payload: parsed.data })
  }

  return (
    <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Komentar Pembaca</h2>
      <p className="mt-1 text-sm text-slate-600">
        Komentar akan tampil setelah disetujui moderator.
      </p>

      <form className="mt-5 space-y-3" onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label htmlFor="comment-author-name" className="text-sm font-medium text-slate-700">
            Nama
          </label>
          <input
            id="comment-author-name"
            data-testid="comment-author-input"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            maxLength={80}
            {...register('author_name', { required: true, minLength: 2 })}
          />
        </div>
        <div>
          <label htmlFor="comment-content" className="text-sm font-medium text-slate-700">
            Komentar
          </label>
          <textarea
            id="comment-content"
            data-testid="comment-content-input"
            className="mt-1 min-h-28 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            maxLength={limitsQuery.data?.comment_max_length || 2000}
            {...register('content', { required: true, minLength: 3 })}
          />
        </div>
        {limitsQuery.isSuccess && (
          <p className="text-xs text-slate-500">
            Batas komentar: {limitsQuery.data.comment_max_length} karakter.
          </p>
        )}
        <button
          data-testid="comment-submit-button"
          type="submit"
          disabled={submitMutation.isPending}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          {submitMutation.isPending ? 'Mengirim...' : 'Kirim komentar'}
        </button>
        {validationError && <p className="text-sm text-danger">{validationError}</p>}
        {submitMutation.isError && (
          <p className="text-sm text-danger">
            {submitMutation.error?.response?.data?.detail || 'Komentar gagal dikirim.'}
          </p>
        )}
        {submitMutation.isSuccess && (
          <p className="text-sm text-success">{submitMutation.data.message}</p>
        )}
      </form>

      <div className="mt-7 border-t border-slate-200 pt-5">
        {commentsQuery.isLoading && <p className="text-sm text-slate-500">Memuat komentar...</p>}
        {commentsQuery.isError && (
          <p className="text-sm text-danger">Gagal memuat komentar publik.</p>
        )}
        {commentsQuery.isSuccess && commentsQuery.data.length === 0 && (
          <p className="text-sm text-slate-500">Belum ada komentar yang disetujui.</p>
        )}
        {commentsQuery.isSuccess && (
          <div className="space-y-3">
            {commentsQuery.data.map((comment) => (
              <article
                key={comment.id}
                data-testid={`public-comment-${comment.id}`}
                className="rounded-lg bg-slate-50 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-slate-900">{comment.author_name}</p>
                  <time className="text-xs text-slate-500">
                    {formatLocalDateTime(comment.created_at)}
                  </time>
                </div>
                <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {comment.content}
                </p>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
