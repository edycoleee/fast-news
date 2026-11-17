import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { BarChart3, FileUp, FolderTree, LayoutDashboard, LogOut, Newspaper, ShieldCheck, UserCog } from 'lucide-react'
import { logout } from '../../auth/api/authApi'

const menus = [
  { to: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/admin/users', label: 'Users', icon: UserCog },
  { to: '/admin/rbac', label: 'RBAC', icon: ShieldCheck },
  { to: '/admin/categories', label: 'Categories', icon: FolderTree },
  { to: '/admin/news', label: 'News', icon: Newspaper },
  { to: '/admin/files', label: 'Files', icon: FileUp },
  { to: '/admin/reports', label: 'Reports', icon: BarChart3 },
]

export function AdminLayout() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['auth', 'me'] })
      navigate('/admin/login', { replace: true })
    },
  })

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[280px_1fr]">
        <aside className="border-r border-slate-800 bg-secondary px-5 py-6 text-slate-100">
          <Link to="/admin/dashboard" className="block rounded-xl bg-primary/20 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-200">NewsHub</p>
            <p className="mt-1 text-lg font-semibold">Admin Console</p>
          </Link>

          <nav className="mt-6 space-y-2">
            {menus.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                    isActive ? 'bg-primary text-white' : 'text-slate-200 hover:bg-slate-700/60'
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}
          </nav>

          <button
            data-testid="logout-button"
            type="button"
            onClick={() => logoutMutation.mutate()}
            className="mt-8 inline-flex items-center gap-2 rounded-xl border border-slate-600 px-3 py-2 text-sm hover:bg-slate-700"
          >
            <LogOut className="h-4 w-4" />
            {logoutMutation.isPending ? 'Logging out...' : 'Logout'}
          </button>
        </aside>

        <div className="flex min-h-screen flex-col">
          <header className="border-b border-slate-200 bg-white px-6 py-4">
            <p className="text-sm font-medium text-slate-500">M08 File Upload</p>
            <h1 className="text-xl font-semibold text-slate-900">NewsHub Administration</h1>
          </header>
          <main className="flex-1 px-6 py-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
