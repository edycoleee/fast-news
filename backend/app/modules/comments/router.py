from fastapi import APIRouter, Depends, Query, Request, status

from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import require_csrf_protection
from app.modules.rbac.dependencies import require_any_permission
from app.modules.security.dependencies import get_rate_limit_service
from app.modules.security.rate_limit import RateLimitService

from .dependencies import get_comment_service
from .permissions import (
    DELETE_COMMENT_PERMISSION,
    MANAGE_COMMENT_PERMISSION,
    MODERATE_COMMENT_PERMISSION,
    READ_COMMENT_PERMISSION,
)
from .schemas import (
    AdminCommentResponse,
    CommentDeleteResponse,
    CommentListResponse,
    CommentModerateRequest,
    CommentSubmitResponse,
    PublicCommentCreateRequest,
    PublicCommentResponse,
)
from .service import CommentService

public_router = APIRouter(prefix='/api/public', tags=['comments'])
router = APIRouter(prefix='/api/comments', tags=['comments'])

READ_PERMISSIONS = [READ_COMMENT_PERMISSION, MANAGE_COMMENT_PERMISSION, 'news.manage']
MODERATE_PERMISSIONS = [MODERATE_COMMENT_PERMISSION, MANAGE_COMMENT_PERMISSION, 'news.manage']
DELETE_PERMISSIONS = [DELETE_COMMENT_PERMISSION, MANAGE_COMMENT_PERMISSION, 'news.manage']


@public_router.get(
    '/news/{slug}/comments',
    response_model=list[PublicCommentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_public_comments(
    slug: str,
    comment_service: CommentService = Depends(get_comment_service),
) -> list[PublicCommentResponse]:
    comments = await comment_service.list_public_comments(slug)
    return [PublicCommentResponse.model_validate(comment) for comment in comments]


@public_router.post(
    '/news/{slug}/comments',
    response_model=CommentSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_public_comment(
    slug: str,
    payload: PublicCommentCreateRequest,
    request: Request,
    comment_service: CommentService = Depends(get_comment_service),
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
) -> CommentSubmitResponse:
    await rate_limit_service.check_public_comment(request)
    comment = await comment_service.submit_public_comment(
        slug=slug,
        author_name=payload.author_name,
        content=payload.content,
        parent_id=payload.parent_id,
    )
    return CommentSubmitResponse(
        id=comment.id,
        message='Komentar diterima dan menunggu moderasi.',
    )


@router.get('/query', response_model=CommentListResponse, status_code=status.HTTP_200_OK)
async def list_comments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    status_filter: str | None = Query(default=None),
    _: AuthSession = Depends(require_any_permission(READ_PERMISSIONS)),
    comment_service: CommentService = Depends(get_comment_service),
) -> CommentListResponse:
    items, total = await comment_service.list_comments(
        page=page,
        page_size=page_size,
        status_filter=status_filter,
    )
    return CommentListResponse(
        items=[AdminCommentResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    '/{comment_id}/moderate',
    response_model=AdminCommentResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def moderate_comment(
    comment_id: int,
    payload: CommentModerateRequest,
    auth_session: AuthSession = Depends(require_any_permission(MODERATE_PERMISSIONS)),
    comment_service: CommentService = Depends(get_comment_service),
) -> AdminCommentResponse:
    comment = await comment_service.moderate_comment(
        actor_user_id=auth_session.user_id,
        comment_id=comment_id,
        target_status=payload.status,
        note=payload.note,
    )
    return AdminCommentResponse.model_validate(comment)


@router.delete(
    '/{comment_id}',
    response_model=CommentDeleteResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def delete_comment(
    comment_id: int,
    auth_session: AuthSession = Depends(require_any_permission(DELETE_PERMISSIONS)),
    comment_service: CommentService = Depends(get_comment_service),
) -> CommentDeleteResponse:
    await comment_service.delete_comment(
        actor_user_id=auth_session.user_id,
        comment_id=comment_id,
    )
    return CommentDeleteResponse(message='Comment deleted.')
