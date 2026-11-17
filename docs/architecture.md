# Architecture Overview

## 1. Tujuan arsitektur

NewsHub CMS dibangun dengan pendekatan modular monolith yang memisahkan domain bisnis dan lapisan teknis secara jelas. Fokus utama adalah:

- memisahkan frontend dan backend,
- menjaga business logic di service layer,
- menyederhanakan pengembangan bertahap,
- menjaga keamanan dan konsistensi data,
- memudahkan migrasi dan deployment di masa depan.

## 2. Prinsip arsitektur

- Modular monolith: setiap fitur dibuat dalam module yang relatif mandiri.
- Frontend dan backend dipisahkan secara fisik.
- Router hanya menangani HTTP request/response.
- Service layer memegang business logic dan transaction orchestration.
- Repository menangani akses data dan query.
- Model SQLAlchemy mewakili entitas database.
- Schema Pydantic dipakai untuk validasi input/output.
- Dependency injection digunakan untuk session, auth, dan service.
- Database transaction didefinisikan pada service/use-case level.
- Tidak mengolah SQL langsung di frontend.
- Testing diterapkan pada setiap fitur utama.

## 3. Struktur modular yang disarankan

Backend:
- app/
  - core/
  - shared/
  - modules/
    - auth/
    - users/
    - roles/
    - permissions/
    - news/
    - categories/
    - comments/
    - files/
    - audit/

Setiap module berisi:
- router.py
- service.py
- repository.py
- models.py
- schemas.py
- dependencies.py
- tests/

Frontend:
- src/
  - app/
  - features/
    - auth/
    - dashboard/
    - news/
    - admin/
    - comments/
  - shared/
    - components/
    - hooks/
    - utils/
    - api/

## 4. Design system

Project menggunakan design system enterprise modern dengan fokus pada healthcare-like UX:

- primary blue: #2563EB
- secondary dark blue: #0F4C81
- success: #10B981
- warning: #F59E0B
- danger: #EF4444
- background: #F8FAFC
- surface: #FFFFFF
- text: #111827

Prinsip visual:
- 60% ruang netral terang
- 30% area navigasi sekunder gelap
- 10% accent untuk action utama
- readability > dekorasi
- accessible dan data-dense

## 5. Security-first design

- password hash menggunakan Argon2id
- secure cookies dengan HttpOnly, Secure, SameSite
- CSRF protection
- RBAC dan authorization di backend
- upload file dengan validasi MIME, ukuran, dan content
- audit log pada aksi sensitif
- hindari XSS dan SQL injection

## 6. Tahapan pengembangan

Project dibangun secara bertahap sesuai milestone berikut:

- M00 Discovery & Design Foundation
- M01 Project Setup
- M02 Database & Schema
- M03 Authentication
- M04 RBAC
- M05 Admin UI & Dashboard
- M06 News & Category CRUD
- M07 Rich Text Editor
- M08 File Upload
- M09 Signature
- M10 Comments
- M11 Security & Testing
- M12 Deployment

Untuk detail lengkap lihat [docs/roadmap.md](roadmap.md).

## 7. Keputusan arsitektur penting

- Menggunakan modular monolith agar pengembangan bertahap tetap manageable.
- Menjaga database dan UI terpisah agar lebih mudah di-scale dan di-test.
- Menggunakan transaction boundary di service layer untuk operasi multi tabel.
- Menggunakan Alembic untuk semua perubahan skema database.
- Menjaga backend sebagai sumber kebenaran auth dan permission.
- Menganggap design system sebagai bagian dari roadmap, bukan dekorasi akhir.
