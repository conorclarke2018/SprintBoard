"""Global exception handlers: log every error and return a clear JSON message."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError

logger = logging.getLogger("app.errors")


def format_validation_errors(errors: list[dict]) -> str:
    """Turn Pydantic's error list into one readable sentence, e.g. 'Title: ...'."""
    messages = []
    for error in errors:
        location = [str(part) for part in error.get("loc", ()) if part not in ("body", "query", "path")]
        message = str(error.get("msg", "Invalid value")).removeprefix("Value error, ")
        if location:
            field = location[0].replace("_", " ").capitalize()
            messages.append(f"{field}: {message}")
        else:
            messages.append(message)
    return "; ".join(messages) or "Invalid request"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "%s %s -> %s: %s", request.method, request.url.path, exc.status_code, exc.message
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        message = format_validation_errors(list(exc.errors()))
        logger.warning("Validation failed on %s %s: %s", request.method, request.url.path, message)
        return JSONResponse(status_code=422, content={"detail": message})

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            logger.warning("404 Not found: %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500, content={"detail": "Something went wrong. Please try again."}
        )
