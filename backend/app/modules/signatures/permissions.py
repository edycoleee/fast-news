from app.core.permissions import FeaturePermission


READ_SIGNATURE_PERMISSION = 'signature.read'
CREATE_SIGNATURE_PERMISSION = 'signature.create'
REVOKE_SIGNATURE_PERMISSION = 'signature.revoke'
MANAGE_SIGNATURE_PERMISSION = 'signature.manage'

PERMISSIONS = (
    FeaturePermission(READ_SIGNATURE_PERMISSION, 'signature', 'read'),
    FeaturePermission(CREATE_SIGNATURE_PERMISSION, 'signature', 'create'),
    FeaturePermission(REVOKE_SIGNATURE_PERMISSION, 'signature', 'revoke'),
    FeaturePermission(MANAGE_SIGNATURE_PERMISSION, 'signature', 'manage'),
)
