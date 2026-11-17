# M02 — Database & Schema

## Tujuan milestone

M02 adalah tahap pembentukan fondasi data NewsHub CMS. Pada tahap ini, sistem database secara konseptual dan teknis disiapkan agar fitur berikutnya seperti auth, RBAC, news CRUD, comment moderation, dan audit log dapat dibangun dengan struktur data yang konsisten.

## Fokus milestone

- menyiapkan model SQLAlchemy dasar
- mendefinisikan entitas utama aplikasi
- membuat migration Alembic awal
- memastikan relasi, constraints, dan index dasar sudah sesuai
- menyusun proposal schema yang bisa dijadikan landasan M03 dan berikutnya

## Scope yang dibatasi

Pada M02 kita fokus pada foundation database.

Tidak memasukkan:

- business logic CRUD lengkap
- auth flow
- permission logic runtime
- frontend UI CRUD
- deployment production penuh

## Entitas utama

### User
- id
- username
- email
- password_hash
- is_active
- created_at
- updated_at

### Role
- id
- name
- description
- created_at
- updated_at

### Permission
- id
- name
- resource
- action
- created_at

### UserRole
- id
- user_id
- role_id

### RolePermission
- id
- role_id
- permission_id

### Category
- id
- name
- slug
- description
- parent_id
- created_at
- updated_at

### News
- id
- title
- slug
- summary
- content
- status
- author_id
- category_id
- published_at
- created_at
- updated_at

### Comment
- id
- news_id
- user_id
- parent_id
- content
- status
- created_at

### FileAsset
- id
- original_name
- storage_key
- mime_type
- size_bytes
- uploaded_by
- created_at
- updated_at

### AuditLog
- id
- user_id
- action
- entity_type
- entity_id
- details (stored in metadata column)
- created_at

## Relasi database

- User memiliki banyak Role via UserRole
- Role memiliki banyak Permission via RolePermission
- User memiliki banyak News
- Category memiliki banyak News
- Category bisa memiliki parent category
- News memiliki banyak Comment
- Comment bisa memiliki parent comment untuk nested reply
- User memiliki banyak FileAsset
- User memiliki banyak AuditLog

## Prinsip integrity

- foreign key selalu digunakan
- cascade delete diatur secara eksplisit untuk relasi sensitif
- unique constraints untuk kombinasi yang seharusnya unik
- index untuk kolom yang sering difilter, seperti email, username, role, status, slug, category
- data integrity tidak hanya di-validate di aplikasi, tetapi juga di database

## Alembic dan migration

Semua perubahan skema harus dilakukan melalui migration.

Workflow yang disarankan:

```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## Output yang diharapkan

- model SQLAlchemy dasar siap dipakai
- migration Alembic awal dibuat
- relasi utama sudah terdokumentasi
- schema proposal siap menjadi landasan M03 dan M04

## Status implementasi saat ini

M02 telah berhasil diselesaikan pada level foundation:
- model utama telah dibuat dan terdaftar di metadata Base
- migration awal berhasil dibuat dan dijalankan
- database PostgreSQL dev yang berjalan melalui Docker sudah terhubung dari backend lokal
- tabel utama seperti users, roles, permissions, news, comments, categories, dan audit_logs sudah terbentuk

Catatan penting untuk workflow dev:
- backend lokal berjalan dengan DATABASE_URL menggunakan `localhost:5432`
- backend yang berjalan di container production harus menggunakan service name `db`
- ini dipisahkan agar dev tidak perlu rebuild container setiap perubahan skema kecil

## Acceptance criteria

- semua model utama sudah dibuat
- import model terhubung ke metadata Base
- alembic migration dapat dibuat dan dijalankan
- ERD dasar sudah terkonsolidasi
- project siap untuk authentication dan RBAC

## Validation checklist

- jalankan docker compose dev untuk PostgreSQL
- jalankan alembic upgrade head
- cek koneksi database berhasil
- koreksi jika migration gagal karena relasi atau naming
- pastikan tabel utama muncul di database
