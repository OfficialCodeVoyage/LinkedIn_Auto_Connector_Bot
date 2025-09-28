"""
Custom exceptions for LinkedIn Auto Connector Bot.

This module defines all custom exceptions used throughout the application
for better error handling and debugging.
"""

from typing import Optional, Dict, Any


class LinkedInBotException(Exception):
    """Base exception for all LinkedIn bot exceptions."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize LinkedInBotException.

        Args:
            message: Error message
            details: Optional dictionary with additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        """String representation of the exception."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


# Authentication Exceptions
class AuthenticationException(LinkedInBotException):
    """Base exception for authentication-related errors."""
    pass


class LoginFailedException(AuthenticationException):
    """Exception raised when login fails."""

    def __init__(self, message: str = "Failed to login to LinkedIn", **kwargs):
        super().__init__(message, kwargs)


class SessionExpiredException(AuthenticationException):
    """Exception raised when session has expired."""

    def __init__(self, message: str = "LinkedIn session has expired", **kwargs):
        super().__init__(message, kwargs)


class CaptchaRequiredException(AuthenticationException):
    """Exception raised when CAPTCHA verification is required."""

    def __init__(self, message: str = "CAPTCHA verification required", **kwargs):
        super().__init__(message, kwargs)


class TwoFactorAuthException(AuthenticationException):
    """Exception raised for two-factor authentication issues."""

    def __init__(self, message: str = "Two-factor authentication required", **kwargs):
        super().__init__(message, kwargs)


class SecurityCheckpointException(AuthenticationException):
    """Exception raised when LinkedIn security checkpoint is triggered."""

    def __init__(self, message: str = "LinkedIn security checkpoint detected", **kwargs):
        super().__init__(message, kwargs)


# Rate Limiting Exceptions
class RateLimitException(LinkedInBotException):
    """Base exception for rate limiting errors."""
    pass


class DailyLimitExceededException(RateLimitException):
    """Exception raised when daily connection limit is exceeded."""

    def __init__(self, limit: int, current: int, **kwargs):
        message = f"Daily limit of {limit} connections exceeded (current: {current})"
        super().__init__(message, {'limit': limit, 'current': current, **kwargs})


class WeeklyLimitExceededException(RateLimitException):
    """Exception raised when weekly connection limit is exceeded."""

    def __init__(self, limit: int, current: int, **kwargs):
        message = f"Weekly limit of {limit} connections exceeded (current: {current})"
        super().__init__(message, {'limit': limit, 'current': current, **kwargs})


class RateLimitWarning(RateLimitException):
    """Warning when approaching rate limits."""

    def __init__(self, percentage: float, limit: int, current: int, **kwargs):
        message = f"Approaching rate limit: {percentage:.0f}% of {limit} limit reached ({current} sent)"
        super().__init__(message, {'percentage': percentage, 'limit': limit, 'current': current, **kwargs})


# Connection Exceptions
class ConnectionException(LinkedInBotException):
    """Base exception for connection-related errors."""
    pass


class ProfileNotFoundException(ConnectionException):
    """Exception raised when profile cannot be found."""

    def __init__(self, profile_url: Optional[str] = None, **kwargs):
        message = f"Profile not found: {profile_url}" if profile_url else "Profile not found"
        super().__init__(message, {'profile_url': profile_url, **kwargs})


class ConnectionButtonNotFoundException(ConnectionException):
    """Exception raised when Connect button cannot be found."""

    def __init__(self, message: str = "Connect button not found on profile", **kwargs):
        super().__init__(message, kwargs)


class AlreadyConnectedException(ConnectionException):
    """Exception raised when already connected with profile."""

    def __init__(self, profile: Optional[str] = None, **kwargs):
        message = f"Already connected with {profile}" if profile else "Already connected with this profile"
        super().__init__(message, {'profile': profile, **kwargs})


class ConnectionPendingException(ConnectionException):
    """Exception raised when connection request is already pending."""

    def __init__(self, profile: Optional[str] = None, **kwargs):
        message = f"Connection request pending for {profile}" if profile else "Connection request already pending"
        super().__init__(message, {'profile': profile, **kwargs})


class MessageTooLongException(ConnectionException):
    """Exception raised when connection message exceeds LinkedIn's limit."""

    def __init__(self, length: int, max_length: int = 300, **kwargs):
        message = f"Message too long: {length} characters (max: {max_length})"
        super().__init__(message, {'length': length, 'max_length': max_length, **kwargs})


# Configuration Exceptions
class ConfigurationException(LinkedInBotException):
    """Base exception for configuration errors."""
    pass


class InvalidConfigException(ConfigurationException):
    """Exception raised when configuration is invalid."""

    def __init__(self, field: str, value: Any, reason: str, **kwargs):
        message = f"Invalid configuration for '{field}': {value} - {reason}"
        super().__init__(message, {'field': field, 'value': value, 'reason': reason, **kwargs})


class MissingConfigException(ConfigurationException):
    """Exception raised when required configuration is missing."""

    def __init__(self, field: str, **kwargs):
        message = f"Missing required configuration: {field}"
        super().__init__(message, {'field': field, **kwargs})


class EnvironmentVariableException(ConfigurationException):
    """Exception raised for environment variable issues."""

    def __init__(self, variable: str, **kwargs):
        message = f"Environment variable not set: {variable}"
        super().__init__(message, {'variable': variable, **kwargs})


# Browser/WebDriver Exceptions
class BrowserException(LinkedInBotException):
    """Base exception for browser-related errors."""
    pass


class WebDriverNotFoundException(BrowserException):
    """Exception raised when WebDriver cannot be found."""

    def __init__(self, driver_type: str, **kwargs):
        message = f"WebDriver not found for {driver_type}"
        super().__init__(message, {'driver_type': driver_type, **kwargs})


class BrowserCrashedException(BrowserException):
    """Exception raised when browser has crashed."""

    def __init__(self, message: str = "Browser has crashed or become unresponsive", **kwargs):
        super().__init__(message, kwargs)


class ElementNotFoundException(BrowserException):
    """Exception raised when expected element cannot be found."""

    def __init__(self, element: str, locator: Optional[str] = None, **kwargs):
        message = f"Element not found: {element}"
        if locator:
            message += f" (locator: {locator})"
        super().__init__(message, {'element': element, 'locator': locator, **kwargs})


class ElementNotClickableException(BrowserException):
    """Exception raised when element cannot be clicked."""

    def __init__(self, element: str, **kwargs):
        message = f"Element not clickable: {element}"
        super().__init__(message, {'element': element, **kwargs})


class PageLoadTimeoutException(BrowserException):
    """Exception raised when page fails to load in time."""

    def __init__(self, url: str, timeout: int, **kwargs):
        message = f"Page load timeout for {url} after {timeout} seconds"
        super().__init__(message, {'url': url, 'timeout': timeout, **kwargs})


# Network Exceptions
class NetworkException(LinkedInBotException):
    """Base exception for network-related errors."""
    pass


class ProxyException(NetworkException):
    """Exception raised for proxy-related issues."""

    def __init__(self, proxy: str, reason: str, **kwargs):
        message = f"Proxy error for {proxy}: {reason}"
        super().__init__(message, {'proxy': proxy, 'reason': reason, **kwargs})


class NetworkTimeoutException(NetworkException):
    """Exception raised for network timeout."""

    def __init__(self, operation: str, timeout: int, **kwargs):
        message = f"Network timeout during {operation} after {timeout} seconds"
        super().__init__(message, {'operation': operation, 'timeout': timeout, **kwargs})


# Data Exceptions
class DataException(LinkedInBotException):
    """Base exception for data-related errors."""
    pass


class InvalidDataException(DataException):
    """Exception raised when data is invalid."""

    def __init__(self, data_type: str, reason: str, **kwargs):
        message = f"Invalid {data_type}: {reason}"
        super().__init__(message, {'data_type': data_type, 'reason': reason, **kwargs})


class DataCorruptedException(DataException):
    """Exception raised when data is corrupted."""

    def __init__(self, file_path: str, **kwargs):
        message = f"Data corrupted in file: {file_path}"
        super().__init__(message, {'file_path': file_path, **kwargs})


# Session Exceptions
class SessionException(LinkedInBotException):
    """Base exception for session-related errors."""
    pass


class SessionSaveException(SessionException):
    """Exception raised when session cannot be saved."""

    def __init__(self, username: str, reason: str, **kwargs):
        message = f"Failed to save session for {username}: {reason}"
        super().__init__(message, {'username': username, 'reason': reason, **kwargs})


class SessionLoadException(SessionException):
    """Exception raised when session cannot be loaded."""

    def __init__(self, username: str, reason: str, **kwargs):
        message = f"Failed to load session for {username}: {reason}"
        super().__init__(message, {'username': username, 'reason': reason, **kwargs})


class SessionCorruptedException(SessionException):
    """Exception raised when session data is corrupted."""

    def __init__(self, username: str, **kwargs):
        message = f"Session data corrupted for {username}"
        super().__init__(message, {'username': username, **kwargs})


# Operation Exceptions
class OperationException(LinkedInBotException):
    """Base exception for operation-related errors."""
    pass


class OperationTimeoutException(OperationException):
    """Exception raised when operation times out."""

    def __init__(self, operation: str, timeout: int, **kwargs):
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(message, {'operation': operation, 'timeout': timeout, **kwargs})


class RetryExceededException(OperationException):
    """Exception raised when maximum retries exceeded."""

    def __init__(self, operation: str, max_retries: int, **kwargs):
        message = f"Maximum retries ({max_retries}) exceeded for operation: {operation}"
        super().__init__(message, {'operation': operation, 'max_retries': max_retries, **kwargs})


class OperationCancelledException(OperationException):
    """Exception raised when operation is cancelled."""

    def __init__(self, operation: str, reason: Optional[str] = None, **kwargs):
        message = f"Operation '{operation}' was cancelled"
        if reason:
            message += f": {reason}"
        super().__init__(message, {'operation': operation, 'reason': reason, **kwargs})


# Validation Exceptions
class ValidationException(LinkedInBotException):
    """Base exception for validation errors."""
    pass


class CredentialValidationException(ValidationException):
    """Exception raised when credentials are invalid."""

    def __init__(self, field: str, reason: str, **kwargs):
        message = f"Invalid credential for '{field}': {reason}"
        super().__init__(message, {'field': field, 'reason': reason, **kwargs})


class URLValidationException(ValidationException):
    """Exception raised when URL is invalid."""

    def __init__(self, url: str, reason: str, **kwargs):
        message = f"Invalid URL '{url}': {reason}"
        super().__init__(message, {'url': url, 'reason': reason, **kwargs})


# Helper function to handle exceptions
def handle_exception(exception: Exception, logger=None, reraise: bool = True):
    """
    Helper function to handle exceptions consistently.

    Args:
        exception: The exception to handle
        logger: Optional logger instance
        reraise: Whether to re-raise the exception after handling
    """
    if logger:
        if isinstance(exception, LinkedInBotException):
            logger.error(f"{exception.__class__.__name__}: {exception}")
            if exception.details:
                logger.debug(f"Exception details: {exception.details}")
        else:
            logger.exception(f"Unexpected error: {exception}")

    if reraise:
        raise exception


# Example usage
if __name__ == "__main__":
    # Test custom exceptions
    try:
        raise DailyLimitExceededException(limit=20, current=25)
    except RateLimitException as e:
        print(f"Rate limit error: {e}")
        print(f"Details: {e.details}")

    try:
        raise LoginFailedException(username="test@example.com", error="Invalid password")
    except AuthenticationException as e:
        print(f"\nAuthentication error: {e}")
        print(f"Details: {e.details}")

    try:
        raise MessageTooLongException(length=350, max_length=300)
    except ConnectionException as e:
        print(f"\nConnection error: {e}")
        print(f"Details: {e.details}")