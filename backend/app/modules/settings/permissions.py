from app.core.permissions import FeaturePermission


READ_SETTINGS_PERMISSION = 'settings.read'
UPDATE_SETTINGS_PERMISSION = 'settings.update'
MANAGE_SETTINGS_PERMISSION = 'settings.manage'

PERMISSIONS = (
    FeaturePermission(READ_SETTINGS_PERMISSION, 'settings', 'read'),
    FeaturePermission(UPDATE_SETTINGS_PERMISSION, 'settings', 'update'),
    FeaturePermission(MANAGE_SETTINGS_PERMISSION, 'settings', 'manage'),
)
