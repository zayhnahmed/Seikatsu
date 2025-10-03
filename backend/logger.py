import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional
import json
from config import settings

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    Useful for log aggregation tools (ELK, Grafana, etc.)
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data["extra"] = getattr(record, "extra_data", {})
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for better readability in development
    """
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format: [TIMESTAMP] LEVEL - MODULE:FUNCTION:LINE - MESSAGE
        formatted = (
            f"{log_color}[{self.formatTime(record)}] "
            f"{record.levelname:8s}{reset} - "
            f"{record.module}:{record.funcName}:{record.lineno} - "
            f"{record.getMessage()}"
        )
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logger(
    name: str = "seikatsu",
    log_level: Optional[str] = None,
    log_to_file: bool = True,
    log_to_console: bool = True,
    json_format: bool = False
) -> logging.Logger:
    """
    Setup and configure logger with file and console handlers
    
    Args:
        name: Logger name
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Enable file logging
        log_to_console: Enable console logging
        json_format: Use JSON format (useful for production)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level from config or parameter
    level = log_level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    if log_to_file:
        log_dir.mkdir(exist_ok=True)
    
    # Console Handler (for development)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if settings.is_development else logging.INFO)
        
        if json_format:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(ColoredFormatter(
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
        
        logger.addHandler(console_handler)
    
    # File Handler - Rotating by size (for all logs)
    if log_to_file:
        file_handler = RotatingFileHandler(
            filename=log_dir / f"{name}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        
        if json_format or settings.is_production:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(
                "[%(asctime)s] %(levelname)-8s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",  # cspell:ignore levelname
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
        
        logger.addHandler(file_handler)
    
    # Error File Handler - Rotating daily (errors only)
    if log_to_file:
        error_handler = TimedRotatingFileHandler(
            filename=log_dir / f"{name}_errors.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)-8s - %(module)s:%(funcName)s:%(lineno)d\n"
            "Message: %(message)s\n"
            "%(pathname)s\n",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(error_handler)
    
    return logger


# Create default logger instance
logger = setup_logger(
    name="seikatsu",
    log_to_file=True,
    log_to_console=True,
    json_format=settings.is_production
)


# Convenience functions for logging with context
def log_api_request(method: str, path: str, user_id: Optional[int] = None, **kwargs):
    """Log API request with context"""
    extra_data = {
        "method": method,
        "path": path,
        "user_id": user_id,
        **kwargs
    }
    logger.info(f"API Request: {method} {path}", extra={"extra_data": extra_data})


def log_api_response(method: str, path: str, status_code: int, duration_ms: float, **kwargs):
    """Log API response with timing"""
    extra_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        **kwargs
    }
    logger.info(
        f"API Response: {method} {path} - {status_code} ({duration_ms:.2f}ms)",
        extra={"extra_data": extra_data}
    )


def log_database_operation(operation: str, table: str, success: bool, **kwargs):
    """Log database operations"""
    extra_data = {
        "operation": operation,
        "table": table,
        "success": success,
        **kwargs
    }
    level = logging.INFO if success else logging.ERROR
    logger.log(
        level,
        f"DB Operation: {operation} on {table} - {'Success' if success else 'Failed'}",
        extra={"extra_data": extra_data}
    )


def log_exception(exc: Exception, context: str = "", **kwargs):
    """Log exception with context"""
    extra_data = {
        "exception_type": type(exc).__name__,
        "context": context,
        **kwargs
    }
    logger.error(
        f"Exception in {context}: {str(exc)}",
        exc_info=True,
        extra={"extra_data": extra_data}
    )


# Export logger and utility functions
__all__ = [
    "logger",
    "setup_logger",
    "log_api_request",
    "log_api_response",
    "log_database_operation",
    "log_exception",
]