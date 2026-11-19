import { Link } from 'react-router-dom'
import { Activity, ArrowRight, FileCheck2, Globe, Newspaper, ShieldCheck, Users } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../shared/api/client'
import { listPublicNews } from '../api/publicNewsApi'
import { Badge } from '../../../shared/components/ui/Badge'

const featureCards = [
  {
    title: 'Newsroom publik',
    description: 'Publikasikan berita yang terstruktur, mudah ditemukan, dan nyaman dibaca.',
    icon: Newspaper,
  },
  {
    title: 'Editorial terkelola',
    description: 'Kelola kategori, media, rich text, signature, dan moderation dari satu workspace.',
    icon: FileCheck2,
  },
  {
    title: 'Operasi tim aman',
    description: 'Session aman, RBAC granular, CSRF protection, dan audit trail di setiap aksi penting.',
    icon: ShieldCheck,
  },
  {
    title: 'Kolaborasi jelas',
    description: 'Role, pengguna, permission, komentar, dan workflow approval tersusun transparan.',
    icon: Users,
  },
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
    <div className="min-h-screen bg-background text-slate-950">
      <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-white shadow-sm">
              <Globe className="h-5 w-5" />
            </span>
            <span>
              <span className="block text-lg font-bold tracking-tight text-slate-950">NewsHub</span>
              <span className="block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">
                News Management
              </span>
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link to="/news" className="hidden text-sm font-semibold text-slate-600 hover:text-primary sm:block">
              Newsroom
            </Link>
            <Link to="/admin/login" className="button-primary">
              Admin login
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden border-b border-slate-200 bg-secondary">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(20,184,166,0.22),_transparent_38%)]" />
          <div className="relative mx-auto grid max-w-7xl gap-10 px-4 py-20 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:px-8 lg:py-28">
            <div>
              <Badge className="bg-white/10 text-blue-50 ring-white/20" variant="neutral">
                Newsroom modern untuk tim editorial
              </Badge>
              <h1 className="mt-6 max-w-3xl text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
                Kelola berita lebih cepat, aman, dan terstruktur.
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-8 text-blue-100 sm:text-lg">
                Satu platform untuk publikasi, media, approval, komentar, akses tim, dan audit trail.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/news" className="button-primary bg-white text-secondary hover:bg-blue-50">
                  Jelajahi berita
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  to="/admin/dashboard"
                  className="inline-flex items-center gap-2 rounded-xl border border-white/25 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/15"
                >
                  Buka dashboard
                </Link>
              </div>
            </div>

            <div className="rounded-3xl border border-white/20 bg-white/10 p-5 text-white shadow-2xl backdrop-blur-md sm:p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-blue-100">System status</p>
                  <h2 className="mt-1 text-2xl font-bold">Backend terhubung</h2>
                </div>
                <Activity className="h-6 w-6 text-teal-300" />
              </div>
              <div
                data-testid="health-status"
                className={`mt-6 rounded-2xl border px-4 py-4 ${
                  healthQuery.isSuccess
                    ? 'border-teal-300/30 bg-teal-300/10'
                    : 'border-white/20 bg-white/5'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      healthQuery.isSuccess ? 'bg-teal-300' : 'bg-amber-300'
                    }`}
                  />
                  <span className="font-semibold">
                    {healthQuery.isLoading
                      ? 'Memeriksa layanan...'
                      : healthQuery.isSuccess
                        ? 'API siap digunakan'
                        : 'Layanan belum tersedia'}
                  </span>
                </div>
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3">
                <div className="rounded-2xl bg-white/10 p-4">
                  <p className="text-xs text-blue-100">Berita publik</p>
                  <p className="mt-1 text-2xl font-bold">
                    {publicNewsQuery.isSuccess ? publicNewsQuery.data.length : '—'}
                  </p>
                </div>
                <div className="rounded-2xl bg-white/10 p-4">
                  <p className="text-xs text-blue-100">Milestone aktif</p>
                  <p className="mt-1 text-2xl font-bold">M10</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-20">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Platform</p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Newsroom profesional dari publikasi hingga approval.
            </h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Fondasi modular dengan UX yang bersih, akses yang terkontrol, dan workflow yang dapat diaudit.
            </p>
          </div>
          <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {featureCards.map(({ title, description, icon: Icon }) => (
              <article
                key={title}
                className="surface-card p-6 transition duration-300 hover:-translate-y-1 hover:shadow-lift"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 text-lg font-bold text-slate-950">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-7 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <p>NewsHub CMS · Modular, secure, and editorial-first.</p>
          <div className="flex gap-5">
            <Link to="/news" className="hover:text-primary">Newsroom</Link>
            <Link to="/admin/login" className="hover:text-primary">Admin</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
