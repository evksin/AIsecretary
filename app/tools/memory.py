from __future__ import annotations

import logging
from typing import Any


logger = logging.getLogger(__name__)


def save_memory(user_id: str, content: str) -> dict[str, Any]:
    logger.info("save_memory called for user_id=%s", user_id)
    return {
        "status": "not_implemented",
        "message": "Tool save_memory will be implemented on next stage.",
        "user_id": user_id,
        "content": content,
    }


def search_memory(user_id: str, query: str) -> dict[str, Any]:
    logger.info("search_memory called for user_id=%s", user_id)
    return {
        "status": "not_implemented",
        "message": "Tool search_memory will be implemented on next stage.",
        "user_id": user_id,
        "query": query,
        "results": [],
    }

