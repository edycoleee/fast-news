import { useMemo, useState } from 'react'
import { Check, Search, X } from 'lucide-react'

export function RolePermissionPicker({
  roleName,
  permissions,
  selectedIds,
  isSaving,
  onSave,
  onClose,
}) {
  const [search, setSearch] = useState('')
  const [draftIds, setDraftIds] = useState(() => new Set(selectedIds))
  const filteredPermissions = useMemo(() => {
    const query = search.trim().toLowerCase()
    if (!query) {
      return permissions
    }
    return permissions.filter((permission) =>
      `${permission.name} ${permission.resource} ${permission.action}`.toLowerCase().includes(query),
    )
  }, [permissions, search])

  const togglePermission = (permissionId) => {
    setDraftIds((current) => {
      const next = new Set(current)
      if (next.has(permissionId)) {
        next.delete(permissionId)
      } else {
        next.add(permissionId)
      }
      return next
    })
  }

  return (
    <div
      data-testid="role-permission-picker"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="permission-picker-title"
    >
      <div className="flex max-h-[85vh] w-full max-w-2xl flex-col rounded-xl bg-white shadow-2xl">
        <div className="flex items-start justify-between border-b border-slate-200 px-5 py-4">
          <div>
            <h3 id="permission-picker-title" className="text-lg font-semibold text-slate-900">
              Permission untuk {roleName}
            </h3>
            <p className="mt-1 text-sm text-slate-600">
              Cari dan centang beberapa permission sekaligus.
            </p>
          </div>
          <button
            data-testid="permission-picker-close"
            type="button"
            onClick={onClose}
            disabled={isSaving}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 disabled:opacity-50"
            aria-label="Tutup pemilih permission"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="border-b border-slate-200 p-4">
          <label className="relative block">
            <span className="sr-only">Cari permission</span>
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              data-testid="permission-picker-search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="w-full rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              placeholder="Cari permission, resource, atau action..."
              autoFocus
            />
          </label>
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-600">
            <span className="rounded-full bg-blue-50 px-2 py-1 font-medium text-primary">
              {draftIds.size} dipilih
            </span>
            <button
              type="button"
              onClick={() =>
                setDraftIds((current) => {
                  const next = new Set(current)
                  filteredPermissions.forEach((item) => next.add(item.id))
                  return next
                })
              }
              className="font-semibold text-primary hover:underline"
            >
              Pilih hasil pencarian
            </button>
            <button
              type="button"
              onClick={() => setDraftIds(new Set())}
              className="font-semibold text-slate-600 hover:underline"
            >
              Hapus semua
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          {filteredPermissions.length === 0 && (
            <p className="p-6 text-center text-sm text-slate-500">
              Tidak ada permission yang cocok.
            </p>
          )}
          <div className="grid gap-2 md:grid-cols-2">
            {filteredPermissions.map((permission) => {
              const checked = draftIds.has(permission.id)
              return (
                <label
                  key={permission.id}
                  className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition ${
                    checked
                      ? 'border-primary bg-blue-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => togglePermission(permission.id)}
                    className="mt-0.5 h-4 w-4 accent-primary"
                  />
                  <span className="min-w-0 flex-1">
                    <span className="block break-words text-sm font-semibold text-slate-900">
                      {permission.name}
                    </span>
                    <span className="mt-1 block text-xs text-slate-500">
                      {permission.resource} · {permission.action}
                    </span>
                  </span>
                  {checked && <Check className="h-4 w-4 shrink-0 text-primary" />}
                </label>
              )
            })}
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-slate-200 px-5 py-4">
          <button
            type="button"
            onClick={onClose}
            disabled={isSaving}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 disabled:opacity-50"
          >
            Batal
          </button>
          <button
            data-testid="permission-picker-save"
            type="button"
            onClick={() => onSave(Array.from(draftIds))}
            disabled={isSaving}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
          >
            {isSaving ? 'Menyimpan...' : `Simpan ${draftIds.size} permission`}
          </button>
        </div>
      </div>
    </div>
  )
}
