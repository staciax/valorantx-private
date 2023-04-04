import datetime

import pytest

from valorantx2.valorant_api import AbilityType, RelationType, RewardType

from .conftest import BaseTest  # BaseAuthTest


class TestValorantAPI(BaseTest):
    @pytest.mark.asyncio
    async def test_fetch_assets(self) -> None:
        await self.client.valorant_api.init()

    # async def asset_test(self, asset: Optional[Asset]) -> None:
    #     if asset is None:
    #         return

    #     # read the asset
    #     await asset.read()

    #     # to file the asset
    #     await asset.to_file()

    #     # # save the asset
    #     # await asset.save('.')

    @pytest.mark.asyncio
    async def test_agents(self) -> None:
        assert len(self.valorant_api.agents) > 0
        for agent in self.valorant_api.agents:
            assert agent.display_name is not None
            assert agent.description is not None
            assert agent.display_icon is not None
            assert agent.bust_portrait is not None
            assert agent.full_portrait is not None
            assert agent.full_portrait_v2 is not None
            assert agent.killfeed_portrait is not None
            assert agent.background is not None

            assert agent.role is not None
            assert agent.role.display_name is not None
            assert agent.role.description is not None
            assert agent.role.display_icon is not None

            assert agent.abilities is not None
            assert isinstance(agent.abilities, list)
            assert len(agent.abilities) >= 4 or len(agent.abilities) <= 5
            for ability in agent.abilities:
                assert ability is not None
                assert ability.slot is not None
                assert isinstance(ability.slot, AbilityType)
                assert ability.display_name is not None
                assert ability.description is not None
                if ability.display_icon:
                    assert ability.display_icon is not None

            assert agent.voice_line_localization is not None
            voice_line = agent.voice_line
            if voice_line is not None:
                assert agent.voice_line_localization.voice_locale == voice_line
                for voice in agent.voice_line_localization.all():
                    assert voice is not None
                    assert voice.min_duration is not None
                    assert voice.max_duration is not None
                    assert voice.media_list is not None
                    for media in voice.media_list:
                        assert media is not None
                        assert media.id is not None
                        assert media.wwise is not None
                        assert media.wave is not None

    @pytest.mark.asyncio
    async def test_buddies(self) -> None:
        assert len(self.valorant_api.buddies) > 0
        for buddy in self.valorant_api.buddies:
            assert buddy is not None
            assert buddy.display_name is not None
            assert isinstance(buddy.is_hidden_if_not_owned(), bool)
            # assert buddy.theme is not None
            assert buddy.display_icon is not None
            assert buddy.asset_path is not None
            assert len(buddy.levels) > 0
            assert buddy.get_buddy_level(1) is not None

            for level in buddy.levels:
                assert level is not None
                assert level.charm_level is not None
                assert level.display_name is not None
                assert level.display_icon is not None
                assert level.asset_path is not None

    @pytest.mark.asyncio
    async def test_bundles(self) -> None:
        assert len(self.valorant_api.bundles) > 0
        for bundle in self.valorant_api.bundles:
            assert bundle is not None
            assert bundle.display_name is not None
            assert bundle.description is not None
            # assert bundle.display_name_sub_text is not None
            # assert bundle.extra_description is not None
            # assert bundle.promo_description is not None
            assert isinstance(bundle.use_additional_context, bool)
            assert bundle.display_icon is not None
            assert bundle.display_icon_2 is not None
            if bundle.vertical_promo_image:
                assert bundle.vertical_promo_image is not None
            assert bundle.asset_path is not None

    @pytest.mark.asyncio
    async def test_ceremonies(self) -> None:
        assert len(self.valorant_api.ceremonies) > 0
        for ceremony in self.valorant_api.ceremonies:
            assert ceremony is not None
            assert ceremony.display_name is not None
            assert ceremony.asset_path is not None

    @pytest.mark.asyncio
    async def test_competitive_tiers(self) -> None:
        assert len(self.valorant_api.competitive_tiers) > 0
        for c_tier in self.valorant_api.competitive_tiers:
            assert c_tier is not None
            assert c_tier.asset_path is not None
            assert len(c_tier.tiers) > 0
            for tier in c_tier.tiers:
                assert tier is not None
                assert tier.tier is not None
                assert tier.name is not None
                assert tier.division is not None
                assert tier.division_name is not None
                assert tier.color is not None
                assert tier.background_color is not None
                if tier.small_icon:
                    assert tier.small_icon is not None
                if tier.large_icon:
                    assert tier.large_icon is not None
                if tier.rank_triangle_down_icon:
                    assert tier.rank_triangle_down_icon is not None
                if tier.rank_triangle_up_icon:
                    assert tier.rank_triangle_up_icon is not None

    @pytest.mark.asyncio
    async def test_content_tiers(self) -> None:
        assert len(self.valorant_api.content_tiers) > 0
        for content_tier in self.valorant_api.content_tiers:
            assert content_tier is not None
            assert content_tier.display_name is not None
            assert content_tier.dev_name is not None
            assert content_tier.rank is not None
            assert content_tier.juice_value is not None
            assert content_tier.juice_cost is not None
            assert content_tier.highlight_color is not None
            assert content_tier.display_icon is not None
            assert content_tier.asset_path is not None

    @pytest.mark.asyncio
    async def test_contracts(self) -> None:
        assert len(self.valorant_api.contracts) > 0
        for contract in self.valorant_api.contracts:
            assert contract is not None
            assert contract.display_name is not None
            # assert contract.display_icon is not None
            assert isinstance(contract.ship_it, bool)
            # assert contract.free_reward_schedule is not None
            assert contract.asset_path is not None
            content = contract.content
            assert content is not None
            assert isinstance(content.relation_type, RelationType)
            assert content.premium_vp_cost is not None
            # assert content.premium_reward_chedule is not None
            # assert content.relation is not None
            chapters = content.chapters
            assert len(chapters) > 0
            for chapter in chapters:
                assert chapter is not None
                assert isinstance(chapter.is_epilogue(), bool)
                assert len(chapter.levels) > 0
                for level in chapter.levels:
                    assert level is not None
                    assert level.reward is not None
                    reward = level.reward
                    assert reward.type is not None
                    assert isinstance(reward.type, RewardType)
                    assert isinstance(reward.amount, int)
                    # assert reward.item is not None
                    assert isinstance(level.xp, int)
                    assert isinstance(level.vp_cost, int)
                    assert isinstance(level.is_purchasable_with_vp(), bool)

                if chapter.free_rewards is not None:
                    assert len(chapter.free_rewards) > 0
                    for reward in chapter.free_rewards:
                        assert reward is not None

    @pytest.mark.asyncio
    async def test_currencies(self) -> None:
        assert len(self.valorant_api.currencies) > 0
        for currency in self.valorant_api.currencies:
            assert currency is not None
            assert currency.display_name is not None
            assert currency.display_name_singular is not None
            assert currency.display_icon is not None
            assert currency.large_icon is not None
            assert currency.asset_path is not None

    @pytest.mark.asyncio
    async def test_events(self) -> None:
        assert len(self.valorant_api.events) > 0
        for event in self.valorant_api.events:
            assert event is not None
            assert event.display_name is not None
            assert event.short_display_name is not None
            assert event.start_time is not None
            assert isinstance(event.start_time, datetime.datetime)
            assert event.end_time is not None
            assert isinstance(event.end_time, datetime.datetime)
            assert event.asset_path is not None

    @pytest.mark.asyncio
    async def test_gamemodes(self) -> None:
        assert len(self.valorant_api.game_modes) > 0
        for gm in self.valorant_api.game_modes:
            assert gm is not None
            assert gm.display_name is not None
            assert isinstance(gm.allows_match_timeouts, bool)
            assert isinstance(gm.is_team_voice_allowed(), bool)
            assert isinstance(gm.is_minimap_hidden(), bool)
            assert gm.orb_count is not None
            assert isinstance(gm.orb_count, int)
            assert gm.rounds_per_half is not None
            assert isinstance(gm.rounds_per_half, int)
            team_roles = gm.team_roles
            if team_roles is not None:
                assert isinstance(team_roles, list)
                assert len(team_roles) > 0
                for tr in team_roles:
                    assert tr is not None
                    assert isinstance(tr, str)
            feature_overrides = gm.game_feature_overrides
            if feature_overrides is not None:
                assert len(feature_overrides) > 0
                for fo in feature_overrides:
                    assert fo is not None
                    assert fo.feature_name is not None
                    assert isinstance(fo.state, bool)
            game_rule_bool_overrides = gm.game_rule_bool_overrides
            if game_rule_bool_overrides is not None:
                assert len(game_rule_bool_overrides) > 0
                for gro in game_rule_bool_overrides:
                    assert gro is not None
                    assert gro.rule_name is not None
                    assert isinstance(gro.state, bool)
            if gm.display_icon:
                assert gm.display_icon is not None
            assert gm.asset_path is not None

    @pytest.mark.asyncio
    async def test_gamemode_equippables(self) -> None:
        assert len(self.valorant_api.game_mode_equippables) > 0
        for gme in self.valorant_api.game_mode_equippables:
            assert gme is not None
            assert gme.display_name is not None
            assert gme.display_icon is not None
            assert gme.kill_stream_icon is not None
            assert gme.asset_path is not None

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        await self.client.close()
