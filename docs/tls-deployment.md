# TLS Production Preparation

## Status

TLS tidak diaktifkan pada development/LAN karena memerlukan domain dan certificate. Template production tersedia di `nginx/default.ssl.conf.example`.

## Aktivasi

1. Tentukan production domain.
2. Ubah `server_name`.
3. Dapatkan certificate dari ACME/provider organisasi.
4. Mount certificate:
   - `/etc/nginx/certs/fullchain.pem`
   - `/etc/nginx/certs/privkey.pem`
5. Mount template TLS ke Nginx sebagai config aktif.
6. Buka port 443 pada firewall/load balancer.
7. Pastikan `SESSION_COOKIE_SECURE=true`.
8. Pastikan `CORS_ORIGINS` dan public URL memakai HTTPS.
9. Verifikasi redirect HTTP → HTTPS.
10. Uji renewal dan rollback sebelum menerima traffic.

## HSTS rollout

Aktifkan HSTS hanya setelah:

- seluruh route frontend/API HTTPS;
- mixed content tidak ditemukan;
- certificate renewal sudah otomatis;
- rollback path dipahami.

Jangan memasang `preload` pada rollout pertama.

## Headers aktif saat ini

Nginx development/staging mengirim:

- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- CSP

HSTS hanya ada pada template TLS.

## Verification

```bash
curl -I http://host
curl -I https://host
curl -sI https://host/api/health
```

Periksa:

- redirect hanya HTTP;
- certificate valid;
- security headers;
- no mixed content;
- API dan cookie secure;
- request upload di bawah/di atas request cap.
