from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.exceptions import (
    BaseAPIException,
    NotFoundException,
    DuplicateEntryException,
    ValidationException,
    DatabaseException
)

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(BaseAPIException)
    async def base_api_exception_handler(request: Request, exc: BaseAPIException):
        """Handle custom API exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "detail": exc.detail,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        """Handle 404 Not Found"""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "error_code": "RESOURCE_NOT_FOUND",
                "detail": exc.detail,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(DuplicateEntryException)
    async def duplicate_exception_handler(request: Request, exc: DuplicateEntryException):
        """Handle 409 Conflict"""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "status": "error",
                "error_code": "DUPLICATE_ENTRY",
                "detail": exc.detail,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        """Handle 422 Validation Error"""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "error_code": "VALIDATION_ERROR",
                "detail": exc.detail,
                "errors": exc.errors if hasattr(exc, 'errors') else None,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "error_code": "VALIDATION_ERROR",
                "detail": "Request validation failed",
                "errors": exc.errors(),
                "path": request.url.path
            }
        )
    
    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        """Handle 500 Database errors"""
        logger.error(f"Database error: {exc.detail}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error_code": "DATABASE_ERROR",
                "detail": exc.detail,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle SQLAlchemy errors"""
        logger.error(f"SQLAlchemy error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error_code": "DATABASE_ERROR",
                "detail": "Database operation failed",
                "path": request.url.path
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "detail": "An unexpected error occurred",
                "path": request.url.path
            }
        )