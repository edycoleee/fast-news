# M00 — Discovery & Design Foundation

## Tujuan milestone

M00 adalah tahap fondasi arsitektur dan desain NewsHub CMS. Tujuan utamanya adalah memahami kebutuhan produk, menentukan scope yang tepat, dan menyiapkan blueprint visual serta teknis agar milestone selanjutnya tidak ambigu.

## Fokus milestone

- analisis kebutuhan bisnis dan pengguna
- menentukan audience utama dan user flow
- mengidentifikasi modul inti aplikasi
- menetapkan design system awal
- membuat struktur project yang akan dipakai dalam milestone berikutnya
- menulis arsitektur awal dan roadmap yang jelas

## Scope yang dibatasi

Pada M00, kita tidak membangun fitur produk secara penuh. Fokus hanya pada:

- kebutuhan bisnis
- target pengguna
- alur utama aplikasi
- visual identity
- design system
- struktur modul awal
- dokumentasi pondasi proyek

Hal yang tidak termasuk di M00:

- login/logout real
- database production
- CRUD berita penuh
- authentication logic
- RBAC penuh
- deployment production

## Audience utama

### 1. Publik pembaca
- membaca berita terbaru
- mencari topik tertentu
- melihat detail artikel
- melihat kategori
- melihat komentar publik

### 2. Admin / editor
- login ke panel admin
- mengelola berita
- mengatur kategori
- mengelola pengguna dan role
- meninjau komentar
- mengelola file/media
- melihat dashboard summary

## User journey utama

### Publik
1. Pengguna membuka landing page
2. Melihat berita utama dan daftar berita terbaru
3. Mencari berita berdasarkan kata kunci atau kategori
4. Membuka detail berita
5. Menambahkan komentar publik (jika berlaku)

### Admin
1. Admin login ke panel
2. Melihat dashboard ringkasan
3. Mengakses halaman user management
4. Mengelola role dan permission
5. Membuat atau memperbarui berita
6. Mengelola kategori
7. Upload file/media
8. Meninjau komentar dan audit log

## Modul utama yang akan dibangun

- Public site
  - landing page
  - news listing
  - news detail
  - search
  - categories
  - public comments

- Admin panel
  - authentication
  - dashboard
  - user management
  - role management
  - permission management
  - news CRUD
  - category CRUD
  - file management
  - signature approval
  - comment moderation
  - audit log

## Design system

Warna utama yang dipakai sejak awal:

- Primary: #2563EB
- Secondary: #0F4C81
- Success: #10B981
- Warning: #F59E0B
- Danger: #EF4444
- Background: #F8FAFC
- Surface: #FFFFFF
- Text: #111827

Aturan penggunaan warna:

- 60% area dominan netral terang
- 30% navigasi/section sekunder gelap biru
- 10% accent untuk CTA dan elemen aktif
- semantic colors hanya untuk status, alert, dan error
- hindari gradient berlebihan, neon, glassmorphism, dan shadow berlebihan

### Prinsip UI yang dipakai

- professional
- clean
- trustworthy
- accessible
- data-friendly
- enterprise modern

## Layout concept

### Landing page publik
- hero section dengan judul dan CTA utama
- highlight news section
- latest news grid
- kategori populer
- sidebar quick links
- footer informasi

### Halaman detail berita
- judul berita besar
- metadata penulis/tanggal/kategori
- konten utama tulisan
- related news
- komentar publik

### Admin dashboard
- sidebar dark blue
- top header white
- metric cards summary
- table list data
- quick actions
- status badges
- filter/search bar

## Arsitektur awal yang disepakati

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

### Arsitektur aplikasi
- modular monolith
- frontend dan backend dipisah
- router hanya menangani request/response
- service layer untuk business logic
- repository untuk akses data
- dependency injection
- transaction boundary di service/use-case layer

## Output yang diharapkan di M00

1. Design brief dokumentasi awal
2. Arsitektur overview awal
3. User flow dan kebutuhan produk
4. Wireframe concept untuk halaman publik dan admin
5. daftar modul utama yang dibangun pada milestone berikutnya
6. roadmap M00–M12 yang jelas
7. update README dan docs indikator project status

## Acceptance criteria

- kebutuhan produk sudah dijelaskan dengan jelas
- target pengguna dan alur utama sudah terdefinisi
- design system basic sudah dibuat dan konsisten
- struktur modul utama sudah ditentukan
- roadmap milestone sudah tersusun logis
- tidak ada scope yang terlalu luas atau ambigua

## Validation checklist

- review kebutuhan produk
- review user flow
- review design consistency
- review arsitektur awal
- review roadmap logika tahapan
- pastikan milestone berikutnya bisa dibangun dari hasil M00

## Kesimpulan

M00 adalah pondasi penting. Hasil dari milestone ini harus menjadi baseline yang jelas untuk seluruh pengembangan project. Jika fondasi produk, arsitektur, dan visual sudah stabil, maka milestone berikutnya seperti M01 setup dan M02 database akan berjalan lebih terarah, aman, dan efisien.
