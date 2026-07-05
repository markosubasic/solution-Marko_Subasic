import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tickethub.db")
    dummyjson_url: str = os.getenv("DUMMYJSON_URL", "https://dummyjson.com")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    token_expire_minutes: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))
    sync_interval_seconds: int = int(os.getenv("SYNC_INTERVAL_SECONDS", "300"))
    stats_cache_ttl: int = int(os.getenv("STATS_CACHE_TTL", "30"))


settings = Settings()
