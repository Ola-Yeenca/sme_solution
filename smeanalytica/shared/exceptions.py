"""Custom exceptions for SME Analytica."""

class SMEAnalyticaError(Exception):
    """Base exception for SME Analytica."""
    pass

class ValidationError(SMEAnalyticaError):
    """Raised when input validation fails."""
    pass

class ResourceNotFoundError(SMEAnalyticaError):
    """Raised when a requested resource is not found."""
    pass

class APIError(SMEAnalyticaError):
    """Raised when an external API call fails."""
    pass

class AuthenticationError(SMEAnalyticaError):
    """Raised when authentication fails."""
    pass

class RateLimitError(SMEAnalyticaError):
    """Raised when rate limit is exceeded."""
    pass

class CacheError(SMEAnalyticaError):
    """Raised when cache operations fail."""
    pass

class ConfigurationError(SMEAnalyticaError):
    """Raised when there is a configuration error."""
    pass

class DatabaseError(SMEAnalyticaError):
    """Raised when database operations fail."""
    pass

class ModelError(SMEAnalyticaError):
    """Raised when AI model operations fail."""
    pass

class AnalysisError(SMEAnalyticaError):
    """Raised when business analysis operations fail."""
    pass
