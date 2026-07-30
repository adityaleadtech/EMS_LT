from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all API errors"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class NotFoundException(BaseAPIException):
    """Resource not found (404)"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' not found",
            error_code="RESOURCE_NOT_FOUND"
        )


class DuplicateEntryException(BaseAPIException):
    """Duplicate entry (409)"""
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with {field} '{value}' already exists",
            error_code="DUPLICATE_ENTRY"
        )


class ValidationException(BaseAPIException):
    """Validation error (422)"""
    def __init__(self, detail: str, errors: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )
        self.errors = errors


class BusinessRuleException(BaseAPIException):
    """Business rule violation (400)"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BUSINESS_RULE_VIOLATION"
        )


class UnauthorizedException(BaseAPIException):
    """Unauthorized access (401)"""
    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED"
        )


class ForbiddenException(BaseAPIException):
    """Forbidden access (403)"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN"
        )


class DatabaseException(BaseAPIException):
    """Database error (500)"""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )


class ImportException(BaseAPIException):
    """Import error (400)"""
    def __init__(self, detail: str, errors: Optional[list] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="IMPORT_ERROR"
        )
        self.errors = errors