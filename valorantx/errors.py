# Copyright (c) 2023-present STACiA, 2021-present Rapptz
# Licensed under the MIT
# inspired by https://github.com/Rapptz/discord.py/blob/master/discord/errors.py

from __future__ import annotations

from valorantx.valorant_api.errors import (
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
    'AuthRequired',
    'BadRequest',
    'Forbidden',
    'HTTPException',
    'InternalServerError',
    'NotFound',
    'RateLimited',
    'RiotAuthError',
    'RiotAuthenticationError',
    'RiotMultifactorError',
    'RiotRatelimitError',
    'RiotUnknownErrorTypeError',
    'RiotUnknownResponseTypeError',
    'ValorantAPIError',
    'ValorantXException',
)


class AuthRequired(ValorantXException):
    """Exception that's raised when the client is not logged in."""

    pass


class RiotAuthError(HTTPException):
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
