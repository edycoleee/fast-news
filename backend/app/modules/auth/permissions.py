from app.core.permissions import FeaturePermission


MANAGE_SESSIONS_PERMISSION = 'session.manage'

PERMISSIONS = (
    FeaturePermission(MANAGE_SESSIONS_PERMISSION, 'session', 'manage'),
)
