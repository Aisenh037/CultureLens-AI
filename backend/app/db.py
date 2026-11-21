"""Database access for the wedge experiments (waitlist + funnel events).

Postgres in production (DATABASE_URL from Render), SQLite in tests. When no
DATABASE_URL is configured the experiment endpoints answer 503 and the rest
of the app runs as before.
"""
import logging
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool

logger = logging.getLogger("app.db")


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WaitlistSignup(Base):
    __tablename__ = "waitlist_signups"
    __table_args__ = (UniqueConstraint("wedge", "email", name="uq_waitlist_wedge_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wedge: Mapped[str] = mapped_column(String(40), index=True)
    email: Mapped[str] = mapped_column(String(254))
    name: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[Optional[str]] = mapped_column(String(100))
    note: Mapped[Optional[str]] = mapped_column(String(500))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    wants_interview: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class ExperimentEvent(Base):
    __tablename__ = "experiment_events"
    __table_args__ = (Index("ix_events_wedge_event", "wedge", "event"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wedge: Mapped[str] = mapped_column(String(40))
    event: Mapped[str] = mapped_column(String(20))
    visitor_id: Mapped[str] = mapped_column(String(64))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


def normalise_url(url: str) -> str:
    """Render hands out postgres:// URLs; SQLAlchemy's async driver needs the dialect named."""
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


def make_engine(url: str) -> AsyncEngine:
    url = normalise_url(url)
    if url.startswith("sqlite"):
        # One shared connection so an in-memory test database persists.
        return create_async_engine(url, poolclass=StaticPool, connect_args={"check_same_thread": False})
    return create_async_engine(url, pool_size=5, max_overflow=5, pool_pre_ping=True)


class Database:
    def __init__(self, url: Optional[str]):
        self.engine: Optional[AsyncEngine] = make_engine(url) if url else None
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False) if self.engine else None

    @property
    def enabled(self) -> bool:
        return self.engine is not None

    async def create_tables(self) -> None:
        if not self.engine:
            logger.info("DATABASE_URL not set; experiment endpoints are disabled.")
            return
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        if self.engine:
            await self.engine.dispose()

    async def session(self) -> AsyncIterator[AsyncSession]:
        assert self.sessions is not None
        async with self.sessions() as session:
            yield session
