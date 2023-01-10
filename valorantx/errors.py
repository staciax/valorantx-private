"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz
Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

Exception handler functions: https://github.com/Rapptz/discord.py/blob/master/discord/errors.py
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse

__all__: Tuple[str, ...] = (
    'ValorantException',
    'HandshakeError',
    'ResponseError',
    'PhaseError',
    'HTTPException',
    'AuthFailure',
    'Forbidden',
    'NotFound',
    'InternalServerError',
    'RateLimited',
    'RiotAuthError',
    'RiotAuthenticationError',
    'RiotRatelimitError',
    'RiotMultifactorError',
    'RiotUnknownResponseTypeError',
    'RiotUnknownErrorTypeError',
    'AuthRequired',
    'InvalidContractType',
    'InvalidRelationType',
    'PartyNotOwner',
    'NotInPreGame',
    'NotInCoreGame',
    'InvalidPuuid',
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


class ValorantException(Exception):
    """Base class for all exceptions in this module."""

    pass


class HandshakeError(Exception):
    """
    Raised whenever there's a problem while attempting to communicate with the local Riot server.
    """

    pass


class ResponseError(Exception):
    """
    Raised whenever an empty response is given by the Riot server.
    """

    pass


class PhaseError(Exception):
    """
    Raised whenever there's a problem while attempting to fetch phase data.
    This typically occurs when the phase is null (i.e. player is not in the agent select phase.)
    """


class HTTPException(ValorantException):
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


class AuthFailure(ResponseError):
    """Exception that's raised when the :meth:`Client.login` function
    fails to log you in from improper credentials or some other misc.
    failure.
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


class RiotAuthError(Exception):
    """Base class for RiotAuth errors."""


class RiotAuthenticationError(RiotAuthError):
    """Failed to authenticate."""


class RiotRatelimitError(RiotAuthError):
    """Ratelimit error."""


class RiotMultifactorError(RiotAuthError):
    """Error related to multifactor authentication."""


class RiotUnknownResponseTypeError(RiotAuthError):
    """Unknown response type."""


class RiotUnknownErrorTypeError(RiotAuthError):
    """Unknown response error type."""


class AuthRequired(ValorantException):
    """Exception that's raised when the client is not logged in."""

    pass


# model exceptions


class InvalidContractType(ValueError):
    """Exception that's raised when the contract type is invalid."""

    pass


class InvalidRelationType(ValueError):
    """Exception that's raised when the relation type is invalid."""

    pass


class PartyNotOwner(ValorantException):
    """Exception that's raised when the user is not the owner of the party."""

    pass


class NotInPreGame(ValorantException):
    """Exception that's raised when the user is not in a pre-game."""

    pass


class NotInCoreGame(ValorantException):
    """Exception that's raised when the user is not in a core-game."""

    pass


class InvalidPuuid(ValorantException):
    """Exception that's raised when the puuid is invalid."""

    pass
