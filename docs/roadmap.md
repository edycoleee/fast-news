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

Status:
- **Selesai**
- canvas Signature Pad admin telah terintegrasi
- signature menyimpan user, berita opsional, purpose, file PNG privat, status, dan revocation metadata
- create/revoke dilindungi RBAC dan CSRF serta dicatat dalam audit log
- migrasi database, backend tests, frontend unit test, lint, dan production build telah dijalankan
- detail implementasi: [docs/m09-signature.md](m09-signature.md)

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

Status:
- **Selesai**
- komentar publik tamu tersimpan sebagai pending
- hanya komentar approved tampil pada halaman berita
- admin dapat meninjau, approve, reject, dan delete
- moderation metadata dan audit log disimpan
- permission registry mencakup `comment.read`, `comment.moderate`, `comment.delete`, dan `comment.manage`
- detail implementasi: [docs/m10-comments.md](m10-comments.md)

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

Status:
- **Selesai untuk baseline M11**
- menu Admin Settings untuk batas upload, signature, komentar, rate limit, dan login cooldown
- runtime settings disimpan database dan perubahan diaudit
- secrets/startup config tetap environment
- rate limiter PostgreSQL berlaku pada login, public comment, file upload, dan signature upload
- login failure threshold memicu temporary cooldown
- dependency audit, backend suite, frontend test, lint, dan build telah dijalankan
- CAPTCHA eksternal tidak diaktifkan tanpa provider terpercaya; tercatat sebagai keputusan security residual
- detail: [docs/m11-security-testing.md](m11-security-testing.md)

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

Tahapan detail (untuk eksekusi saat production):
1. **Infrastructure baseline**
   - siapkan host production dan struktur direktori deploy;
   - pastikan secret/env production tidak berada di Git;
   - aktifkan storage backup terenkripsi.
2. **Compose production activation**
   - jalankan service `db`, `backend`, `frontend`, `nginx` dari `docker-compose.prod.yml`;
   - verifikasi health `/api/health` dan readiness `/api/readiness`.
3. **TLS dan Nginx hardening**
   - pasang certificate TLS production;
   - aktifkan redirect HTTP→HTTPS;
   - validasi header keamanan (HSTS/CSP/X-Content-Type-Options dan lainnya sesuai policy).
4. **Ops scheduler (production only)**
   - aktifkan scheduler host/orchestrator untuk backup harian:
     `docker compose -f docker-compose.prod.yml --profile ops run --rm backup`;
   - aktifkan scheduler untuk retention cleanup:
     `docker compose -f docker-compose.prod.yml --profile ops run --rm cleanup`;
   - dev/staging tetap manual atau ad-hoc.
5. **Backup, retention, dan restore drill**
   - verifikasi file backup `.dump` + checksum `.sha256`;
   - cek audit event `retention.cleanup`;
   - lakukan restore drill ke database khusus test/restore.
6. **Security gate production**
   - jalankan test, lint, dan build terakhir;
   - jalankan dependency/security scan sesuai baseline M11;
   - verifikasi CSRF/session/RBAC pada alur login-admin kritikal.
7. **Go-live checklist**
   - dokumentasikan jadwal job, lokasi log, owner on-call, dan runbook incident;
   - catat evidence deployment (versi image, timestamp, hasil verifikasi).

Acceptance M12:
- semua service production berjalan stabil;
- TLS aktif dan redirect HTTPS berhasil;
- backup scheduler dan cleanup scheduler berjalan sukses;
- restore drill terakhir sukses dan terdokumentasi;
- monitoring minimum serta audit log dapat ditinjau admin.

Referensi implementasi detail: [docs/m12.md](m12.md), [docs/backup-restore.md](backup-restore.md), [docs/tls-deployment.md](tls-deployment.md).

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
