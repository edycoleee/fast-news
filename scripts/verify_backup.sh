#!/bin/sh
set -eu

BACKUP_DIR=${BACKUP_DIR:-/backups}

case "$BACKUP_DIR" in
  ""|"/")
    echo "BACKUP_DIR must resolve to a non-root directory." >&2
    exit 1
    ;;
esac

found=0
for checksum_file in "$BACKUP_DIR"/newshub-*.dump.sha256; do
  if [ ! -f "$checksum_file" ]; then
    continue
  fi
  found=1
  sha256sum -c "$checksum_file"
done

if [ "$found" -eq 0 ]; then
  echo "No backup checksum files found in $BACKUP_DIR." >&2
  exit 1
fi
