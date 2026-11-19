from app.core.permissions import FeaturePermission


READ_COMMENT_PERMISSION = 'comment.read'
MODERATE_COMMENT_PERMISSION = 'comment.moderate'
DELETE_COMMENT_PERMISSION = 'comment.delete'
MANAGE_COMMENT_PERMISSION = 'comment.manage'

PERMISSIONS = (
    FeaturePermission(READ_COMMENT_PERMISSION, 'comment', 'read'),
    FeaturePermission(MODERATE_COMMENT_PERMISSION, 'comment', 'moderate'),
    FeaturePermission(DELETE_COMMENT_PERMISSION, 'comment', 'delete'),
    FeaturePermission(MANAGE_COMMENT_PERMISSION, 'comment', 'manage'),
)
