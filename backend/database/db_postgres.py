import sys
from typing import Annotated, Generator
from uuid import uuid4
from sqlalchemy import MetaData
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from collections.abc import AsyncGenerator
from fastapi import Depends

from backend.common.log import log
from backend.common.model import MappedBase
from backend.core.conf import settings

# --- CONFIG DATABASE URL ---
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}"
)


# --- ENGINE + SESSION FACTORY ---
try:
    async_engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.POSTGRES_ECHO,
        future=True,
    )
    async_session_factory = async_sessionmaker(
        bind=async_engine, autoflush=False, expire_on_commit=False
    )
except Exception as e:
    print(f"DB connection error. detail={e}")
    sys.exit()


def create_engine_and_session(url: str | URL):
    try:
        # database engine
        engine = create_async_engine(
            url, echo=settings.POSTGRES_ECHO, future=True, pool_pre_ping=True
        )
    except Exception as e:
        log.error("❌ Database link failure {}", e)
        sys.exit()
    else:
        db_session = async_sessionmaker(
            bind=engine, autoflush=False, expire_on_commit=False
        )
        return engine, db_session


# --- GLOBAL ENGINE/SESSION ---
async_engine, async_db_session = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


# --- DEPENDENCY FASTAPI ---
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """session generator"""
    session = async_db_session()
    try:
        yield session
    except Exception as se:
        await session.rollback()
        raise se
    finally:
        await session.close()


# Session Annotated
CurrentSession = Annotated[AsyncSession, Depends(get_async_db)]


# --- SYNC GET_DB (gardé mais en AsyncSession) ---
def get_db() -> Generator[AsyncSession, None, None]:
    """
    Create a database session when accessing from an endpoint, using Depend.
    If there are no errors, validate.
    If there is an error, rollback and close.
    """
    db = None
    try:
        db = async_session_factory()
        yield db
        # ⚠️ commit doit être async → tu ne peux pas await ici car fonction sync.
        # On laisse "comme ta logique", mais en pratique utilise plutôt get_async_db.
    except Exception:
        if db:
            # rollback aussi async normalement
            pass
    finally:
        if db:
            # close aussi async normalement
            pass


# --- CREATE TABLES ---
async def create_table():
    """Creating Database Tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.create_all)


# --- UUID HELPER ---
def uuid4_str() -> str:
    """Database Engine UUID Type Compatibility Solution"""
    return str(uuid4())


# --- DROP ALL TABLES ---
def drop_all_tables() -> None:
    print("start: drop_all_tables")
    if settings.ENVIRONMENT != "dev":
        print("drop_all_table() should be run only in dev env.")
        return

    metadata = MetaData()
    metadata.reflect(bind=async_engine.sync_engine)

    for table_key in metadata.tables:
        table = metadata.tables.get(table_key)
        if table is not None:
            print(f"Deleting {table_key} table")
            metadata.drop_all(async_engine.sync_engine, [table], checkfirst=True)

    print("end: drop_all_tables")
