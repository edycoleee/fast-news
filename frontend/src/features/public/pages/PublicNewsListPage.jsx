import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listPublicNews } from '../api/publicNewsApi'

export function PublicNewsListPage() {
  const newsQuery = useQuery({
    queryKey: ['public-news'],
    queryFn: () => listPublicNews(),
    retry: false,
  })

  return (
    <div className="min-h-screen bg-slate-50 px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Public Newsroom</h1>
            <p className="mt-2 text-sm text-slate-600">Daftar berita published dari NewsHub CMS.</p>
          </div>
          <Link to="/" className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700">
            Kembali ke landing
          </Link>
        </div>

        {newsQuery.isLoading && <p className="text-sm text-slate-500">Memuat berita...</p>}
        {newsQuery.isError && <p className="text-sm text-danger">Gagal memuat berita publik.</p>}
        {newsQuery.isSuccess && newsQuery.data.length === 0 && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
            Belum ada berita published.
          </div>
        )}

        {newsQuery.isSuccess && newsQuery.data.length > 0 && (
          <div className="grid gap-4">
            {newsQuery.data.map((item) => (
              <article key={item.id} className="rounded-xl border border-slate-200 bg-white p-5">
                <h2 className="text-xl font-semibold text-slate-900">{item.title}</h2>
                <p className="mt-2 text-sm text-slate-600">{item.summary || 'Tanpa ringkasan.'}</p>
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-xs text-slate-500">
                    {item.published_at ? new Date(item.published_at).toLocaleString() : 'Belum ada tanggal publish'}
                  </span>
                  <Link to={`/news/${item.slug}`} className="text-sm font-semibold text-primary hover:underline">
                    Baca detail
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
