import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, Search, ShieldAlert } from 'lucide-react'
import { exportAuditLogs, listAuditLogs } from '../api/auditApi'
import { Badge } from '../../../shared/components/ui/Badge'
import { PageHeader } from '../../../shared/components/ui/PageHeader'
import { formatLocalDateTime } from '../../../shared/utils/dateTime'

const EVENT_VARIANTS = {
  failure: 'danger',
  reject: 'danger',
  revoke: 'warning',
  denied: 'warning',
  success: 'success',
  create: 'primary',
  approved: 'success',
}

function eventVariant(action) {
  const matched = Object.keys(EVENT_VARIANTS).find((key) => action.includes(key))
  return matched ? EVENT_VARIANTS[matched] : 'neutral'
}

export function AdminAuditPage() {
  const [action, setAction] = useState('')
  const [userId, setUserId] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [page, setPage] = useState(1)
  const [exporting, setExporting] = useState(false)
  const filters = useMemo(
    () => ({ page, pageSize: 25, action, userId, dateFrom, dateTo }),
    [page, action, userId, dateFrom, dateTo],
  )
  const logsQuery = useQuery({
    queryKey: ['audit-logs', filters],
    queryFn: () => listAuditLogs(filters),
    retry: false,
  })

  const handleExport = async () => {
    setExporting(true)
    try {
      const blob = await exportAuditLogs({ action, userId, dateFrom, dateTo })
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = 'newshub-audit.csv'
      anchor.click()
      URL.revokeObjectURL(url)
    } finally {
      setExporting(false)
    }
  }

  const totalPages = logsQuery.data
    ? Math.max(1, Math.ceil(logsQuery.data.total / logsQuery.data.page_size))
    : 1

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="M11.1 Monitoring"
        title="Audit & Security Events"
        description="Tinjau tindakan sensitif, actor, entity, dan waktu. Export dibatasi 10.000 baris dan tidak memuat token/secret."
        actions={
          <button
            data-testid="audit-export-button"
            type="button"
            onClick={handleExport}
            disabled={exporting}
            className="button-secondary"
          >
            <Download className="h-4 w-4" />
            {exporting ? 'Exporting...' : 'Export CSV'}
          </button>
        }
      />

      <section className="surface-card p-5">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <label>
            <span className="text-xs font-semibold text-slate-600">Action</span>
            <div className="relative mt-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <input
                data-testid="audit-action-filter"
                value={action}
                onChange={(event) => {
                  setAction(event.target.value)
                  setPage(1)
                }}
                className="field-control pl-9"
                placeholder="auth.login, settings..."
              />
            </div>
          </label>
          <label>
            <span className="text-xs font-semibold text-slate-600">User ID</span>
            <input
              value={userId}
              onChange={(event) => {
                setUserId(event.target.value)
                setPage(1)
              }}
              type="number"
              min="1"
              className="field-control mt-1"
            />
          </label>
          <label>
            <span className="text-xs font-semibold text-slate-600">Dari</span>
            <input
              value={dateFrom}
              onChange={(event) => {
                setDateFrom(event.target.value)
                setPage(1)
              }}
              type="date"
              className="field-control mt-1"
            />
          </label>
          <label>
            <span className="text-xs font-semibold text-slate-600">Sampai</span>
            <input
              value={dateTo}
              onChange={(event) => {
                setDateTo(event.target.value)
                setPage(1)
              }}
              type="date"
              className="field-control mt-1"
            />
          </label>
        </div>
      </section>

      <section className="surface-card overflow-hidden">
        {logsQuery.isLoading && <p className="p-5 text-sm text-slate-500">Memuat audit log...</p>}
        {logsQuery.isError && (
          <p className="m-5 rounded-xl bg-danger/10 p-3 text-sm text-danger">
            {logsQuery.error?.response?.data?.detail || 'Gagal memuat audit log.'}
          </p>
        )}
        {logsQuery.isSuccess && logsQuery.data.items.length === 0 && (
          <div className="p-10 text-center">
            <ShieldAlert className="mx-auto h-8 w-8 text-slate-300" />
            <p className="mt-3 text-sm text-slate-500">Tidak ada event yang cocok.</p>
          </div>
        )}
        {logsQuery.isSuccess && logsQuery.data.items.length > 0 && (
          <div className="divide-y divide-slate-200">
            {logsQuery.data.items.map((event) => (
              <article key={event.id} className="p-5">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant={eventVariant(event.action)}>{event.action}</Badge>
                      <span className="text-xs text-slate-500">
                        {event.entity_type}
                        {event.entity_id ? ` #${event.entity_id}` : ''}
                      </span>
                    </div>
                    <p className="mt-2 break-all text-xs text-slate-600">
                      {JSON.stringify(event.details || {})}
                    </p>
                  </div>
                  <div className="shrink-0 text-left text-xs text-slate-500 md:text-right">
                    <p>{formatLocalDateTime(event.created_at)}</p>
                    <p className="mt-1">{event.user_id ? `Actor user #${event.user_id}` : 'System/public actor'}</p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
        {logsQuery.isSuccess && (
          <div className="flex items-center justify-between border-t border-slate-200 px-5 py-4">
            <p className="text-xs text-slate-500">
              Page {logsQuery.data.page} of {totalPages} · Total {logsQuery.data.total}
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPage((current) => Math.max(1, current - 1))}
                disabled={page <= 1}
                className="button-secondary px-3 py-1.5 disabled:opacity-50"
              >
                Prev
              </button>
              <button
                type="button"
                onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
                disabled={page >= totalPages}
                className="button-secondary px-3 py-1.5 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
