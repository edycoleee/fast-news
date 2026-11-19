from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SignatureCreateRequest(BaseModel):
    purpose: str = Field(min_length=3, max_length=500)
    news_id: int | None = None
    signature_data_url: str = Field(min_length=1, max_length=1_000_000)


class SignatureRevokeRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class SignatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    signer_id: int | None
    news_id: int | None
    file_asset_id: int
    purpose: str
    status: str
    revocation_reason: str | None
    revoked_by_id: int | None
    revoked_at: datetime | None
    created_at: datetime


class SignatureListResponse(BaseModel):
    items: list[SignatureResponse]
    total: int
    page: int
    page_size: int
