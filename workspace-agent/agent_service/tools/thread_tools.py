from __future__ import annotations

from datetime import UTC, datetime

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from sqlalchemy import Boolean, DateTime, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from agent_service.db.session import session_scope


class Base(DeclarativeBase):
    pass


class Thread(Base):
    __tablename__ = "threads"

    thread_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_uid: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str | None] = mapped_column(String)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def ensure_thread_record(thread_id: str, user_uid: str, title: str | None = None) -> dict:
    now = datetime.now(UTC)
    with session_scope() as db:
        thread = db.scalar(select(Thread).where(Thread.thread_id == thread_id))
        if thread is None:
            thread = Thread(
                thread_id=thread_id,
                user_uid=user_uid,
                title=title,
                is_archived=False,
                created_at=now,
                updated_at=now,
                last_message_at=now,
            )
            db.add(thread)
        elif thread.user_uid != user_uid:
            return {"error": "Thread does not belong to this user"}
        else:
            thread.updated_at = now
            thread.last_message_at = now
        return {
            "thread_id": thread.thread_id,
            "user_uid": thread.user_uid,
            "title": thread.title,
            "is_archived": thread.is_archived,
        }


@tool
def get_thread_metadata_tool(config: RunnableConfig) -> dict:
    """Read persisted metadata for the current conversation thread."""
    configurable = config.get("configurable", {})
    thread_id = configurable.get("thread_id")
    user_uid = configurable.get("user_uid")
    if not thread_id or not user_uid:
        return {"error": "thread_id and user_uid are required"}
    with session_scope() as db:
        thread = db.scalar(select(Thread).where(Thread.thread_id == thread_id))
        if thread is None or thread.user_uid != user_uid:
            return {"error": "Thread not found"}
        return {
            "thread_id": thread.thread_id,
            "user_uid": thread.user_uid,
            "title": thread.title,
            "is_archived": thread.is_archived,
            "updated_at": thread.updated_at.isoformat(),
            "last_message_at": thread.last_message_at.isoformat(),
        }
