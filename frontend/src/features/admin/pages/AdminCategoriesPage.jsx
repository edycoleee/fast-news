import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { createCategory, deleteCategory, listCategories, updateCategory } from '../api/categoryApi'

const EMPTY_CATEGORY_FORM = { name: '', slug: '', description: '' }

export function AdminCategoriesPage() {
  const queryClient = useQueryClient()
  const [selectedCategoryId, setSelectedCategoryId] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 5
  const categoriesQuery = useQuery({
    queryKey: ['categories', { page, pageSize, searchTerm }],
    queryFn: () => listCategories({ page, pageSize, search: searchTerm }),
    retry: false,
  })
  const { register, handleSubmit, reset } = useForm({
    defaultValues: EMPTY_CATEGORY_FORM,
  })

  const saveCategoryMutation = useMutation({
    mutationFn: ({ categoryId, payload }) =>
      categoryId ? updateCategory(categoryId, payload) : createCategory(payload),
    onSuccess: async () => {
      setSelectedCategoryId(null)
      reset(EMPTY_CATEGORY_FORM)
      await queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })

  const deleteCategoryMutation = useMutation({
    mutationFn: deleteCategory,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })

  const filteredCategories = useMemo(() => categoriesQuery.data?.items || [], [categoriesQuery.data])
  const totalPages = useMemo(() => {
    if (!categoriesQuery.data) {
      return 1
    }
    return Math.max(1, Math.ceil(categoriesQuery.data.total / categoriesQuery.data.page_size))
  }, [categoriesQuery.data])

  const onSubmit = (values) => {
    saveCategoryMutation.mutate({ categoryId: selectedCategoryId, payload: values })
  }

  const onEdit = (category) => {
    setSelectedCategoryId(category.id)
    reset({
      name: category.name,
      slug: category.slug,
      description: category.description || '',
    })
  }

  const onCancelEdit = () => {
    setSelectedCategoryId(null)
    reset(EMPTY_CATEGORY_FORM)
  }

  const onDelete = (categoryId) => {
    if (!window.confirm('Hapus kategori ini?')) {
      return
    }
    deleteCategoryMutation.mutate(categoryId)
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">{selectedCategoryId ? 'Edit Category' : 'Create Category'}</h2>
        <form className="mt-4 grid gap-3 md:grid-cols-3" onSubmit={handleSubmit(onSubmit)}>
          <input
            data-testid="category-name-input"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Category name"
            {...register('name', { required: true })}
          />
          <input
            data-testid="category-slug-input"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="category-slug"
            {...register('slug', { required: true })}
          />
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Description"
            {...register('description')}
          />
          <div className="flex gap-2 md:col-span-3">
            <button
              data-testid="category-submit-button"
              type="submit"
              className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white"
              disabled={saveCategoryMutation.isPending}
            >
              {saveCategoryMutation.isPending ? 'Saving...' : selectedCategoryId ? 'Update category' : 'Save category'}
            </button>
            {selectedCategoryId && (
              <button type="button" onClick={onCancelEdit} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">
                Cancel
              </button>
            )}
          </div>
        </form>
        {saveCategoryMutation.isError && (
          <p className="mt-3 text-sm text-danger">
            {saveCategoryMutation.error?.response?.data?.detail || 'Failed to save category.'}
          </p>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3">
          <h3 className="text-base font-semibold text-slate-900">Category list</h3>
          <input
            data-testid="category-search-input"
            value={searchTerm}
            onChange={(event) => {
              setSearchTerm(event.target.value)
              setPage(1)
            }}
            className="mt-3 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm md:max-w-sm"
            placeholder="Search category..."
          />
        </div>
        <div className="p-4">
          {categoriesQuery.isLoading && <p className="text-sm text-slate-500">Loading categories...</p>}
          {categoriesQuery.isError && <p className="text-sm text-danger">Failed to load categories.</p>}
          {categoriesQuery.isSuccess && (
            <div className="overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-0 text-sm">
                <thead>
                  <tr className="bg-blue-50 text-left text-slate-700">
                    <th className="rounded-tl-lg border border-slate-200 px-3 py-2">Name</th>
                    <th className="border border-slate-200 px-3 py-2">Slug</th>
                    <th className="border border-slate-200 px-3 py-2">Description</th>
                    <th className="rounded-tr-lg border border-slate-200 px-3 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCategories.map((category) => (
                    <tr key={category.id} className="hover:bg-slate-50">
                      <td className="border border-slate-200 px-3 py-2">{category.name}</td>
                      <td className="border border-slate-200 px-3 py-2">{category.slug}</td>
                      <td className="border border-slate-200 px-3 py-2">{category.description || '-'}</td>
                      <td className="border border-slate-200 px-3 py-2">
                        <div className="flex items-center gap-2">
                          <button type="button" onClick={() => onEdit(category)} className="rounded border border-slate-300 px-2 py-1 text-xs text-slate-700">
                            Edit
                          </button>
                          <button
                            type="button"
                            onClick={() => onDelete(category.id)}
                            className="rounded border border-danger/30 px-2 py-1 text-xs text-danger"
                            disabled={deleteCategoryMutation.isPending}
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
          {categoriesQuery.isSuccess && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Page {categoriesQuery.data.page} of {totalPages} • Total {categoriesQuery.data.total}
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
          {deleteCategoryMutation.isError && (
            <p className="mt-3 text-sm text-danger">
              {deleteCategoryMutation.error?.response?.data?.detail || 'Failed to delete category.'}
            </p>
          )}
        </div>
      </section>
    </div>
  )
}
