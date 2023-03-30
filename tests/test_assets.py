import pytest

import valorantx


@pytest.mark.asyncio
async def test_assets(client: valorantx.Client):
    await client.fetch_assets(reload=True)
    # after fetch_assets, you can comment above line and use below line
    # client.reload_assets()
    # if new version available, please use `await client.fetch_assets()` again

    agent = client.get_agent('Killjoy')
    assert agent is not None
    assert agent.display_name.default == 'Killjoy'

    buddy = client.get_buddy({"ar-AE": "ملحق فرقة العمليات 809"})
    assert buddy is not None
    assert buddy.display_name.ar_AE == 'ملحق فرقة العمليات 809'

    bundle = client.get_bundle('Champions 2022')
    assert bundle is not None
    assert bundle.display_name.default == 'Champions 2022'

    player_card = client.get_player_card('The Way Forward Card')
    assert player_card is not None
    assert player_card.display_name.default == 'The Way Forward Card'

    player_title = client.get_player_title('Fortune Title')
    assert player_title is not None
    assert player_title.display_name.default == 'Fortune Title'

    spray = client.get_spray('3d2bcfc5-442b-812e-3c08-9180d6b36077')
    assert spray is not None
    assert spray.uuid == '3d2bcfc5-442b-812e-3c08-9180d6b36077'

    spray_level = client.get_spray_level('60adbf1b-48b7-b4a1-ccee-50b889c34514')
    assert spray_level is not None
    assert spray_level.uuid == '60adbf1b-48b7-b4a1-ccee-50b889c34514'

    mission = client.get_mission('2bbe195c-48ce-ae72-2a0e-8288b8827f1f')
    assert mission is not None
    assert mission.uuid == '2bbe195c-48ce-ae72-2a0e-8288b8827f1f'

    content_tier = client.get_content_tier('0cebb8be-46d7-c12a-d306-e9907bfc5a25')
    assert content_tier is not None
    assert content_tier.uuid == '0cebb8be-46d7-c12a-d306-e9907bfc5a25'

    contract = client.get_contract('7ae5ad85-400b-beba-989d-42924ccf39be')
    assert contract is not None
    assert contract.uuid == '7ae5ad85-400b-beba-989d-42924ccf39be'

    weapon = client.get_weapon('Operator')
    assert weapon is not None
    assert weapon.display_name.default == 'Operator'

    if weapon is not None:
        for skin in weapon.get_skins():
            assert skin is not None
            for chroma in skin.chromas:
                assert chroma is not None
            for level in skin.levels:
                assert level is not None

    skin = client.get_skin('Glitchpop Odin')
    assert skin is not None
    assert skin.display_name.default == 'Glitchpop Odin'
    assert skin.get_weapon() is not None

    skin_level = client.get_skin_level('Xenohunter Odin Level 2')
    assert skin_level is not None
    assert skin_level.display_name.default == 'Xenohunter Odin Level 2'
    assert skin_level.get_weapon() is not None
    assert skin_level.get_skin() is not None

    skin_chroma = client.get_skin_chroma('Glitchpop Odin')
    assert skin_chroma is not None
    assert skin_chroma.display_name.default == 'Glitchpop Odin'
    assert skin_chroma.get_weapon() is not None
    assert skin_chroma.get_skin() is not None

    all_bundles = client.get_all_bundles()
    for bundle in sorted(all_bundles, key=lambda b: b.display_name):
        assert bundle is not None

    ceremony = client.get_ceremony('1e71c55c-476e-24ac-0687-e48b547dbb35')
    assert ceremony is not None

    competitive_tier = client.get_competitive_tier('564d8e28-c226-3180-6285-e48a390db8b1')
    assert competitive_tier is not None
    assert competitive_tier.uuid == '564d8e28-c226-3180-6285-e48a390db8b1'
    assert competitive_tier.get_tiers() is not None

    currency = client.get_currency('VP')
    assert currency is not None
    assert currency.display_name.default == 'VP'

    game_mode = client.get_game_mode('96bd3920-4f36-d026-2b28-c683eb0bcac5')
    assert game_mode is not None
    assert game_mode.uuid == '96bd3920-4f36-d026-2b28-c683eb0bcac5'

    game_mode_equippable = client.get_game_mode_equippable('c5de005c-4bdc-26a7-a47d-c295eaaae9d8')
    assert game_mode_equippable is not None
    assert game_mode_equippable.uuid == 'c5de005c-4bdc-26a7-a47d-c295eaaae9d8'

    gear = client.get_gear('Light')
    assert gear is not None
    assert gear.display_name.default == 'Light Shields'

    event = client.get_event('024d36a7-46e3-8a29-30c6-09a7fb81bebe')
    assert event is not None

    level_border = client.get_level_border('ebc736cd-4b6a-137b-e2b0-1486e31312c9')
    assert level_border is not None
    assert level_border.uuid == 'ebc736cd-4b6a-137b-e2b0-1486e31312c9'

    level_border = client.get_level_border(20)
    assert level_border is not None
    assert level_border.starting_level >= 20

    map_ = client.get_map('ascent')
    assert map_ is not None
    assert map_.display_name.default == 'Ascent'

    season = client.get_season('0df5adb9-4dcb-6899-1306-3e9860661dd3')
    assert season is not None
    assert season.uuid == '0df5adb9-4dcb-6899-1306-3e9860661dd3'

    theme = client.get_theme('fdfe356c-40c4-ac6a-864e-16998fc784ef')
    assert theme is not None
    assert theme.uuid == 'fdfe356c-40c4-ac6a-864e-16998fc784ef'
