# Copyright (c) 2023-present STACiA, 2021-present Rapptz
# Licensed under the MIT
# inspired by https://github.com/Rapptz/discord.py/blob/master/discord/errors.py

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse

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
    'ValorantXError',
)


def _flatten_error_dict(d: Dict[str, Any], key: str = '') -> Dict[str, str]:
    items: List[Tuple[str, str]] = []
    for k, v in d.items():
        new_key = key + '.' + k if key else k

        if isinstance(v, dict):
            try:
                _errors: List[Dict[str, Any]] = v['_errors']
            except KeyError:
                items.extend(_flatten_error_dict(v, new_key).items())
            else:
                items.append((new_key, ' '.join(x.get('message', '') for x in _errors)))
        else:
            items.append((new_key, v))

    return dict(items)


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
        self.status: int = response.status  # This attribute is filled by the library even if using requests # noqa: E501
        self.code: int
        self.text: str
        if isinstance(message, dict):
            self.code = message.get('code', 0)
            base = message.get('message', '')
            errors = message.get('errors')
            if errors:
                errors = _flatten_error_dict(errors)
                helpful = '\n'.join('In %s: %s' % t for t in errors.items())
                self.text = base + '\n' + helpful
            else:
                self.text = base
        else:
            self.text = message or ''
            self.code = 0

        fmt = '{0.status} {0.reason} (error code: {1})'
        if len(self.text):
            fmt += ': {2}'

        super().__init__(fmt.format(self.response, self.code, self.text))


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


class AuthRequired(ValorantXError):
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
