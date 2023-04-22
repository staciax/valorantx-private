"""
Links to the original source code: https://github.com/floxay/python-riot-auth
"""
from secrets import token_urlsafe
from typing import Any, Dict, Optional, Tuple

import aiohttp
from riot_auth import RiotAuth as _RiotAuth

from .errors import (
    RiotAuthenticationError,
    RiotMultifactorError,
    RiotRatelimitError,
    RiotUnknownErrorTypeError,
    RiotUnknownResponseTypeError,
)

# fmt: off
__all__: Tuple[str, ...] = (
    'RiotAuth',
)
# fmt: on


class RiotAuth(_RiotAuth):
    def __init__(self) -> None:
        super().__init__()
        self.name: Optional[str] = None
        self.tag: Optional[str] = None
        self.region: Optional[str] = None

    @property
    def puuid(self) -> str:
        return self.user_id or ''

    @property
    def display_name(self) -> str:
        if self.name is None or self.tag is None:
            return ''
        return f'{self.name}#{self.tag}'

    async def authorize(
        self, username: str, password: str, use_query_response_mode: bool = False, remember: bool = False
    ) -> None:
        """
        Authenticate using username and password.
        """
        if username and password:
            self._cookie_jar.clear()

        conn = aiohttp.TCPConnector(ssl=self._auth_ssl_ctx)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=True, cookie_jar=self._cookie_jar) as session:
            headers = {
                'Accept-Encoding': 'deflate, gzip, zstd',
                'user-agent': RiotAuth.RIOT_CLIENT_USER_AGENT % 'rso-auth',
                'Cache-Control': 'no-assets',
                'Accept': 'application/json',
            }

            # region Begin auth/Reauth
            body = {
                'acr_values': '',
                'claims': '',
                'client_id': 'riot-client',
                'code_challenge': '',
                'code_challenge_method': '',
                'nonce': token_urlsafe(16),
                'redirect_uri': 'http://localhost/redirect',
                'response_type': 'token id_token',
                'scope': 'openid link ban lol_region account',
            }
            if use_query_response_mode:
                body['response_mode'] = 'query'
            async with session.post(
                'https://auth.riotgames.com/api/v1/authorization',
                json=body,
                headers=headers,
            ) as r:
                data: Dict = await r.json()
                resp_type = data['type']
            # endregion

            if resp_type != 'response':  # not reauth
                # region Authenticate
                body = {
                    'language': 'en_US',
                    'password': password,
                    'region': None,
                    'remember': remember,
                    'type': 'auth',
                    'username': username,
                }
                async with session.put(
                    'https://auth.riotgames.com/api/v1/authorization',
                    json=body,
                    headers=headers,
                ) as r:
                    data: Dict = await r.json()
                    resp_type = data['type']
                    if resp_type == 'response':
                        ...
                    elif resp_type == 'auth':
                        err = data.get('error')
                        if err == 'auth_failure':
                            raise RiotAuthenticationError(
                                f'Failed to authenticate. Make sure username and password are correct. `{err}`.'
                            )
                        elif err == 'rate_limited':
                            raise RiotRatelimitError()
                        else:
                            raise RiotUnknownErrorTypeError(f'Got unknown error `{err}` during authentication.')
                    elif resp_type == 'multifactor':
                        raise RiotMultifactorError('Multi-factor authentication is not currently supported.')
                    else:
                        raise RiotUnknownResponseTypeError(f'Got unknown response type `{resp_type}` during authentication.')
                # endregion

            self._cookie_jar = session.cookie_jar
            self.__set_tokens_from_uri(data)

            # Get new entitlements token
            headers['Authorization'] = f'{self.token_type} {self.access_token}'
            async with session.post(
                'https://entitlements.auth.riotgames.com/api/token/v1',
                headers=headers,
                json={},
                # json={'urn': 'urn:entitlement:%'},
            ) as r:
                self.entitlements_token = (await r.json())['entitlements_token']

    async def fetch_region(self) -> Optional[str]:
        # Get regions
        body = {'id_token': self.id_token}
        headers = {'Authorization': f'{self.token_type} {self.access_token}'}
        async with aiohttp.ClientSession(cookie_jar=self._cookie_jar) as session:
            async with session.put(
                'https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body
            ) as r:
                data = await r.json()
                self.region = data['affinities']['live']
        return self.region

    async def fetch_userinfo(self) -> None:
        # Get user info
        headers = {'Authorization': f'{self.token_type} {self.access_token}'}
        async with aiohttp.ClientSession(cookie_jar=self._cookie_jar) as session:
            async with session.post('https://auth.riotgames.com/userinfo', headers=headers) as r:
                data = await r.json()
                # self.user_id = data['sub'] # puuid
                self.name = data['acct']['game_name']
                self.tag = data['acct']['tag_line']

    async def reauthorize(self) -> bool:
        """
        Reauthenticate using cookies.

        Returns a ``bool`` indicating success or failure.
        """
        try:
            await self.authorize('', '')
            return True
        except RiotAuthenticationError:  # because credentials are empty
            return False

    def from_data(self, data: Dict[str, Any]) -> None:
        """
        Set the token data from a dictionary.
        """
        self.access_token = data['access_token']
        self.id_token = data['id_token']
        self.entitlements_token = data['entitlements_token']
        self.token_type = data['token_type']
        self.expires_at = int(data['expires_at'])
        self.user_id = data['user_id']
        self.name = data['name']
        self.tag = data['tag']
        self.region = data['region']

    def to_dict(self) -> Dict[str, Any]:
        """
        Return the token data as a dictionary.
        """
        payload = {
            'access_token': self.access_token,
            'id_token': self.id_token,
            'entitlements_token': self.entitlements_token,
            'token_type': self.token_type,
            'expires_at': self.expires_at,
            'user_id': self.user_id,
            'name': self.name,
            'tag': self.tag,
            'region': self.region,
        }
        return payload
