from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.db.session import get_db
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.categories.router import router as category_router
from app.modules.comments.router import public_router as public_comments_router
from app.modules.comments.router import router as comments_router
from app.modules.files.router import public_router as public_files_router
from app.modules.files.router import router as files_router
from app.modules.news.router import router as news_router
from app.modules.rbac.router import router as rbac_router
from app.modules.settings.router import router as settings_router
from app.modules.signatures.router import router as signatures_router
from app.modules.users.router import router as users_router

app = FastAPI(title="NewsHub CMS API", version="0.1.0")
configure_logging()
app.add_middleware(RequestContextMiddleware)

origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(rbac_router)
app.include_router(settings_router)
app.include_router(category_router)
app.include_router(comments_router)
app.include_router(public_comments_router)
app.include_router(news_router)
app.include_router(files_router)
app.include_router(public_files_router)
app.include_router(signatures_router)
app.include_router(users_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get('/api/readiness')
async def readiness(db=Depends(get_db)) -> dict[str, str]:
    await db.execute(text('SELECT 1'))
    return {'status': 'ready', 'database': 'connected'}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "NewsHub CMS API"}
