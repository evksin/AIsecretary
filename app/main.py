from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from openai import OpenAIError
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.services.agent import AgentService


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


configure_logging()
app = FastAPI(title="AI Secretary API")
logger = logging.getLogger(__name__)
agent_service = AgentService()


class AgentRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class AgentResponse(BaseModel):
    response: str


def _error_payload(code: str, message: str, details: object | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent", response_model=AgentResponse)
async def agent(payload: AgentRequest) -> AgentResponse:
    logger.info("POST /agent called for user_id=%s", payload.user_id)
    response_text = await agent_service.handle_message(
        user_id=payload.user_id,
        message=payload.message,
    )
    return AgentResponse(response=response_text)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Validation failed for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_payload(
            code="validation_error",
            message="Некорректные входные данные.",
            details=exc.errors(),
        ),
    )


@app.exception_handler(OpenAIError)
async def openai_exception_handler(request: Request, exc: OpenAIError) -> JSONResponse:
    logger.exception("OpenAI error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=_error_payload(
            code="openai_error",
            message="Ошибка AI-провайдера. Повторите попытку позже.",
            details=str(exc),
        ),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=_error_payload(
            code="database_error",
            message="Ошибка базы данных. Повторите попытку позже.",
            details=str(exc.__class__.__name__),
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload(
            code="internal_error",
            message="Внутренняя ошибка сервиса.",
            details=str(exc.__class__.__name__),
        ),
    )

