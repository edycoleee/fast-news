from app.core.permissions import FeaturePermission


READ_AUDIT_PERMISSION = 'audit.read'
MANAGE_AUDIT_PERMISSION = 'audit.manage'

PERMISSIONS = (
    FeaturePermission(READ_AUDIT_PERMISSION, 'audit', 'read'),
    FeaturePermission(MANAGE_AUDIT_PERMISSION, 'audit', 'manage'),
)
