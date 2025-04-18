from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

engine = create_async_engine(url=settings.get_db_url_async)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
