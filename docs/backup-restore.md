# Backup and Restore Operations

## Scope

NewsHub menggunakan PostgreSQL custom-format backup melalui `pg_dump`. Pytest tidak menjalankan backup atau restore terhadap database production.

## Backup

Menggunakan production stack:

```bash
docker compose -f docker-compose.prod.yml --profile ops run --rm backup
```

Default:

- volume: `backup_data`
- path container: `/backups`
- retention: 30 hari
- format: PostgreSQL custom
- checksum: SHA-256

Override:

```env
BACKUP_DATABASE_URL=postgresql://...
BACKUP_RETENTION_DAYS=30
```

## Verifikasi checksum

Untuk script host:

```bash
BACKUP_DIR=/secure/newshub-backups ./scripts/verify_backup.sh
```

## Restore aman

Restore memerlukan database tujuan eksplisit dan acknowledgement:

```bash
BACKUP_FILE=/secure/newshub-backups/newshub-....dump \
RESTORE_DATABASE_URL=postgresql://.../newshub_restore_test \
ALLOW_RESTORE=yes \
./scripts/restore_database.sh
```

Script menjalankan `pg_restore --clean --if-exists` dan tidak memilih production database sendiri. Jangan restore production tanpa change approval, maintenance window, dan backup terbaru.

Setelah restore:

1. jalankan `alembic upgrade head`;
2. jalankan `/api/health`;
3. jalankan `/api/readiness`;
4. smoke test login, news, files, dan comments;
5. catat waktu, checksum backup, hasil restore, dan actor.

## Restore acceptance

- restore database khusus berhasil;
- checksum valid;
- migration head sesuai;
- readiness connected;
- login dan permission bekerja;
- sample data dapat diakses sesuai policy;
- evidence restore tersimpan.

## Encryption

Backup volume production harus memakai encrypted storage pada layer infrastructure. Jika backup dipindahkan ke object storage, aktifkan server-side encryption dan credential terpisah. Kunci encryption tidak boleh dibaca oleh application runtime.

## Schedule

Jadwalkan job harian melalui cron, systemd timer, atau orchestrator. Scheduler mencatat exit code, waktu, nama file, dan checksum. Aktivasi scheduler bergantung lingkungan deployment dan dilaksanakan pada M12.

## Security retention cleanup

Cleanup dijalankan terpisah dari backup:

```bash
docker compose -f docker-compose.prod.yml --profile ops run --rm cleanup python -m scripts.cleanup_security_data --dry-run
docker compose -f docker-compose.prod.yml --profile ops run --rm cleanup
```

Alternatif manual dari UI admin tersedia pada `/admin/settings` (retention cleanup dry-run/execute) dengan permission settings dan CSRF protection.

Retention aktif:

- audit log: 180 hari default;
- revoked/expired session: 30 hari default;
- rate-limit bucket: 7 hari default.

Active session tidak dihapus. Cleanup berjalan batch dan dry-run tidak melakukan perubahan.

Sebelum cleanup audit, export/archive harus sudah tersedia bila policy organisasi mensyaratkan penyimpanan lebih lama. Nilai retention diubah melalui Admin Settings dan tetap dibatasi schema.
