import asyncio
import valorant

client = valorant.Client(locale='en-US')

async def main():
    async with client:
        await client.fetch_all_assets()

        agent = client.assets.get_agent('killjoy')
        print("Agent:", agent.name)

        buddy = client.assets.get_buddy('rgx')
        print("Buddy:", buddy.name_localizations.japanese)

        player_card = client.assets.get_player_card('The Way Forward Card')
        print("Player Card:", player_card.name)

        player_title = client.assets.get_player_title('Fortune Title')
        print("Player Title:", player_title.name_localizations.german)

        spray = client.assets.get_spray('20d547a4-4ec8-c9ef-dd9d-1c8b74d0e6f7')
        print("Spray:", spray.display_icon)

        bundle = client.assets.get_bundle('sentinels')
        print("Bundle:", bundle.name_localizations.english)

if __name__ == '__main__':
    asyncio.run(main())
