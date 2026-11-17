import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, Clock3, Users } from 'lucide-react'
import { getMyPermissions } from '../api/rbacApi'

const cards = [
  { label: 'Published news', value: '0', icon: CheckCircle2, color: 'text-success' },
  { label: 'Pending review', value: '0', icon: Clock3, color: 'text-warning' },
  { label: 'Active editors', value: '0', icon: Users, color: 'text-primary' },
  { label: 'Moderation alerts', value: '0', icon: AlertTriangle, color: 'text-danger' },
]

export function AdminDashboardPage() {
  const permissionsQuery = useQuery({
    queryKey: ['rbac', 'my-permissions'],
    queryFn: getMyPermissions,
    retry: false,
  })

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map(({ label, value, icon: Icon, color }) => (
          <article key={label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-start justify-between">
              <p className="text-sm text-slate-500">{label}</p>
              <Icon className={`h-5 w-5 ${color}`} />
            </div>
            <p className="mt-3 text-2xl font-semibold text-slate-900">{value}</p>
          </article>
        ))}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3">
          <h2 className="text-base font-semibold text-slate-900">Permission summary</h2>
          <p className="text-sm text-slate-500">Permission aktif user login berdasarkan backend RBAC.</p>
        </div>
        <div className="p-4">
          {permissionsQuery.isLoading && <p className="text-sm text-slate-500">Loading permissions...</p>}
          {permissionsQuery.isError && (
            <p className="rounded-lg border border-danger/20 bg-danger/10 px-3 py-2 text-sm text-danger">
              Gagal memuat permissions.
            </p>
          )}
          {permissionsQuery.isSuccess && (
            <div className="overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-0 text-sm">
                <thead>
                  <tr className="bg-blue-50 text-left text-slate-700">
                    <th className="rounded-tl-lg border border-slate-200 px-3 py-2">User ID</th>
                    <th className="rounded-tr-lg border border-slate-200 px-3 py-2">Permissions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="hover:bg-slate-50">
                    <td className="border border-slate-200 px-3 py-2">{permissionsQuery.data.user_id}</td>
                    <td className="border border-slate-200 px-3 py-2">
                      {permissionsQuery.data.permissions.length > 0
                        ? permissionsQuery.data.permissions.join(', ')
                        : 'No permissions assigned'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
