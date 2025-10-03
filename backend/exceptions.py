from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# ===================== #
#  BASE CUSTOM EXCEPTIONS
# ===================== #

class SeikatsuException(Exception):
    """Base exception for all Seikatsu-specific errors"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


# ===================== #
#  RESOURCE EXCEPTIONS
# ===================== #

class ResourceNotFoundException(SeikatsuException):
    """Raised when a requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: Optional[int] = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" with ID {resource_id}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The requested {resource_type.lower()} does not exist"
        )


class ResourceAlreadyExistsException(SeikatsuException):
    """Raised when attempting to create a resource that already exists"""
    
    def __init__(self, resource_type: str, field: str, value: str):
        super().__init__(
            message=f"{resource_type} with {field} '{value}' already exists",
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A {resource_type.lower()} with this {field} is already registered"
        )


class ResourceAccessDeniedException(SeikatsuException):
    """Raised when user attempts to access a resource they don't own"""
    
    def __init__(self, resource_type: str):
        super().__init__(
            message=f"Access denied to {resource_type}",
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )


# ===================== #
#  AUTHENTICATION EXCEPTIONS
# ===================== #

class AuthenticationException(SeikatsuException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or authentication token"
        )


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid"""
    
    def __init__(self):
        super().__init__(message="Invalid username or password")


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired"""
    
    def __init__(self):
        super().__init__(message="Authentication token has expired")


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid or malformed"""
    
    def __init__(self):
        super().__init__(message="Invalid authentication token")


# ===================== #
#  VALIDATION EXCEPTIONS
# ===================== #

class ValidationException(SeikatsuException):
    """Raised when request data validation fails"""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error: {field}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )


class InvalidXPAmountException(ValidationException):
    """Raised when XP amount is invalid"""
    
    def __init__(self):
        super().__init__(
            field="xp_gained",
            message="XP amount must be a non-zero integer"
        )


class InvalidDateRangeException(ValidationException):
    """Raised when date range is invalid"""
    
    def __init__(self):
        super().__init__(
            field="date_range",
            message="End date must be after start date"
        )


class InvalidPaginationException(ValidationException):
    """Raised when pagination parameters are invalid"""
    
    def __init__(self, param: str):
        super().__init__(
            field=param,
            message=f"Invalid pagination parameter: {param} must be positive"
        )


# ===================== #
#  DATABASE EXCEPTIONS
# ===================== #

class DatabaseException(SeikatsuException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


class DatabaseConnectionException(DatabaseException):
    """Raised when database connection fails"""
    
    def __init__(self):
        super().__init__(message="Failed to connect to database")


class DatabaseIntegrityException(DatabaseException):
    """Raised when database integrity constraints are violated"""
    
    def __init__(self, constraint: str):
        super().__init__(
            message=f"Database integrity violation: {constraint}"
        )


# ===================== #
#  BUSINESS LOGIC EXCEPTIONS
# ===================== #

class TaskAlreadyCompletedException(SeikatsuException):
    """Raised when attempting to complete an already completed task"""
    
    def __init__(self):
        super().__init__(
            message="Task is already completed",
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task has already been marked as complete"
        )


class TaskNotCompletedException(SeikatsuException):
    """Raised when attempting to uncomplete a task that isn't completed"""
    
    def __init__(self):
        super().__init__(
            message="Task is not completed",
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not marked as complete"
        )


class InsufficientXPException(SeikatsuException):
    """Raised when user doesn't have enough XP for an operation"""
    
    def __init__(self, required: int, current: int):
        super().__init__(
            message="Insufficient XP",
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Required: {required} XP, Current: {current} XP"
        )


# ===================== #
#  ERROR RESPONSE BUILDER
# ===================== #

def build_error_response(
    message: str,
    status_code: int,
    detail: Optional[str] = None,
    path: Optional[str] = None,
    errors: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build a standardized error response"""
    response = {
        "error": message,
        "status_code": status_code
    }
    
    if detail:
        response["detail"] = detail
    
    if path:
        response["path"] = path
    
    if errors:
        response["errors"] = errors
    
    return response


# ===================== #
#  EXCEPTION HANDLERS
# ===================== #

async def seikatsu_exception_handler(request: Request, exc: SeikatsuException) -> JSONResponse:
    """Handler for all Seikatsu custom exceptions"""
    logger.error(f"Seikatsu Exception: {exc.message} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(
            message=exc.message,
            status_code=exc.status_code,
            detail=exc.detail,
            path=str(request.url.path)
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for FastAPI validation errors"""
    logger.warning(f"Validation Error - Path: {request.url.path}, Errors: {exc.errors()}")
    
    # Format validation errors
    formatted_errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        formatted_errors[field] = error["msg"]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_error_response(
            message="Validation error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="One or more fields contain invalid data",
            path=str(request.url.path),
            errors=formatted_errors
        )
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handler for SQLAlchemy database errors"""
    logger.error(f"Database Error - Path: {request.url.path}, Error: {str(exc)}")
    
    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        # Extract constraint name if available
        error_str = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=build_error_response(
                message="Database constraint violation",
                status_code=status.HTTP_409_CONFLICT,
                detail="The operation violates database constraints (duplicate entry or foreign key)",
                path=str(request.url.path)
            )
        )
    
    # Generic database error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_response(
            message="Database error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while accessing the database",
            path=str(request.url.path)
        )
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for all unhandled exceptions"""
    logger.error(f"Unhandled Exception - Path: {request.url.path}, Error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_response(
            message="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
            path=str(request.url.path)
        )
    )


# ===================== #
#  EXCEPTION HANDLER REGISTRATION
# ===================== #

def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app
    
    Usage in main.py:
        from exceptions import register_exception_handlers
        
        app = FastAPI()
        register_exception_handlers(app)
    """
    app.add_exception_handler(SeikatsuException, seikatsu_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered successfully")


# ===================== #
#  HELPER FUNCTIONS
# ===================== #

def raise_not_found(resource_type: str, resource_id: Optional[int] = None) -> None:
    """Helper to raise not found exception"""
    raise ResourceNotFoundException(resource_type, resource_id)


def raise_already_exists(resource_type: str, field: str, value: str) -> None:
    """Helper to raise already exists exception"""
    raise ResourceAlreadyExistsException(resource_type, field, value)


def raise_access_denied(resource_type: str) -> None:
    """Helper to raise access denied exception"""
    raise ResourceAccessDeniedException(resource_type)


def raise_invalid_credentials() -> None:
    """Helper to raise invalid credentials exception"""
    raise InvalidCredentialsException()