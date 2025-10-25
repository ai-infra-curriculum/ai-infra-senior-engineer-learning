"""Logging utilities for the Kubernetes operator.

TODO for students: Enhance logging with:
- Structured logging (JSON format)
- Log aggregation integration (ELK, Loki)
- Request tracing with correlation IDs
- Log sampling for high-volume events
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    json_format: bool = False,
) -> None:
    """Configure logging for the operator.

    TODO for students: Implement JSON logging format for better parsing

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string
        json_format: Whether to use JSON format
    """
    if format_string is None:
        format_string = (
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        )

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # TODO for students: Add JSON formatter if json_format is True
    # from pythonjsonlogger import jsonlogger
    # if json_format:
    #     handler = logging.StreamHandler(sys.stdout)
    #     formatter = jsonlogger.JsonFormatter()
    #     handler.setFormatter(formatter)
    #     logging.root.handlers = [handler]

    # Reduce noise from kubernetes client
    logging.getLogger("kubernetes").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    TODO for students: Add context injection (namespace, resource name)

    Args:
        name: Logger name (usually __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if level:
        logger.setLevel(getattr(logging, level.upper()))

    return logger


class OperatorLogger:
    """Context-aware logger for operator.

    TODO for students: Implement this class to add contextual information
    to all log messages (namespace, resource name, reconciliation ID)

    Example usage:
        logger = OperatorLogger("controller", namespace="default", name="job-1")
        logger.info("Starting reconciliation")
        # Output: [INFO] [controller] [default/job-1] Starting reconciliation
    """

    def __init__(
        self,
        name: str,
        namespace: Optional[str] = None,
        resource_name: Optional[str] = None,
    ):
        """Initialize operator logger.

        TODO for students: Store context and wrap logger methods
        """
        self.logger = get_logger(name)
        self.namespace = namespace
        self.resource_name = resource_name
        self.context = {}

        if namespace and resource_name:
            self.context["resource"] = f"{namespace}/{resource_name}"

    def _format_message(self, message: str) -> str:
        """Format message with context.

        TODO for students: Add more context fields
        """
        if self.context:
            context_str = " ".join([f"[{k}={v}]" for k, v in self.context.items()])
            return f"{context_str} {message}"
        return message

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self.logger.debug(self._format_message(message), **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self.logger.info(self._format_message(message), **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self.logger.warning(self._format_message(message), **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self.logger.error(self._format_message(message), **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with context."""
        self.logger.exception(self._format_message(message), **kwargs)
