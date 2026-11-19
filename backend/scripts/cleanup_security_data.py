from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import AsyncSessionLocal
from app.modules.operations.retention import RetentionService


async def run(dry_run: bool, batch_size: int) -> dict:
    async with AsyncSessionLocal() as session:
        return await RetentionService(session).cleanup(
            dry_run=dry_run,
            batch_size=batch_size,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--batch-size', type=int, default=1000)
    args = parser.parse_args()
    if args.batch_size < 1 or args.batch_size > 10_000:
        parser.error('--batch-size must be between 1 and 10000')
    result = asyncio.run(run(args.dry_run, args.batch_size))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
