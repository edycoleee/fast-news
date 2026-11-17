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

## 6. Anti-abuse dan audit

- rate limiting untuk endpoint sensitif
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

## 9. Review keamanan per milestone

Setiap milestone harus dilakukan review keamanan singkat terhadap:
- auth dan session
- input validation
- file upload
- permission
- audit trail
- TLS/CORS setting bila sudah di deploy
