import asyncio
import valorant

client = valorant.Client(locale='en-US')

async def main():
    async with client:
        await client.fetch_all_assets()

        # asset = client.asset.get_agent('yoru')
        # print(asset)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
