"""Custom exception classes for the ArenaFlow 2026 application.

This module provides a hierarchy of specific error types to replace generic
exceptions, improving readability, error logging, and debugging.
"""

class ArenaFlowException(Exception):
    """Base exception class for all custom errors in ArenaFlow."""
    pass


class SecurityValidationError(ArenaFlowException):
    """Raised when an input fails security checks, size guards, or rate limits."""
    pass


class DataLoadError(ArenaFlowException):
    """Raised when loading or parsing configuration or grounding data fails."""
    pass


class LLMRequestError(ArenaFlowException):
    """Raised when requests to the Generative AI endpoints fail or time out."""
    pass
