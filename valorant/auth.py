"""
The MIT License (MIT)

Copyright (c) 2022-present Huba Tuba (floxay)
Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Links to the original source code: https://github.com/floxay/python-riot-auth

"""

from secrets import token_urlsafe
from typing import Any, Dict, Optional

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
__all__ = (
    "RiotAuth",
)
# fmt: on


class _CookieSentinel:
    __slots__ = ()

    def __getattr__(self, attr: str) -> None:
        msg = 'loop attribute cannot be accessed in non-async contexts. '
        raise AttributeError(msg)


_cookie_jar: Any = _CookieSentinel()


class RiotAuth(_RiotAuth):
    def __init__(self) -> None:
        self._auth_ssl_ctx = RiotAuth.create_riot_auth_ssl_ctx()
        self._cookie_jar: aiohttp.CookieJar = _cookie_jar
        self.access_token: Optional[str] = None
        self.scope: Optional[str] = None
        self.id_token: Optional[str] = None
        self.token_type: Optional[str] = None
        self.expires_at: int = 0
        self.user_id: Optional[str] = None
        self.entitlements_token: Optional[str] = None
        self.name: Optional[str] = None
        self.tag: Optional[str] = None
        self.region: Optional[str] = None
        # multi-factor
        self.__waif_for_2fa: bool = False
        self.multi_factor_email: Optional[str] = None

    @property
    def puuid(self) -> Optional[str]:
        return self.user_id

    @puuid.setter
    def puuid(self, value: str) -> None:
        self.user_id = value

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
        if self._cookie_jar is _cookie_jar:
            self._cookie_jar = aiohttp.CookieJar()

        if username and password:
            self._cookie_jar.clear()

        conn = aiohttp.TCPConnector(ssl=self._auth_ssl_ctx)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=True, cookie_jar=self._cookie_jar) as session:
            headers = {
                "Accept-Encoding": "deflate, gzip, zstd",
                "user-agent": RiotAuth.RIOT_CLIENT_USER_AGENT % "rso-auth",
                "Cache-Control": "no-assets",
                "Accept": "application/json",
            }

            # region Begin auth/Reauth
            body = {
                "acr_values": "",
                "claims": "",
                "client_id": "riot-client",
                "code_challenge": "",
                "code_challenge_method": "",
                "nonce": token_urlsafe(16),
                "redirect_uri": "http://localhost/redirect",
                "response_type": "token id_token",
                "scope": "openid link ban lol_region account",
            }
            if use_query_response_mode:
                body["response_mode"] = "query"
            async with session.post(
                "https://auth.riotgames.com/api/v1/authorization",
                json=body,
                headers=headers,
            ) as r:
                data: Dict = await r.json()
                resp_type = data["type"]
            # endregion

            if resp_type != "response":  # not reauth
                # region Authenticate
                body = {
                    "language": "en_US",
                    "password": password,
                    "region": None,
                    "remember": remember,
                    "type": "auth",
                    "username": username,
                }
                async with session.put(
                    "https://auth.riotgames.com/api/v1/authorization",
                    json=body,
                    headers=headers,
                ) as r:
                    data: Dict = await r.json()
                    resp_type = data["type"]
                    if resp_type == "response":
                        ...
                    elif resp_type == "auth":
                        err = data.get("error")
                        if err == "auth_failure":
                            raise RiotAuthenticationError(
                                f"Failed to authenticate. Make sure username and password are correct. `{err}`."
                            )
                        elif err == "rate_limited":
                            raise RiotRatelimitError()
                        else:
                            raise RiotUnknownErrorTypeError(f"Got unknown error `{err}` during authentication.")
                    elif resp_type == "multifactor":
                        if self.__waif_for_2fa:
                            if 'method' in data['multifactor']:
                                if data['multifactor']['method'] == 'email':
                                    self.multi_factor_email = data['multifactor']['email']
                        raise RiotMultifactorError("Multi-factor authentication is not currently supported.")
                    else:
                        raise RiotUnknownResponseTypeError(f"Got unknown response type `{resp_type}` during authentication.")
                # endregion

            self._cookie_jar = session.cookie_jar
            self.__set_tokens_from_uri(data)

            # region Get new entitlements token
            headers["Authorization"] = f"{self.token_type} {self.access_token}"
            async with session.post(
                "https://entitlements.auth.riotgames.com/api/token/v1",
                headers=headers,
                json={},
                # json={"urn": "urn:entitlement:%"},
            ) as r:
                self.entitlements_token = (await r.json())["entitlements_token"]

            # Get user info

            async with session.post('https://auth.riotgames.com/userinfo', headers=headers) as r:
                data = await r.json()
                self.puuid = data['sub']
                self.name = data['acct']['game_name']
                self.tag = data['acct']['tag_line']

            # Get regions

            body = {"id_token": self.id_token}
            async with session.put(
                'https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body
            ) as r:
                data = await r.json()
                self.region = data['affinities']['live']

            # endregion

    async def reauthorize(self) -> bool:
        """
        Reauthenticate using cookies.

        Returns a ``bool`` indicating success or failure.
        """
        try:
            await self.authorize("", "")
            return True
        except RiotAuthenticationError:  # because credentials are empty
            return False
