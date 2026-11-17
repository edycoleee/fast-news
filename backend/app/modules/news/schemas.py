from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NewsCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    slug: str = Field(min_length=3, max_length=255)
    summary: str | None = Field(default=None, max_length=500)
    content: str = Field(min_length=1)
    status: str = Field(default='draft', max_length=30)
    category_id: int | None = None


class NewsUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    slug: str | None = Field(default=None, min_length=3, max_length=255)
    summary: str | None = Field(default=None, max_length=500)
    content: str | None = None
    status: str | None = Field(default=None, max_length=30)
    category_id: int | None = None


class NewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str | None
    content: str
    status: str
    author_id: int | None
    category_id: int | None
    published_at: datetime | None


class PublicNewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str | None
    content: str
    published_at: datetime | None
    category_id: int | None


class NewsListResponse(BaseModel):
    items: list[NewsResponse]
    total: int
    page: int
    page_size: int
