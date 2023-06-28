"""
Exception handler functions: https://github.com/Rapptz/discord.py/blob/master/discord/errors.py
"""

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
    'ValorantAPIError',
)


class ValorantAPIError(Exception):
    """Exception that's raised when a Valorant API request operation fails."""

    pass


class HTTPException(ValorantAPIError):
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
        self.status: int = response.status  # This attribute is filled by the library even if using requests # noqa: E501
        self.text: str
        if isinstance(message, dict):
            self.text = message.get('message') or message.get('error', '')
        else:
            self.text = message or ''

        fmt = '{0.status} {0.reason}'
        if len(self.text):
            fmt += ': {2}'

        super().__init__(fmt.format(self.response, self.text))


class BadRequest(HTTPException):
    """Exception that's raised for when status code 400 occurs.
    Subclass of :exc:`HTTPException`
    """

    pass


class Forbidden(HTTPException):
    """Exception that's raised for when status code 403 occurs.
    Subclass of :exc:`HTTPException`
    """

    pass


class NotFound(HTTPException):
    """Exception that's raised for when status code 404 occurs.
    Subclass of :exc:`HTTPException`
    """

    pass


class InternalServerError(HTTPException):
    """Exception that's raised for when status code 500 occurs.
    Subclass of :exc:`HTTPException`
    """

    pass


class RateLimited(HTTPException):
    """Exception that's raised for when a 429 status code occurs.
    Subclass of :exc:`HTTPException`.
    """

    pass
