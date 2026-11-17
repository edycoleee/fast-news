# M06 — News & Category CRUD

## Tujuan milestone

M06 mengaktifkan fitur inti CMS: manajemen kategori dan berita di backend serta baseline UI admin untuk operasi CRUD.

## Scope implementasi

- backend Category CRUD (admin)
- backend News CRUD (admin)
- endpoint public untuk daftar dan detail berita published
- enforce authorization berbasis permission:
  - `category.manage`
  - `news.manage`
- admin UI dasar:
  - create/list/edit/delete category
  - create/list/edit/delete news
  - search dasar pada tabel category dan news
  - users CRUD admin
  - RBAC CRUD admin (roles & permissions)

## Backend module baru

- `app/modules/categories/*`
- `app/modules/news/*`

Terintegrasi di:
- `app/main.py`

## Endpoint backend

Category (admin):
- `GET /api/categories`
- `GET /api/categories/query?page=&page_size=&search=`
- `POST /api/categories`
- `GET /api/categories/{category_id}`
- `PUT /api/categories/{category_id}`
- `DELETE /api/categories/{category_id}`

News (admin):
- `GET /api/news`
- `GET /api/news/query?page=&page_size=&search=&status_filter=`
- `POST /api/news`
- `GET /api/news/{news_id}`
- `PUT /api/news/{news_id}`
- `DELETE /api/news/{news_id}`

News (public):
- `GET /api/public/news`
- `GET /api/public/news/{slug}`

## Frontend update

Route admin baru:
- `/admin/categories`
- `/admin/news`

File utama:
- `frontend/src/features/admin/pages/AdminCategoriesPage.jsx`
- `frontend/src/features/admin/pages/AdminNewsPage.jsx`
- `frontend/src/features/admin/pages/AdminUsersPage.jsx`
- `frontend/src/features/admin/pages/AdminRbacPage.jsx`
- `frontend/src/features/public/pages/LandingPage.jsx`
- `frontend/src/features/public/pages/PublicNewsListPage.jsx`
- `frontend/src/features/public/pages/PublicNewsDetailPage.jsx`
- `frontend/src/features/admin/api/categoryApi.js`
- `frontend/src/features/admin/api/newsApi.js`
- `frontend/src/features/admin/api/usersApi.js`
- `frontend/src/features/admin/api/rbacCrudApi.js`
- `frontend/src/features/public/api/publicNewsApi.js`
- `frontend/src/shared/api/client.js`

Fitur UI tambahan:
- konfirmasi sebelum delete category/news
- search category/news
- pagination category/news
- filter status untuk daftar news
- halaman Users menampilkan role per user
- halaman RBAC dapat menampilkan daftar permission yang dimiliki role terpilih
- card "Public newsroom" pada landing terhubung ke halaman list berita publik
- halaman list publik (`/news`) dan detail artikel (`/news/:slug`) membaca data dari endpoint public news

Catatan permission:
- endpoint `GET /api/categories/query` dipakai juga untuk dropdown kategori pada form news, sehingga cukup membutuhkan session login valid.
- parameter `page_size` pada endpoint query dibatasi maksimal `100`; gunakan nilai `<=100` pada frontend agar tidak terkena `422`.

## Bootstrap permission superadmin

Untuk memastikan akun superadmin bisa langsung memakai endpoint RBAC + M06:

```bash
cd backend
source .venv/bin/activate
set -a && . ./.env && set +a
python scripts/seed_superadmin.py
```

Script:
- `backend/scripts/seed_superadmin.py`

## Validasi

Backend tests:

```bash
pytest backend/tests/test_m06_cms.py backend/tests/test_auth.py backend/tests/test_rbac.py backend/tests/test_health.py
```

Frontend build:

```bash
cd frontend
npm run build
```

Semua validasi di atas lulus pada implementasi ini.
Users (admin):
- `GET /api/users/query?page=&page_size=&search=`
- `GET /api/users/{user_id}`
- `POST /api/users`
- `PUT /api/users/{user_id}`
- `DELETE /api/users/{user_id}`

RBAC (admin):
- `GET /api/rbac/roles/query?page=&page_size=&search=`
- `POST /api/rbac/roles`
- `PUT /api/rbac/roles/{role_id}`
- `DELETE /api/rbac/roles/{role_id}`
- `GET /api/rbac/permissions/query?page=&page_size=&search=`
- `POST /api/rbac/permissions`
- `PUT /api/rbac/permissions/{permission_id}`
- `DELETE /api/rbac/permissions/{permission_id}`
- `POST /api/rbac/roles/{role_id}/permissions/{permission_id}`
- `POST /api/rbac/users/{user_id}/roles/{role_id}`
- `GET /api/rbac/users/{user_id}/roles`
- `GET /api/rbac/roles/{role_id}/permissions`

