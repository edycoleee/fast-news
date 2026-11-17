# M01 — Project Setup

## Tujuan milestone

M01 adalah tahap fondasi teknis: menyiapkan project frontend, backend, dan container agar aplikasi bisa dijalankan secara terpisah di lingkungan lokal. Fokus utama adalah memastikan project memiliki baseline yang sehat sebelum masuk ke database, authentication, dan fitur bisnis.

## Fokus milestone

- setup React + Vite frontend
- setup FastAPI backend
- setup PostgreSQL untuk development via Docker
- memastikan backend memiliki health endpoint
- memastikan frontend bisa memanggil endpoint backend
- menjaga konfigurasi env dan CORS sesuai dev environment
- menyiapkan workflow development dan production yang jelas
- menyiapkan dokumentasi dasar untuk menjalankan project

## Scope yang dibatasi

Pada M01 kita hanya fokus pada project foundation. Tidak membangun:

- authentication real
- user CRUD
- news CRUD
- RBAC
- category management
- comment moderation
- rich text editor
- file upload
- deployment production penuh

## Arsitektur dasar yang dibuat

### Frontend
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

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pytest

### Infrastructure
- Docker Compose
- Nginx
- Git

## Workflow yang dipilih

### Development workflow
- PostgreSQL berjalan di Docker
- backend berjalan langsung dari terminal lokal
- frontend berjalan langsung dari terminal lokal
- database schema dikelola melalui Alembic migration
- tidak perlu rebuild container untuk perubahan kecil

### Production workflow
- full stack dalam Docker Compose
- db + backend + frontend + nginx
- build image dan deployment lebih terintegrasi

## Design system yang dipakai di M01

Warna utama:

- Primary: #2563EB
- Secondary: #0F4C81
- Success: #10B981
- Warning: #F59E0B
- Danger: #EF4444
- Background: #F8FAFC
- Surface: #FFFFFF
- Text: #111827

Prinsip UI:

- 60% area netral terang
- 30% area navigasi dark blue
- 10% accent blue
- fokus pada readability, whitespace, dan enterprise modern look
- hindari dekorasi visual yang mengganggu fungsi utama

## Struktur folder yang disiapkan

### Frontend
- frontend/
  - src/
  - public/
  - package.json
  - vite.config.js
  - tailwind.config.js
  - postcss.config.js
  - .env.example

### Backend
- backend/
  - app/
  - requirements.txt
  - .env.example
  - alembic.ini
  - Dockerfile
  - tests/

### Root project
- docker-compose.dev.yml
- docker-compose.prod.yml
- docker-compose.yml
- README.md
- docs/
- .gitignore
- .env.example
- nginx/default.conf

## Deliverables M01

### 1. Frontend foundations
- React project initialized via Vite
- app shell siap dikembangkan
- Tailwind CSS aktif
- base styling menggunakan design tokens
- routing skeleton ready
- health status UI untuk cek backend

### 2. Backend foundations
- FastAPI application initialized
- app structure dengan core modules awal
- health endpoint GET /api/health
- CORS configuration sesuai environment development
- validasi basic API respons

### 3. Database & container foundations
- PostgreSQL dev container via Docker Compose
- production compose file untuk stack lengkap
- env variables managed via .env
- healthcheck aktif di DB
- workflow dev vs prod jelas

### 4. Documentation
- README project setup
- workflow development dan production terdokumentasi
- catatan konfigurasi environment
- catatan penggunaan Alembic

## Health endpoint requirement

Backend harus memiliki endpoint berikut:

- GET /api/health

Response minimal:

```json
{
  "status": "ok",
  "service": "backend"
}
```

Tujuan endpoint ini adalah sebagai validasi dasar bahwa service backend berjalan dengan benar.

## CORS requirement

Konfigurasi CORS harus dibatasi untuk origin development yang jelas, misalnya:

- http://localhost:5173
- http://127.0.0.1:5173

Jangan menyalakan CORS yang terlalu luas.

Untuk skenario akses remote LAN (misalnya frontend dibuka dari `http://192.10.10.154:5173`), origin tersebut harus ditambahkan secara eksplisit ke `CORS_ORIGINS`.

## Environment requirement

Semua configuration sensitif harus dipisahkan dari repo dan di-assign ke file .env.example atau environment local.

Contoh variabel:

- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DATABASE_URL
- BACKEND_PORT
- FRONTEND_PORT
- CORS_ORIGINS

## Docker requirement

### Development
- PostgreSQL hanya dipakai di Docker
- backend dan frontend berjalan dari terminal lokal
- tidak perlu rebuild container untuk perubahan kecil

### Production
- semua service digabung di docker-compose prod
- Nginx dan frontend/backend ditempatkan dalam satu stack
- env production dipisah dari env development

## Output yang diharapkan

- project frontend siap dijalankan
- project backend siap dijalankan
- PostgreSQL development service siap dipakai via Docker
- Docker Compose dev dan prod valid
- health endpoint bekerja
- frontend dapat memanggil backend health endpoint
- README memuat cara menjalankan aplikasi
- workflow dev dan prod jelas

## Acceptance criteria

- Docker Compose dev valid dan bisa dijalankan
- Docker Compose prod valid dan bisa dijalankan
- backend service berjalan tanpa error
- frontend service berjalan tanpa error
- GET /api/health success
- CORS terbatas sesuai origin dev
- environment variables aman dan terstruktur
- project bisa digunakan sebagai baseline untuk M02

## Validation checklist

Setelah implementasi:

1. Jalankan docker compose dev untuk database
2. Jalankan backend lokal
3. Jalankan frontend lokal
4. Cek health endpoint backend
5. Cek frontend bisa membuka app dan memanggil endpoint health
6. Validasi compose prod
7. Pastikan tidak ada secret yang masuk ke repo

### Tambahan validasi untuk akses dari komputer lain (remote LAN)

Jika frontend diakses dari perangkat lain dalam jaringan yang sama:

1. Jalankan backend dengan host `0.0.0.0`:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. Pastikan `CORS_ORIGINS` memuat origin frontend remote, contoh:
   ```env
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://192.10.10.154:5173
   ```
3. Pastikan frontend memakai endpoint API yang benar:
   - rekomendasi: `VITE_API_URL=` (kosong) agar fallback otomatis ke host halaman (`<host-frontend>:8000`)
   - hindari hardcode `VITE_API_URL=http://localhost:8000` jika frontend diakses dari komputer lain
4. Jika muncul `Failed to fetch`, cek:
   - backend belum aktif di port `8000`
   - origin frontend belum masuk `CORS_ORIGINS`
   - frontend masih mengarah ke `localhost:8000` saat diakses dari perangkat lain
5. Jika log backend menampilkan `OPTIONS ... 400 Bad Request` dan `Disallowed CORS origin`:
   - pastikan origin remote sudah ada di `CORS_ORIGINS`
   - restart backend setelah update `.env`

## Prompt M01 yang siap pakai

```text
Saya ingin melanjutkan milestone M01 dari NewsHub CMS.

Tujuan milestone:
- setup React + Vite frontend
- setup FastAPI backend
- setup PostgreSQL untuk development via Docker
- memastikan aplikasi bisa berjalan terpisah
- menyiapkan project foundation untuk milestone berikutnya

Scope:
- fokus pada project setup dan foundation
- tidak implementasikan authentication atau modul bisnis
- tidak menambah fitur di luar M01
- hanya setup yang dibutuhkan agar backend dan frontend bisa berjalan

Teknologi:
- Frontend: React, Vite, Tailwind CSS, React Router, TanStack Query, Axios
- Backend: Python, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, PostgreSQL
- Infrastructure: Docker Compose, Nginx, Git

Prinsip arsitektur:
- modular monolith
- frontend dan backend terpisah
- business logic tidak ada di router
- dependency injection untuk service dan session
- database transaction dipelihara di service layer
- semua fitur harus memiliki testing yang relevan di tahap yang sesuai

Workflow dev vs prod:
- development: PostgreSQL di Docker, backend/frontend jalan dari terminal lokal
- production: full stack Docker Compose dengan nginx
- Alembic dipakai untuk migration database

Design system:
- Primary #2563EB
- Secondary #0F4C81
- Success #10B981
- Warning #F59E0B
- Danger #EF4444
- Background #F8FAFC
- Surface #FFFFFF
- Text #111827
- Gunakan 60-30-10 untuk layout visual
- Desain harus professional, clean, readable, enterprise modern

Output yang diharapkan:
- frontend project siap berjalan
- backend project siap berjalan
- PostgreSQL dev service tersedia via Docker
- docker-compose.dev.yml dan docker-compose.prod.yml valid
- health endpoint GET /api/health aktif
- CORS dev terbatas ke origin tertentu
- README berisi instruksi menjalankan aplikasi
- .env.example dan gitignore siap

Acceptance criteria:
- Docker Compose dev valid
- Docker Compose prod valid
- backend berjalan dan /api/health response ok
- frontend dapat berkomunikasi dengan backend
- project tidak menyimpan secret di Git
- project siap menjadi baseline untuk M02

Validation:
- docker compose -f docker-compose.dev.yml config
- docker compose -f docker-compose.prod.yml config
- cek endpoint health backend
- cek frontend loading page
- cek log container apabila error terjadi

Catatan:
- fokus pada foundation saja
- jangan menambah modul lain di luar M01
- jangan mengubah arsitektur tanpa persetujuan
- semua perubahan harus terdokumentasi
- jika ada keputusan arsitektur yang belum jelas, tanyakan sebelum implementasi
```

## Kesimpulan

M01 adalah milestone penting karena semua pengembangan berikutnya bergantung pada foundation yang kuat. Jika setup backend, frontend, dan container sudah benar, dan workflow dev/prod sudah jelas, maka M02 database dan M03 authentication dapat dibangun dengan lebih aman, lebih cepat, dan lebih konsisten.
