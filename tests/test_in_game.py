import asyncio
import logging

import valorant

# loggin
logging.basicConfig(level=logging.ERROR)

client = valorant.Client(locale=valorant.Locale.thai)


async def main():
    async with client:
        await client.authorize('username', 'password')

        await client.fetch_assets(with_price=True, reload=True)  # 'with_price=True' is requires authorization
        # after `client.fetch_assets`, you can comment above line and use below line
        # `client.reload_assets(with_price=True)` # will reload assets without authorization
        # if new version available, please use `await client.fetch_assets(with_price=True)` again

        sf = await client.fetch_store_front()
        for skin in sf.store:
            print(skin.display_name)
            print(skin.display_icon)
            print(skin.name_localizations.japanese)
            print(skin.price)

        history = await client.fetch_match_history(queue_id=valorant.QueueID.deathmatch)
        print(repr(history))

        sf = await client.fetch_store_front()
        for skin in sf.store:
            print(skin.display_name)
            print(skin.display_icon)
            print(skin.name_localizations)
            print(skin.name_localizations.chinese_simplified)
            print(skin.name_localizations.ko_KR)

        content = await client.fetch_content()
        print(repr(content.seasons))

        wallet = await client.fetch_wallet()
        print(repr(wallet))

        for locale in valorant.Locale:
            patch_note = await client.fetch_patch_notes(locale=locale)
            print(repr(patch_note.latest))

        loadout = await client.fetch_player_loadout()
        print(repr(loadout.skins))
        for skin in loadout.skins:
            print(skin.display_name, skin.display_icon)


if __name__ == '__main__':
    asyncio.run(main())
