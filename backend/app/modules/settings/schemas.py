from pydantic import BaseModel, Field


class RuntimeSettingResponse(BaseModel):
    key: str
    category: str
    label: str
    value_type: str
    value: int | bool
    minimum: int | None
    maximum: int | None
    is_default: bool


class RuntimeSettingsResponse(BaseModel):
    items: list[RuntimeSettingResponse]


class RuntimeSettingUpdate(BaseModel):
    key: str = Field(min_length=3, max_length=120)
    value: int | bool


class RuntimeSettingsUpdateRequest(BaseModel):
    settings: list[RuntimeSettingUpdate] = Field(min_length=1, max_length=50)


class RuntimeSettingsPublicResponse(BaseModel):
    comment_max_length: int
    upload_max_size_bytes: int
    signature_max_size_bytes: int


class RetentionCleanupRequest(BaseModel):
    dry_run: bool = True
    batch_size: int = Field(default=1000, ge=1, le=10_000)


class RetentionCleanupCounts(BaseModel):
    audit_logs: int
    auth_sessions: int
    rate_limit_buckets: int


class RetentionCleanupResponse(BaseModel):
    dry_run: bool
    eligible: RetentionCleanupCounts
    deleted: RetentionCleanupCounts
    cutoff: dict[str, str]
