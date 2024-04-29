# Copyright (c) 2023-present STACiA, 2021-present Rapptz
# Licensed under the MIT
# inspired by https://github.com/Rapptz/discord.py/blob/master/discord/errors.py

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse

__all__ = (
    'BadRequest',
    'Forbidden',
    'HTTPException',
    'InternalServerError',
    'NotFound',
    'RateLimited',
    'RiotAuthRequired',
    'RiotAuthError',
    'RiotAuthenticationError',
    'RiotMultifactorError',
    'RiotRatelimitError',
    'RiotUnknownErrorTypeError',
    'RiotUnknownResponseTypeError',
    'ValorantXError',
)


class ValorantXError(Exception):
    """Base class for all exceptions in this module."""

    pass


class HTTPException(ValorantXError):
    """Exception that's raised when an HTTP request operation fails.
    Attributes
    ------------
    response: :class:`aiohttp.ClientResponse`
        The response of the failed HTTP request. This is an
        instance of :class:`aiohttp.ClientResponse`. In some cases
        this could also be a :class:`requests.Response`.
    text: :class:`str`
        The text of the error. Could be an empty string.
    status: :class:`int`
        The status code of the HTTP request.
    code: :class:`int`
        The Valorantx specific error code for the failure.
    """

    def __init__(self, response: ClientResponse, message: Optional[Union[str, Dict[str, Any]]]):
        self.response: ClientResponse = response
        self.status: int = (
            response.status
        )  # This attribute is filled by the library even if using requests # noqa: E501
        self.text: str
        self.code: str
        if isinstance(message, dict):
            self.text = message.get('message', '')
            self.code = message.get('errorCode', '')
        else:
            self.text = message or ''
            self.code = ''

        fmt = '{0.status} {0.reason} (error code: {1})'
        if len(self.text):
            fmt += ': {2}'

        super().__init__(fmt.format(self.response, self.code, self.text))


class InGameAPIError(HTTPException):
    """Exception that's raised when an in-game error occurs."""

    pass


class BadRequest(InGameAPIError):
    """Exception that's raised for when status code 400 occurs."""

    pass


class Forbidden(InGameAPIError):
    """Exception that's raised for when status code 403 occurs."""

    pass


class NotFound(InGameAPIError):
    """Exception that's raised for when status code 404 occurs."""

    pass


class InternalServerError(InGameAPIError):
    """Exception that's raised for when status code 500 occurs."""

    pass


class RiotScheduledDowntime(InGameAPIError):
    """Exception that's raised for when status code 503 occurs."""

    pass


class RateLimited(InGameAPIError):
    """Exception that's raised for when a 429 status code occurs.
    .
    """

    pass


class RiotAuthRequired(ValorantXError):
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
