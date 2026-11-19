# M09 — Signature & Approval

## Tujuan milestone

M09 menyediakan workflow tanda tangan dan persetujuan admin yang dapat dicatat, ditinjau, dan dicabut tanpa menghapus bukti historis.

## Deliverables

### Backend

- tabel `signatures` dengan foreign key ke user, news opsional, dan file asset
- PNG signature disimpan di storage sebagai `FileAsset` privat
- file signature tidak tersedia melalui `/api/public/files`
- validasi PNG data URL, struktur file, dimensi, dan batas ukuran 512KB
- create signature membuat file asset, signature, dan audit log dalam satu transaksi database
- revoke signature menyimpan alasan, aktor, waktu, status, dan audit log
- permission granular `signature.read`, `signature.create`, dan `signature.revoke`
- fallback kompatibilitas `signature.manage` atau `news.manage`
- CSRF untuk create dan revoke

### Frontend

- halaman `/admin/signatures`
- Signature Pad canvas dengan aksi clear
- pilihan berita opsional dan tujuan approval
- loading, error, empty, success, filter, pagination, preview, dan revoke states
- stable `data-testid` untuk canvas, form, filter, dan action utama
- integrasi TanStack Query dan centralized Axios client

## API

- `GET /api/signatures/query?page=&page_size=&status_filter=`
- `POST /api/signatures`
- `GET /api/signatures/{signature_id}`
- `GET /api/signatures/{signature_id}/download`
- `POST /api/signatures/{signature_id}/revoke`

## Acceptance criteria

- user tanpa permission tidak dapat membuat, melihat, atau mencabut signature
- request perubahan tanpa CSRF ditolak
- data selain PNG atau PNG rusak ditolak
- file signature tidak dapat diunduh secara publik
- file bukti tidak dapat dihapus saat signature masih ada
- revoke membutuhkan alasan dan tidak dapat diulang
- audit log tersimpan bersama signature transaction
- halaman admin dapat menggambar, menyimpan, melihat, dan mencabut signature

## Verifikasi

Backend:

```bash
cd backend
.venv/bin/pytest -q tests/test_m09_signatures.py tests/test_m08_files.py tests/test_m06_cms.py tests/test_rbac.py
```

Frontend:

```bash
cd frontend
npm test
npm run lint
npm run build
```

Database:

```bash
cd backend
.venv/bin/alembic upgrade head
```
