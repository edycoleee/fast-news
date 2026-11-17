import { Link } from 'react-router-dom'
import { Activity, ArrowRight, Globe, Newspaper, ShieldCheck, Users } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../shared/api/client'
import { listPublicNews } from '../api/publicNewsApi'

const featureCards = [
  { title: 'Public newsroom', description: 'Landing page, news list, and article detail experience.', icon: Newspaper },
  { title: 'Admin ops', description: 'Dashboard, categories, users, permissions, and moderated content.', icon: Users },
  { title: 'Security first', description: 'Protected routes, session security, and auditable actions.', icon: ShieldCheck },
]

async function getHealth() {
  const response = await apiClient.get('/api/health')
  return response.data
}

export function LandingPage() {
  const healthQuery = useQuery({
    queryKey: ['system', 'health'],
    queryFn: getHealth,
    retry: false,
  })
  const publicNewsQuery = useQuery({
    queryKey: ['landing-public-news'],
    queryFn: () => listPublicNews(),
    retry: false,
  })

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-white">
              <Globe className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">NewsHub</p>
              <h1 className="text-lg font-semibold text-slate-900">CMS Foundation</h1>
            </div>
          </div>
          <Link
            to="/admin/login"
            className="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            Admin Login
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-10">
        <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <div className="mb-4 inline-flex rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              Milestone M06
            </div>
            <h2 className="max-w-xl text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">
              NewsHub CMS dengan Category & News CRUD siap pakai.
            </h2>
            <p className="mt-5 max-w-xl text-lg text-slate-600">
              Tahap ini mengaktifkan workflow editorial inti: manajemen kategori, berita, dan publikasi konten.
            </p>
            <Link
              to="/admin/dashboard"
              className="mt-8 inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              Open dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">System status</p>
                <h3 className="mt-1 text-xl font-bold text-slate-900">Backend health</h3>
              </div>
              <div className="flex items-center gap-2 rounded-full bg-slate-100 px-2.5 py-1.5 text-xs font-medium text-slate-600">
                <Activity className="h-3.5 w-3.5" />
                API
              </div>
            </div>
            <div
              data-testid="health-status"
              className={`mt-6 flex items-center gap-3 rounded-xl border px-4 py-3 ${
                healthQuery.isSuccess
                  ? 'border-success/20 bg-success/10 text-success'
                  : healthQuery.isLoading
                    ? 'border-slate-200 bg-slate-50 text-slate-600'
                    : 'border-danger/20 bg-danger/10 text-danger'
              }`}
            >
              <span
                className={`h-2.5 w-2.5 rounded-full ${
                  healthQuery.isSuccess ? 'bg-success' : healthQuery.isLoading ? 'bg-slate-400' : 'bg-danger'
                }`}
              />
              <span className="font-medium">
                {healthQuery.isLoading ? 'Checking backend...' : healthQuery.isSuccess ? 'Connected' : 'Connection error'}
              </span>
            </div>
            <div className="mt-5 rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
              <p className="font-medium text-slate-700">Status message</p>
              <p className="mt-2">
                {healthQuery.isSuccess ? JSON.stringify(healthQuery.data) : healthQuery.error?.message || 'Waiting response...'}
              </p>
            </div>
          </div>
        </section>

        <section className="mt-12 grid gap-6 md:grid-cols-3">
          {featureCards.map(({ title, description, icon: Icon }) => {
            if (title === 'Public newsroom') {
              return (
                <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
                  <p className="mt-3 text-xs text-slate-500">
                    {publicNewsQuery.isSuccess ? `${publicNewsQuery.data.length} artikel published tersedia.` : 'Memuat artikel publik...'}
                  </p>
                  <Link to="/news" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline">
                    Buka newsroom
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </article>
              )
            }

            return (
              <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
              </article>
            )
          })}
        </section>
      </main>
    </div>
  )
}
