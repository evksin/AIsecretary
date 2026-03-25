from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db import SessionLocal
from app.models import Task, User


logger = logging.getLogger(__name__)


def create_task(user_id: str, title: str, description: str | None = None) -> dict[str, Any]:
    logger.info("create_task called for user_id=%s", user_id)
    if not title or not title.strip():
        return {
            "status": "error",
            "message": "Task title is required.",
            "user_id": user_id,
        }

    db = SessionLocal()
    try:
        user = _get_or_create_user(db=db, external_id=user_id)
        task = Task(
            user_id=user.id,
            title=title.strip(),
            description=description.strip() if description else None,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info("Task created: id=%s user_id=%s", task.id, user_id)
        return {
            "status": "success",
            "message": "Task created.",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "due_at": task.due_at.isoformat() if task.due_at else None,
                "created_at": task.created_at.isoformat(),
            },
        }
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to create task for user_id=%s", user_id)
        return {
            "status": "error",
            "message": "Failed to create task due to database error.",
            "user_id": user_id,
        }
    finally:
        db.close()


def get_tasks(user_id: str) -> dict[str, Any]:
    logger.info("get_tasks called for user_id=%s", user_id)
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.external_id == user_id))
        if user is None:
            return {
                "status": "success",
                "message": "No tasks found.",
                "user_id": user_id,
                "tasks": [],
            }

        items = db.scalars(select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())).all()
        tasks = [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "status": item.status,
                "due_at": item.due_at.isoformat() if item.due_at else None,
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ]
        return {
            "status": "success",
            "message": "Tasks fetched.",
            "user_id": user_id,
            "tasks": tasks,
        }
    except SQLAlchemyError:
        logger.exception("Failed to fetch tasks for user_id=%s", user_id)
        return {
            "status": "error",
            "message": "Failed to fetch tasks due to database error.",
            "user_id": user_id,
            "tasks": [],
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

