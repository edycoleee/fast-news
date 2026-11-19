from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class PublicCommentCreateRequest(BaseModel):
    author_name: str = Field(min_length=2, max_length=80)
    content: str = Field(min_length=3, max_length=10_000)
    parent_id: int | None = Field(default=None, gt=0)


class CommentModerateRequest(BaseModel):
    status: str = Field(pattern='^(approved|rejected)$')
    note: str | None = Field(default=None, max_length=500)


class PublicCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: str
    content: str
    parent_id: int | None
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> str:
        return value.replace(tzinfo=value.tzinfo or timezone.utc).isoformat()


class AdminCommentResponse(PublicCommentResponse):
    news_id: int
    user_id: int | None
    status: str
    moderation_note: str | None
    moderated_by_id: int | None
    moderated_at: datetime | None

    @field_serializer('moderated_at')
    def serialize_moderated_at(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.replace(tzinfo=value.tzinfo or timezone.utc).isoformat()


class CommentListResponse(BaseModel):
    items: list[AdminCommentResponse]
    total: int
    page: int
    page_size: int


class CommentSubmitResponse(BaseModel):
    id: int
    message: str


class CommentDeleteResponse(BaseModel):
    message: str
