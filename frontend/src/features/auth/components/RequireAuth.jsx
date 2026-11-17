import { Navigate, useLocation } from 'react-router-dom'
import { useAuthMe } from '../hooks/useAuth'

export function RequireAuth({ children }) {
  const location = useLocation()
  const authQuery = useAuthMe()

  if (authQuery.isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <p className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
          Checking session...
        </p>
      </div>
    )
  }

  if (authQuery.isError) {
    return <Navigate to="/admin/login" state={{ from: location.pathname }} replace />
  }

  return children
}
