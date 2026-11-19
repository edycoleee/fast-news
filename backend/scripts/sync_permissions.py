from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.models.permission import Permission
from app.modules.rbac.permission_registry import get_registered_permissions


def sync_permissions(session: Session) -> int:
    created = 0
    for definition in get_registered_permissions():
        permission = session.execute(
            select(Permission).where(Permission.name == definition.name)
        ).scalar_one_or_none()
        if permission is None:
            session.add(
                Permission(
                    name=definition.name,
                    resource=definition.resource,
                    action=definition.action,
                )
            )
            created += 1
            continue
        if (
            permission.resource != definition.resource
            or permission.action != definition.action
        ):
            raise RuntimeError(
                f'Permission metadata conflict for {definition.name}; '
                'resolve it through a reviewed migration.'
            )

    return created


def main() -> None:
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as session:
        created = sync_permissions(session)
        session.commit()
    print(f'Permission registry synchronized: {created} created, 0 updated.')


if __name__ == '__main__':
    main()
