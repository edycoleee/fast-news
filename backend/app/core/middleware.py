from __future__ import annotations

from time import perf_counter
import logging
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger('newshub.http')


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = (
            request.headers.get('X-Correlation-ID')
            or request.headers.get('X-Request-ID')
            or uuid.uuid4().hex
        )
        request.state.correlation_id = correlation_id
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((perf_counter() - started) * 1000, 2)
            logger.exception(
                'request_failed',
                extra={
                    'correlation_id': correlation_id,
                    'method': request.method,
                    'path': request.url.path,
                    'duration_ms': duration_ms,
                },
            )
            raise
        duration_ms = round((perf_counter() - started) * 1000, 2)
        response.headers['X-Correlation-ID'] = correlation_id
        logger.info(
            'request_completed',
            extra={
                'correlation_id': correlation_id,
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration_ms': duration_ms,
            },
        )
        return response
