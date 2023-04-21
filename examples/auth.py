import asyncio

import valorantx2
from valorantx2 import Region

client = valorantx2.Client(locale=valorantx2.Locale.thai)


async def main() -> None:
    async with client:  # use async context manager to automatically close the client or await client.init() and await client.close()
        await client.authorize("username", "password", region=Region.AP)

        await client.wait_until_ready()
        print('RIOT ID:', client.me.riot_id)
        print('REGION:', client.me.region)

        # close the client


if __name__ == "__main__":
    asyncio.run(main())
