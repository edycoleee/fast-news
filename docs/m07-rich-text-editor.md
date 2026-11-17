# M07 — Rich Text Editor

## Tujuan milestone

M07 menambahkan pengalaman penulisan artikel rich text untuk admin sekaligus memastikan konten HTML aman sebelum disimpan dan dipublikasikan.

## Scope implementasi

- integrasi editor rich text (Tiptap) pada form news admin
- sanitization HTML di backend sebelum create/update news
- validasi agar konten kosong setelah sanitization ditolak
- rendering konten HTML published pada halaman detail berita publik

## Perubahan utama

Frontend:
- `frontend/src/features/admin/components/RichTextEditor.jsx`
- `frontend/src/features/admin/pages/AdminNewsPage.jsx`
- `frontend/src/features/public/pages/PublicNewsDetailPage.jsx`
- `frontend/src/features/public/api/publicNewsApi.js`

Backend:
- `backend/app/modules/news/sanitizer.py`
- `backend/app/modules/news/service.py`
- `backend/requirements.txt` (bleach)

## Aturan sanitization

- tag HTML di-whitelist (contoh: `p`, `strong`, `em`, `ul`, `ol`, `li`, `blockquote`, `h1-h3`, `a`)
- atribut link dibatasi (`href`, `title`, `target`, `rel`)
- protocol link dibatasi (`http`, `https`, `mailto`)
- script/tag berbahaya dibuang
- konten tanpa teks bermakna setelah sanitization akan ditolak (`400`)

## Validasi

Backend tests:

```bash
pytest backend/tests/test_m06_cms.py backend/tests/test_rbac.py
```

Frontend build:

```bash
cd frontend
npm run build
```
