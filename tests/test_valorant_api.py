from __future__ import annotations

from typing import TYPE_CHECKING, Dict

import pytest

from valorantx2 import AbilityType
from valorantx2.valorant_api import Asset, Localization

from .conftest import BaseAuthTest

if TYPE_CHECKING:
    from valorantx2.valorant_api.types import agents


class TestValorantAPI(BaseAuthTest):
    @pytest.mark.asyncio
    async def test_fetch_assets(self) -> None:
        await self.client.valorant_api.init()

    @pytest.mark.asyncio
    async def test_agents(self) -> None:
        def localization_test(localization: Dict[str, str]) -> None:
            assert isinstance(localization, dict)
            for key, value in localization.items():
                assert key is not None
                assert value is not None
                assert isinstance(key, str)
                assert isinstance(value, str)

        def voice_test(voice: agents.VoiceLine) -> None:
            assert isinstance(voice, dict)
            min_duration = voice['minDuration']
            max_duration = voice['maxDuration']
            media_list = voice['mediaList']
            assert min_duration is not None
            assert isinstance(min_duration, float)
            assert max_duration is not None
            assert isinstance(max_duration, float)
            assert media_list is not None
            assert isinstance(media_list, list)
            for media in media_list:
                assert media is not None
                assert media['id'] is not None
                assert media['wwise'] is not None
                assert media['wave'] is not None

        api = self.client.valorant_api
        for agent in api.agents:
            # verify data from the API

            assert agent is not None
            assert agent._display_name is not None
            assert agent._description is not None
            assert agent.developer_name is not None
            if agent.character_tags is not None:
                assert isinstance(agent.character_tags, list)
                for tag in agent.character_tags:
                    assert tag is not None
                    assert isinstance(tag, (str, dict))
                    if isinstance(tag, dict):
                        localization_test(tag)
                    else:
                        assert isinstance(tag, str)

            assert agent._display_icon_small is not None
            assert agent._bust_portrait is not None
            assert agent._full_portrait is not None
            assert agent._full_portrait_v2 is not None
            assert agent._killfeed_portrait is not None
            assert agent._background is not None
            assert agent.background_gradient_colors is not None
            assert agent.asset_path is not None
            assert isinstance(agent._is_full_portrait_right_facing, bool)
            assert isinstance(agent._is_playable_character, bool)
            assert isinstance(agent._is_available_for_test, bool)
            assert isinstance(agent._is_base_content, bool)

            # role
            assert agent._role is not None
            assert agent._role['uuid'] is not None
            role_display_name = agent._role['displayName']
            assert role_display_name is not None
            assert isinstance(role_display_name, (str, dict))
            if isinstance(role_display_name, dict):
                localization_test(role_display_name)
            else:
                assert isinstance(role_display_name, str)

            role_description = agent._role['description']
            assert role_description is not None
            assert isinstance(role_description, (str, dict))
            if isinstance(role_description, dict):
                localization_test(role_description)

            assert agent._role['displayIcon'] is not None
            assert agent._role['assetPath'] is not None

            # abilities

            assert isinstance(agent._abilities, list)
            for ability in agent._abilities:
                assert ability is not None
                assert ability['slot'] is not None
                ability_display_name = ability['displayName']
                assert ability_display_name is not None
                assert isinstance(ability_display_name, (str, dict))
                if isinstance(ability_display_name, dict):
                    localization_test(ability_display_name)
                else:
                    assert isinstance(ability_display_name, str)

                ability_description = ability['description']
                assert ability_description is not None
                assert isinstance(ability_description, (str, dict))
                if isinstance(ability_description, dict):
                    localization_test(ability_description)
                else:
                    assert isinstance(ability_description, str)

                if ability['displayIcon'] is not None:
                    assert isinstance(ability['displayIcon'], str)

            # voice lines

            voice_line = agent._voice_line
            assert voice_line is not None
            assert isinstance(voice_line, dict)
            if 'mediaList' in voice_line:
                voice_test(voice_line)  # type: ignore
            else:
                for voice_locale in voice_line.values():
                    if voice_locale is not None:
                        voice_test(voice_locale)

            # verify model

            assert agent.display_name is not None
            assert isinstance(agent.display_name, Localization)
            assert agent.description is not None
            assert isinstance(agent.description, Localization)
            assert agent.display_icon is not None
            assert isinstance(agent.display_icon, Asset)
            assert agent.bust_portrait is not None
            assert isinstance(agent.bust_portrait, Asset)
            assert agent.full_portrait is not None
            assert isinstance(agent.full_portrait, Asset)
            assert agent.full_portrait_v2 is not None
            assert isinstance(agent.full_portrait_v2, Asset)
            assert agent.killfeed_portrait is not None
            assert isinstance(agent.killfeed_portrait, Asset)
            assert agent.background is not None
            assert isinstance(agent.background, Asset)

            assert agent.role is not None
            assert agent.role.display_name is not None
            assert isinstance(agent.role.display_name, Localization)
            assert agent.role.description is not None
            assert isinstance(agent.role.description, Localization)
            assert agent.role.display_icon is not None
            assert isinstance(agent.role.display_icon, Asset)

            assert agent.abilities is not None
            assert isinstance(agent.abilities, list)
            for ability in agent.abilities:
                assert ability is not None
                assert ability.slot is not None
                assert isinstance(ability.slot, AbilityType)
                assert ability.display_name is not None
                assert isinstance(ability.display_name, Localization)
                assert ability.description is not None
                assert isinstance(ability.description, Localization)
                if ability.display_icon is not None:
                    assert isinstance(ability.display_icon, Asset)

            assert agent.voice_line_localization is not None
            voice_line = agent.voice_line
            if voice_line is not None:
                assert agent.voice_line_localization.voice_locale == voice_line
                for voice in agent.voice_line_localization.all():
                    assert voice is not None

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        await self.client.close()
