from __future__ import annotations

import logging
from typing import Any


logger = logging.getLogger(__name__)


def create_task(user_id: str, title: str, description: str | None = None) -> dict[str, Any]:
    logger.info("create_task called for user_id=%s", user_id)
    return {
        "status": "not_implemented",
        "message": "Tool create_task will be implemented on next stage.",
        "user_id": user_id,
        "title": title,
        "description": description,
    }


def get_tasks(user_id: str) -> dict[str, Any]:
    logger.info("get_tasks called for user_id=%s", user_id)
    return {
        "status": "not_implemented",
        "message": "Tool get_tasks will be implemented on next stage.",
        "user_id": user_id,
        "tasks": [],
    }

