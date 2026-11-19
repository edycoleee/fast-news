from app.modules.categories.permissions import PERMISSIONS as CATEGORY_PERMISSIONS
from app.modules.auth.permissions import PERMISSIONS as AUTH_PERMISSIONS
from app.modules.audit.permissions import PERMISSIONS as AUDIT_PERMISSIONS
from app.modules.comments.permissions import PERMISSIONS as COMMENT_PERMISSIONS
from app.modules.files.permissions import PERMISSIONS as FILE_PERMISSIONS
from app.modules.news.permissions import PERMISSIONS as NEWS_PERMISSIONS
from app.modules.rbac.permissions import PERMISSIONS as RBAC_PERMISSIONS
from app.modules.settings.permissions import PERMISSIONS as SETTINGS_PERMISSIONS
from app.modules.signatures.permissions import PERMISSIONS as SIGNATURE_PERMISSIONS

from app.core.permissions import FeaturePermission


def get_registered_permissions() -> tuple[FeaturePermission, ...]:
    manifests = (
        CATEGORY_PERMISSIONS,
        AUTH_PERMISSIONS,
        AUDIT_PERMISSIONS,
        COMMENT_PERMISSIONS,
        FILE_PERMISSIONS,
        NEWS_PERMISSIONS,
        RBAC_PERMISSIONS,
        SETTINGS_PERMISSIONS,
        SIGNATURE_PERMISSIONS,
    )
    permissions = tuple(permission for manifest in manifests for permission in manifest)
    names = [permission.name for permission in permissions]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise RuntimeError(f'Duplicate permission definitions: {duplicates}')
    return permissions


def get_registered_permission_names() -> frozenset[str]:
    return frozenset(permission.name for permission in get_registered_permissions())
