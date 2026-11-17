# Database Design

## 1. Database utama

- PostgreSQL sebagai database utama.
- SQLAlchemy 2.x dengan async session strategy.
- Alembic untuk schema migration.

## 2. Prinsip database

- model dikelompokkan berdasarkan modul fitur,
- foreign key dan constraints dipakai eksplisit,
- index dipasang pada kolom yang sering difilter,
- transaction boundary dikelola di service layer,
- repositori tidak melakukan commit sendiri,
- commit dilakukan dalam unit of work yang lebih tinggi.

## 3. Entitas utama

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

### Permission
- id
- name
- resource
- action

### UserRole
- user_id
- role_id

### RolePermission
- role_id
- permission_id

### Category
- id
- name
- slug
- parent_id
- created_at

### News
- id
- title
- slug
- summary
- content
- status
- published_at
- author_id
- category_id
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

### AuditLog
- id
- user_id
- action
- entity_type
- entity_id
- metadata
- created_at

## 4. Transaction policy

- operasional yang mencakup banyak tabel harus dalam satu transaksi,
- repositori tidak commit secara mandiri,
- flush dipakai bila dibutuhkan generated id,
- rollback terjadi jika exception naik,
- transaksi dibatasi di service layer.

## 5. Concurrency dan integrity

- gunakan unique constraints untuk mencegah duplikasi
- gunakan optimistic locking untuk update yang sering terjadi
- gunakan select for update bila operasi benar-benar perlu locking kuat
- gunakan PostgreSQL READ COMMITTED sebagai default

## 6. Migration strategy

Semua perubahan skema harus didokumentasikan melalui Alembic migration.

Tahap awal:
- users
- roles
- permissions
- user-role mapping
- categories
- news
- comments
- file assets
- audit logs

## 7. Testing database

- gunakan PostgreSQL terpisah untuk test
- test rollback dan constraint behavior
- test concurrency untuk operasi sensitif
- jangan pernah menjalankan automated test terhadap database produksi
