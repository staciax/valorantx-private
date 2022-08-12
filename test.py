import asyncio
import valorant

client = valorant.Client(locale='en-US')

async def main():
    async with client:
        # await client.fetch_all_assets()

        agent = client.asset.get_agent('killjoy')
        print(agent['displayName']['en-US'])

        buddy = client.asset.get_buddy('rgx')
        print(buddy['displayName']['en-US'])

        bundle = client.asset.get_bundle('sentinels')
        print(bundle['displayName']['en-US'])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
