"""
Exception handler functions: https://github.com/Rapptz/discord.py/blob/master/discord/errors.py
"""

from __future__ import annotations

from .valorant_api.errors import (
    BadRequest as BadRequest,
    Forbidden as Forbidden,
    HTTPException as HTTPException,
    InternalServerError as InternalServerError,
    NotFound as NotFound,
    RateLimited as RateLimited,
    ValorantAPIError as ValorantAPIError,
    ValorantXException as ValorantXException,
)

__all__ = (
    'ValorantXException',
    'ValorantAPIError',
    'HTTPException',
    'BadRequest',
    'NotFound',
    'InternalServerError',
    'Forbidden',
    'RateLimited',
    'AuthRequired',
    'RiotAuthError',
    'RiotAuthenticationError',
    'RiotRatelimitError',
    'RiotMultifactorError',
    'RiotUnknownResponseTypeError',
    'RiotUnknownErrorTypeError',
)


class AuthRequired(ValorantXException):
    """Exception that's raised when the client is not logged in."""

    pass


class RiotAuthError(ValorantXException):
    """Base class for RiotAuth errors."""

    pass


class RiotAuthenticationError(RiotAuthError):
    """Failed to authenticate."""

    pass


class RiotRatelimitError(RiotAuthError):
    """Ratelimit error."""

    pass


class RiotMultifactorError(RiotAuthError):
    """Error related to multifactor authentication."""

    pass


class RiotUnknownResponseTypeError(RiotAuthError):
    """Unknown response type."""

    pass


class RiotUnknownErrorTypeError(RiotAuthError):
    """Unknown response error type."""

    pass
