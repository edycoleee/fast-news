#!/bin/sh
set -eu

BACKUP_DIR=${BACKUP_DIR:-/backups}
DATABASE_URL=${DATABASE_URL:-postgresql://newshub:change_me@db:5432/newshub}
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

case "$BACKUP_DIR" in
  ""|"/")
    echo "BACKUP_DIR must resolve to a non-root directory." >&2
    exit 1
    ;;
esac

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR" 2>/dev/null || true
umask 077

timestamp=$(date -u +%Y%m%dT%H%M%SZ)
backup_file="$BACKUP_DIR/newshub-$timestamp.dump"
checksum_file="$backup_file.sha256"

echo "Creating PostgreSQL backup..."
pg_dump "$DATABASE_URL" --format=custom --no-owner --no-acl --file="$backup_file"
sha256sum "$backup_file" > "$checksum_file"
chmod 600 "$backup_file" "$checksum_file"

find "$BACKUP_DIR" -maxdepth 1 -type f -name 'newshub-*.dump' \
  -mtime "+$BACKUP_RETENTION_DAYS" -delete
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'newshub-*.dump.sha256' \
  -mtime "+$BACKUP_RETENTION_DAYS" -delete

echo "Backup created: $backup_file"
echo "Checksum created: $checksum_file"
