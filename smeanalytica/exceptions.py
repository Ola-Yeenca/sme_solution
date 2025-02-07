"""Custom exceptions for SME Analytica."""

class AnalysisError(Exception):
    """Base exception for analysis errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}

class BusinessAnalysisError(AnalysisError):
    """Exception for business analysis specific errors."""
    pass

class ValidationError(AnalysisError):
    """Exception for validation errors."""
    pass

class ResourceNotFoundError(AnalysisError):
    """Exception for resource not found errors."""
    pass

class AuthenticationError(AnalysisError):
    """Exception for authentication errors."""
    pass

class APIError(AnalysisError):
    """Exception for API errors."""
    pass
