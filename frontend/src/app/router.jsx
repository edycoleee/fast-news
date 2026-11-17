import { Navigate, Route, Routes } from 'react-router-dom'
import { AdminLayout } from '../features/admin/layout/AdminLayout'
import { AdminCategoriesPage } from '../features/admin/pages/AdminCategoriesPage'
import { AdminDashboardPage } from '../features/admin/pages/AdminDashboardPage'
import { AdminFilesPage } from '../features/admin/pages/AdminFilesPage'
import { AdminNewsPage } from '../features/admin/pages/AdminNewsPage'
import { AdminRbacPage } from '../features/admin/pages/AdminRbacPage'
import { AdminUsersPage } from '../features/admin/pages/AdminUsersPage'
import { RequireAuth } from '../features/auth/components/RequireAuth'
import { AdminLoginPage } from '../features/auth/pages/AdminLoginPage'
import { LandingPage } from '../features/public/pages/LandingPage'
import { PublicNewsDetailPage } from '../features/public/pages/PublicNewsDetailPage'
import { PublicNewsListPage } from '../features/public/pages/PublicNewsListPage'

function PlaceholderPage({ title }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 text-slate-700">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
      <p className="mt-2 text-sm">Halaman ini akan dilanjutkan di milestone berikutnya.</p>
    </div>
  )
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/news" element={<PublicNewsListPage />} />
      <Route path="/news/:slug" element={<PublicNewsDetailPage />} />
      <Route path="/admin/login" element={<AdminLoginPage />} />
      <Route
        path="/admin"
        element={
          <RequireAuth>
            <AdminLayout />
          </RequireAuth>
        }
      >
        <Route path="dashboard" element={<AdminDashboardPage />} />
        <Route path="users" element={<AdminUsersPage />} />
        <Route path="rbac" element={<AdminRbacPage />} />
        <Route path="categories" element={<AdminCategoriesPage />} />
        <Route path="news" element={<AdminNewsPage />} />
        <Route path="files" element={<AdminFilesPage />} />
        <Route path="reports" element={<PlaceholderPage title="Reports" />} />
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
