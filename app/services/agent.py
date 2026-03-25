from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable
from json import JSONDecodeError
from typing import Any

from openai import OpenAI

from app.tools.memory import save_memory, search_memory
from app.tools.tasks import create_task, get_tasks

logger = logging.getLogger(__name__)


class AgentService:
    """Application service for agent orchestration."""

    def __init__(self) -> None:
        self._model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._tool_handlers: dict[str, Callable[..., dict[str, Any]]] = {
            "create_task": create_task,
            "get_tasks": get_tasks,
            "save_memory": save_memory,
            "search_memory": search_memory,
        }
        self._tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a task for the current user.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                        },
                        "required": ["title"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_tasks",
                    "description": "Get tasks for the current user.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "save_memory",
                    "description": "Save a memory item for the current user.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "kind": {"type": "string"},
                        },
                        "required": ["content"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_memory",
                    "description": "Search memory for the current user.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                },
            },
        ]

    async def handle_message(self, user_id: str, message: str) -> str:
        logger.info("AgentService.handle_message called for user_id=%s", user_id)
        try:
            messages: list[dict[str, Any]] = [
                {
                    "role": "system",
                    "content": (
                        "You are an AI secretary. Use available functions when needed. "
                        "When you answer, be concise and actionable."
                    ),
                },
                {
                    "role": "user",
                    "content": f"user_id={user_id}\nmessage={message}",
                },
            ]

            for _ in range(5):
                completion = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    tools=self._tools,
                    tool_choice="auto",
                )
                assistant_message = completion.choices[0].message
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": call.id,
                                "type": call.type,
                                "function": {
                                    "name": call.function.name,
                                    "arguments": call.function.arguments,
                                },
                            }
                            for call in (assistant_message.tool_calls or [])
                        ],
                    }
                )

                tool_calls = assistant_message.tool_calls or []
                if not tool_calls:
                    return assistant_message.content or "Не удалось сформировать ответ."

                for call in tool_calls:
                    tool_name = call.function.name
                    tool_args = self._parse_tool_arguments(call.function.arguments)
                    tool_result = self._run_tool(tool_name=tool_name, user_id=user_id, tool_args=tool_args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(tool_result, ensure_ascii=False),
                        }
                    )

            logger.warning("Agent loop reached max iterations for user_id=%s", user_id)
            return "Я выполнил все шаги, но не смог завершить ответ. Попробуйте переформулировать запрос."
        except Exception:
            logger.exception("AgentService failed for user_id=%s", user_id)
            return "Произошла ошибка при обработке сообщения. Попробуйте еще раз."


    def _parse_tool_arguments(self, raw_arguments: str) -> dict[str, Any]:
        if not raw_arguments:
            return {}
        try:
            parsed: Any = json.loads(raw_arguments)
            if isinstance(parsed, dict):
                return parsed
            logger.warning("Tool arguments are not a JSON object: %s", raw_arguments)
            return {}
        except JSONDecodeError:
            logger.warning("Failed to decode tool arguments: %s", raw_arguments)
            return {}

    def _run_tool(self, tool_name: str, user_id: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        handler = self._tool_handlers.get(tool_name)
        if handler is None:
            logger.warning("Unknown tool requested: %s", tool_name)
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}

        try:
            if tool_name in {"create_task", "get_tasks", "save_memory", "search_memory"}:
                return handler(user_id=user_id, **tool_args)
            return {"status": "error", "message": f"Unsupported tool: {tool_name}"}
        except TypeError:
            logger.exception("Invalid tool arguments for %s: %s", tool_name, tool_args)
            return {
                "status": "error",
                "message": f"Invalid arguments for tool {tool_name}.",
                "tool_args": tool_args,
            }
        except Exception:
            logger.exception("Tool execution failed for %s", tool_name)
            return {"status": "error", "message": f"Tool {tool_name} execution failed."}

