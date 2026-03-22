class LLMRetryableError(Exception):
    """Raised by backends for transient errors that should be retried."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class LLMFatalError(Exception):
    """Raised by backends for non-retryable errors."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
