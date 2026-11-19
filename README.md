# NewsHub CMS

NewsHub CMS adalah aplikasi modular monolith untuk mengelola berita internal dan publik dengan frontend dan backend yang terpisah.

## Tujuan proyek

- Menyediakan portal berita publik untuk membaca dan mencari artikel.
- Menyediakan panel admin untuk mengelola berita, kategori, pengguna, role, permission, komentar, dan upload file.
- Menjaga arsitektur aman, terukur, dan siap dikembangkan secara bertahap.

## Stack utama

Frontend:
- React
- Vite
- JavaScript ES Modules
- Tailwind CSS
- React Router
- TanStack Query
- Axios
- React Hook Form
- Zod
- Lucide React
- Tiptap Editor
- Signature Pad

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pytest

Infrastructure:
- Docker Compose
- Nginx
- Git

## Design system utama

Warna standar yang dipakai:
- Primary: #2563EB
- Secondary: #0F4C81
- Success: #10B981
- Warning: #F59E0B
- Danger: #EF4444
- Background: #F8FAFC
- Surface: #FFFFFF
- Text: #111827

Prinsip desain:
- 60% area netral terang
- 30% area navigasi sekunder gelap
- 10% accent untuk CTA utama
- Prioritaskan readability, whitespace, dan data density
- Desain enterprise modern, professional, trustworthy, accessible

## Roadmap utama

Lihat dokumen [docs/roadmap.md](docs/roadmap.md).

## Struktur proyek

- backend/: aplikasi FastAPI dan konfigurasi service
- frontend/: aplikasi React + Vite
- docs/: dokumentasi arsitektur, database, security, roadmap
- .github/instructions/: aturan pengembangan dan milestone

## Status saat ini

M11 Security & Testing telah selesai untuk baseline keamanan. Milestone berikutnya: M12 Deployment.

Status implementasi:
- M00 discovery & design foundation telah disiapkan
- M01 project setup telah selesai
- M02 database schema, model SQLAlchemy, dan migration awal sudah dibuat dan diverifikasi
- M03 authentication backend (session cookie + CSRF + Argon2id) telah diimplementasikan
- M04 RBAC backend (permission enforcement + role/permission assignment API) telah diimplementasikan
- M05 admin shell frontend + login integration ke backend telah diimplementasikan
- M06 category/news CRUD backend + admin UI dasar telah diimplementasikan
- M06 refinement: CRUD users + CRUD RBAC admin page telah diimplementasikan
- M07 rich text editor (Tiptap) + backend sanitization HTML telah diimplementasikan
- M08 file upload management (image/PDF) + validasi backend telah diimplementasikan
- M09 canvas signature, approval record, revoke flow, private signature storage, dan audit trail telah diimplementasikan
- M10 public comment form, pending moderation queue, approve/reject/delete, sanitization, dan audit trail telah diimplementasikan
- M11 runtime security settings, PostgreSQL rate limiting, login cooldown, hard caps, dan audit perubahan setting telah diimplementasikan

## Workflow development vs production

### Development workflow

Pada tahap development, pola yang dipakai adalah:
- PostgreSQL berjalan di Docker
- backend berjalan langsung dari terminal lokal
- frontend berjalan langsung dari terminal lokal
- database schema dikelola melalui Alembic migration
- project tidak perlu rebuild container setiap kali ada perubahan kecil

#### 1. Jalankan PostgreSQL dari Docker

```bash
docker compose -f docker-compose.dev.yml up -d db
```

#### 2. Setup backend lokal

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

#### 3. Jalankan migrasi database

```bash
alembic upgrade head
```

#### 4. Jalankan backend dari terminal

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 5. Setup frontend lokal

```bash
cd frontend
cp .env.example .env
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Periksa:
- Backend: http://localhost:8000/api/health
- Frontend: http://localhost:5173

#### Akses dari komputer lain (remote LAN)

Jika frontend dibuka dari perangkat lain (contoh `http://192.10.10.154:5173`), pastikan:

1. Backend berjalan dengan host `0.0.0.0`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
2. `CORS_ORIGINS` di `backend/.env` berisi origin frontend remote, misalnya:
```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://192.10.10.154:5173
```
3. Frontend **jangan hardcode localhost** saat diakses dari perangkat lain.
   Rekomendasi default:
```env
VITE_API_URL=
```
   Dengan konfigurasi ini, frontend otomatis menggunakan host halaman aktif (`<host-frontend>:8000`).

Jika kartu status frontend menampilkan `Failed to fetch`, penyebab paling umum:
- backend belum berjalan di port `8000`
- origin frontend belum masuk ke `CORS_ORIGINS`
- frontend masih mengarah ke `localhost:8000` saat dibuka dari perangkat lain

Jika log backend menunjukkan:
- `OPTIONS /api/auth/login ... 400 Bad Request`
- `Disallowed CORS origin`

maka penyebabnya hampir pasti konfigurasi CORS origin belum sesuai.
Solusi:
1. Pastikan origin frontend remote masuk ke `CORS_ORIGINS`.
2. Pastikan backend membaca konfigurasi dari settings app (bukan default origin statis).
3. Restart backend setelah mengubah `.env`.

### Production workflow

Pada tahap production, semua service dibundel dalam satu stack Docker Compose untuk deployment yang konsisten:
- database
- backend API
- frontend build/static serve atau app service
- Nginx reverse proxy
- environment config production

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Tujuan produksi:
- cluster service lebih terintegrasi
- build lebih repeatable
- konfigurasi lebih aman
- deployment lebih konsisten

## Penggunaan Alembic

Semua perubahan skema database harus dilakukan melalui migration, bukan perubahan manual di database local yang sedang berjalan.

```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "deskripsi perubahan"
alembic upgrade head
```

Prinsipnya:
- model berubah di code
- migration dibuat otomatis atau manual
- migration dijalankan secara eksplisit
- database tetap aman dan terdokumentasi

## Sinkronisasi permission registry

Permission teknis fitur disimpan dalam `permissions.py` pada setiap module. Setelah menambah fitur atau deploy, sinkronkan permission ke database:

```bash
cd backend
.venv/bin/python -m scripts.sync_permissions
```

Command idempotent. Role dan user assignment tidak otomatis berubah; admin tetap mengaturnya lewat RBAC.

## Environment variables

Secret, database URL, cookie security, CORS, dan provider credential tetap dikelola environment. Batas upload, komentar, dan rate limit dapat diubah dari Admin Settings, tetapi tidak boleh melewati hard cap deployment.

### Development
- DATABASE_URL=postgresql+psycopg://newshub:change_me@localhost:5432/newshub
- BACKEND_PORT=8000
- FRONTEND_PORT=5173
- CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
- SESSION_COOKIE_NAME=newshub_session
- CSRF_COOKIE_NAME=newshub_csrf
- CSRF_HEADER_NAME=X-CSRF-Token
- SESSION_TTL_MINUTES=480
- SESSION_COOKIE_SECURE=false

### Production
- DATABASE_URL=postgresql+psycopg://newshub:change_me@db:5432/newshub
- CORS_ORIGINS=https://app.example.com
- APP_ENV=production
- SESSION_COOKIE_SECURE=true

## Endpoint authentication (M03)

- `POST /api/auth/login`
  - body: `username_or_email`, `password`
  - hasil: set cookie session HttpOnly + cookie CSRF
- `GET /api/auth/me`
  - validasi session aktif dari cookie
- `POST /api/auth/logout`
  - membutuhkan header `X-CSRF-Token` yang sesuai dengan cookie CSRF
  - menonaktifkan session aktif

## Endpoint signature (M09)

- `GET /api/signatures/query` — list signature dengan pagination dan filter status
- `POST /api/signatures` — menyimpan PNG signature dan record approval
- `GET /api/signatures/{signature_id}` — detail signature
- `POST /api/signatures/{signature_id}/revoke` — mencabut signature dengan alasan audit

Operasi perubahan memerlukan permission `signature.manage` atau `news.manage` dan header CSRF yang valid. File signature bersifat privat, tidak dapat diakses melalui endpoint file publik, dan file bukti tidak dapat dihapus selama signature masih tersimpan.

## Endpoint komentar (M10)

- `GET /api/public/news/{slug}/comments`
- `POST /api/public/news/{slug}/comments`
- `GET /api/comments/query`
- `POST /api/comments/{comment_id}/moderate`
- `DELETE /api/comments/{comment_id}`

Komentar publik otomatis berstatus `pending`. Hanya komentar `approved` yang dikembalikan pada endpoint publik. Moderasi memakai permission granular `comment.read`, `comment.moderate`, dan `comment.delete`.

Catatan operasional:
- variabel `SUPERADMIN_*` di `.env` tidak otomatis membuat user di database
- akun admin dev tetap harus dibuat/seed ke tabel `users`

## Endpoint RBAC (M04)

- `POST /api/rbac/roles`
- `POST /api/rbac/permissions`
- `GET /api/rbac/roles/query`
- `PUT /api/rbac/roles/{role_id}`
- `DELETE /api/rbac/roles/{role_id}`
- `GET /api/rbac/permissions/query`
- `PUT /api/rbac/permissions/{permission_id}`
- `DELETE /api/rbac/permissions/{permission_id}`
- `POST /api/rbac/roles/{role_id}/permissions/{permission_id}`
- `POST /api/rbac/users/{user_id}/roles/{role_id}`
- `GET /api/rbac/me/permissions`
- `GET /api/rbac/users/{user_id}/permissions`

Catatan:
- endpoint write RBAC membutuhkan login session aktif, CSRF header, dan permission `rbac.manage`

## Endpoint M06 (Category & News CRUD)

- `GET /api/categories`
- `GET /api/categories/query`
- `POST /api/categories`
- `GET /api/categories/{category_id}`
- `PUT /api/categories/{category_id}`
- `DELETE /api/categories/{category_id}`

- `GET /api/news`
- `GET /api/news/query`
- `POST /api/news`
- `GET /api/news/{news_id}`
- `PUT /api/news/{news_id}`
- `DELETE /api/news/{news_id}`

- `GET /api/files/query`
- `POST /api/files/upload`
- `GET /api/files/{file_id}/download`
- `DELETE /api/files/{file_id}`

Public:
- `GET /api/public/news`
- `GET /api/public/news/{slug}`

Catatan:
- category CRUD memerlukan permission `category.manage`
- news CRUD memerlukan permission `news.manage`
- `GET /api/categories/query` digunakan untuk dropdown kategori di form news dan cukup butuh session login valid
- file management menerima permission `file.manage` atau `news.manage`

## Endpoint Users CRUD (admin)

- `GET /api/users/query`
- `GET /api/users/{user_id}`
- `POST /api/users`
- `PUT /api/users/{user_id}`
- `DELETE /api/users/{user_id}`

Catatan:
- users CRUD membutuhkan permission `rbac.manage`

## Frontend route baseline (M05)

- `/` landing page + backend health check
- `/admin/login` login admin ke endpoint auth backend
- `/admin/dashboard` admin dashboard shell (protected route)
- `/admin/users`, `/admin/rbac`, `/admin/reports` placeholder page untuk milestone lanjutan
- `/admin/categories` category CRUD dasar
- `/admin/news` news CRUD dasar
- halaman admin category/news sudah mendukung create, list, edit, delete, dan search dasar
- `/admin/users` users CRUD
- `/admin/rbac` roles/permissions CRUD + assignment role/permission
- `/news` public news listing
- `/news/:slug` public news detail
- `/admin/files` file upload, list, download, delete

## Bootstrap permission superadmin (dev)

Setelah mengisi `SUPERADMIN_*` di `backend/.env`, jalankan:

```bash
cd backend
source .venv/bin/activate
set -a && . ./.env && set +a
python scripts/seed_superadmin.py
```

Script ini memastikan:
- user superadmin tersedia
- role `superadmin` tersedia
- permission `rbac.manage`, `category.manage`, `news.manage` tersedia
- permission `file.manage` tersedia
- role dan permission ter-assign ke user superadmin

## Catatan penting

- Pastikan port 8000 dan 5173 tidak sedang dipakai oleh service lain di lingkungan yang sama.
- Saat port bentrok, sesuaikan konfigurasi file .env atau config dev.
- Semua secret dan konfigurasi sensitif tidak boleh masuk ke Git.
- Development dan production harus dipisahkan dengan file compose yang berbeda.

### Menutup proses yang bentrok port (uvicorn / npm run dev)

Jika port dipakai proses lain, hentikan berdasarkan PID (jangan pakai `pkill`/`killall`):

```bash
# Cari PID yang memakai port backend (8000)
lsof -ti :8000

# Hentikan proses backend (ganti <PID>)
kill <PID>
```

```bash
# Cari PID yang memakai port frontend (5173)
lsof -ti :5173

# Hentikan proses frontend (ganti <PID>)
kill <PID>
```

Jika proses tidak berhenti dengan `kill`, pakai force stop:

```bash
kill -9 <PID>
```

## Catatan pengembangan

- Setiap milestone harus mematuhi batasan scope dan acceptance criteria.
- Tidak membangun semua modul sekaligus.
- Setiap fitur harus menambahkan uji yang relevan.
- Dokumentasi diperbarui setiap tahapan penting.
