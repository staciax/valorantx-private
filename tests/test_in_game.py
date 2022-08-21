import asyncio
import valorant

client = valorant.Client(locale='en-US')

async def main():
    async with client:
        await client.fetch_all_assets()

        await client.http.static_login('username', 'password')

        store = await client.fetch_store_front()
        print(store)

        wallet = await client.fetch_wallet()
        print(wallet)

        patch_note = await client.fetch_patch_notes(locale=valorant.Locale.thai)
        print(patch_note)

if __name__ == '__main__':
    asyncio.run(main())
