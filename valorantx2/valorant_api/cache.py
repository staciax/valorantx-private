from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from .models import Agent

if TYPE_CHECKING:
    from ..enums import Locale
    from .http import HTTPClient
    from .types.agents import Agent as AgentPayload

# class BaseCache(ABC):

#     @abstractmethod
#     def get(self):
#         raise NotImplementedError

#     @abstractmethod
#     def find(self):
#         raise NotImplementedError


class CacheState:
    def __init__(self, *, locale: Locale, http: HTTPClient, to_file: bool = False) -> None:
        self.locale = locale
        self.http = http
        self._to_file: bool = to_file

        self._agents: Dict[str, Agent] = {}

    def find(self, **kwargs) -> ...:
        ...

    @property
    def agents(self) -> List[Agent]:
        return list(self._agents.values())

    def get_agent(self, uuid: Optional[str]) -> Optional[Agent]:
        return self._agents.get(uuid)  # type: ignore

    def store_agent(self, data: AgentPayload) -> Agent:
        agent_id = data['uuid']
        self._agents[agent_id] = agent = Agent(state=self, data=data)
        return agent
