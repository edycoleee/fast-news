# Roadmap Pengembangan NewsHub CMS

## Master tahapan

Project dibangun secara bertahap dan edukatif dengan pendekatan full-stack yang konsisten. Setiap milestone memiliki fokus utama, tetapi frontend dan backend tetap berkembang bersama secara proporsional.

## Design system yang dipakai sejak awal

Warna utama:
- Primary: #2563EB
- Secondary: #0F4C81
- Success: #10B981
- Warning: #F59E0B
- Danger: #EF4444
- Background: #F8FAFC
- Surface: #FFFFFF
- Text: #111827

Aturan visual:
- 60% netral terang
- 30% navigasi gelap
- 10% accent action
- prioritaskan readability dan data density
- hindari dekorasi visual yang mengganggu penggunaan

## Urutan milestone yang disarankan

### M00 — Discovery & Design Foundation
Tujuan:
- analisis kebutuhan bisnis dan pengguna
- menentukan audience publik dan admin
- membuat blueprint arsitektur dan roadmap
- menyusun design system awal

Fokus utama:
- user journey
- wireframe
- modul utama
- kontrak visual

Output:
- design brief
- architecture brief
- roadmap awal
- layout concept public dan admin

### M01 — Project Setup
Tujuan:
- menyiapkan frontend, backend, dan container dasar

Fokus utama:
- React + Vite
- FastAPI
- PostgreSQL dan Docker Compose
- health endpoint
- env configuration
- CORS dev

Output:
- frontend dan backend berjalan terpisah
- health endpoint /api/health
- README dan environment baseline

### M02 — Database & Schema
Tujuan:
- membangun foundation data untuk seluruh fitur utama

Fokus utama:
- SQLAlchemy models
- Alembic migrations
- ERD awal
- constraints, relation, index

Output:
- schema dasar user, role, permission, category, news, comment, file asset, audit log
- migration awal

### M03 — Authentication
Tujuan:
- memastikan sistem auth aman untuk admin dan user

Fokus utama:
- backend auth API
- password hashing Argon2id
- secure cookies
- session management
- frontend login page
- testing auth

Output:
- login/logout secure flow
- session protection

### M04 — RBAC
Tujuan:
- mengelola user, role, permission, dan access control

Fokus utama:
- backend permission enforcement
- admin user management API
- role & permission UI
- frontend access control
- testing authorization

Output:
- role assignment dan permission checking yang konsisten

### M05 — Admin UI & Dashboard
Tujuan:
- membangun shell admin dan dashboard professional

Fokus utama:
- sidebar dan topbar
- dashboard cards
- reusable layout
- frontend admin shell
- backend endpoints untuk statistic ringkas
- UI integration dan testing

Output:
- admin page siap untuk dashboard module lanjutan

### M06 — News & Category CRUD
Tujuan:
- membangun fitur utama CMS berita

Fokus utama:
- backend CRUD API news dan category
- frontend admin CRUD interface
- public listing dan detail page
- validation dan testing

Output:
- admin dapat membuat dan mengelola berita
- publik dapat melihat daftar dan detail berita

### M07 — Rich Text Editor
Tujuan:
- memudahkan editor menulis konten dengan format rich text

Fokus utama:
- Tiptap editor frontend
- backend sanitization untuk HTML
- save/publish flow
- UX editing dan testing

Output:
- artikel dapat dibuat dengan editor rich text aman

### M08 — File Upload
Tujuan:
- menyediakan media management untuk image dan PDF

Fokus utama:
- backend upload validation
- frontend upload area
- preview file
- metadata file
- security testing

Output:
- upload file aman dan berfungsi

### M09 — Signature
Tujuan:
- menyediakan fungsi tanda tangan / approval workflow

Fokus utama:
- backend signature record
- frontend canvas signature
- approval flow dan audit log
- testing

Output:
- workflow approval atau persetujuan dapat tercatat

### M10 — Comments
Tujuan:
- membangun interaksi publik dan moderasi komentar

Fokus utama:
- backend comment API
- public comment form
- admin moderation interface
- approved/pending/rejected status
- testing dan keamanan

Output:
- komentar publik bisa dibuat dan dimoderasi

### M11 — Security & Testing
Tujuan:
- hardening aplikasi secara menyeluruh sebelum deployment

Fokus utama:
- auth testing
- authorization testing
- API contract testing
- frontend testing for critical routes
- E2E workflow
- security review
- audit log review
- rate limiting untuk endpoint sensitif (terutama login)
- proteksi brute-force (cooldown/temporary lockout)
- evaluasi dan implementasi CAPTCHA berbasis risk (minimal setelah kegagalan login berulang)

Output:
- kualitas keamanan dan stabilitas siap untuk production baseline

### M12 — Deployment
Tujuan:
- menyiapkan stack siap deploy production

Fokus utama:
- Docker production config
- Nginx config
- env management
- production readiness docs
- final verification

Output:
- aplikasi bisa dijalankan secara deployment-ready

## Prinsip eksekusi tahapan

- Analisis kebutuhan terlebih dahulu.
- Jelaskan teknologi yang dipakai.
- Buat struktur file yang akan diubah.
- Implementasikan fokus milestone saat ini.
- Jalankan test relevan.
- Review keamanan.
- Update dokumentasi.
- Ringkas hasil dan pekerjaan berikutnya.

## Catatan penting untuk alur full-stack

- M00–M02: fokus utama pada foundation, arsitektur, dan database.
- M03–M04: fokus utama pada backend keamanan dan authorization.
- M05–M10: fokus utama pada product feature dan UI, tetapi tetap full-stack karena frontend dan backend berkembang bersamaan.
- M11: fokus pada security, quality, dan testing menyeluruh.
- M12: fokus pada deployment dan production readiness.

## Batasan penting

- Tidak membangun seluruh modul sekaligus.
- Tidak melompati milestone tanpa alasan teknis.
- Setiap fitur harus mempunyai testing yang relevan.
- Dokumentasi harus diperbarui tiap tahapan penting.
- Milestone berikutnya baru dijalankan setelah milestone sebelumnya stabil.
