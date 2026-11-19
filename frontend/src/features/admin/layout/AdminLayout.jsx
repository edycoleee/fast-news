import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { BarChart3, FileSearch, FileUp, FolderTree, LayoutDashboard, LogOut, MessageSquare, Newspaper, PenTool, Settings2, ShieldCheck, UserCog } from 'lucide-react'
import { logout } from '../../auth/api/authApi'
import { Badge } from '../../../shared/components/ui/Badge'

const menus = [
  { to: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/admin/users', label: 'Users', icon: UserCog },
  { to: '/admin/rbac', label: 'RBAC', icon: ShieldCheck },
  { to: '/admin/categories', label: 'Categories', icon: FolderTree },
  { to: '/admin/news', label: 'News', icon: Newspaper },
  { to: '/admin/files', label: 'Files', icon: FileUp },
  { to: '/admin/signatures', label: 'Signatures', icon: PenTool },
  { to: '/admin/comments', label: 'Comments', icon: MessageSquare },
  { to: '/admin/settings', label: 'Settings', icon: Settings2 },
  { to: '/admin/audit', label: 'Audit', icon: FileSearch },
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
    <div className="min-h-screen bg-background text-text">
      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[272px_1fr]">
        <aside className="border-r border-white/10 bg-secondary px-4 py-5 text-slate-100 lg:sticky lg:top-0 lg:h-screen lg:overflow-y-auto lg:px-5 lg:py-6">
          <Link to="/admin/dashboard" className="block rounded-2xl border border-white/15 bg-white/10 px-4 py-4 shadow-sm">
            <p className="text-xs uppercase tracking-[0.22em] text-blue-100">NewsHub</p>
            <p className="mt-1 text-lg font-bold">Admin Console</p>
            <p className="mt-1 text-xs text-blue-100/80">Editorial operations</p>
          </Link>

          <nav className="mt-6 space-y-2">
            {menus.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium ${
                    isActive
                      ? 'bg-white text-secondary shadow-sm'
                      : 'text-blue-50/90 hover:bg-white/10 hover:text-white'
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
            className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-white/20 bg-white/5 px-3 py-2.5 text-sm font-semibold hover:bg-white/10"
          >
            <LogOut className="h-4 w-4" />
            {logoutMutation.isPending ? 'Logging out...' : 'Logout'}
          </button>
        </aside>

        <div className="flex min-h-screen flex-col">
          <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 px-4 py-4 backdrop-blur-md sm:px-6 lg:px-8">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">
                  NewsHub Operations
                </p>
                <h1 className="mt-0.5 text-xl font-bold tracking-tight text-slate-950">
                  Administration
                </h1>
              </div>
              <Badge variant="success">Secure session</Badge>
            </div>
          </header>
          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
