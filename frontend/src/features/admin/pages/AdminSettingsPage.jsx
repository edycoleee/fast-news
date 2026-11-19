import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ShieldCheck, SlidersHorizontal } from 'lucide-react'
import { listSettings, runRetentionCleanup, updateSettings } from '../api/settingsApi'
import { Badge } from '../../../shared/components/ui/Badge'
import { PageHeader } from '../../../shared/components/ui/PageHeader'
import { SessionManager } from '../components/SessionManager'

const CATEGORY_LABELS = {
  upload: 'Upload dan media',
  comments: 'Komentar publik',
  security: 'Keamanan dan rate limit',
  retention: 'Retention dan cleanup',
}

function displayValue(setting, value) {
  if (setting.key.endsWith('_bytes')) {
    return Number(value) / (1024 * 1024)
  }
  return value
}

function inputValue(setting, displayedValue) {
  if (setting.key.endsWith('_bytes')) {
    return Math.round(Number(displayedValue) * 1024 * 1024)
  }
  return Number(displayedValue)
}

export function AdminSettingsPage() {
  const queryClient = useQueryClient()
  const [draft, setDraft] = useState({})
  const [retentionReport, setRetentionReport] = useState(null)
  const settingsQuery = useQuery({
    queryKey: ['admin-settings'],
    queryFn: listSettings,
    retry: false,
  })

  const updateMutation = useMutation({
    mutationFn: (values) =>
      updateSettings(
        settingsQuery.data.items.map((setting) => ({
          key: setting.key,
          value: inputValue(setting, values[setting.key]),
        })),
      ),
    onSuccess: async (data) => {
      queryClient.setQueryData(['admin-settings'], data)
      setDraft({})
    },
  })
  const retentionMutation = useMutation({
    mutationFn: runRetentionCleanup,
    onSuccess: (data) => {
      setRetentionReport(data)
    },
  })

  const groupedSettings = useMemo(() => {
    const groups = {}
    settingsQuery.data?.items.forEach((setting) => {
      groups[setting.category] ||= []
      groups[setting.category].push(setting)
    })
    return groups
  }, [settingsQuery.data])

  const handleSubmit = (event) => {
    event.preventDefault()
    updateMutation.mutate(draft)
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="M11 Security & Operations"
        title="System Settings"
        description="Atur batas operasional aplikasi. Credential, cookie secret, CORS, database URL, dan hard cap deployment tetap dikelola melalui environment."
        actions={<Badge variant="primary">Runtime configuration</Badge>}
      />

      <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
        Nilai UI tetap dibatasi oleh schema dan hard cap environment. Setiap perubahan tersimpan
        dalam audit log bersama actor serta nilai lama dan baru.
      </div>

      <SessionManager />

      {settingsQuery.isLoading && <p className="text-sm text-slate-500">Memuat settings...</p>}
      {settingsQuery.isError && (
        <p className="rounded-xl border border-danger/20 bg-danger/10 px-4 py-3 text-sm text-danger">
          {settingsQuery.error?.response?.data?.detail || 'Gagal memuat settings.'}
        </p>
      )}
      {settingsQuery.isSuccess && (
        <form className="space-y-5" onSubmit={handleSubmit}>
          {Object.entries(groupedSettings).map(([category, items]) => (
            <section key={category} className="surface-card overflow-hidden">
              <div className="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
                {category === 'security' ? (
                  <ShieldCheck className="h-5 w-5 text-primary" />
                ) : (
                  <SlidersHorizontal className="h-5 w-5 text-primary" />
                )}
                <div>
                  <h2 className="font-bold text-slate-950">{CATEGORY_LABELS[category] || category}</h2>
                  <p className="text-xs text-slate-500">
                    {items.length} setting runtime
                  </p>
                </div>
              </div>
              <div className="grid gap-4 p-5 md:grid-cols-2">
                {items.map((setting) => {
                  const isBytes = setting.key.endsWith('_bytes')
                  const min = isBytes
                    ? Number((setting.minimum / (1024 * 1024)).toFixed(3))
                    : setting.minimum
                  const max = isBytes
                    ? Number((setting.maximum / (1024 * 1024)).toFixed(3))
                    : setting.maximum
                  return (
                    <label key={setting.key} className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
                      <span className="flex items-center justify-between gap-3">
                        <span className="text-sm font-semibold text-slate-900">{setting.label}</span>
                        {setting.is_default && <Badge>Default</Badge>}
                      </span>
                      <span className="mt-1 block break-all text-xs text-slate-500">{setting.key}</span>
                      <div className="mt-3 flex items-center gap-2">
                        <input
                          data-testid={`setting-${setting.key}`}
                          type="number"
                          step={isBytes ? 'any' : '1'}
                          min={min ?? undefined}
                          max={max ?? undefined}
                          value={
                            draft[setting.key] ??
                            displayValue(setting, setting.value)
                          }
                          onChange={(event) =>
                            setDraft((current) => ({
                              ...current,
                              [setting.key]: event.target.value,
                            }))
                          }
                          className="field-control"
                          required
                        />
                        {isBytes && <span className="text-sm font-semibold text-slate-500">MB</span>}
                      </div>
                      <span className="mt-2 block text-xs text-slate-500">
                        Batas {min}–{max}{isBytes ? ' MB' : ''}
                      </span>
                    </label>
                  )
                })}
              </div>
            </section>
          ))}
          <section className="surface-card overflow-hidden">
            <div className="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
              <SlidersHorizontal className="h-5 w-5 text-primary" />
              <div>
                <h2 className="font-bold text-slate-950">Retention cleanup manual</h2>
                <p className="text-xs text-slate-500">
                  Jalankan dry-run atau cleanup langsung dari Admin.
                </p>
              </div>
            </div>
            <div className="space-y-3 p-5">
              <div className="flex flex-wrap gap-2">
                <button
                  data-testid="retention-dry-run-button"
                  type="button"
                  onClick={() => retentionMutation.mutate({ dry_run: true })}
                  disabled={retentionMutation.isPending}
                  className="button-secondary"
                >
                  {retentionMutation.isPending ? 'Memproses...' : 'Dry run retention'}
                </button>
                <button
                  data-testid="retention-cleanup-button"
                  type="button"
                  onClick={() => {
                    if (window.confirm('Jalankan retention cleanup sekarang?')) {
                      retentionMutation.mutate({ dry_run: false })
                    }
                  }}
                  disabled={retentionMutation.isPending}
                  className="button-primary"
                >
                  {retentionMutation.isPending ? 'Memproses...' : 'Jalankan cleanup'}
                </button>
              </div>
              {retentionMutation.isError && (
                <p className="text-sm text-danger">
                  {retentionMutation.error?.response?.data?.detail || 'Gagal menjalankan retention cleanup.'}
                </p>
              )}
              {retentionReport && (
                <div
                  data-testid="retention-cleanup-report"
                  className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700"
                >
                  <p className="font-semibold text-slate-900">
                    Hasil {retentionReport.dry_run ? 'dry-run' : 'cleanup'}
                  </p>
                  <p>
                    Eligible — audit: {retentionReport.eligible.audit_logs}, session:{' '}
                    {retentionReport.eligible.auth_sessions}, rate-limit:{' '}
                    {retentionReport.eligible.rate_limit_buckets}
                  </p>
                  <p>
                    Deleted — audit: {retentionReport.deleted.audit_logs}, session:{' '}
                    {retentionReport.deleted.auth_sessions}, rate-limit:{' '}
                    {retentionReport.deleted.rate_limit_buckets}
                  </p>
                </div>
              )}
            </div>
          </section>
          {updateMutation.isError && (
            <p className="text-sm text-danger">
              {updateMutation.error?.response?.data?.detail || 'Gagal menyimpan settings.'}
            </p>
          )}
          {updateMutation.isSuccess && (
            <p className="text-sm text-success">Runtime settings berhasil disimpan.</p>
          )}
          <div className="flex justify-end">
            <button
              data-testid="settings-save-button"
              type="submit"
              disabled={updateMutation.isPending}
              className="button-primary"
            >
              {updateMutation.isPending ? 'Menyimpan...' : 'Simpan settings'}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
