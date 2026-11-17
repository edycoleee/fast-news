from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import get_current_auth_session, require_csrf_protection
from app.modules.rbac.dependencies import require_any_permission, require_permission

from .dependencies import get_category_service
from .schemas import CategoryCreateRequest, CategoryListResponse, CategoryResponse, CategoryUpdateRequest
from .service import CategoryService

router = APIRouter(prefix='/api/categories', tags=['categories'])

MANAGE_CATEGORY_PERMISSION = 'category.manage'
MANAGE_NEWS_PERMISSION = 'news.manage'


@router.get('', response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
async def list_categories(
    _: AuthSession = Depends(require_any_permission([MANAGE_CATEGORY_PERMISSION, MANAGE_NEWS_PERMISSION])),
    category_service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponse]:
    categories = await category_service.list_categories()
    return [CategoryResponse.model_validate(item) for item in categories]


@router.get('/query', response_model=CategoryListResponse, status_code=status.HTTP_200_OK)
async def list_categories_paginated(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    _: AuthSession = Depends(get_current_auth_session),
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryListResponse:
    items, total = await category_service.list_categories_paginated(page=page, page_size=page_size, search=search)
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get('/{category_id}', response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category(
    category_id: int,
    _: AuthSession = Depends(require_permission(MANAGE_CATEGORY_PERMISSION)),
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    category = await category_service.get_category(category_id)
    return CategoryResponse.model_validate(category)


@router.post(
    '',
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf_protection)],
)
async def create_category(
    payload: CategoryCreateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_CATEGORY_PERMISSION)),
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    category = await category_service.create_category(
        actor_user_id=auth_session.user_id,
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        parent_id=payload.parent_id,
    )
    return CategoryResponse.model_validate(category)


@router.put(
    '/{category_id}',
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def update_category(
    category_id: int,
    payload: CategoryUpdateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_CATEGORY_PERMISSION)),
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    category = await category_service.update_category(
        actor_user_id=auth_session.user_id,
        category_id=category_id,
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        parent_id=payload.parent_id,
    )
    return CategoryResponse.model_validate(category)


@router.delete(
    '/{category_id}',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def delete_category(
    category_id: int,
    auth_session: AuthSession = Depends(require_permission(MANAGE_CATEGORY_PERMISSION)),
    category_service: CategoryService = Depends(get_category_service),
) -> dict[str, str]:
    await category_service.delete_category(actor_user_id=auth_session.user_id, category_id=category_id)
    return {'message': 'Category deleted.'}
