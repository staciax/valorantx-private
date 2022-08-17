from __future__ import annotations
from typing import Any, Dict, Union, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse

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
        The Discord specific error code for the failure.
    """

    def __init__(self, response: ClientResponse, message: Optional[Union[str, Dict[str, Any]]]):
        self.response: ClientResponse = response
        self.status: int = response.status  # type: ignore # This attribute is filled by the library even if using requests # noqa: E501
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

class RiotServerError(HTTPException):
    """Exception that's raised for when a 500 range status code occurs.
    Subclass of :exc:`HTTPException`.
    """
    pass
