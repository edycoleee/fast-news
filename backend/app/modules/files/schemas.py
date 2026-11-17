from pydantic import BaseModel, ConfigDict


class FileAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    mime_type: str
    size_bytes: int


class FileListResponse(BaseModel):
    items: list[FileAssetResponse]
    total: int
    page: int
    page_size: int


class FileDeleteResponse(BaseModel):
    message: str
