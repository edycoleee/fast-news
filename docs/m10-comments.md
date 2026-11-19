# M10 — Public Comments & Moderation

## Tujuan milestone

M10 menyediakan interaksi komentar publik yang aman: pengiriman komentar oleh pembaca, moderasi admin, dan hanya komentar yang disetujui yang tampil di halaman publik.

## Deliverables

### Backend

- komentar publik menggunakan `author_name` dan tidak memerlukan akun;
- komentar baru selalu berstatus `pending`;
- nama dan isi disanitasi sebagai plain text;
- daftar publik hanya mengembalikan status `approved`;
- reply parent opsional harus approved dan berasal dari berita yang sama;
- admin dapat approve, reject, dan delete;
- moderation note, moderator, dan timestamp disimpan;
- audit log untuk submit, approve, reject, dan delete;
- CSRF pada operasi moderasi;
- permission granular dari RBAC registry.

### Frontend

- form komentar pada halaman detail berita;
- loading, error, validation, success, dan empty state;
- daftar hanya komentar yang disetujui;
- halaman admin `/admin/comments`;
- filter status dan pagination;
- aksi approve, reject, delete dengan note/prompt;
- stable `data-testid` untuk form dan tindakan moderasi.

## Permission

- `comment.read`
- `comment.moderate`
- `comment.delete`
- `comment.manage`

`comment.manage` dan `news.manage` diterima sebagai fallback kompatibilitas eksplisit. Operasi moderasi tetap granular pada role baru.

## API

Public:

- `GET /api/public/news/{slug}/comments`
- `POST /api/public/news/{slug}/comments`

Admin:

- `GET /api/comments/query`
- `POST /api/comments/{comment_id}/moderate`
- `DELETE /api/comments/{comment_id}`

## Acceptance criteria

- publik dapat mengirim komentar valid;
- komentar baru tidak langsung tampil;
- komentar approved tampil sebagai teks, bukan HTML;
- komentar rejected tidak tampil;
- reply tidak dapat menunjuk komentar/news lain yang invalid;
- user tanpa permission moderasi mendapat 403;
- operasi moderasi tanpa CSRF mendapat 403;
- approve/reject tidak dapat dijalankan dua kali;
- delete tercatat audit;
- UI admin menangani loading, empty, error, dan status.

## Verifikasi

```bash
cd backend
.venv/bin/alembic upgrade head
.venv/bin/pytest -q tests/test_m10_comments.py
```

```bash
cd frontend
npm test
npm run lint
npm run build
```

## Batas security

Rate limiting, abuse scoring, dan CAPTCHA risk-based merupakan bagian M11. Endpoint publik M10 tetap membatasi panjang payload dan menerapkan moderation-before-publish, tetapi belum mengklaim proteksi anti-spam menyeluruh.
