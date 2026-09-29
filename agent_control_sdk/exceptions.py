"""
Custom exceptions for the Agent Control SDK.
"""

class AgentControlError(Exception):
    """Base exception for all agent_control_sdk errors."""
    pass

class ConnectionError(AgentControlError):
    """Raised when connection to the Agent Control server fails."""
    pass

class APIError(AgentControlError):
    """Raised when the Agent Control API returns an error response."""
    def __init__(self, message: str, status_code: int = 500, response_data: dict = None):
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.response_data = response_data or {}

class NotFoundError(APIError):
    """Raised when a requested resource is not found (404)."""
    pass

class ValidationError(APIError):
    """Raised when client inputs fail validation (422)."""
    pass

class AuthenticationError(APIError):
    """Raised on authentication/permission failure (401/403)."""
    pass
