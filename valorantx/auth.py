# Copyright (c) 2023-present STACiA, 2022 Huba Tuba (floxay)
# Licensed under the MIT
# riot-auth library: https://github.com/floxay/python-riot-auth

from __future__ import annotations

from secrets import token_urlsafe
from typing import TYPE_CHECKING, Any, Dict, Optional

import aiohttp
import yarl
from riot_auth import RiotAuth as _RiotAuth

from .errors import (
    RiotAuthenticationError,
    RiotMultifactorError,
    RiotRatelimitError,
    RiotUnknownErrorTypeError,
    RiotUnknownResponseTypeError,
)

if TYPE_CHECKING:
    from typing_extensions import Self

# fmt: off
__all__ = (
    'RiotAuth',
)
# fmt: on


class RiotAuth(_RiotAuth):
    def __init__(self) -> None:
        super().__init__()
        self.game_name: Optional[str] = None
        self.tag_line: Optional[str] = None
        self.region: Optional[str] = None
        # multi-factor
        # self.__waif_for_2fa: bool = False
        self.multi_factor_email: Optional[str] = None

    @property
    def puuid(self) -> str:
        return self.user_id or ''

    @property
    def riot_id(self) -> str:
        if self.game_name is None or self.tag_line is None:
            return ''
        return f'{self.game_name}#{self.tag_line}'

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
                                r, f'Failed to authenticate. Make sure username and password are correct. `{err}`.'
                            )
                        elif err == 'rate_limited':
                            raise RiotRatelimitError(r, f'Rate limited. Try again later. `{err}`.')
                        else:
                            raise RiotUnknownErrorTypeError(r, f'Got unknown error `{err}` during authentication.')
                    elif resp_type == 'multifactor':
                        # pre for multi-factor authentication
                        if 'method' in data['multifactor']:
                            if data['multifactor']['method'] == 'email':
                                self.multi_factor_email = data['multifactor']['email']
                        # -
                        raise RiotMultifactorError(r, 'Multi-factor authentication is not currently supported.')
                    else:
                        raise RiotUnknownResponseTypeError(
                            r, f'Got unknown response type `{resp_type}` during authentication.'
                        )
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
                self.game_name = data['acct']['game_name']
                self.tag_line = data['acct']['tag_line']

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

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> Self:
        """
        Set the token data from a dictionary.
        """
        self = cls()
        self.access_token = data['access_token']
        self.id_token = data['id_token']
        self.entitlements_token = data['entitlements_token']
        self.token_type = data['token_type']
        self.expires_at = int(data['expires_at'])
        self.user_id = data['user_id']
        self.game_name = data['game_name']
        self.tag_line = data['tag_line']
        self.region = data['region']
        if 'ssid' in data:
            self._cookie_jar.update_cookies({'ssid': data['ssid']}, yarl.URL('https://auth.riotgames.com'))
        return self

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
            'game_name': self.game_name,
            'tag_line': self.tag_line,
            'region': self.region,
        }
        riotgames_cookies = self._cookie_jar.filter_cookies(yarl.URL('https://auth.riotgames.com'))
        ssid = riotgames_cookies.get('ssid')
        if ssid:
            payload['ssid'] = ssid.value
        return payload
