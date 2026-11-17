from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import require_csrf_protection
from app.modules.rbac.dependencies import require_permission

from .dependencies import get_news_service
from .schemas import NewsCreateRequest, NewsListResponse, NewsResponse, NewsUpdateRequest, PublicNewsResponse
from .service import NewsService

router = APIRouter(tags=['news'])

MANAGE_NEWS_PERMISSION = 'news.manage'


@router.get('/api/news', response_model=list[NewsResponse], status_code=status.HTTP_200_OK)
async def list_news(
    _: AuthSession = Depends(require_permission(MANAGE_NEWS_PERMISSION)),
    news_service: NewsService = Depends(get_news_service),
) -> list[NewsResponse]:
    news_items = await news_service.list_news()
    return [NewsResponse.model_validate(item) for item in news_items]


@router.get('/api/news/query', response_model=NewsListResponse, status_code=status.HTTP_200_OK)
async def list_news_paginated(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    status_filter: str | None = Query(default=None),
    _: AuthSession = Depends(require_permission(MANAGE_NEWS_PERMISSION)),
    news_service: NewsService = Depends(get_news_service),
) -> NewsListResponse:
    news_items, total = await news_service.list_news_paginated(
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
    )
    return NewsListResponse(
        items=[NewsResponse.model_validate(item) for item in news_items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get('/api/news/{news_id}', response_model=NewsResponse, status_code=status.HTTP_200_OK)
async def get_news(
    news_id: int,
    _: AuthSession = Depends(require_permission(MANAGE_NEWS_PERMISSION)),
    news_service: NewsService = Depends(get_news_service),
) -> NewsResponse:
    news = await news_service.get_news(news_id)
    return NewsResponse.model_validate(news)


@router.post(
    '/api/news',
    response_model=NewsResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf_protection)],
)
async def create_news(
    payload: NewsCreateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_NEWS_PERMISSION)),
    news_service: NewsService = Depends(get_news_service),
) -> NewsResponse:
    news = await news_service.create_news(
        actor_user_id=auth_session.user_id,
        title=payload.title,
        slug=payload.slug,
        summary=payload.summary,
        content=payload.content,
        status_value=payload.status,
        category_id=payload.category_id,
    )
    return NewsResponse.model_validate(news)


@router.put(
    '/api/news/{news_id}',
    response_model=NewsResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def update_news(
    news_id: int,
    payload: NewsUpdateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_NEWS_PERMISSION)),
    news_service: NewsService = Depends(get_news_service),
) -> NewsResponse:
    news = await news_service.update_news(
        actor_user_id=auth_session.user_id,
        news_id=news_id,
        title=payload.title,
        slug=payload.slug,
        summary=payload.summary,
        content=payload.content,
        status_value=payload.status,
        category_id=payload.category_id,
    )
    return NewsResponse.model_validate(news)


@router.delete(
    '/api/news/{news_id}',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def delete_news(
    news_id: int,
    auth_session: AuthSession = Depends(require_permission(MANAGE_NEWS_PERMISSION)),
    news_service: NewsService = Depends(get_news_service),
) -> dict[str, str]:
    await news_service.delete_news(actor_user_id=auth_session.user_id, news_id=news_id)
    return {'message': 'News deleted.'}


@router.get('/api/public/news', response_model=list[PublicNewsResponse], status_code=status.HTTP_200_OK)
async def list_public_news(
    search: str | None = Query(default=None),
    news_service: NewsService = Depends(get_news_service),
) -> list[PublicNewsResponse]:
    news_items = await news_service.list_public_news()
    if search:
        normalized_search = search.strip().lower()
        news_items = [
            item
            for item in news_items
            if normalized_search in item.title.lower() or (item.summary and normalized_search in item.summary.lower())
        ]
    return [PublicNewsResponse.model_validate(item) for item in news_items]


@router.get('/api/public/news/{slug}', response_model=PublicNewsResponse, status_code=status.HTTP_200_OK)
async def get_public_news_by_slug(
    slug: str,
    news_service: NewsService = Depends(get_news_service),
) -> PublicNewsResponse:
    news = await news_service.get_public_news_by_slug(slug=slug)
    return PublicNewsResponse.model_validate(news)
