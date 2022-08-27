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

import ctypes
import json
import ssl
import sys
import warnings
from base64 import urlsafe_b64decode
from secrets import token_urlsafe
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from urllib.parse import parse_qsl, urlsplit

import aiohttp

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


class RiotAuth:
    RIOT_CLIENT_USER_AGENT = "RiotClient/56.0.0.4578455.4552318 %s (Windows;10;;Professional, x64)"
    CIPHERS13 = ":".join(  # https://docs.python.org/3/library/ssl.html#tls-1-3
        (
            "TLS_CHACHA20_POLY1305_SHA256",
            "TLS_AES_128_GCM_SHA256",
            "TLS_AES_256_GCM_SHA384",
        )
    )
    CIPHERS = ":".join(
        (
            "ECDHE-ECDSA-CHACHA20-POLY1305",
            "ECDHE-RSA-CHACHA20-POLY1305",
            "ECDHE-ECDSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES128-GCM-SHA256",
            "ECDHE-ECDSA-AES256-GCM-SHA384",
            "ECDHE-RSA-AES256-GCM-SHA384",
            "ECDHE-ECDSA-AES128-SHA",
            "ECDHE-RSA-AES128-SHA",
            "ECDHE-ECDSA-AES256-SHA",
            "ECDHE-RSA-AES256-SHA",
            "AES128-GCM-SHA256",
            "AES256-GCM-SHA384",
            "AES128-SHA",
            "AES256-SHA",
            "DES-CBC3-SHA",  # most likely not available
        )
    )
    SIGALGS = ":".join(
        (
            "ecdsa_secp256r1_sha256",
            "rsa_pss_rsae_sha256",
            "rsa_pkcs1_sha256",
            "ecdsa_secp384r1_sha384",
            "rsa_pss_rsae_sha384",
            "rsa_pkcs1_sha384",
            "rsa_pss_rsae_sha512",
            "rsa_pkcs1_sha512",
            "rsa_pkcs1_sha1",  # will get ignored and won't be negotiated
        )
    )

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
        self.puuid: Optional[str] = None
        self.name: Optional[str] = None
        self.tag: Optional[str] = None
        self.region: Optional[str] = None

    @staticmethod
    def create_riot_auth_ssl_ctx() -> ssl.SSLContext:
        ssl_ctx = ssl.create_default_context()

        # https://github.com/python/cpython/issues/88068
        addr = id(ssl_ctx) + sys.getsizeof(object())
        ssl_ctx_addr = ctypes.cast(addr, ctypes.POINTER(ctypes.c_void_p)).contents

        if sys.platform.startswith("win32"):
            libssl = ctypes.CDLL("libssl-1_1.dll")
        elif sys.platform.startswith(("linux", "darwin")):
            libssl = ctypes.CDLL(ssl._ssl.__file__)
        else:
            raise NotImplementedError("Only Windows (win32), Linux (linux) and macOS (darwin) are supported.")

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1  # deprecated since 3.10
        ssl_ctx.set_alpn_protocols(["http/1.1"])
        ssl_ctx.options |= 1 << 19  # SSL_OP_NO_ENCRYPT_THEN_MAC
        libssl.SSL_CTX_set_ciphersuites(ssl_ctx_addr, RiotAuth.CIPHERS13.encode())
        libssl.SSL_CTX_set_cipher_list(ssl_ctx_addr, RiotAuth.CIPHERS.encode())
        # setting SSL_CTRL_SET_SIGALGS_LIST
        libssl.SSL_CTX_ctrl(ssl_ctx_addr, 98, 0, RiotAuth.SIGALGS.encode())

        # print([cipher["name"] for cipher in ssl_ctx.get_ciphers()])
        return ssl_ctx

    def __update(
        self,
        extract_jwt: bool = False,
        key_attr_pairs: Sequence[Tuple[str, str]] = (
            ("sub", "user_id"),
            ("exp", "expires_at"),
        ),
        **kwargs,
    ) -> None:
        # ONLY PREDEFINED PUBLIC KEYS ARE SET, rest is silently ignored!
        predefined_keys = [key for key in self.__dict__.keys() if key[0] != "_"]

        self.__dict__.update((key, val) for key, val in kwargs.items() if key in predefined_keys)

        if extract_jwt:  # extract additional data from access JWT
            additional_data = self.__get_keys_from_access_token(key_attr_pairs)
            self.__dict__.update((key, val) for key, val in additional_data if key in predefined_keys)

    def __get_keys_from_access_token(
        self, key_attr_pairs: Sequence[Tuple[str, str]]
    ) -> List[Tuple[str, Union[str, int, List, Dict, None]]]:  # List[Tuple[str, JSONType]]
        payload = self.access_token.split(".")[1]
        decoded = urlsafe_b64decode(f"{payload}===")
        temp_dict: Dict = json.loads(decoded)
        return [(attr, temp_dict.get(key)) for key, attr in key_attr_pairs]

    def __set_tokens_from_uri(self, data: Dict) -> None:
        mode = data["response"]["mode"]
        uri = data["response"]["parameters"]["uri"]

        result = getattr(urlsplit(uri), mode)
        data = dict(parse_qsl(result))
        self.__update(extract_jwt=True, **data)

    async def authorize(self, username: str, password: str, use_query_response_mode: bool = False) -> None:
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
                    "remember": False,
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
