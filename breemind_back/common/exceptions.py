class ApplicationError(Exception):
    """Base application error."""

    def __init__(self, message: str, extra: dict | None = None):
        self.message = message
        self.extra = extra or {}
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """Validation error."""


class AuthenticationError(ApplicationError):
    """Authentication error."""


class NotFoundError(ApplicationError):
    """Not found error."""
