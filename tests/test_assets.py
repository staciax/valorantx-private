import asyncio
import logging

import valorant

client = valorant.Client(locale=valorant.Locale.japanese)

# get basic logging
logging.basicConfig(level=logging.ERROR)


async def main():
    async with client:

        await client.fetch_assets(reload=True)
        # after fetch_assets, you can comment above line and use below line
        # client.reload_assets()
        # if new version available, please use `await client.fetch_assets()` again

        agent = client.get_agent('Killjoy')
        print(repr(agent))

        buddy = client.get_buddy({"ar-AE": "ملحق فرقة العمليات 809"})
        print(repr(buddy))

        bundle = client.get_bundle('Champions 2022')
        print(repr(bundle))

        player_card = client.get_player_card('The Way Forward Card')
        print(repr(player_card))

        player_title = client.get_player_title('Fortune Title')
        print(repr(player_title))

        spray = client.get_spray('60adbf1b-48b7-b4a1-ccee-50b889c34514')
        print(repr(spray))

        mission = client.get_mission('2bbe195c-48ce-ae72-2a0e-8288b8827f1f')
        print(repr(mission))

        content_tier = client.get_content_tier('0cebb8be-46d7-c12a-d306-e9907bfc5a25')
        print(repr(content_tier))

        contract = client.get_contract('7ae5ad85-400b-beba-989d-42924ccf39be')
        print(repr(contract))

        weapon = client.get_weapon('Operator')
        print(repr(weapon))

        for skin in weapon.skins:
            print(repr(skin))
            for chroma in skin.chromas:
                print(repr(chroma))
            for level in skin.levels:
                print(repr(level))

        skin = client.get_skin('Glitchpop Odin')
        print(repr(skin.base_weapon))

        skin_level = client.get_skin_level('Xenohunter Odin Level 2')
        print(repr(skin_level.base_weapon))
        print(repr(skin_level.base_skin))

        skin_chroma = client.get_skin_chroma('Glitchpop Odin')
        print(repr(skin_chroma.base_weapon))
        print(repr(skin_chroma.base_skin))

        all_bundles = client.get_all_bundles()
        print(list(sorted(all_bundles, key=lambda b: b.display_name)))

        ceremony = client.get_ceremony('1e71c55c-476e-24ac-0687-e48b547dbb35')
        print(repr(ceremony))

        competitive_tier = client.get_competitive_tier('564d8e28-c226-3180-6285-e48a390db8b1')
        print(repr(competitive_tier.tiers))
        print(repr(competitive_tier))

        currency = client.get_currency('VP')
        print(repr(currency))

        game_mode = client.get_game_mode('96bd3920-4f36-d026-2b28-c683eb0bcac5')
        print(repr(game_mode))

        game_mode_equippable = client.get_game_mode_equippable('c5de005c-4bdc-26a7-a47d-c295eaaae9d8')
        print(repr(game_mode_equippable))

        gear = client.get_gear('Light')
        print(repr(gear))

        event = client.get_event('024d36a7-46e3-8a29-30c6-09a7fb81bebe')
        print(repr(event))

        level_border = client.get_level_border('ebc736cd-4b6a-137b-e2b0-1486e31312c9')
        print(repr(level_border))

        level_border = client.get_level_border(20)
        print(repr(level_border))

        map_ = client.get_map('ascent')
        print(repr(map_))

        season = client.get_season('0df5adb9-4dcb-6899-1306-3e9860661dd3')
        print(repr(season))

        theme = client.get_theme('fdfe356c-40c4-ac6a-864e-16998fc784ef')
        print(repr(theme))


if __name__ == '__main__':
    asyncio.run(main())
