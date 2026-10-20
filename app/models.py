from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    handle: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    max_rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    rank: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    max_rank: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    contest_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    contest_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    old_rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    new_rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    contest_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    problem_index: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    problem_name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    verdict: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    programming_language: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    submission_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    contest_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    problem_index: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    tags: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    handle: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )