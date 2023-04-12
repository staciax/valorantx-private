from __future__ import annotations

from typing import TYPE_CHECKING

from ..valorant_api.models.agents import Agent as AgentValorantAPI

if TYPE_CHECKING:
    from ..valorant_api.types.agents import Agent as AgentValorantAPIPayload


class Agent(AgentValorantAPI):
    pass
