from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True, slots=True)
class SettingDefinition:
    key: str
    category: str
    label: str
    value_type: str
    default: int | bool
    minimum: int | None = None
    maximum: int | None = None

    def validate(self, value: object) -> int | bool:
        if self.value_type == 'boolean':
            if not isinstance(value, bool):
                raise ValueError(f'{self.key} must be boolean.')
            return value
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f'{self.key} must be integer.')
        if self.minimum is not None and value < self.minimum:
            raise ValueError(f'{self.key} minimum is {self.minimum}.')
        if self.maximum is not None and value > self.maximum:
            raise ValueError(f'{self.key} maximum is {self.maximum}.')
        return value


DEFINITIONS = (
    SettingDefinition(
        'upload.max_size_bytes',
        'upload',
        'Maksimum ukuran upload',
        'integer',
        settings.UPLOAD_MAX_SIZE_BYTES,
        1024,
        settings.UPLOAD_HARD_CAP_BYTES,
    ),
    SettingDefinition(
        'signature.max_size_bytes',
        'upload',
        'Maksimum ukuran signature',
        'integer',
        settings.SIGNATURE_MAX_SIZE_BYTES,
        1024,
        settings.SIGNATURE_HARD_CAP_BYTES,
    ),
    SettingDefinition(
        'comment.max_length',
        'comments',
        'Maksimum panjang komentar',
        'integer',
        2000,
        100,
        settings.COMMENT_HARD_CAP_LENGTH,
    ),
    SettingDefinition(
        'login.rate_limit_per_minute',
        'security',
        'Batas login per menit per IP',
        'integer',
        10,
        3,
        60,
    ),
    SettingDefinition(
        'login.failure_threshold',
        'security',
        'Batas kegagalan sebelum cooldown',
        'integer',
        5,
        3,
        20,
    ),
    SettingDefinition(
        'login.cooldown_seconds',
        'security',
        'Durasi cooldown login',
        'integer',
        300,
        60,
        7200,
    ),
    SettingDefinition(
        'comment.rate_limit_per_hour',
        'security',
        'Batas komentar per jam per IP',
        'integer',
        20,
        1,
        100,
    ),
    SettingDefinition(
        'upload.rate_limit_per_hour',
        'security',
        'Batas upload per jam per user',
        'integer',
        60,
        1,
        500,
    ),
    SettingDefinition(
        'retention.audit_log_days',
        'retention',
        'Retention audit log',
        'integer',
        180,
        30,
        730,
    ),
    SettingDefinition(
        'retention.auth_session_days',
        'retention',
        'Retention session selesai/expired',
        'integer',
        30,
        7,
        365,
    ),
    SettingDefinition(
        'retention.rate_limit_days',
        'retention',
        'Retention rate-limit bucket',
        'integer',
        7,
        1,
        90,
    ),
    SettingDefinition(
        'retention.audit_archive_days',
        'retention',
        'Target archive audit sebelum cleanup',
        'integer',
        365,
        180,
        730,
    ),
)

DEFINITIONS_BY_KEY = {definition.key: definition for definition in DEFINITIONS}
