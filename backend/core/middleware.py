"""
Middleware configuration for Seikatsu backend.
Handles CORS, request/response logging, and optional authentication checks.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import time
import logging

# Configure logger for middleware
logger = logging.getLogger("middleware")
logger.setLevel(logging.INFO)

# Create console handler if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def setup_middleware(app: FastAPI):
    """
    Sets up all middleware for the FastAPI app, including:
    - CORS configuration for frontend access
    - Request/response logging with duration tracking
    - Optional authentication validation
    
    Args:
        app: FastAPI application instance
    """
    
    # -------------------------
    # 1. CORS Middleware
    # -------------------------
    # Allows Expo React Native frontend to communicate with backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*",  # Replace with specific origins in production
            # "exp://192.168.1.x:8081",  # Expo development
            # "https://your-production-domain.com"
        ],
        allow_credentials=True,
        allow_methods=["*"],  # GET, POST, PUT, DELETE, PATCH, OPTIONS
        allow_headers=["*"],  # Authorization, Content-Type, etc.
    )
    
    # -------------------------
    # 2. Request Logging Middleware
    # -------------------------
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Logs all incoming requests and their response times.
        Useful for debugging, monitoring, and performance tracking.
        """
        start_time = time.time()
        
        # Log incoming request
        logger.info(f"Incoming: {request.method} {request.url.path}")
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate duration
            duration = round(time.time() - start_time, 3)
            
            # Log completion with status code
            logger.info(
                f"Completed: {request.method} {request.url.path} "
                f"[{response.status_code}] in {duration}s"
            )
            
            return response
            
        except Exception as e:
            # Log errors
            duration = round(time.time() - start_time, 3)
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"failed after {duration}s - {str(e)}"
            )
            raise
    
    # -------------------------
    # 3. Optional: Auth Middleware (Commented Out)
    # -------------------------
    # Uncomment and modify when you implement JWT authentication
    
    # @app.middleware("http")
    # async def check_jwt(request: Request, call_next):
    #     """
    #     Validates JWT token and attaches user info to request state.
    #     Skips validation for public endpoints like /auth/login, /auth/register
    #     """
    #     # Skip auth for public endpoints
    #     public_paths = ["/auth/login", "/auth/register", "/docs", "/openapi.json"]
    #     if any(request.url.path.startswith(path) for path in public_paths):
    #         return await call_next(request)
    #     
    #     # Get token from Authorization header
    #     auth_header = request.headers.get("Authorization")
    #     if not auth_header or not auth_header.startswith("Bearer "):
    #         return JSONResponse(
    #             status_code=401,
    #             content={"detail": "Missing or invalid authorization header"}
    #         )
    #     
    #     token = auth_header.replace("Bearer ", "")
    #     
    #     try:
    #         # Validate token and extract user info (implement in security.py)
    #         # from app.core.security import decode_jwt
    #         # user_data = decode_jwt(token)
    #         # request.state.user = user_data
    #         pass
    #     except Exception as e:
    #         logger.warning(f"JWT validation failed: {str(e)}")
    #         return JSONResponse(
    #             status_code=401,
    #             content={"detail": "Invalid or expired token"}
    #         )
    #     
    #     return await call_next(request)
    
    # -------------------------
    # 4. Optional: Error Handler Middleware
    # -------------------------
    @app.middleware("http")
    async def catch_exceptions(request: Request, call_next):
        """
        Catches unhandled exceptions and returns consistent JSON error responses.
        Prevents server errors from leaking sensitive information.
        """
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "message": "An unexpected error occurred. Please try again later."
                }
            )
    
    logger.info("✓ Middleware setup completed")


# -------------------------
# Optional: Rate Limiting Helper
# -------------------------
# You can add rate limiting later using libraries like slowapi or fastapi-limiter
# Example structure:
#
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
#
# limiter = Limiter(key_func=get_remote_address)
#
# def setup_rate_limiting(app: FastAPI):
#     app.state.limiter = limiter
#     app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
#
# Then use @limiter.limit("5/minute") on your routes