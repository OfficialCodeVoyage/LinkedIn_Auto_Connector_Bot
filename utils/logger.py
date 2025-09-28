"""
Enhanced logging system for LinkedIn Auto Connector Bot.

This module provides comprehensive logging with file rotation, colored console output,
and structured logging for better debugging and monitoring.
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
import traceback


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output.
    """

    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record):
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        # Format the message
        formatted = super().format(record)

        # Reset color at the end
        return formatted


class StructuredFormatter(logging.Formatter):
    """
    Formatter that outputs logs in JSON format for structured logging.
    """

    def format(self, record):
        """Format log record as JSON."""
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_obj[key] = value

        return json.dumps(log_obj)


class BotLogger:
    """
    Main logger class for the LinkedIn bot with enhanced features.
    """

    def __init__(
        self,
        name: str = "LinkedInBot",
        log_dir: str = "logs",
        log_level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
        structured_logs: bool = False
    ):
        """
        Initialize BotLogger.

        Args:
            name: Logger name
            log_dir: Directory for log files
            log_level: Logging level
            console_output: Enable console output
            file_output: Enable file output
            structured_logs: Use JSON structured logging
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        self.console_output = console_output
        self.file_output = file_output
        self.structured_logs = structured_logs

        # Create log directory
        self.log_dir.mkdir(exist_ok=True)

        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        self.logger.handlers = []  # Clear existing handlers

        # Setup handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers."""
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)

            if self.structured_logs:
                console_formatter = StructuredFormatter()
            else:
                console_formatter = ColoredFormatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )

            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # File handlers
        if self.file_output:
            # Main log file with rotation
            main_log_file = self.log_dir / f"{self.name}.log"
            file_handler = RotatingFileHandler(
                main_log_file,
                maxBytes=10485760,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)

            if self.structured_logs:
                file_formatter = StructuredFormatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )

            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            # Error log file
            error_log_file = self.log_dir / f"{self.name}_errors.log"
            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=10485760,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            self.logger.addHandler(error_handler)

            # Daily log file
            daily_log_file = self.log_dir / f"{self.name}_daily.log"
            daily_handler = TimedRotatingFileHandler(
                daily_log_file,
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            daily_handler.setLevel(self.log_level)
            daily_handler.setFormatter(file_formatter)
            self.logger.addHandler(daily_handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

    def log_with_context(self, level: str, message: str, **context):
        """
        Log message with additional context.

        Args:
            level: Log level
            message: Log message
            **context: Additional context as keyword arguments
        """
        extra = {}
        for key, value in context.items():
            extra[key] = value

        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=extra)

    def log_exception(self, message: str, exception: Exception, **context):
        """
        Log exception with full traceback.

        Args:
            message: Log message
            exception: Exception object
            **context: Additional context
        """
        tb = traceback.format_exc()
        self.logger.error(
            f"{message}: {str(exception)}\nTraceback:\n{tb}",
            extra=context
        )

    def log_performance(self, operation: str, duration: float, **metrics):
        """
        Log performance metrics.

        Args:
            operation: Operation name
            duration: Duration in seconds
            **metrics: Additional metrics
        """
        self.logger.info(
            f"Performance: {operation} completed in {duration:.2f}s",
            extra={'operation': operation, 'duration': duration, **metrics}
        )

    def create_child_logger(self, name: str) -> logging.Logger:
        """
        Create a child logger.

        Args:
            name: Child logger name

        Returns:
            Child logger instance
        """
        child_logger = self.logger.getChild(name)
        return child_logger


class LoggerManager:
    """
    Manages multiple loggers for different components.
    """

    _instance = None
    _loggers = {}

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize LoggerManager."""
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.config = {}

    def setup(self, config: Dict[str, Any]):
        """
        Setup logger configuration.

        Args:
            config: Logger configuration dictionary
        """
        self.config = config

        # Create main logger
        main_logger = BotLogger(
            name="LinkedInBot",
            log_dir=config.get('log_dir', 'logs'),
            log_level=config.get('log_level', 'INFO'),
            console_output=config.get('console_output', True),
            file_output=config.get('file_output', True),
            structured_logs=config.get('structured_logs', False)
        )

        self._loggers['main'] = main_logger.get_logger()

    def get_logger(self, name: str = 'main') -> logging.Logger:
        """
        Get logger by name.

        Args:
            name: Logger name

        Returns:
            Logger instance
        """
        if name not in self._loggers:
            # Create new logger as child of main
            if 'main' in self._loggers:
                self._loggers[name] = self._loggers['main'].getChild(name)
            else:
                # Create standalone logger if main doesn't exist
                bot_logger = BotLogger(name=name)
                self._loggers[name] = bot_logger.get_logger()

        return self._loggers[name]


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    console: bool = True,
    file: bool = True,
    structured: bool = False
) -> logging.Logger:
    """
    Quick setup function for logging.

    Args:
        log_level: Logging level
        log_dir: Directory for log files
        console: Enable console output
        file: Enable file output
        structured: Use structured logging

    Returns:
        Configured logger instance
    """
    logger_manager = LoggerManager()
    logger_manager.setup({
        'log_level': log_level,
        'log_dir': log_dir,
        'console_output': console,
        'file_output': file,
        'structured_logs': structured
    })

    return logger_manager.get_logger('main')


def get_logger(name: str) -> logging.Logger:
    """
    Get logger by name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger_manager = LoggerManager()
    return logger_manager.get_logger(name)


# Context manager for timed operations
class TimedOperation:
    """Context manager for timing operations."""

    def __init__(self, logger: logging.Logger, operation: str):
        """
        Initialize TimedOperation.

        Args:
            logger: Logger instance
            operation: Operation name
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        """Start timing."""
        self.start_time = datetime.now()
        self.logger.debug(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log duration."""
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.info(f"Operation '{self.operation}' completed in {duration:.2f}s")
        else:
            self.logger.error(
                f"Operation '{self.operation}' failed after {duration:.2f}s: {exc_val}"
            )

        return False  # Don't suppress exceptions


# Example usage
if __name__ == "__main__":
    # Setup logging
    logger = setup_logging(
        log_level="DEBUG",
        log_dir="logs",
        console=True,
        file=True,
        structured=False
    )

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Test timed operation
    with TimedOperation(logger, "test_operation"):
        import time
        time.sleep(1)
        logger.info("Doing some work...")

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        bot_logger = BotLogger()
        bot_logger.log_exception("An error occurred", e)

    print("\nCheck the 'logs' directory for log files!")