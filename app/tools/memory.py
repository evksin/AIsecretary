from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db import SessionLocal
from app.models import Memory, User


logger = logging.getLogger(__name__)


def save_memory(user_id: str, content: str, kind: str = "note") -> dict[str, Any]:
    logger.info("save_memory called for user_id=%s", user_id)
    if not content or not content.strip():
        return {
            "status": "error",
            "message": "Memory content is required.",
            "user_id": user_id,
        }

    db = SessionLocal()
    try:
        user = _get_or_create_user(db=db, external_id=user_id)
        memory = Memory(
            user_id=user.id,
            content=content.strip(),
            kind=kind.strip() if kind.strip() else "note",
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)

        logger.info("Memory saved: id=%s user_id=%s", memory.id, user_id)
        return {
            "status": "success",
            "message": "Memory saved.",
            "memory": {
                "id": memory.id,
                "kind": memory.kind,
                "content": memory.content,
                "created_at": memory.created_at.isoformat(),
            },
        }
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to save memory for user_id=%s", user_id)
        return {
            "status": "error",
            "message": "Failed to save memory due to database error.",
            "user_id": user_id,
        }
    finally:
        db.close()


def search_memory(user_id: str, query: str) -> dict[str, Any]:
    logger.info("search_memory called for user_id=%s", user_id)
    if not query or not query.strip():
        return {
            "status": "error",
            "message": "Search query is required.",
            "user_id": user_id,
            "results": [],
        }

    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.external_id == user_id))
        if user is None:
            return {
                "status": "success",
                "message": "No memory found.",
                "user_id": user_id,
                "query": query,
                "results": [],
            }

        items = db.scalars(
            select(Memory)
            .where(Memory.user_id == user.id, Memory.content.ilike(f"%{query.strip()}%"))
            .order_by(Memory.created_at.desc())
            .limit(20)
        ).all()

        results = [
            {
                "id": item.id,
                "kind": item.kind,
                "content": item.content,
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ]

        return {
            "status": "success",
            "message": "Memory search completed.",
            "user_id": user_id,
            "query": query,
            "results": results,
        }
    except SQLAlchemyError:
        logger.exception("Failed to search memory for user_id=%s", user_id)
        return {
            "status": "error",
            "message": "Failed to search memory due to database error.",
            "user_id": user_id,
            "query": query,
            "results": [],
        }
    finally:
        db.close()


def _get_or_create_user(db: Any, external_id: str) -> User:
    user = db.scalar(select(User).where(User.external_id == external_id))
    if user is not None:
        return user

    user = User(external_id=external_id)
    db.add(user)
    db.flush()
    return user

