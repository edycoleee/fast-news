#!/bin/sh
set -eu

: "${BACKUP_FILE:?BACKUP_FILE is required.}"
: "${RESTORE_DATABASE_URL:?RESTORE_DATABASE_URL must name a dedicated restore/test database.}"
: "${ALLOW_RESTORE:?Set ALLOW_RESTORE=yes to acknowledge that restore replaces schema/data.}"

if [ "$ALLOW_RESTORE" != "yes" ]; then
  echo "Restore refused: ALLOW_RESTORE must equal yes." >&2
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE" >&2
  exit 1
fi

checksum_file="$BACKUP_FILE.sha256"
if [ ! -f "$checksum_file" ]; then
  echo "Checksum file not found: $checksum_file" >&2
  exit 1
fi

sha256sum -c "$checksum_file"

echo "Restoring backup into explicit restore database."
pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  --dbname="$RESTORE_DATABASE_URL" \
  "$BACKUP_FILE"

echo "Restore completed. Run application migration and smoke checks before use."
