import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { listCategories } from '../api/categoryApi'
import { listFiles } from '../api/filesApi'
import { RichTextEditor } from '../components/RichTextEditor'
import { createNews, deleteNews, listNews, updateNews } from '../api/newsApi'
import { API_BASE_URL } from '../../../shared/api/client'

const EMPTY_NEWS_FORM = {
  title: '',
  slug: '',
  summary: '',
  content: '',
  status: 'draft',
  category_id: '',
}

export function AdminNewsPage() {
  const queryClient = useQueryClient()
  const [selectedNewsId, setSelectedNewsId] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const [contentHtml, setContentHtml] = useState('<p></p>')
  const [mediaSearchTerm, setMediaSearchTerm] = useState('')
  const [copiedMediaUrl, setCopiedMediaUrl] = useState('')
  const [insertMediaInfo, setInsertMediaInfo] = useState('')
  const pageSize = 5
  const newsQuery = useQuery({
    queryKey: ['news', { page, pageSize, searchTerm, statusFilter }],
    queryFn: () => listNews({ page, pageSize, search: searchTerm, statusFilter }),
    retry: false,
  })
  const categoriesQuery = useQuery({ queryKey: ['categories-options'], queryFn: () => listCategories({ page: 1, pageSize: 100 }), retry: false })
  const mediaFilesQuery = useQuery({
    queryKey: ['news-media-options', mediaSearchTerm],
    queryFn: () => listFiles({ page: 1, pageSize: 8, search: mediaSearchTerm }),
    retry: false,
  })
  const { register, handleSubmit, reset } = useForm({
    defaultValues: EMPTY_NEWS_FORM,
  })

  const saveNewsMutation = useMutation({
    mutationFn: ({ newsId, payload }) => (newsId ? updateNews(newsId, payload) : createNews(payload)),
    onSuccess: async () => {
      setSelectedNewsId(null)
      setContentHtml('<p></p>')
      reset(EMPTY_NEWS_FORM)
      await queryClient.invalidateQueries({ queryKey: ['news'] })
    },
  })

  const deleteNewsMutation = useMutation({
    mutationFn: deleteNews,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['news'] })
    },
  })

  const filteredNews = useMemo(() => newsQuery.data?.items || [], [newsQuery.data])
  const totalPages = useMemo(() => {
    if (!newsQuery.data) {
      return 1
    }
    return Math.max(1, Math.ceil(newsQuery.data.total / newsQuery.data.page_size))
  }, [newsQuery.data])

  const onSubmit = (values) => {
    saveNewsMutation.mutate({
      newsId: selectedNewsId,
      payload: {
        ...values,
        content: contentHtml,
        category_id: values.category_id ? Number(values.category_id) : null,
      },
    })
  }

  const onEdit = (newsItem) => {
    setSelectedNewsId(newsItem.id)
    reset({
      title: newsItem.title,
      slug: newsItem.slug,
      summary: newsItem.summary || '',
      status: newsItem.status,
      category_id: newsItem.category_id ? String(newsItem.category_id) : '',
    })
    setContentHtml(newsItem.content || '<p></p>')
  }

  const onCancelEdit = () => {
    setSelectedNewsId(null)
    setContentHtml('<p></p>')
    reset(EMPTY_NEWS_FORM)
  }

  const onCopyMediaUrl = async (fileId) => {
    const downloadUrl = `${API_BASE_URL}/api/files/${fileId}/download`
    try {
      await navigator.clipboard.writeText(downloadUrl)
      setCopiedMediaUrl(downloadUrl)
    } catch {
      const textArea = document.createElement('textarea')
      textArea.value = downloadUrl
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      const copied = document.execCommand('copy')
      document.body.removeChild(textArea)

      if (copied) {
        setCopiedMediaUrl(downloadUrl)
      } else {
        setCopiedMediaUrl(`Gagal menyalin otomatis. Salin manual URL ini: ${downloadUrl}`)
      }
    }
  }

  const onInsertMediaUrl = (fileId, originalName, mimeType) => {
    const downloadUrl = `${API_BASE_URL}/api/files/${fileId}/download`
    const safeLabel = originalName.replace(/"/g, '&quot;')
    const insertHtml = mimeType?.startsWith('image/')
      ? `<p><img src="${downloadUrl}" alt="${safeLabel}" title="${safeLabel}"></p>`
      : `<p><a href="${downloadUrl}" target="_blank" rel="noopener noreferrer">${safeLabel}</a></p>`
    const nextContent = `${contentHtml}${insertHtml}`
    setContentHtml(nextContent)
    setInsertMediaInfo(
      mimeType?.startsWith('image/')
        ? `Gambar disisipkan ke konten: ${downloadUrl}`
        : `URL media disisipkan ke konten: ${downloadUrl}`,
    )
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">{selectedNewsId ? 'Edit News' : 'Create News'}</h2>
        <form className="mt-4 grid gap-3 md:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Title" {...register('title', { required: true })} />
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Slug" {...register('slug', { required: true })} />
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2" placeholder="Summary" {...register('summary')} />
          <div className="md:col-span-2">
            <p className="mb-2 text-sm font-medium text-slate-700">Content</p>
            <RichTextEditor value={contentHtml} onChange={setContentHtml} />
          </div>
          <select className="rounded-lg border border-slate-300 px-3 py-2 text-sm" {...register('status')}>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="archived">Archived</option>
          </select>
          <select className="rounded-lg border border-slate-300 px-3 py-2 text-sm" {...register('category_id')}>
            <option value="">No category</option>
            {categoriesQuery.data?.items?.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          {categoriesQuery.isError && (
            <p className="text-sm text-danger md:col-span-2">
              Gagal memuat kategori. {categoriesQuery.error?.response?.data?.detail || 'Pastikan sesi login masih valid dan user memiliki akses yang sesuai.'}
            </p>
          )}
          <div className="flex gap-2 md:col-span-2">
            <button type="submit" className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white" disabled={saveNewsMutation.isPending}>
              {saveNewsMutation.isPending ? 'Saving...' : selectedNewsId ? 'Update news' : 'Save news'}
            </button>
            {selectedNewsId && (
              <button type="button" onClick={onCancelEdit} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">
                Cancel
              </button>
            )}
          </div>
        </form>
        {saveNewsMutation.isError && (
          <p className="mt-3 text-sm text-danger">{saveNewsMutation.error?.response?.data?.detail || 'Failed to save news.'}</p>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Media untuk konten berita</h3>
            <p className="text-sm text-slate-600">Upload dulu di menu Files, lalu salin URL untuk dipakai pada konten rich text.</p>
          </div>
          <Link to="/admin/files" className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
            Buka halaman Files
          </Link>
        </div>
        <input
          value={mediaSearchTerm}
          onChange={(event) => setMediaSearchTerm(event.target.value)}
          className="mt-3 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm md:max-w-sm"
          placeholder="Cari media..."
        />
        <div className="mt-3 space-y-2">
          {mediaFilesQuery.isLoading && <p className="text-sm text-slate-500">Loading media...</p>}
          {mediaFilesQuery.isError && <p className="text-sm text-danger">Gagal memuat daftar media.</p>}
          {mediaFilesQuery.isSuccess && mediaFilesQuery.data.items.length === 0 && (
            <p className="text-sm text-slate-500">Belum ada media yang cocok.</p>
          )}
          {mediaFilesQuery.isSuccess &&
            mediaFilesQuery.data.items.map((file) => (
              <div key={file.id} className="flex flex-col gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="font-medium text-slate-900">{file.original_name}</p>
                  <p className="text-xs text-slate-500">{file.mime_type}</p>
                </div>
                <button
                  type="button"
                  onClick={() => onCopyMediaUrl(file.id)}
                  className="rounded border border-slate-300 px-2 py-1 text-xs font-semibold text-slate-700"
                >
                  Salin URL
                </button>
                <button
                  type="button"
                  onClick={() => onInsertMediaUrl(file.id, file.original_name, file.mime_type)}
                  className="rounded border border-primary/30 px-2 py-1 text-xs font-semibold text-primary"
                >
                  Sisipkan ke konten
                </button>
              </div>
            ))}
        </div>
        {copiedMediaUrl && <p className="mt-3 text-xs text-slate-600">Info: {copiedMediaUrl}</p>}
        {insertMediaInfo && <p className="mt-1 text-xs text-slate-600">Info: {insertMediaInfo}</p>}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3">
          <h3 className="text-base font-semibold text-slate-900">News list</h3>
          <div className="mt-3 flex flex-col gap-2 md:flex-row">
            <input
              value={searchTerm}
              onChange={(event) => {
                setSearchTerm(event.target.value)
                setPage(1)
              }}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm md:max-w-sm"
              placeholder="Search news..."
            />
            <select
              value={statusFilter}
              onChange={(event) => {
                setStatusFilter(event.target.value)
                setPage(1)
              }}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:w-52"
            >
              <option value="">All status</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>
        <div className="p-4">
          {newsQuery.isLoading && <p className="text-sm text-slate-500">Loading news...</p>}
          {newsQuery.isError && <p className="text-sm text-danger">Failed to load news.</p>}
          {newsQuery.isSuccess && (
            <div className="overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-0 text-sm">
                <thead>
                  <tr className="bg-blue-50 text-left text-slate-700">
                    <th className="rounded-tl-lg border border-slate-200 px-3 py-2">Title</th>
                    <th className="border border-slate-200 px-3 py-2">Slug</th>
                    <th className="border border-slate-200 px-3 py-2">Status</th>
                    <th className="border border-slate-200 px-3 py-2">Category ID</th>
                    <th className="rounded-tr-lg border border-slate-200 px-3 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredNews.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50">
                      <td className="border border-slate-200 px-3 py-2">{item.title}</td>
                      <td className="border border-slate-200 px-3 py-2">{item.slug}</td>
                      <td className="border border-slate-200 px-3 py-2">{item.status}</td>
                      <td className="border border-slate-200 px-3 py-2">{item.category_id || '-'}</td>
                      <td className="border border-slate-200 px-3 py-2">
                        <div className="flex items-center gap-2">
                          <button type="button" onClick={() => onEdit(item)} className="rounded border border-slate-300 px-2 py-1 text-xs text-slate-700">
                            Edit
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              if (window.confirm('Hapus berita ini?')) {
                                deleteNewsMutation.mutate(item.id)
                              }
                            }}
                            className="rounded border border-danger/30 px-2 py-1 text-xs text-danger"
                            disabled={deleteNewsMutation.isPending}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {newsQuery.isSuccess && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Page {newsQuery.data.page} of {totalPages} • Total {newsQuery.data.total}
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  disabled={page <= 1}
                  className="rounded border border-slate-300 px-3 py-1 text-xs text-slate-700 disabled:opacity-50"
                >
                  Prev
                </button>
                <button
                  type="button"
                  onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
                  disabled={page >= totalPages}
                  className="rounded border border-slate-300 px-3 py-1 text-xs text-slate-700 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
          {deleteNewsMutation.isError && (
            <p className="mt-3 text-sm text-danger">{deleteNewsMutation.error?.response?.data?.detail || 'Failed to delete news.'}</p>
          )}
        </div>
      </section>
    </div>
  )
}
