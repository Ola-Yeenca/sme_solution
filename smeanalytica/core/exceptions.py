"""Custom exceptions for the SME Analytica application."""

class BusinessAnalysisError(Exception):
    """Base exception for business analysis errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details

class ValidationError(BusinessAnalysisError):
    """Raised when input validation fails."""
    pass

class AnalysisError(BusinessAnalysisError):
    """Raised when business analysis fails."""
    pass

class DataFetchError(BusinessAnalysisError):
    """Raised when fetching required data fails."""
    pass

class ModelError(BusinessAnalysisError):
    """Raised when AI model operations fail."""
    pass

class ConfigurationError(BusinessAnalysisError):
    """Raised when there are configuration issues."""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

class AuthorizationError(Exception):
    """Raised when authorization fails."""
    pass

class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass

class APIError(Exception):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
