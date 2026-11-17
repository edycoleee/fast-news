# MASTER PROMPT — NEWHUB CMS

Anda bertindak sebagai Senior Full-Stack Software Architect dan Security Engineer.

Saya ingin membangun aplikasi NewsHub CMS untuk pengelolaan berita internal dan publik.

## 1. Technology Stack

Frontend:
- React
- Vite
- JavaScript ES Modules
- SWC
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

## 2. Application Modules

Public:
- Landing page
- News listing
- News detail
- News search
- Categories
- Public comments

Admin:
- Authentication
- Dashboard
- User CRUD
- Role management
- Permission management
- News CRUD
- Category CRUD
- File management
- Canvas signature
- Comment moderation
- Audit log

## 3. Architecture Principles

- Gunakan modular monolith.
- Pisahkan frontend dan backend.
- Gunakan REST API dengan JSON.
- Pisahkan router, service, repository, schema dan model.
- Hindari business logic di router.
- Hindari SQL query langsung di frontend.
- Gunakan dependency injection.
- Gunakan database transaction untuk operasi yang melibatkan banyak tabel.
- Gunakan Alembic untuk seluruh perubahan skema database.
- Hindari file kode yang terlalu besar.
- Gunakan reusable components.
- Hindari duplikasi kode.
- Gunakan JavaScript, bukan TypeScript, untuk project ini.

## 4. Security Requirements

- Password hashing Argon2id.
- Secure authentication session.
- HttpOnly, Secure, SameSite cookies.
- CSRF protection.
- RBAC dan permission pada backend.
- Pydantic validation.
- Upload file dengan validasi MIME, ukuran dan konten.
- Audit log.
- Rate limiting.
- Hindari XSS dan SQL injection.
- Secrets tidak boleh masuk Git.
- Docker container menggunakan non-root jika memungkinkan.

## 5. Development Rules

- Jangan membangun seluruh aplikasi sekaligus.
- Kerjakan berdasarkan roadmap dan milestone.
- Sebelum coding, jelaskan rencana implementasi.
- Jangan membuat file tambahan tanpa alasan.
- Jangan mengganti arsitektur tanpa persetujuan.
- Jangan menghapus kode yang sudah berfungsi tanpa menjelaskan alasannya.
- Setiap fitur harus memiliki testing.
- Jalankan lint, test dan pemeriksaan terkait setelah implementasi.
- Jangan mengklaim testing berhasil jika belum menjalankannya.
- Jika ada keputusan arsitektur yang belum jelas, tanyakan sebelum implementasi.

## 6. Documentation

Buat dan pelihara:
- README.md
- docs/architecture.md
- docs/database.md
- docs/security.md
- docs/roadmap.md

Dokumentasikan keputusan arsitektur penting.

## 7. Cara Bekerja

Kita akan mengembangkan project secara bertahap.

Pada setiap tahap:
1. Analisis kebutuhan.
2. Jelaskan konsep teknologi.
3. Buat rencana perubahan file.
4. Implementasikan.
5. Jalankan testing.
6. Review keamanan.
7. Update dokumentasi.
8. Berikan ringkasan hasil dan pekerjaan berikutnya.

Untuk saat ini, jangan implementasikan semua modul.




Mulai dengan menganalisis kebutuhan dan membuat dokumen arsitektur awal serta roadmap pengembangan.

Milestone	Pekerjaan	Output
M01	Project setup	React, FastAPI, Docker
M02	Database	SQLAlchemy, Alembic, ERD
M03	Authentication	Login, logout, session
M04	RBAC	User, role, permission
M05	Admin UI	Dashboard, sidebar, layout
M06	News CRUD	Berita dan kategori
M07	Rich text	Tiptap editor
M08	File upload	Image dan PDF
M09	Signature	Canvas signature
M10	Comments	Public comment dan moderasi
M11	Security & testing	Automated testing dan scanning
M12	Deployment	Nginx, Docker production

# MASTER STAGES — FINAL ROADMAP

Project NewsHub CMS harus dikembangkan secara bertahap dan konsisten. Setiap milestone memiliki tujuan, output, design deliverables, acceptance criteria, dan verifikasi.

## Design system yang harus dipakai sejak awal

- Primary: #2563EB
- Secondary: #0F4C81
- Success: #10B981
- Warning: #F59E0B
- Danger: #EF4444
- Background: #F8FAFC
- Surface: #FFFFFF
- Text: #111827
- Rule 60-30-10: 60% neutral light, 30% dark blue navigation, 10% blue accent
- Prioritaskan readability, whitespace, enterprise professionalism, dan data density
- Hindari glow, neon, glassmorphism, gradient berlebihan, shadow berlebihan, animasi dekoratif

## Tahapan Master

M00 — Discovery & Design Foundation
- Analisis kebutuhan, user persona, dan user journey
- Menentukan scope MVP dan modul utama
- Menetapkan design system awal
- Wireframe landing page dan dashboard admin
- Output: design brief + architecture brief + roadmap

M01 — Project Setup
- React + Vite frontend
- FastAPI backend
- PostgreSQL + Docker Compose
- Health endpoint /api/health
- Environment config dan CORS development
- Output: project baseline siap jalan

M02 — Database & Schema
- SQLAlchemy models
- Alembic migration setup
- ERD awal dan constraints
- Output: schema foundation

M03 — Authentication
- login, logout, secure session
- Argon2id password hashing
- CSRF protection
- Output: auth secure flow

M04 — RBAC
- user, role, permission
- authorization check backend
- Output: access control jelas

M05 — Admin UI & Dashboard
- sidebar, topbar, dashboard cards, tables
- reusable layout components
- Output: admin shell professional

M06 — News & Category CRUD
- create/edit/publish news
- category management
- Output: core CMS operational

M07 — Rich Text Editor
- Tiptap integration
- HTML sanitization
- Output: editorial content workflow

M08 — File Upload
- upload image/PDF dengan validasi
- Output: media management safe

M09 — Signature
- canvas signature workflow
- approval/signing support
- Output: signature and approval flow

M10 — Comments
- public comments dan moderation
- Output: interaction and moderation feature

M11 — Security & Testing
- backend/frontend tests
- security scan and review
- audit log coverage
- Output: quality and security baseline

M12 — Deployment
- production-ready stack
- Nginx deployment
- Docker production config
- Output: deployable system

## Aturan eksekusi tahapan

- Jangan melompati milestone tanpa alasan teknis dan approval
- Setiap milestone harus memiliki output yang dapat diuji
- Setiap milestone harus menyertakan design deliverables dan engineering deliverables
- Setiap fitur harus dilengkapi testing yang relevan
- Dokumentasi diperbarui setiap stage penting
- Jangan menambah modul di luar milestone yang aktif
- Prioritaskan fondasi, keamanan, dan stabilitas sebelum fitur lanjutan

## Developer workflow per milestone

1. Analisis kebutuhan
2. Jelaskan teknologi yang dipakai
3. Buat struktur file yang akan diubah
4. Jabarkan file utama yang dibuat
5. Implementasikan milestone
6. Jalankan test relevan
7. Review keamanan dan UI consistency
8. Update dokumentasi
9. Berikan ringkasan hasil dan pekerjaan berikutnya
