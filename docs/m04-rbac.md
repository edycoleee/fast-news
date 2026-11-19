# M04 — RBAC

## Tujuan milestone

M04 memastikan kontrol akses dijalankan dari backend melalui role dan permission terstruktur, dapat diperluas setiap fitur, dan tetap dapat diaudit.

## Model operasional

Gunakan pola **Permission-as-Code + Role-as-Data**.

- Developer menentukan permission yang tersedia untuk setiap modul.
- Registry permission disinkronkan ke database secara idempotent.
- Admin RBAC menentukan permission mana yang dimiliki role.
- Admin RBAC menentukan role mana yang dimiliki user.
- Backend endpoint memeriksa permission, bukan nama role.
- Frontend hanya memakai permission untuk UX; frontend bukan otoritas keamanan.

Alur:

```text
permissions.py module
    -> permission registry
    -> sync_permissions command
    -> tabel permissions
    -> role_permission
    -> user_role
    -> backend permission guard
```

## Standar permission

Nama wajib mengikuti:

```text
<resource>.<action>
```

Contoh:

```text
signature.read
signature.create
signature.revoke
signature.manage
```

`resource` dan `action` juga harus cocok dengan nama permission. Validasi dijalankan saat registry dimuat.

`manage` disediakan untuk kompatibilitas/pengelolaan luas. Operasi sensitif seperti publish, revoke, delete, export, dan assign-role tetap sebaiknya memiliki action granular.

## Registry per fitur

Setiap modul backend wajib memiliki `permissions.py`:

```text
backend/app/modules/<feature>/
├── permissions.py
├── router.py
├── service.py
├── repository.py
├── schemas.py
└── tests/
```

Contoh:

```python
from app.core.permissions import FeaturePermission

READ = 'signature.read'
CREATE = 'signature.create'
REVOKE = 'signature.revoke'

PERMISSIONS = (
    FeaturePermission(READ, 'signature', 'read'),
    FeaturePermission(CREATE, 'signature', 'create'),
    FeaturePermission(REVOKE, 'signature', 'revoke'),
)
```

Manifest fitur kemudian didaftarkan di `app/modules/rbac/permission_registry.py`. Registry menolak nama duplikat dan mismatch `resource.action`.

## Sinkronisasi ke database

Jalankan:

```bash
cd backend
.venv/bin/python -m scripts.sync_permissions
```

Command bersifat idempotent:

- permission baru ditambahkan;
- permission yang sudah sama dilewati;
- konflik metadata dihentikan dengan error eksplisit;
- role assignment tidak diubah;
- command aman dijalankan kembali.

Permission yang dikelola registry tidak boleh diubah atau dihapus melalui RBAC API biasa. Perubahan nama/action memerlukan perubahan kode dan review migration.

## Role dan permission assignment

Role tetap merupakan data database:

- role tidak di-hardcode pada router atau service fitur;
- admin membuat/menentukan role sesuai struktur organisasi;
- admin memasukkan permission registry ke role;
- role diberikan ke user;
- perubahan assignment menghasilkan audit log.

Role template boleh dipakai untuk seed/setup awal, tetapi tidak boleh menimpa role atau assignment yang sudah dimodifikasi admin.

Seeder superadmin memakai registry dan memberikan seluruh permission aplikasi kepada role `superadmin` saat bootstrap.

## Endpoint RBAC

- `POST /api/rbac/roles`
- `PUT /api/rbac/roles/{role_id}`
- `DELETE /api/rbac/roles/{role_id}`
- `GET /api/rbac/roles/query`
- `POST /api/rbac/permissions`
- `PUT /api/rbac/permissions/{permission_id}`
- `DELETE /api/rbac/permissions/{permission_id}`
- `GET /api/rbac/permissions/query`
- `POST /api/rbac/roles/{role_id}/permissions/{permission_id}`
- `PUT /api/rbac/roles/{role_id}/permissions`

Endpoint `PUT` menggantikan keseluruhan permission role dalam satu transaksi. UI memuat permission role terlebih dahulu, membuka modal pencarian multi-checklist, kemudian mengirim satu daftar final. Endpoint lama satu-permission tetap dipertahankan untuk kompatibilitas.
- `POST /api/rbac/users/{user_id}/roles/{role_id}`
- `GET /api/rbac/me/permissions`
- `GET /api/rbac/me/roles`
- `GET /api/rbac/users/{user_id}/permissions`
- `GET /api/rbac/users/{user_id}/roles`
- `GET /api/rbac/roles/{role_id}/permissions`

Semua endpoint administrasi RBAC tetap memerlukan session valid, CSRF pada write, dan `rbac.manage`.

## Pemetaan endpoint

Setiap fitur wajib mendokumentasikan matriks:

| Operasi | Permission | Endpoint |
|---|---|---|
| list/detail | `<feature>.read` | GET |
| create | `<feature>.create` | POST |
| update | `<feature>.update` | PUT/PATCH |
| delete/revoke | permission operasi khusus | DELETE/POST action |

Contoh Signature:

| Endpoint | Permission |
|---|---|
| `GET /api/signatures/query` | `signature.read` |
| `GET /api/signatures/{id}` | `signature.read` |
| `GET /api/signatures/{id}/download` | `signature.read` |
| `POST /api/signatures` | `signature.create` |
| `POST /api/signatures/{id}/revoke` | `signature.revoke` |

Untuk kompatibilitas, `signature.manage` dan `news.manage` dapat diberlakukan sebagai fallback eksplisit pada endpoint M09. Fallback harus dicantumkan jelas dalam kode dan dokumentasi, bukan wildcard tersembunyi.

## Checklist wajib fitur baru

- [ ] resource dan action fitur didaftarkan;
- [ ] `permissions.py` dibuat di module;
- [ ] permission masuk central registry;
- [ ] nama tervalidasi sebagai `resource.action`;
- [ ] sync command dijalankan;
- [ ] endpoint memakai permission guard backend;
- [ ] operasi write memakai CSRF;
- [ ] role tidak di-hardcode;
- [ ] assignment tidak otomatis diberikan kecuali bootstrap superadmin;
- [ ] frontend menyesuaikan permission untuk UX;
- [ ] operasi sensitif menulis audit log;
- [ ] test tanpa permission menghasilkan 403;
- [ ] test dengan permission menghasilkan hasil yang benar;
- [ ] test permission lain tidak mendapat akses;
- [ ] matriks endpoint-permission didokumentasikan.

## Testing

```bash
cd backend
.venv/bin/pytest -q tests/test_rbac.py tests/test_m09_signatures.py
```

Test M04/M09 mencakup registry unik, granular permission, forbidden access, idempotent synchronization melalui command, proteksi permission registry-managed, dan backward compatibility `manage`.
