import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { deleteFile, listFiles, uploadFile } from '../api/filesApi'
import { API_BASE_URL } from '../../../shared/api/client'

export function AdminFilesPage() {
  const queryClient = useQueryClient()
  const [selectedFile, setSelectedFile] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 10

  const filesQuery = useQuery({
    queryKey: ['admin-files', { page, pageSize, searchTerm }],
    queryFn: () => listFiles({ page, pageSize, search: searchTerm }),
    retry: false,
  })

  const uploadMutation = useMutation({
    mutationFn: uploadFile,
    onSuccess: async () => {
      setSelectedFile(null)
      await queryClient.invalidateQueries({ queryKey: ['admin-files'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteFile,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['admin-files'] })
    },
  })

  const totalPages = filesQuery.data ? Math.max(1, Math.ceil(filesQuery.data.total / filesQuery.data.page_size)) : 1

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">Upload File</h2>
        <p className="mt-1 text-sm text-slate-600">Mendukung PNG, JPG, WEBP, dan PDF (maks. 5MB).</p>
        <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center">
          <input
            type="file"
            accept=".png,.jpg,.jpeg,.webp,.pdf,image/png,image/jpeg,image/webp,application/pdf"
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
          <button
            type="button"
            onClick={() => {
              if (selectedFile) {
                uploadMutation.mutate(selectedFile)
              }
            }}
            disabled={!selectedFile || uploadMutation.isPending}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload file'}
          </button>
        </div>
        {uploadMutation.isError && (
          <p className="mt-3 text-sm text-danger">{uploadMutation.error?.response?.data?.detail || 'Gagal upload file.'}</p>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3">
          <h3 className="text-base font-semibold text-slate-900">Daftar File</h3>
          <input
            value={searchTerm}
            onChange={(event) => {
              setSearchTerm(event.target.value)
              setPage(1)
            }}
            className="mt-3 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm md:max-w-sm"
            placeholder="Cari file..."
          />
        </div>
        <div className="p-4">
          {filesQuery.isLoading && <p className="text-sm text-slate-500">Loading files...</p>}
          {filesQuery.isError && <p className="text-sm text-danger">Gagal memuat file.</p>}
          {filesQuery.isSuccess && (
            <div className="overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-0 text-sm">
                <thead>
                  <tr className="bg-blue-50 text-left text-slate-700">
                    <th className="rounded-tl-lg border border-slate-200 px-3 py-2">Original name</th>
                    <th className="border border-slate-200 px-3 py-2">MIME</th>
                    <th className="border border-slate-200 px-3 py-2">Size</th>
                    <th className="rounded-tr-lg border border-slate-200 px-3 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filesQuery.data.items.map((file) => (
                    <tr key={file.id} className="hover:bg-slate-50">
                      <td className="border border-slate-200 px-3 py-2">{file.original_name}</td>
                      <td className="border border-slate-200 px-3 py-2">{file.mime_type}</td>
                      <td className="border border-slate-200 px-3 py-2">{(file.size_bytes / 1024).toFixed(1)} KB</td>
                      <td className="border border-slate-200 px-3 py-2">
                        <div className="flex items-center gap-2">
                          <a
                            href={`${API_BASE_URL}/api/files/${file.id}/download`}
                            target="_blank"
                            rel="noreferrer"
                            className="rounded border border-slate-300 px-2 py-1 text-xs text-slate-700"
                          >
                            Download
                          </a>
                          <button
                            type="button"
                            onClick={() => {
                              if (window.confirm('Hapus file ini?')) {
                                deleteMutation.mutate(file.id)
                              }
                            }}
                            className="rounded border border-danger/30 px-2 py-1 text-xs text-danger"
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
          {filesQuery.isSuccess && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Page {filesQuery.data.page} of {totalPages} • Total {filesQuery.data.total}
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
          {deleteMutation.isError && (
            <p className="mt-3 text-sm text-danger">{deleteMutation.error?.response?.data?.detail || 'Gagal menghapus file.'}</p>
          )}
        </div>
      </section>
    </div>
  )
}
