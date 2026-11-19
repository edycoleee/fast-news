import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Laptop, LogOut, ShieldCheck } from 'lucide-react'
import {
  listAllSessions,
  listMySessions,
  revokeOtherSessions,
  revokeSession,
} from '../../auth/api/authApi'
import { Badge } from '../../../shared/components/ui/Badge'
import { formatLocalDateTime } from '../../../shared/utils/dateTime'

export function SessionManager() {
  const queryClient = useQueryClient()
  const allSessionsQuery = useQuery({
    queryKey: ['auth', 'all-sessions'],
    queryFn: listAllSessions,
    retry: false,
  })
  const mySessionsQuery = useQuery({
    queryKey: ['auth', 'my-sessions'],
    queryFn: listMySessions,
    enabled: allSessionsQuery.isError,
    retry: false,
  })
  const sessionsQuery = allSessionsQuery.isSuccess ? allSessionsQuery : mySessionsQuery

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ['auth'] })
  }
  const revokeOneMutation = useMutation({
    mutationFn: revokeSession,
    onSuccess: refresh,
  })
  const revokeOthersMutation = useMutation({
    mutationFn: revokeOtherSessions,
    onSuccess: refresh,
  })

  return (
    <section className="surface-card overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <ShieldCheck className="h-5 w-5 text-primary" />
          <div>
            <h2 className="font-bold text-slate-950">Active Sessions</h2>
            <p className="text-xs text-slate-500">
              Tinjau dan cabut sesi aktif. Token session tidak pernah ditampilkan.
            </p>
          </div>
        </div>
        <button
          data-testid="revoke-other-sessions"
          type="button"
          onClick={() => {
            if (window.confirm('Cabut semua session lain milik akun Anda?')) {
              revokeOthersMutation.mutate()
            }
          }}
          disabled={revokeOthersMutation.isPending}
          className="button-secondary"
        >
          <LogOut className="h-4 w-4" />
          {revokeOthersMutation.isPending ? 'Mencabut...' : 'Cabut session lain'}
        </button>
      </div>
      <div className="p-5">
        {sessionsQuery.isLoading && <p className="text-sm text-slate-500">Memuat session...</p>}
        {sessionsQuery.isError && (
          <p className="text-sm text-danger">
            {sessionsQuery.error?.response?.data?.detail || 'Gagal memuat session.'}
          </p>
        )}
        {sessionsQuery.isSuccess && sessionsQuery.data.items.length === 0 && (
          <p className="text-sm text-slate-500">Tidak ada active session.</p>
        )}
        {sessionsQuery.isSuccess && (
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {sessionsQuery.data.items.map((session) => (
              <article key={session.id} className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Laptop className="h-5 w-5 text-slate-500" />
                    <div>
                      <p className="text-sm font-semibold text-slate-900">
                        Session #{session.id}
                      </p>
                      <p className="text-xs text-slate-500">
                        {session.username || `User #${session.user_id}`}
                      </p>
                    </div>
                  </div>
                  {session.is_current ? (
                    <Badge variant="success">Current</Badge>
                  ) : (
                    <Badge>Active</Badge>
                  )}
                </div>
                <dl className="mt-4 space-y-1 text-xs text-slate-600">
                  <div><dt className="inline font-semibold">IP:</dt> <dd className="inline">{session.ip_address || '-'}</dd></div>
                  <div><dt className="inline font-semibold">Device:</dt> <dd className="inline">{session.user_agent || '-'}</dd></div>
                  <div><dt className="inline font-semibold">Last seen:</dt> <dd className="inline">{formatLocalDateTime(session.last_seen_at)}</dd></div>
                  <div><dt className="inline font-semibold">Expires:</dt> <dd className="inline">{formatLocalDateTime(session.expires_at)}</dd></div>
                </dl>
                <button
                  data-testid={`revoke-session-${session.id}`}
                  type="button"
                  disabled={revokeOneMutation.isPending}
                  onClick={() => {
                    if (window.confirm('Cabut session ini?')) {
                      revokeOneMutation.mutate(session.id)
                    }
                  }}
                  className="mt-4 rounded-lg border border-danger/30 px-3 py-2 text-xs font-semibold text-danger hover:bg-danger/5 disabled:opacity-50"
                >
                  Revoke session
                </button>
              </article>
            ))}
          </div>
        )}
        {revokeOneMutation.isError && (
          <p className="mt-3 text-sm text-danger">
            {revokeOneMutation.error?.response?.data?.detail || 'Gagal mencabut session.'}
          </p>
        )}
      </div>
    </section>
  )
}
