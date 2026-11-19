# M11 — Security & Testing

## Tujuan milestone

M11 memperkuat aplikasi dengan runtime settings terkontrol, anti-abuse baseline, testing terintegrasi, dan batas jelas antara environment dan admin configuration.

## Runtime settings

Menu `/admin/settings` menyediakan:

- batas upload file;
- batas upload signature;
- batas panjang komentar;
- login rate per IP;
- failure threshold login;
- login cooldown;
- komentar per jam per IP;
- upload per jam per user.
- trigger manual retention cleanup (dry-run/execute) untuk audit log, auth session expired/revoked, dan rate-limit bucket.

Permission:

- `settings.read`
- `settings.update`
- `settings.manage`

Semua update memerlukan CSRF, registry key, schema validation, environment hard cap, dan audit log.

## Yang tetap di environment

- `DATABASE_URL`
- credentials database/storage
- session/cookie security
- CORS origin
- ports/public URL
- provider secrets
- hard cap:
  - `UPLOAD_HARD_CAP_BYTES`
  - `SIGNATURE_HARD_CAP_BYTES`
  - `COMMENT_HARD_CAP_LENGTH`

UI tidak dapat mengubah secret atau hard cap.

## Keterangan halaman Settings dan ISO/IEC 27001:2022

Halaman Settings menyediakan kontrol teknis operasional yang dapat membantu implementasi Sistem Manajemen Keamanan Informasi (SMKI/ISMS), tetapi **NewsHub belum dapat diklaim patuh atau tersertifikasi ISO/IEC 27001:2022**.

Pernyataan yang aman:

> NewsHub dibangun dengan baseline kontrol keamanan teknis yang mendukung penerapan ISO/IEC 27001:2022.

Sertifikasi membutuhkan penerapan control organisasi, proses, bukti, audit internal, review manajemen, dan penilaian pihak audit yang terakreditasi. Perubahan setting melalui UI bukan pengganti kebijakan dan tata kelola tersebut.

## Baseline teknis yang sudah tersedia

- Argon2id password hashing;
- database-backed session, secure cookie configuration, dan CSRF;
- RBAC granular serta permission registry;
- Pydantic input validation dan HTML sanitization;
- validasi MIME, ukuran, dan content upload;
- audit log operasi penting;
- rate limiting dan login cooldown;
- environment boundary untuk secret dan deployment hard cap;
- transaction service/repository yang jelas;
- Alembic migration dan database integrity;
- automated test, dependency audit, lint, dan build.

Kontrol ini membantu penyiapan bukti teknis, tetapi tidak mengkonfirmasi kecocokan seluruh Annex A atau scope ISMS.

## Gap coding teknis yang perlu ditambah

### P0 — sebelum production baseline

1. TLS/HTTPS enforcement, HSTS, CSP, dan security headers.
2. Container non-root dan hardening Nginx/production.
3. Secret management serta produksi CORS/trusted host.
4. Scheduled database/storage backup dan restore verification.
5. CI/CD SAST, dependency scan, container scan, secret scan, dan SBOM.
6. Audit/security event dashboard dengan request correlation ID.
7. Alert untuk login failure, rate limit, forbidden, dan CSRF rejection.

### P1 — access dan data lifecycle

1. Remove role dari user dan remove permission dari role.
2. Periodic access review dan reason pada perubahan sensitif.
3. Session management UI: list/revoke active session dan force logout.
4. Password reset/change dengan session revocation.
5. Data retention, orphan file cleanup, dan retention audit log.
6. Version/history setting dan rollback configuration.
7. File integrity hash dan malware scanning hook.

### P2 — operational security

1. Incident management dan security evidence workflow.
2. Tamper-evident audit export/archive.
3. User/data export sesuai kebutuhan legal.
4. Security training, supplier review, dan policy evidence di luar aplikasi.
5. Integrasi provider CAPTCHA yang terverifikasi.

## Batas halaman Settings

Halaman Settings hanya boleh mengelola parameter runtime yang memiliki schema, batas minimum/maksimum, hard cap deployment, permission, dan audit log.

Halaman ini tidak mengubah:

- credential database/storage;
- secret session/encryption;
- provider token;
- CORS production;
- cookie secure policy;
- TLS/Nginx configuration;
- hard cap environment.

Konfigurasi infrastructure tetap melalui environment, secret manager, infrastructure code, atau proses change approval.

## Bukti yang harus dilengkapi di luar coding

- scope dan kebijakan ISMS;
- inventory dan klasifikasi informasi;
- risk assessment serta risk treatment plan;
- Statement of Applicability;
- access review berkala;
- incident register dan exercise;
- backup restore evidence;
- vulnerability/patch evidence;
- supplier review;
- training record;
- internal audit dan management review;
- corrective action.

## Profil aplikasi internal: akses internet, kurang dari 500 user

Untuk NewsHub dengan skala di bawah 500 pengguna internal, tidak semua kontrol enterprise perlu diimplementasikan langsung. Rekomendasi harus proporsional terhadap exposure dan risiko.

### Karakteristik target

- pengguna terbatas kepada karyawan/anggota internal;
- aplikasi dapat diakses dari mana saja melalui internet;
- tidak dibuka untuk registrasi publik;
- data terutama berita internal/editorial, media, komentar, dan approval;
- user management dikelola admin;
- infrastruktur relatif kecil dan tidak memerlukan platform multi-region.

### Baseline wajib

Kontrol berikut tetap wajib karena aplikasi terekspos internet:

1. HTTPS/TLS dan security headers dasar.
2. Session cookie HttpOnly, Secure, dan SameSite.
3. CSRF protection.
4. Argon2id password hashing.
5. RBAC backend dan least privilege.
6. User active/inactive dan immediate session revocation.
7. Rate limit login, brute-force protection, dan cooldown.
8. Input validation, output sanitization, dan safe file upload.
9. Backup database rutin dengan uji restore berkala.
10. Secret melalui environment/secret manager, tidak di Git.
11. Audit log login, perubahan role, publish, moderation, upload, signature, delete, dan settings.
12. Dependency scanning serta secret scanning pada perubahan penting.
13. Monitoring health/error minimum.
14. Retention data dan cleanup orphan file yang ditetapkan.

### Disarankan setelah stabil

- daftar active session dan revoke per session;
- review akses internal per kuartal;
- export audit log untuk tim/management;
- automated vulnerability scan terjadwal;
- malware scanning hook untuk upload;
- MFA untuk admin/superadmin;
- SSO dengan provider organisasi bila tersedia;
- incident register sederhana;
- backup ke lokasi terpisah dan restore drill;
- SBOM sederhana pada setiap release.

### Dapat ditunda agar tidak over-engineering

Untuk skala ini, kontrol berikut tidak perlu menjadi baseline awal:

- multi-region architecture;
- microservices dan service mesh;
- SIEM enterprise yang mahal;
- SOC 24/7;
- custom CAPTCHA sebelum ada bukti abuse nyata;
- tamper-evident blockchain/cryptographic log chain;
- high-availability database multi-node;
- dedicated HSM;
- automated data-loss prevention enterprise;
- full ISO 27001 certification platform;
- access review mingguan;
- formal incident workflow kompleks sebelum proses tim terbentuk.

Beberapa kontrol dapat dimulai sebagai proses sederhana dan dokumen, tidak harus aplikasi khusus.

### Keputusan akses internal via internet

Jangan hanya mengandalkan batasan "user internal" sebagai kontrol keamanan. Aplikasi tetap tersedia untuk internet dan dapat diserang tanpa akun.

Pilihan akses yang disarankan, urut dari sederhana:

1. **SSO/MFA organisasi + HTTPS**
   - cocok bila provider identitas organisasi sudah tersedia;
   - paling mudah membatasi onboarding/offboarding.

2. **VPN atau private access gateway**
   - hanya dipilih jika memang seluruh user dapat memakai VPN;
   - menambah kompleksitas operasional dan support.

3. **IP allowlist**
   - hanya cocok jika kantor/user memiliki IP statis;
   - tidak cukup untuk karyawan remote/mobile.

4. **Domain/corporate email allowlist**
   - tidak boleh menjadi satu-satunya kontrol;
   - tetap perlu auth dan MFA.

Rekomendasi default untuk NewsHub internal: HTTPS + session aman + RBAC + rate limit, kemudian MFA/SSO bila provider organisasi tersedia.

### Threshold implementasi berbasis risiko

Tingkatkan kontrol jika salah satu kondisi berikut terpenuhi:

- aplikasi mulai menyimpan data sangat sensitif;
- upload file dari pihak eksternal diaktifkan;
- user bertambah signifikan atau tersebar antar organisasi;
- ada kebutuhan regulasi/contractual;
- terdapat repeated brute-force atau abuse;
- downtime berdampak besar pada operasi;
- provider/partner eksternal mendapat akses;
- audit formal atau certification diminta.

### Kesimpulan praktis

Untuk akses internet dengan user internal di bawah 500, pendekatan yang tepat adalah:

```text
Security baseline yang wajib
+ proses operasional sederhana
+ monitoring minimum
+ peningkatan bertahap berdasarkan risiko
```

Jangan membangun seluruh framework compliance sekaligus. Implementasikan kontrol teknis yang langsung mengurangi risiko, simpan bukti yang mudah, dan tambahkan tooling enterprise hanya ketika scale, regulasi, incident history, atau exposure membenarkan biaya tersebut.

Matrix implementasi aktual, gap, dan urutan pekerjaan coding tersedia pada [m11-1.md](m11-1.md).

## Rate limiting

Backend memakai PostgreSQL fixed-window bucket:

- login requests per IP/minute;
- login failures per hashed account/cooldown;
- public comment submission per IP/hour;
- file dan signature upload per user/hour.

Counter memakai unique `scope + identifier + window_start` dengan PostgreSQL upsert. Bucket lebih lama dari tujuh hari dibersihkan secara opportunistic.

## Login protection

1. Periksa rate request.
2. Periksa cooldown account.
3. Verifikasi credential Argon2id.
4. Kegagalan menyimpan counter.
5. Threshold mengembalikan `429` + `Retry-After`.
6. Login berhasil membersihkan failure bucket account.

## CAPTCHA decision

CAPTCHA tidak diaktifkan dengan challenge buatan sendiri. Provider eksternal yang verifiable dan terukur harus ditetapkan terlebih dahulu. Sampai itu selesai, mitigasi aktif M11 adalah rate limiting dan temporary cooldown.

## Security controls

- CSRF pada update settings
- backend RBAC
- no free-form setting key
- runtime values tidak menggantikan deployment hard cap
- no secrets returned to frontend
- audit previous/current values
- failed login identifier disimpan sebagai hash
- cleanup bucket lama
- comments tetap moderation-before-publish

## Verifikasi

Backend:

```bash
cd backend
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.sync_permissions
.venv/bin/pytest -q
```

Frontend:

```bash
cd frontend
npm test
npm run lint
npm run build
npm audit --omit=dev --audit-level=high
```

## Acceptance

- settings cannot exceed hard cap
- user tanpa permission mendapat 403
- setting update memakai CSRF dan audit
- login threshold menghasilkan 429
- public comment memakai runtime max length
- upload/signature memakai runtime limits
- tests tidak dijalankan pada production database
- residual risks didokumentasikan

## M11.1 staged controls

Implementasi berlanjut tanpa menunggu seluruh aplikasi selesai:

- session active list/revoke selected/revoke other;
- database readiness dan correlation ID;
- structured JSON log;
- audit/security event UI dan CSV export;
- PostgreSQL backup/restore scripts dan Docker ops profile;
- TLS-ready Nginx template.

Status, residual risk, dan acceptance detail tersedia pada [m11-1.md](m11-1.md). Runbook backup ada pada [backup-restore.md](backup-restore.md), sedangkan aktivasi certificate dijelaskan pada [tls-deployment.md](tls-deployment.md).
