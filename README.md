# valorantx
An Asynchronous Unofficial Valorant API Wrapper with valorant-api.com API Wrapper for Python

## Installation
<!-- # $ pip install valorantx # not yet -->
```bash
$ pip install -U git+https://github.com/staciax/valorantx.git
```
## Quick Example
```python
import asyncio

import valorantx
from valorantx import Locale

client = valorantx.Client(locale=Locale.japanese)

async def main():
    async with client:
        sf = await client.fetch_store_front()
        for skin in sf.skins_panel_layout.skins:
            print('name: ', skin.display_name)
            print('icon: ', skin.display_icon)
            print('cost: ', skin.cost)

asyncio.run(main())
```
<!-- ## Valorant-API Example
```python
import asyncio

import valorantx.valorant_api as valorant_api
from valorantx import Locale

client = valorant_api.Client(locale=Locale.japanese)

async def main():
    async with client:
        for skin in client.skins:
            print(
                skin.display_name,  # detect client locale
                skin.display_name.korean,  # specific locale korean
            )

asyncio.run(main())

``` -->

<!-- ## Lagality
Riot Games, VALORANT, and any associated logos are trademarks, service marks, and/or registered trademarks of Riot Games, Inc.

This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by Riot Games, Inc or any of its affiliates or subsidiaries.

I, the project owner and creator, am not responsible for any legalities that may arise in the use of this project. Use at your own risk. -->

<!-- ## Thanks -->
<!-- ## Support -->

## License
licensed under the [MIT License](LICENSE).