from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


class AgentService:
    """Application service for agent orchestration."""

    async def handle_message(self, user_id: str, message: str) -> str:
        logger.info("AgentService.handle_message called for user_id=%s", user_id)
        return f"Stub response for user '{user_id}': {message}"

