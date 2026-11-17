from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.categories.router import router as category_router
from app.modules.files.router import public_router as public_files_router
from app.modules.files.router import router as files_router
from app.modules.news.router import router as news_router
from app.modules.rbac.router import router as rbac_router
from app.modules.users.router import router as users_router

app = FastAPI(title="NewsHub CMS API", version="0.1.0")

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
app.include_router(rbac_router)
app.include_router(category_router)
app.include_router(news_router)
app.include_router(files_router)
app.include_router(public_files_router)
app.include_router(users_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "NewsHub CMS API"}
