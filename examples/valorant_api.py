import asyncio

from valorantx2.valorant_api import Client, Locale


async def main() -> None:
    async with Client(locale=Locale.japanese) as client:
        for agent in client.agents:
            print(
                agent.display_name,  # detect client locale
                agent.display_name.arabic,  # specific locale arabic
                agent.display_name.korean,  # specific locale korean
            )


if __name__ == '__main__':
    asyncio.run(main())
