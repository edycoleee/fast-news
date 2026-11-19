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
- Accent: #14B8A6
- Background: #F8FAFC
- Surface: #FFFFFF
- Text: #0B1220

Aturan penggunaan warna:

- 60% area dominan netral terang
- 30% navigasi/section sekunder gelap biru
- 10% accent untuk CTA dan elemen aktif
- semantic colors hanya untuk status, alert, dan error
- hindari gradient berlebihan, neon, glassmorphism, dan shadow berlebihan

### Implementasi visual Tailwind

Desain UI mengikuti arah SaaS modern yang profesional, bersih, premium, dan tetap konsisten dengan prinsip enterprise NewsHub.

#### Typography

- font utama: Inter dengan fallback Segoe UI dan sans-serif;
- heading menggunakan tracking rapat dan hierarchy tegas;
- body copy ringkas, mudah dipindai, dan mengutamakan readability;
- headline: besar, langsung menjelaskan nilai;
- deskripsi: pendek dan tidak bertele-tele;
- CTA: jelas dan berbentuk action verb.

#### Radius, border, dan spacing

- border radius umum: `rounded-xl`;
- card/hero utama: `rounded-2xl` atau `rounded-3xl`;
- border tipis menggunakan slate `200/80`;
- container utama menggunakan `max-w-7xl mx-auto`;
- spacing mobile-first dengan breakpoint `sm`, `md`, `lg`, dan `xl`;
- jarak antar section lebih longgar dibanding jarak antar elemen dalam form.

#### Card

Card produk menggunakan pola:

```html
bg-white border border-slate-200/80 rounded-2xl shadow-card
```

Aturan card:

- feature card publik boleh bergerak sedikit saat hover;
- card operasional admin tetap stabil agar tidak mengganggu aktivitas data;
- shadow default lembut;
- shadow lebih kuat hanya untuk modal atau hover card publik;
- isi card tersusun sebagai ikon/status, judul, deskripsi/nilai, dan action.

#### Glassmorphism dan gradient

Glassmorphism bukan gaya utama NewsHub.

Penggunaan yang diperbolehkan:

- navbar publik;
- overlay/hero publik;
- panel status hero;
- modal overlay transparan.

Penggunaan yang dihindari:

- tabel admin;
- form data penting;
- seluruh dashboard;
- card operasional berisi data padat.

Gradient hanya dipakai terbatas untuk meningkatkan keterbacaan hero atau membedakan layer visual. Jangan memakai gradient sebagai latar semua card atau panel.

#### Micro-interaction

- durasi transisi umum: 200–300ms;
- hover card publik boleh menggunakan `hover:-translate-y-1`;
- tabel dan control admin memakai hover border/background yang ringan;
- focus-visible harus terlihat untuk keyboard navigation;
- animasi dekoratif harus dihormati dengan preferensi reduced-motion;
- state loading, disabled, success, empty, dan error harus terlihat jelas.

#### Warna dan kontras

- primary blue dipakai untuk action utama dan focus;
- secondary blue dipakai untuk navigasi dan struktur utama;
- accent teal dipakai terbatas untuk health/status dan detail visual;
- success, warning, dan danger hanya untuk status semantik;
- text utama memakai slate sangat gelap agar kontras tetap tinggi;
- elemen penting tidak boleh bergantung hanya pada warna; gunakan label atau ikon.

### Perbedaan konteks public dan admin

#### Public site

- lebih ekspresif dan premium;
- hero kuat, sticky navbar, feature cards, dan footer;
- glassmorphism terbatas;
- CTA jelas;
- content-first dan nyaman dibaca.

#### Admin site

- enterprise, data-dense, dan operasional;
- sidebar dark blue dengan navigasi jelas;
- header sticky putih;
- tabel, filter, modal, dan form mengutamakan stabilitas;
- glassmorphism tidak digunakan pada data;
- shadow dan animasi lebih kecil.

### Komponen UI reusable

Desain harus dibangun melalui reusable components, bukan class ad hoc yang terus diduplikasi:

- `Button`
- `Card`
- `Badge`
- `PageHeader`
- `Modal`
- `Input` / `Select` / `Textarea`
- `EmptyState`
- `LoadingState`
- `ErrorState`
- `DataTable`

Utility global yang disetujui:

- `surface-card`
- `field-control`
- `button-primary`
- `button-secondary`

Komponen dan utility tersebut membantu menjaga warna, spacing, radius, focus, dan transisi tetap konsisten di seluruh modul.

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

### Standar tanggal dan waktu lintas fitur

Semua waktu dalam NewsHub mengikuti kontrak tunggal agar perilaku antar server, API, dan perangkat pengguna konsisten.

- database menyimpan waktu basis UTC;
- model baru sebaiknya menggunakan datetime timezone-aware;
- API mengirim timestamp ISO 8601 dengan timezone, contoh `2026-11-18T02:26:28+00:00`;
- frontend tidak boleh menganggap timestamp API sebagai waktu lokal tanpa mengetahui timezone;
- timestamp legacy tanpa offset diperlakukan sebagai UTC untuk kompatibilitas;
- UI mengonversi timestamp ke timezone lokal browser saat ditampilkan;
- format UI Indonesia menggunakan tanggal lokal dan jam singkat, contoh `18 Nov 2026, 09.26`;
- label waktu menjelaskan maknanya, misalnya `Dikirim`, `Dimoderasi`, atau `Dipublikasikan`;
- timestamp invalid menggunakan fallback aman dan tidak menyebabkan crash.

Alur waktu standar:

```text
database UTC
    -> API ISO 8601 ber-timezone
    -> parser bersama frontend
    -> Intl.DateTimeFormat
    -> waktu lokal browser
```

Parsing dan formatting frontend menggunakan helper bersama, bukan `new Date(value).toLocaleString(...)` berulang di setiap halaman. Dengan helper ini, konversi UTC ke Asia/Jakarta atau timezone browser lain tetap konsisten.

#### Checklist waktu untuk fitur baru

- [ ] field datetime baru memiliki definisi timezone yang jelas;
- [ ] response API menghasilkan ISO 8601 ber-timezone;
- [ ] data legacy tanpa timezone mempunyai aturan kompatibilitas;
- [ ] halaman memakai formatter tanggal bersama;
- [ ] UI menampilkan label peristiwa dan waktu lokal;
- [ ] timestamp kosong atau invalid ditangani;
- [ ] test mencakup timestamp dengan offset dan timestamp legacy tanpa offset.

### Standar RBAC lintas fitur

NewsHub menggunakan pola **Permission-as-Code + Role-as-Data** sebagai fondasi pengembangan seluruh fitur.

- developer mendefinisikan permission teknis pada `permissions.py` milik setiap module;
- format permission wajib `<resource>.<action>`, contoh `signature.create`;
- permission module didaftarkan pada central registry;
- command sinkronisasi memasukkan permission registry ke database secara idempotent;
- role, relasi role-permission, dan relasi user-role tetap menjadi data database;
- admin menentukan role yang menerima permission melalui RBAC;
- user tidak seharusnya mendapat permission langsung di luar role;
- backend endpoint memeriksa permission, bukan nama role;
- frontend membaca permission hanya untuk UX, bukan sebagai otoritas keamanan;
- operasi sensitif tetap memerlukan CSRF dan audit log;
- permission yang berasal dari registry tidak boleh diubah atau dihapus melalui CRUD RBAC biasa.

Alur standar:

```text
feature permissions.py
    -> central permission registry
    -> sync_permissions command
    -> tabel permissions
    -> role_permission
    -> user_role
    -> permission guard pada endpoint
```

Role tidak di-hardcode pada fitur. Assignment role juga tidak di-hardcode. Hanya identifier permission yang eksplisit di kode karena endpoint harus mengetahui kemampuan teknis yang diperiksa.

Contoh pemetaan minimum untuk sebuah fitur approval:

| Operasi | Permission |
|---|---|
| melihat data | `signature.read` |
| membuat approval | `signature.create` |
| mencabut approval | `signature.revoke` |

Permission `manage` boleh dipakai sebagai kompatibilitas atau akses pengelolaan luas. Operasi sensitif tetap sebaiknya mempunyai permission granular sendiri.

#### Checklist M00 untuk setiap fitur baru

- [ ] resource dan action sudah ditentukan;
- [ ] module memiliki `permissions.py`;
- [ ] permission masuk central registry;
- [ ] permission mengikuti format `resource.action`;
- [ ] role tidak di-hardcode di endpoint/service;
- [ ] sync command idempotent dan dapat dicatat;
- [ ] endpoint memiliki backend permission guard;
- [ ] write request memiliki CSRF protection;
- [ ] aksi penting menghasilkan audit log;
- [ ] test tanpa permission menghasilkan 403;
- [ ] test permission lain tidak mendapat akses;
- [ ] dokumentasi matriks endpoint-permission diperbarui.
- [ ] tampilan waktu mengikuti standar UTC-to-local.
- [ ] UI memakai design tokens dan reusable components;
- [ ] layout responsif diuji pada mobile dan desktop;
- [ ] focus-visible, contrast, loading, error, dan empty state diperiksa;
- [ ] glassmorphism/gradient tidak mengganggu readability atau density.

Detail implementasi dan operasional RBAC dijaga pada [docs/m04-rbac.md](m04-rbac.md).

## Output yang diharapkan di M00

1. Design brief dokumentasi awal
2. Arsitektur overview awal
3. User flow dan kebutuhan produk
4. Wireframe concept untuk halaman publik dan admin
5. daftar modul utama yang dibangun pada milestone berikutnya
6. roadmap M00–M12 yang jelas
7. update README dan docs indikator project status
8. standar permission registry dan role-as-data untuk seluruh fitur
9. standar timestamp API ISO 8601 dan waktu lokal browser
10. sistem visual Tailwind reusable dan aksesibel

## Acceptance criteria

- kebutuhan produk sudah dijelaskan dengan jelas
- target pengguna dan alur utama sudah terdefinisi
- design system basic sudah dibuat dan konsisten
- struktur modul utama sudah ditentukan
- roadmap milestone sudah tersusun logis
- tidak ada scope yang terlalu luas atau ambigua
- setiap fitur baru memiliki dasar RBAC yang konsisten
- tampilan waktu mengikuti standar UTC-to-local yang konsisten
- public site premium dan admin site enterprise menggunakan komponen visual yang konsisten

## Validation checklist

- review kebutuhan produk
- review user flow
- review design consistency
- review arsitektur awal
- review roadmap logika tahapan
- pastikan milestone berikutnya bisa dibangun dari hasil M00
- pastikan fitur baru mengikuti checklist permission registry dan backend guard
- pastikan timestamp API dan format waktu UI mengikuti standar lintas fitur
- review mobile-first, keyboard focus, kontras, dan reduced-motion

## Kesimpulan

M00 adalah pondasi penting. Hasil dari milestone ini harus menjadi baseline yang jelas untuk seluruh pengembangan project. Jika fondasi produk, arsitektur, dan visual sudah stabil, maka milestone berikutnya seperti M01 setup dan M02 database akan berjalan lebih terarah, aman, dan efisien.
