from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def _coerce_async_url(url: str) -> str:
    """Managed Postgres providers (Render / Heroku / Railway) return URLs in
    the sync `postgres://` shape. SQLAlchemy 2.x async needs an explicit driver,
    so we rewrite the scheme before constructing the engine."""
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


engine = create_async_engine(_coerce_async_url(settings.DATABASE_URL), echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
