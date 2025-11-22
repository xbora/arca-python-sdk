"""
Custom exceptions for the Arca SDK
"""

from typing import Optional


class ArcaError(Exception):
    """Base exception for all Arca SDK errors"""
    pass


class ArcaAPIError(ArcaError):
    """Raised when the API returns an error response"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(f"API Error (status {status_code}): {message}" if status_code else message)


class ArcaAuthError(ArcaError):
    """Raised when authentication fails"""
    pass


class ArcaValidationError(ArcaError):
    """Raised when request validation fails"""
    pass
