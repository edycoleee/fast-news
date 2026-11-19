from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    APP_ENV: str = 'development'
    DATABASE_URL: str = 'postgresql+psycopg://newshub:change_me@localhost:5432/newshub'
    CORS_ORIGINS: str = 'http://localhost:5173,http://127.0.0.1:5173'
    SESSION_COOKIE_NAME: str = 'newshub_session'
    CSRF_COOKIE_NAME: str = 'newshub_csrf'
    CSRF_HEADER_NAME: str = 'X-CSRF-Token'
    SESSION_TTL_MINUTES: int = 480
    SESSION_COOKIE_SECURE: bool = False
    UPLOAD_DIR: str = 'storage/uploads'
    UPLOAD_MAX_SIZE_BYTES: int = 5 * 1024 * 1024
    SIGNATURE_MAX_SIZE_BYTES: int = 512 * 1024
    UPLOAD_HARD_CAP_BYTES: int = 100 * 1024 * 1024
    SIGNATURE_HARD_CAP_BYTES: int = 5 * 1024 * 1024
    COMMENT_HARD_CAP_LENGTH: int = 10_000
    SECURITY_SETTINGS_CACHE_SECONDS: int = 15


settings = Settings()
