import asyncio
import logging
import valorant

client = valorant.Client(locale='en-US')

# for uuid in client.assets.ASSET_CACHE['bundles'].keys():
#     content_tier = client.assets.get_bundle(uuid)
#     print(content_tier)

# get basic logging
logging.basicConfig(level=logging.INFO)

async def main():
    async with client:
        await client.fetch_all_assets()

        agent = client.assets.get_agent('killjoy')
        print(agent)

        buddy = client.assets.get_buddy('rgx')
        print(buddy)

        player_card = client.assets.get_player_card('The Way Forward Card')
        print(player_card)

        player_title = client.assets.get_player_title('Fortune Title')
        print(player_title)

        spray = client.assets.get_spray('20d547a4-4ec8-c9ef-dd9d-1c8b74d0e6f7')
        print(spray)

        bundle = client.assets.get_bundle('sentinels')
        print(bundle)

        mission = client.assets.get_mission('2bbe195c-48ce-ae72-2a0e-8288b8827f1f')
        print(mission)

        content_tier = client.assets.get_content_tier('0cebb8be-46d7-c12a-d306-e9907bfc5a25')
        print(content_tier)

        contract = client.assets.get_contract('7ae5ad85-400b-beba-989d-42924ccf39be')
        print(contract)

        weapon = client.assets.get_weapon('63e6c2b6-4a8e-869c-3d4c-e38355226584')
        skins = weapon.skins
        for skin in skins:
            for chroma in skin.chromas:
                print(repr(chroma))
            for level in skin.levels:
                print(repr(level))

        all_bundles = client.assets.get_all_bundles()
        print(list(sorted(all_bundles, key=lambda b: b.name)))

if __name__ == '__main__':
    asyncio.run(main())
