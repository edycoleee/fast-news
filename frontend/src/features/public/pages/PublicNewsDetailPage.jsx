import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getPublicNewsDetail } from '../api/publicNewsApi'

export function PublicNewsDetailPage() {
  const { slug } = useParams()
  const newsDetailQuery = useQuery({
    queryKey: ['public-news-detail', slug],
    queryFn: () => getPublicNewsDetail(slug),
    enabled: Boolean(slug),
    retry: false,
  })

  return (
    <div className="min-h-screen bg-slate-50 px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-4xl">
        <Link to="/news" className="mb-5 inline-flex rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700">
          Kembali ke list berita
        </Link>

        {newsDetailQuery.isLoading && <p className="text-sm text-slate-500">Memuat detail berita...</p>}
        {newsDetailQuery.isError && <p className="text-sm text-danger">Berita tidak ditemukan atau gagal dimuat.</p>}
        {newsDetailQuery.isSuccess && (
          <article className="rounded-xl border border-slate-200 bg-white p-6">
            <h1 className="text-3xl font-bold text-slate-900">{newsDetailQuery.data.title}</h1>
            <p className="mt-2 text-xs text-slate-500">
              {newsDetailQuery.data.published_at
                ? new Date(newsDetailQuery.data.published_at).toLocaleString()
                : 'Belum ada tanggal publish'}
            </p>
            {newsDetailQuery.data.summary && (
              <p className="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{newsDetailQuery.data.summary}</p>
            )}
            <div
              className="prose prose-slate mt-6 max-w-none text-sm leading-7 [&_img]:h-auto [&_img]:max-w-full [&_img]:rounded-lg"
              dangerouslySetInnerHTML={{ __html: newsDetailQuery.data.content }}
            />
          </article>
        )}
      </div>
    </div>
  )
}
