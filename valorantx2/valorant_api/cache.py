from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Dict, List, Optional

from .models import Agent

if TYPE_CHECKING:
    from ..enums import Locale
    from .http import HTTPClient

    # from .types.response import Response as ResponseData
    from .types.agents import Agent as AgentPayload, Data as AgentData

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
        self.cache: bool = True

    async def init(self) -> None:
        tasks = [
            self.http.get_agents,
        ]
        results = await asyncio.gather(*[task() for task in tasks])
        for func, result in zip(tasks, results):
            assert result is not None
            funcname = func.__name__.split('_')[1:]
            funcname = '_'.join(funcname)
            parse_func = getattr(self, f'add_{funcname}')
            parse_func(result)

    def clear(self) -> None:
        self._agents.clear()

    @property
    def agents(self) -> List[Agent]:
        return list(self._agents.values())

    def get_agent(self, uuid: Optional[str]) -> Optional[Agent]:
        return self._agents.get(uuid)  # type: ignore

    def store_agent(self, data: AgentPayload) -> Agent:
        agent_id = data['uuid']
        self._agents[agent_id] = agent = Agent(state=self, data=data)
        return agent

    def add_agents(self, data: AgentData) -> None:
        agent_data = data['data']
        for agent in agent_data:
            existing = self.get_agent(agent['uuid'])
            if existing is None:
                self.store_agent(agent)
