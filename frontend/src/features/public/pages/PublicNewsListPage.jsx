import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listPublicNews } from '../api/publicNewsApi'
import { formatLocalDateTime } from '../../../shared/utils/dateTime'
import { ArrowRight, Newspaper } from 'lucide-react'

export function PublicNewsListPage() {
  const newsQuery = useQuery({
    queryKey: ['public-news'],
    queryFn: () => listPublicNews(),
    retry: false,
  })

  return (
    <div className="min-h-screen bg-background px-4 py-10 text-slate-950 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex flex-col gap-5 border-b border-slate-200 pb-8 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Newsroom</p>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">Berita terbaru</h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">
              Informasi dan pembaruan dari newsroom NewsHub yang telah dipublikasikan.
            </p>
          </div>
          <Link to="/" className="button-secondary">
            Kembali ke beranda
          </Link>
        </div>

        {newsQuery.isLoading && <p className="text-sm text-slate-500">Memuat berita...</p>}
        {newsQuery.isError && <p className="text-sm text-danger">Gagal memuat berita publik.</p>}
        {newsQuery.isSuccess && newsQuery.data.length === 0 && (
          <div className="surface-card p-10 text-center text-sm text-slate-600">
            <Newspaper className="mx-auto h-8 w-8 text-slate-300" />
            <p className="mt-3">Belum ada berita published.</p>
          </div>
        )}

        {newsQuery.isSuccess && newsQuery.data.length > 0 && (
          <div className="grid gap-5 md:grid-cols-2">
            {newsQuery.data.map((item) => (
              <article key={item.id} className="surface-card flex min-h-64 flex-col p-6 transition duration-300 hover:-translate-y-1 hover:shadow-lift">
                <span className="w-fit rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">
                  Publikasi
                </span>
                <h2 className="mt-4 text-2xl font-bold tracking-tight text-slate-950">{item.title}</h2>
                <p className="mt-3 flex-1 text-sm leading-6 text-slate-600">{item.summary || 'Tanpa ringkasan.'}</p>
                <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
                  <span className="text-xs text-slate-500">
                    {item.published_at ? formatLocalDateTime(item.published_at) : 'Belum ada tanggal publish'}
                  </span>
                  <Link to={`/news/${item.slug}`} className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:gap-2.5">
                    Baca
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
