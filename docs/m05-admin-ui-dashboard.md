# M05 — Admin UI & Dashboard

## Tujuan milestone

M05 membangun baseline antarmuka admin profesional dan mulai menghubungkan frontend ke flow autentikasi backend.

## Scope implementasi

- admin layout dengan sidebar + topbar
- dashboard cards dan tabel ringkas
- route admin yang terstruktur
- login page frontend terhubung ke API auth backend
- protected route berbasis session check (`/api/auth/me`)
- integrasi permission summary dari endpoint RBAC

## Struktur frontend yang ditambahkan

- `src/app/router.jsx`
- `src/app/query-client.js`
- `src/shared/api/client.js`
- `src/features/public/pages/LandingPage.jsx`
- `src/features/auth/api/authApi.js`
- `src/features/auth/schemas/loginSchema.js`
- `src/features/auth/hooks/useAuth.js`
- `src/features/auth/components/RequireAuth.jsx`
- `src/features/auth/pages/AdminLoginPage.jsx`
- `src/features/admin/layout/AdminLayout.jsx`
- `src/features/admin/pages/AdminDashboardPage.jsx`
- `src/features/admin/api/rbacApi.js`

## Kontrak route M05

- `/`
- `/admin/login`
- `/admin/dashboard`
- `/admin/users` (placeholder)
- `/admin/rbac` (placeholder)
- `/admin/reports` (placeholder)

## Prinsip arsitektur frontend yang diterapkan

- React Router untuk routing terpusat di `app/router.jsx`
- TanStack Query untuk server state (`auth me`, `health`, `permissions`)
- Axios centralized client di `shared/api/client.js`
- Form login menggunakan React Hook Form + Zod validation
- state loading/error ditangani di halaman login dan dashboard

## Validasi

Perintah validasi yang dijalankan:

```bash
cd frontend
npm run build
```

Hasil: build berhasil.

Regression backend juga dijalankan:

```bash
pytest backend/tests/test_auth.py backend/tests/test_rbac.py backend/tests/test_health.py
```

Hasil: seluruh test lulus.

## Catatan lanjutan

- Halaman CRUD admin detail akan diisi bertahap pada milestone fitur berikutnya.
- UI management RBAC detail (form role/permission) dapat mulai diintegrasikan setelah tahap CRUD admin aktif.

## Troubleshooting penting (remote login)

Jika login di `/admin/login` gagal padahal endpoint login backend terlihat `200`:

1. cek `VITE_API_URL` frontend
   - gunakan `VITE_API_URL=` untuk fallback otomatis ke host aktif
   - hindari hardcode `http://localhost:8000` saat akses dari komputer lain
2. cek log backend untuk preflight:
   - jika ada `OPTIONS /api/auth/login ... 400` dan `Disallowed CORS origin`, maka origin frontend belum diizinkan
3. pastikan `CORS_ORIGINS` memuat origin frontend remote dan restart backend
