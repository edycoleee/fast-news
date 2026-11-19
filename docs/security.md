# Security Overview

## 1. Prinsip keamanan

NewsHub CMS harus selalu menganggap keamanan sebagai kebutuhan inti, bukan fitur tambahan. Semua rute sensitif dan operasi data harus dijaga dari sisi backend.

## 2. Authentication dan session

- password di-hash menggunakan Argon2id
- session disimpan dengan cookie aman
- cookie harus memakai HttpOnly, Secure, SameSite
- backend menjadi authority untuk auth dan authorization
- logout harus menonaktifkan session yang valid

## 3. Authorization

- role-based access control (RBAC)
- permission check dilakukan di backend, tidak hanya frontend
- route guard hanya untuk pengalaman pengguna, bukan keamanan
- setiap operasi kritis harus dijecek permission-nya

## 4. Data validation

- request/response schema memakai Pydantic
- validasi input di backend tidak boleh diandalkan pada frontend
- sanitasi output HTML untuk editor rich text
- gunakan whitelist untuk tipe file yang diizinkan

## 5. File upload safety

- validasi MIME type
- validasi ukuran file
- validasi content file
- simpan metadata hanya di database dan file object di storage yang sesuai
- tidak menyimpan binary file di PostgreSQL tanpa alasan yang jelas
- cleanup untuk upload gagal atau abandoned

## 5.1 Signature safety

- hanya PNG data URL yang diterima
- payload Base64 dan ukuran binary dibatasi (512KB)
- struktur PNG dan dimensi gambar divalidasi di backend
- file signature disimpan sebagai asset privat, bukan binary PostgreSQL
- endpoint publik menolak file signature
- file bukti dilindungi `ON DELETE RESTRICT` selama signature masih ada
- create dan revoke signature menghasilkan audit log
- operasi perubahan memerlukan permission dan CSRF
- permission fitur berasal dari registry code dan disinkronkan secara idempotent
- role dan assignment tetap tersimpan di database
- permission registry-managed tidak dapat diubah/dihapus melalui API RBAC biasa
- download bukti signature menggunakan permission fitur terkait, bukan izin file global

## 5.2 Public comment safety

- komentar public ditampilkan sebagai teks React, bukan HTML
- nama dan konten melalui validasi Pydantic dan sanitasi backend
- komentar baru selalu berstatus `pending`
- endpoint public hanya mengembalikan komentar `approved`
- reply parent harus approved dan berada pada news yang sama
- moderasi memerlukan permission, CSRF, dan audit log
- komentar yang ditolak tidak disajikan kepada publik
- rate limiting, abuse scoring, dan CAPTCHA risk-based ditangani pada M11

## 6. Anti-abuse dan audit

- rate limiting untuk endpoint sensitif
- rate limiter PostgreSQL fixed-window untuk login, public comment, file upload, dan signature upload
- audit log untuk action penting seperti login, update role, publish news, file upload, moderation action
- logging error dan kejadian penting untuk debugging dan audit
- hindari mengembalikan data sensitif pada response

## 7. Web security

- hindari XSS
- hindari SQL injection
- gunakan CORS terbatas untuk origin development tertentu
- gunakan CSRF protection untuk state-changing requests
- pastikan secrets tidak masuk ke Git

## 8. Deployment safety

- container berjalan non-root jika memungkinkan
- env vars dipisahkan dari repo
- semua config sensitif di environment management
- jangan menjalankan automated test terhadap database produksi

## 10. Runtime settings boundary

- secret, database URL, CORS, cookie security, dan provider credential tetap environment
- upload/signature/comment/rate-limit dapat dikelola runtime melalui database
- setiap key berasal dari registry code; admin UI tidak dapat menciptakan key bebas
- update setting memerlukan permission, CSRF, validasi boundary, dan audit log
- hard cap deployment tetap berada di environment dan tidak dapat ditinggikan dari UI
- setting cache diinvalidasi setelah update berhasil

## 11. Login anti-abuse

- request login dibatasi per IP per menit
- kegagalan login berulang dibatasi per account identifier yang di-hash
- threshold memicu cooldown account sementara
- login berhasil menghapus failure bucket account
- response rate-limit mengembalikan `429` dan `Retry-After`

## 12. CAPTCHA decision

CAPTCHA tidak diaktifkan dengan challenge buatan sendiri. Provider eksternal yang verifiable dan terukur harus ditetapkan terlebih dahulu. Sampai itu selesai, mitigasi aktif M11 adalah rate limiting dan temporary cooldown.

## 9. Review keamanan per milestone

Setiap milestone harus dilakukan review keamanan singkat terhadap:
- auth dan session
- input validation
- file upload
- permission
- audit trail
- TLS/CORS setting bila sudah di deploy
