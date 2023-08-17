# Copyright (c) 2023-present STACiA, 2022 Huba Tuba (floxay)
# Licensed under the MIT
# riot-auth library: https://github.com/floxay/python-riot-auth

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

import aiohttp
import yarl
from riot_auth import RiotAuth as _RiotAuth

from .errors import RiotAuthenticationError

if TYPE_CHECKING:
    from typing_extensions import Self

# fmt: off
__all__ = (
    'RiotAuth',
)
# fmt: on

_RiotAuth.RIOT_CLIENT_USER_AGENT = 'RiotClient/69.0.3.228.1352 %s (Windows;10;;Professional, x64)'  # type: ignore


class RiotAuth(_RiotAuth):
    def __init__(self) -> None:
        super().__init__()
        self.game_name: Optional[str] = None
        self.tag_line: Optional[str] = None
        self.region: Optional[str] = None
        self.multi_factor_email: Optional[str] = None

    @property
    def puuid(self) -> str:
        return self.user_id or ''

    @property
    def riot_id(self) -> str:
        if self.game_name is None or self.tag_line is None:
            return ''
        return f'{self.game_name}#{self.tag_line}'

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
