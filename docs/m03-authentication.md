# M03 — Authentication

## Tujuan milestone

M03 membangun fondasi autentikasi backend yang aman untuk admin panel dan fitur sensitif NewsHub CMS.

## Scope M03

- login dengan username/email + password
- logout dengan invalidasi session
- endpoint identitas user saat ini (`/api/auth/me`)
- password hashing Argon2id
- cookie session HttpOnly + SameSite
- CSRF protection untuk request state-changing auth

## Implementasi

Struktur modul auth:

- `app/modules/auth/router.py`
- `app/modules/auth/service.py`
- `app/modules/auth/repository.py`
- `app/modules/auth/schemas.py`
- `app/modules/auth/dependencies.py`
- `app/modules/auth/security.py`

Perubahan model database:

- tabel baru `auth_sessions`
- relasi `users -> auth_sessions`
- migration Alembic: `99bd62ccbb73_add_auth_sessions.py`

## Contract endpoint

### POST `/api/auth/login`

Request body:

```json
{
  "username_or_email": "admin@example.com",
  "password": "StrongPass123!"
}
```

Response:

- status `200`
- payload user aman (tanpa password hash)
- set cookies:
  - session cookie: HttpOnly
  - csrf cookie: readable oleh frontend untuk dikirim di header

### GET `/api/auth/me`

- validasi session dari cookie
- response user saat ini
- unauthorized jika session tidak valid/expired/revoked

### POST `/api/auth/logout`

- validasi session
- validasi CSRF:
  - header `X-CSRF-Token`
  - token pada cookie CSRF
  - token hash yang tersimpan di database session
- revoke session aktif
- clear cookies auth

## Konfigurasi env (backend)

- `SESSION_COOKIE_NAME`
- `CSRF_COOKIE_NAME`
- `CSRF_HEADER_NAME`
- `SESSION_TTL_MINUTES`
- `SESSION_COOKIE_SECURE`

Catatan:
- untuk development HTTP lokal: `SESSION_COOKIE_SECURE=false`
- untuk production HTTPS: `SESSION_COOKIE_SECURE=true`

## Testing yang ditambahkan

File test:

- `backend/tests/test_auth.py`

Coverage:

- login success + me + logout success
- login gagal jika password salah
- logout gagal jika CSRF header tidak ada

## Validation

Langkah verifikasi:

1. jalankan migration terbaru:
   ```bash
   cd backend
   source .venv/bin/activate
   alembic upgrade head
   ```
2. jalankan test:
   ```bash
   pytest tests/test_auth.py tests/test_health.py
   ```

## Troubleshooting login remote LAN

Kasus yang pernah terjadi:
- backend login `POST /api/auth/login` sukses (`200`)
- tetapi browser tetap gagal login karena preflight `OPTIONS` ke endpoint auth mendapat `400 Bad Request`

Gejala di log:
- `Disallowed CORS origin`

Pencegahan:
1. pastikan `CORS_ORIGINS` mencakup origin frontend remote
2. pastikan frontend tidak mengunci API ke `localhost` ketika diakses dari perangkat lain
3. restart backend setelah perubahan `.env`

## Batasan saat ini

- UI login frontend belum diaktifkan pada milestone ini
- rate limiting auth endpoint akan ditambahkan pada milestone keamanan lanjutan
