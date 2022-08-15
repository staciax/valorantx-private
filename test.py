import asyncio
import valorant

client = valorant.Client(locale='en-US')

async def main():
    async with client:
        await client.fetch_all_assets()

        agent = client.asset.get_agent('killjoy')
        print("Agent:", agent.name)

        buddy = client.asset.get_buddy('rgx')
        print("Buddy:", buddy.name_localizations.japanese)

        player_card = client.asset.get_player_card('The Way Forward Card')
        print("Player Card:", player_card.name)

        player_title = client.asset.get_player_title('Fortune Title')
        print("Player Title:", player_title.name_localizations.german)

        spray = client.asset.get_spray('20d547a4-4ec8-c9ef-dd9d-1c8b74d0e6f7')
        print("Spray:", spray.icon)

        bundle = client.asset.get_bundle('sentinels')
        print(bundle['displayName']['en-US'])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
