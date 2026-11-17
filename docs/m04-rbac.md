# M04 — RBAC

## Tujuan milestone

M04 memastikan kontrol akses dijalankan dari backend melalui role dan permission yang terstruktur.

## Scope implementasi

- backend permission enforcement
- API role/permission management untuk admin
- API role assignment ke user
- API membaca permission user
- audit log untuk aksi RBAC penting

## Endpoint RBAC

- `POST /api/rbac/roles`
- `POST /api/rbac/permissions`
- `POST /api/rbac/roles/{role_id}/permissions/{permission_id}`
- `POST /api/rbac/users/{user_id}/roles/{role_id}`
- `GET /api/rbac/me/permissions`
- `GET /api/rbac/me/roles`
- `GET /api/rbac/users/{user_id}/permissions`
- `GET /api/rbac/users/{user_id}/roles`
- `GET /api/rbac/roles/{role_id}/permissions`

## Aturan keamanan

- Semua endpoint write RBAC memerlukan:
  - session login valid
  - CSRF header yang valid (`X-CSRF-Token`)
  - permission `rbac.manage`
- Endpoint read `/api/rbac/users/{user_id}/permissions` juga dibatasi dengan permission `rbac.manage`.

## Struktur modul

- `app/modules/rbac/router.py`
- `app/modules/rbac/service.py`
- `app/modules/rbac/repository.py`
- `app/modules/rbac/schemas.py`
- `app/modules/rbac/dependencies.py`

Integrasi auth:

- dependency `require_permission(...)` menggunakan session auth aktif
- dependency `require_csrf_protection` dipakai untuk endpoint write

## Testing

File:

- `backend/tests/test_rbac.py`

Skenario:

- user tanpa `rbac.manage` mendapat `403 Forbidden` pada endpoint write RBAC
- user dengan `rbac.manage` dapat:
  - create role
  - create permission
  - assign permission ke role
  - assign role ke user
  - membaca permission milik sendiri

## Validasi

Jalankan:

```bash
pytest backend/tests/test_auth.py backend/tests/test_rbac.py backend/tests/test_health.py
```

Hasil terakhir: seluruh test lulus.

## Catatan lanjutan

- UI management RBAC di frontend akan dilanjutkan pada milestone UI admin.
- Seeder data role/permission default bisa ditambahkan pada tahap hardening/ops berikutnya agar bootstrap produksi lebih mudah.

## Alur operasional RBAC (disarankan)

1. Buat role terlebih dahulu sesuai fungsi kerja.
2. Buat permission dengan pola `resource.action`.
3. Assign permission ke role.
4. Assign role ke user.
5. Verifikasi hasil:
   - cek role user (`GET /api/rbac/users/{user_id}/roles`)
   - cek permission role (`GET /api/rbac/roles/{role_id}/permissions`)
   - uji akses user setelah login ulang.

## Jika ada fitur baru, apa yang harus dilakukan pada RBAC?

Setiap fitur baru wajib dievaluasi terhadap RBAC agar akses tetap aman dan terukur.

1. Definisikan aksi fitur baru (contoh: approve, reject, export, archive).
2. Tentukan permission baru dengan format `resource.action` (contoh: `news.approve`).
3. Mapping permission ke role yang tepat (least privilege).
4. Terapkan pengecekan permission di backend endpoint terkait.
5. Sesuaikan UI frontend berdasarkan permission untuk UX yang konsisten.
6. Verifikasi dengan skenario multi-role (boleh vs tidak boleh).

### Contoh singkat

Fitur baru: **Approval Berita**
- Permission:
  - `news.approve`
  - `news.reject`
- Mapping contoh:
  - `editor`: tidak memiliki `news.approve`/`news.reject`
  - `reviewer`: memiliki `news.approve`/`news.reject`
  - `superadmin`: memiliki semua permission

### Checklist implementasi fitur baru (RBAC)

- [ ] Permission baru sudah ditambahkan (atau reuse permission lama sudah disetujui)
- [ ] Role mapping sudah ditetapkan
- [ ] Backend authorization sudah enforced
- [ ] UI sudah menyesuaikan permission
- [ ] Test authorization positif/negatif sudah lulus
- [ ] Dokumentasi endpoint + mapping role diperbarui
