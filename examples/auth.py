import asyncio

import valorantx2
from valorantx2 import Locale, Region

client = valorantx2.Client(region=Region.AP, locale=Locale.thai)


async def main() -> None:
    async with client:  # use async context manager to automatically close the client or await client.init() and await client.close()
        await client.authorize("username", "password")
        # TODO: cookie auth and access token auth

        await client.wait_until_ready()
        print('RIOT ID:', client.me.riot_id)

        # close the client


if __name__ == "__main__":
    asyncio.run(main())
