import { useState } from 'react'
import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { getUserRoles } from '../api/rbacCrudApi'
import { createUser, deleteUser, listUsers, updateUser } from '../api/usersApi'

const EMPTY_FORM = { username: '', email: '', password: '', is_active: true }

export function AdminUsersPage() {
  const queryClient = useQueryClient()
  const [selectedUserId, setSelectedUserId] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 10
  const usersQuery = useQuery({
    queryKey: ['users', { page, pageSize, searchTerm }],
    queryFn: () => listUsers({ page, pageSize, search: searchTerm }),
    retry: false,
  })
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: EMPTY_FORM })
  const userRoleQueries = useQueries({
    queries: (usersQuery.data?.items ?? []).map((user) => ({
      queryKey: ['user-roles', user.id],
      queryFn: () => getUserRoles(user.id),
      enabled: usersQuery.isSuccess,
      retry: false,
    })),
  })

  const saveUserMutation = useMutation({
    mutationFn: ({ userId, payload }) => (userId ? updateUser(userId, payload) : createUser(payload)),
    onSuccess: async () => {
      setSelectedUserId(null)
      reset(EMPTY_FORM)
      await queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
  const deleteUserMutation = useMutation({
    mutationFn: deleteUser,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  const onSubmit = (values) => {
    const payload = { ...values }
    if (selectedUserId && !payload.password) {
      delete payload.password
    }
    saveUserMutation.mutate({ userId: selectedUserId, payload })
  }

  const onEdit = (user) => {
    setSelectedUserId(user.id)
    setValue('username', user.username)
    setValue('email', user.email)
    setValue('password', '')
    setValue('is_active', user.is_active)
  }

  const onCancel = () => {
    setSelectedUserId(null)
    reset(EMPTY_FORM)
  }

  const totalPages = usersQuery.data ? Math.max(1, Math.ceil(usersQuery.data.total / usersQuery.data.page_size)) : 1

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">{selectedUserId ? 'Edit User' : 'Create User'}</h2>
        <form className="mt-4 grid gap-3 md:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Username" {...register('username', { required: true })} />
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Email" {...register('email', { required: true })} />
          <input className="rounded-lg border border-slate-300 px-3 py-2 text-sm" type="password" placeholder={selectedUserId ? 'New password (optional)' : 'Password'} {...register('password', { required: !selectedUserId })} />
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" {...register('is_active')} />
            Active
          </label>
          <div className="flex gap-2 md:col-span-2">
            <button type="submit" className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white" disabled={saveUserMutation.isPending}>
              {saveUserMutation.isPending ? 'Saving...' : selectedUserId ? 'Update user' : 'Save user'}
            </button>
            {selectedUserId && (
              <button type="button" onClick={onCancel} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">
                Cancel
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3">
          <h3 className="text-base font-semibold text-slate-900">Users</h3>
          <input
            value={searchTerm}
            onChange={(event) => {
              setSearchTerm(event.target.value)
              setPage(1)
            }}
            className="mt-3 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm md:max-w-sm"
            placeholder="Search users..."
          />
        </div>
        <div className="p-4">
          {usersQuery.isLoading && <p className="text-sm text-slate-500">Loading users...</p>}
          {usersQuery.isError && <p className="text-sm text-danger">Failed to load users.</p>}
          {usersQuery.isSuccess && (
            <div className="overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-0 text-sm">
                <thead>
                  <tr className="bg-blue-50 text-left text-slate-700">
                    <th className="rounded-tl-lg border border-slate-200 px-3 py-2">Username</th>
                    <th className="border border-slate-200 px-3 py-2">Email</th>
                    <th className="border border-slate-200 px-3 py-2">Active</th>
                    <th className="border border-slate-200 px-3 py-2">Roles</th>
                    <th className="rounded-tr-lg border border-slate-200 px-3 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {usersQuery.data.items.map((user, index) => {
                    const roleQuery = userRoleQueries[index]
                    return (
                      <tr key={user.id} className="hover:bg-slate-50">
                        <td className="border border-slate-200 px-3 py-2">{user.username}</td>
                        <td className="border border-slate-200 px-3 py-2">{user.email}</td>
                        <td className="border border-slate-200 px-3 py-2">{user.is_active ? 'Yes' : 'No'}</td>
                        <td className="border border-slate-200 px-3 py-2">
                          {roleQuery?.isLoading && 'Loading...'}
                          {roleQuery?.isError && 'Failed to load'}
                          {roleQuery?.isSuccess && (roleQuery.data.roles.length > 0 ? roleQuery.data.roles.join(', ') : '-')}
                        </td>
                        <td className="border border-slate-200 px-3 py-2">
                          <div className="flex items-center gap-2">
                            <button type="button" onClick={() => onEdit(user)} className="rounded border border-slate-300 px-2 py-1 text-xs text-slate-700">
                              Edit
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                if (window.confirm('Hapus user ini?')) {
                                  deleteUserMutation.mutate(user.id)
                                }
                              }}
                              className="rounded border border-danger/30 px-2 py-1 text-xs text-danger"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
          {usersQuery.isSuccess && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Page {usersQuery.data.page} of {totalPages} • Total {usersQuery.data.total}
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
        </div>
      </section>
    </div>
  )
}
