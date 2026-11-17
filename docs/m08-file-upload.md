# M08 — File Upload

## Tujuan milestone

M08 menambahkan file management aman untuk kebutuhan newsroom, dengan validasi MIME, ukuran, dan konten file.

## Scope implementasi

- upload file admin (PNG, JPG, WEBP, PDF)
- validasi backend:
  - MIME type whitelist
  - ukuran file maksimal 5MB
  - validasi konten dasar (signature PDF dan deteksi tipe image)
- list file, download file, delete file
- audit log untuk upload/delete file
- halaman admin file management
- integrasi UI pada halaman News untuk melihat daftar media terbaru dan menyalin URL file
- integrasi UI pada halaman News untuk menyisipkan URL media langsung ke konten rich text
- untuk file image, aksi sisipkan akan menambahkan tag `<img>` agar tampil inline pada detail berita publik

## Endpoint backend

- `GET /api/files/query?page=&page_size=&search=`
- `POST /api/files/upload` (multipart form-data: `upload_file`)
- `GET /api/files/{file_id}/download`
- `DELETE /api/files/{file_id}`
- `GET /api/public/files/{file_id}/download` (untuk render media pada halaman publik)

## Permission

- endpoint file management menerima user dengan permission:
  - `file.manage` atau
  - `news.manage`

## Validasi

Backend tests:

```bash
pytest backend/tests/test_m08_files.py backend/tests/test_m06_cms.py backend/tests/test_rbac.py
```

Frontend build:

```bash
cd frontend
npm run build
```
