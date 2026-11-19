from pydantic import BaseModel, ConfigDict, Field


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=255)


class RoleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=255)


class PermissionCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    resource: str = Field(min_length=2, max_length=120)
    action: str = Field(min_length=2, max_length=60)


class PermissionUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    resource: str | None = Field(default=None, min_length=2, max_length=120)
    action: str | None = Field(default=None, min_length=2, max_length=60)


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    resource: str
    action: str


class AssignmentResponse(BaseModel):
    message: str


class UserPermissionsResponse(BaseModel):
    user_id: int
    permissions: list[str]


class UserRolesResponse(BaseModel):
    user_id: int
    roles: list[str]


class RolePermissionsResponse(BaseModel):
    role_id: int
    permissions: list[str]


class RolePermissionsUpdateRequest(BaseModel):
    permission_ids: list[int] = Field(min_length=0, max_length=500)


class RoleListResponse(BaseModel):
    items: list[RoleResponse]
    total: int
    page: int
    page_size: int


class PermissionListResponse(BaseModel):
    items: list[PermissionResponse]
    total: int
    page: int
    page_size: int
