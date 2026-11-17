import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { listUsers } from '../api/usersApi'
import {
  assignPermissionToRole,
  assignRoleToUser,
  createPermission,
  createRole,
  deletePermission,
  deleteRole,
  getRolePermissions,
  getUserRoles,
  listPermissions,
  listRoles,
} from '../api/rbacCrudApi'

export function AdminRbacPage() {
  const queryClient = useQueryClient()
  const [selectedRoleId, setSelectedRoleId] = useState('')
  const [selectedPermissionId, setSelectedPermissionId] = useState('')
  const [selectedUserId, setSelectedUserId] = useState('')
  const [selectedRoleForUserId, setSelectedRoleForUserId] = useState('')
  const [selectedUserRoles, setSelectedUserRoles] = useState([])
  const [selectedRolePermissions, setSelectedRolePermissions] = useState([])

  const rolesQuery = useQuery({ queryKey: ['rbac-roles'], queryFn: () => listRoles({ page: 1, pageSize: 100 }), retry: false })
  const permissionsQuery = useQuery({
    queryKey: ['rbac-permissions'],
    queryFn: () => listPermissions({ page: 1, pageSize: 100 }),
    retry: false,
  })
  const usersQuery = useQuery({ queryKey: ['users-rbac'], queryFn: () => listUsers({ page: 1, pageSize: 100 }), retry: false })

  const roleForm = useForm({ defaultValues: { name: '', description: '' } })
  const permissionForm = useForm({ defaultValues: { name: '', resource: '', action: '' } })

  const createRoleMutation = useMutation({
    mutationFn: createRole,
    onSuccess: async () => {
      roleForm.reset()
      await queryClient.invalidateQueries({ queryKey: ['rbac-roles'] })
    },
  })
  const createPermissionMutation = useMutation({
    mutationFn: createPermission,
    onSuccess: async () => {
      permissionForm.reset()
      await queryClient.invalidateQueries({ queryKey: ['rbac-permissions'] })
    },
  })
  const deleteRoleMutation = useMutation({
    mutationFn: deleteRole,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['rbac-roles'] })
    },
  })
  const deletePermissionMutation = useMutation({
    mutationFn: deletePermission,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['rbac-permissions'] })
    },
  })
  const assignPermissionMutation = useMutation({
    mutationFn: ({ roleId, permissionId }) => assignPermissionToRole(roleId, permissionId),
    onSuccess: async (_, variables) => {
      const result = await getRolePermissions(variables.roleId)
      setSelectedRolePermissions(result.permissions)
    },
  })
  const assignRoleMutation = useMutation({
    mutationFn: ({ userId, roleId }) => assignRoleToUser(userId, roleId),
    onSuccess: async (_, variables) => {
      const result = await getUserRoles(variables.userId)
      setSelectedUserRoles(result.roles)
    },
  })

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Tahapan RBAC</h2>
          <p className="text-sm text-slate-600">Ikuti urutan ini agar role & permission tersusun rapi dan mudah diaudit.</p>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <div className="rounded-lg border border-blue-100 bg-blue-50/50 p-3 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">1) Buat Role</p>
            <p>Tentukan peran kerja, contoh: editor, reviewer, admin-content.</p>
          </div>
          <div className="rounded-lg border border-blue-100 bg-blue-50/50 p-3 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">2) Buat Permission</p>
            <p>Definisikan hak akses berbasis resource.action, contoh: news.publish.</p>
          </div>
          <div className="rounded-lg border border-blue-100 bg-blue-50/50 p-3 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">3) Assign Permission ke Role</p>
            <p>Pilih role lalu tempelkan permission sesuai tugas role tersebut.</p>
          </div>
          <div className="rounded-lg border border-blue-100 bg-blue-50/50 p-3 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">4) Assign Role ke User</p>
            <p>Pilih user lalu assign role. Login ulang user untuk verifikasi akses.</p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="text-lg font-semibold text-slate-900">Langkah 1 — Create Role</h2>
          <form className="mt-4 space-y-3" onSubmit={roleForm.handleSubmit((values) => createRoleMutation.mutate(values))}>
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="role name" {...roleForm.register('name', { required: true })} />
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="description" {...roleForm.register('description')} />
            <button className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white">Save role</button>
          </form>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="text-lg font-semibold text-slate-900">Langkah 2 — Create Permission</h2>
          <form className="mt-4 space-y-3" onSubmit={permissionForm.handleSubmit((values) => createPermissionMutation.mutate(values))}>
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="permission name" {...permissionForm.register('name', { required: true })} />
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="resource" {...permissionForm.register('resource', { required: true })} />
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="action" {...permissionForm.register('action', { required: true })} />
            <button className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white">Save permission</button>
          </form>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="text-base font-semibold text-slate-900">Langkah 3 — Assign Permission to Role</h3>
          <div className="mt-3 grid gap-3">
            <select value={selectedRoleId} onChange={(event) => setSelectedRoleId(event.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select role</option>
              {rolesQuery.data?.items?.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </select>
            <select value={selectedPermissionId} onChange={(event) => setSelectedPermissionId(event.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select permission</option>
              {permissionsQuery.data?.items?.map((permission) => (
                <option key={permission.id} value={permission.id}>
                  {permission.name}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={async () => {
                if (selectedRoleId) {
                  const result = await getRolePermissions(selectedRoleId)
                  setSelectedRolePermissions(result.permissions)
                }
              }}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
            >
              Lihat permission role
            </button>
            <button
              type="button"
              onClick={() => {
                if (selectedRoleId && selectedPermissionId) {
                  assignPermissionMutation.mutate({ roleId: selectedRoleId, permissionId: selectedPermissionId })
                }
              }}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white"
            >
              Assign permission
            </button>
            {selectedRoleId && (
              <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700">
                <p className="font-semibold text-slate-900">Permission role saat ini:</p>
                <p className="mt-1">{selectedRolePermissions.length > 0 ? selectedRolePermissions.join(', ') : 'Belum ada permission.'}</p>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="text-base font-semibold text-slate-900">Langkah 4 — Assign Role to User</h3>
          <div className="mt-3 grid gap-3">
            <select value={selectedUserId} onChange={(event) => setSelectedUserId(event.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select user</option>
              {usersQuery.data?.items?.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.username} ({user.email})
                </option>
              ))}
            </select>
            <select value={selectedRoleForUserId} onChange={(event) => setSelectedRoleForUserId(event.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select role</option>
              {rolesQuery.data?.items?.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={async () => {
                if (selectedUserId) {
                  const result = await getUserRoles(selectedUserId)
                  setSelectedUserRoles(result.roles)
                }
              }}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
            >
              Lihat role user
            </button>
            <button
              type="button"
              onClick={() => {
                if (selectedUserId && selectedRoleForUserId) {
                  assignRoleMutation.mutate({ userId: selectedUserId, roleId: selectedRoleForUserId })
                }
              }}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white"
            >
              Assign role
            </button>
            {selectedUserId && (
              <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700">
                <p className="font-semibold text-slate-900">Role user saat ini:</p>
                <p className="mt-1">{selectedUserRoles.length > 0 ? selectedUserRoles.join(', ') : 'Belum ada role.'}</p>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="text-base font-semibold text-slate-900">Referensi Roles</h3>
          <div className="mt-3 space-y-2">
            {rolesQuery.data?.items?.map((role) => (
              <div key={role.id} className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2 text-sm">
                <span>{role.name}</span>
                <button
                  type="button"
                  onClick={() => {
                    if (window.confirm('Delete role ini?')) {
                      deleteRoleMutation.mutate(role.id)
                    }
                  }}
                  className="rounded border border-danger/30 px-2 py-1 text-xs text-danger"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="text-base font-semibold text-slate-900">Referensi Permissions</h3>
          <div className="mt-3 space-y-2">
            {permissionsQuery.data?.items?.map((permission) => (
              <div key={permission.id} className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2 text-sm">
                <span>{permission.name}</span>
                <button
                  type="button"
                  onClick={() => {
                    if (window.confirm('Delete permission ini?')) {
                      deletePermissionMutation.mutate(permission.id)
                    }
                  }}
                  className="rounded border border-danger/30 px-2 py-1 text-xs text-danger"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
