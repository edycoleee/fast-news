import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { listNews } from '../api/newsApi'
import { createSignature, listSignatures, revokeSignature } from '../api/signaturesApi'
import { SignatureCanvas } from '../components/SignatureCanvas'
import { signatureSchema } from '../schemas/signatureSchema'
import { API_BASE_URL } from '../../../shared/api/client'
import { formatLocalDateTime } from '../../../shared/utils/dateTime'

function errorMessage(error, fallback) {
  return error?.response?.data?.detail || fallback
}

export function AdminSignaturesPage() {
  const queryClient = useQueryClient()
  const [signatureDataUrl, setSignatureDataUrl] = useState('')
  const [signatureCanvasVersion, setSignatureCanvasVersion] = useState(0)
  const [validationError, setValidationError] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 10
  const { register, handleSubmit, reset } = useForm({
    defaultValues: { purpose: '', news_id: '' },
  })

  const signaturesQuery = useQuery({
    queryKey: ['signatures', { page, pageSize, statusFilter }],
    queryFn: () => listSignatures({ page, pageSize, status: statusFilter }),
    retry: false,
  })
  const newsQuery = useQuery({
    queryKey: ['signature-news-options'],
    queryFn: () => listNews({ page: 1, pageSize: 100 }),
    retry: false,
  })

  const createMutation = useMutation({
    mutationFn: createSignature,
    onSuccess: async () => {
      setSignatureDataUrl('')
      setSignatureCanvasVersion((version) => version + 1)
      reset({ purpose: '', news_id: '' })
      setValidationError('')
      await queryClient.invalidateQueries({ queryKey: ['signatures'] })
    },
  })
  const revokeMutation = useMutation({
    mutationFn: revokeSignature,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['signatures'] })
    },
  })

  const onSubmit = (values) => {
    if (!signatureDataUrl) {
      setValidationError('Gambar tanda tangan terlebih dahulu.')
      return
    }

    const parsed = signatureSchema.safeParse({
      purpose: values.purpose,
      news_id: values.news_id ? Number(values.news_id) : null,
      signature_data_url: signatureDataUrl,
    })
    if (!parsed.success) {
      setValidationError(parsed.error.issues[0]?.message || 'Data tanda tangan tidak valid.')
      return
    }

    setValidationError('')
    createMutation.mutate(parsed.data)
  }

  const onRevoke = (signatureId) => {
    const reason = window.prompt('Alasan pencabutan signature:')
    if (!reason?.trim() || reason.trim().length < 3) {
      return
    }
    revokeMutation.mutate({ signatureId, reason: reason.trim() })
  }

  const totalPages = signaturesQuery.data
    ? Math.max(1, Math.ceil(signaturesQuery.data.total / signaturesQuery.data.page_size))
    : 1

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Tanda Tangan Approval</h2>
          <p className="mt-1 text-sm text-slate-600">
            Buat bukti approval yang terikat ke user penandatangan dan, bila dipilih, ke berita.
          </p>
        </div>
        <form className="mt-5 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
          <input
            data-testid="signature-purpose-input"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Tujuan approval"
            {...register('purpose', { required: true, minLength: 3 })}
          />
          <select
            data-testid="signature-news-select"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('news_id')}
          >
            <option value="">Approval umum</option>
            {newsQuery.data?.items?.map((news) => (
              <option key={news.id} value={news.id}>
                {news.title}
              </option>
            ))}
          </select>
          <div className="md:col-span-2">
            <SignatureCanvas
              key={signatureCanvasVersion}
              onChange={setSignatureDataUrl}
            />
          </div>
          <div className="flex items-center gap-3 md:col-span-2">
            <button
              data-testid="signature-save-button"
              type="submit"
              disabled={createMutation.isPending}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
            >
              {createMutation.isPending ? 'Menyimpan...' : 'Simpan signature'}
            </button>
            {validationError && <p className="text-sm text-danger">{validationError}</p>}
            {createMutation.isError && (
              <p className="text-sm text-danger">{errorMessage(createMutation.error, 'Gagal menyimpan signature.')}</p>
            )}
          </div>
        </form>
        {newsQuery.isError && <p className="mt-3 text-sm text-danger">Gagal memuat pilihan berita.</p>}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="flex flex-col gap-3 border-b border-slate-200 px-4 py-3 md:flex-row md:items-center md:justify-between">
          <h3 className="text-base font-semibold text-slate-900">Riwayat Signature</h3>
          <select
            data-testid="signature-status-filter"
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value)
              setPage(1)
            }}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="">Semua status</option>
            <option value="active">Active</option>
            <option value="revoked">Revoked</option>
          </select>
        </div>
        <div className="p-4">
          {signaturesQuery.isLoading && <p className="text-sm text-slate-500">Memuat signature...</p>}
          {signaturesQuery.isError && (
            <p className="text-sm text-danger">{errorMessage(signaturesQuery.error, 'Gagal memuat signature.')}</p>
          )}
          {signaturesQuery.isSuccess && signaturesQuery.data.items.length === 0 && (
            <p className="text-sm text-slate-500">Belum ada signature.</p>
          )}
          {signaturesQuery.isSuccess && signaturesQuery.data.items.length > 0 && (
            <div className="space-y-3">
              {signaturesQuery.data.items.map((signature) => (
                <article
                  key={signature.id}
                  data-testid={`signature-row-${signature.id}`}
                  className="grid gap-4 rounded-lg border border-slate-200 p-4 md:grid-cols-[160px_1fr_auto]"
                >
                  <img
                    src={`${API_BASE_URL}/api/signatures/${signature.id}/download`}
                    alt={`Signature ${signature.id}`}
                    className="h-20 w-full rounded border border-slate-200 bg-white object-contain"
                  />
                  <div>
                    <p className="font-semibold text-slate-900">{signature.purpose}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      Signer #{signature.signer_id} · News {signature.news_id ? `#${signature.news_id}` : 'umum'} ·{' '}
                      {formatLocalDateTime(signature.created_at)}
                    </p>
                    <p className={`mt-2 text-xs font-semibold ${signature.status === 'active' ? 'text-success' : 'text-danger'}`}>
                      {signature.status.toUpperCase()}
                    </p>
                    {signature.revocation_reason && (
                      <p className="mt-1 text-xs text-slate-600">Alasan: {signature.revocation_reason}</p>
                    )}
                  </div>
                  <div className="flex items-start gap-2">
                    <a
                      href={`${API_BASE_URL}/api/signatures/${signature.id}/download`}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700"
                    >
                      Unduh
                    </a>
                    {signature.status === 'active' && (
                      <button
                        data-testid={`signature-revoke-button-${signature.id}`}
                        type="button"
                        disabled={revokeMutation.isPending}
                        onClick={() => onRevoke(signature.id)}
                        className="rounded border border-danger/30 px-3 py-2 text-xs font-semibold text-danger disabled:opacity-50"
                      >
                        Revoke
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
          {revokeMutation.isError && (
            <p className="mt-3 text-sm text-danger">{errorMessage(revokeMutation.error, 'Gagal mencabut signature.')}</p>
          )}
          {signaturesQuery.isSuccess && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Page {signaturesQuery.data.page} of {totalPages} · Total {signaturesQuery.data.total}
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
    </div>
  )
}
