from __future__ import annotations

import asyncio
import json
import os
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List, Optional

from .models import Agent, Buddy, BuddyLevel

if TYPE_CHECKING:
    from ..enums import Locale
    from .http import HTTPClient
    from .types import agents, buddies

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
        self.cache: bool = True
        self._to_file: bool = to_file

        self._agents: Dict[str, Agent] = {}
        self._buddies: Dict[str, Buddy] = {}
        self._buddy_levels: Dict[str, BuddyLevel] = {}

    async def init(self) -> None:
        tasks = [
            self.http.get_agents,
            self.http.get_buddies,
            # self.http.get_bundles,
            # self.http.get_ceremonies,
            # self.http.get_competitive_tiers,
            # self.http.get_content_tiers,
            # self.http.get_contracts,
            # self.http.get_currencies,
            # self.http.get_events,
            # self.http.get_gear,
            # self.http.get_level_borders,
            # self.http.get_maps,
            # self.http.get_player_cards,
            # self.http.get_player_titles,
            # self.http.get_seasons,
            # self.http.get_sprays,
            # self.http.get_themes,
            # self.http.get_weapons,
            # self.http.get_version,
        ]
        # if self._to_file:

        #     # read from file
        #     for func in tasks:
        #         funcname = func.__name__.split('_')[1:]
        #         filename = '_'.join(funcname) + '.json'
        #         # add_to_cache = getattr(self, f'add_{funcname}')
        #         # if os.path.exists(filename):
        #         #     with open(filename, 'r') as f:
        #         #         data = json.load(f)
        #         #         continue
        #         # else:
        #         #     data = await func()
        #         #     self._add_to_file(data, filename)
        #         # add_to_cache = getattr(self, f'add_{funcname}')
        # else:
        # results = await self._fetch_data_from_api(tasks)

        results = await asyncio.gather(*[task() for task in tasks])
        for func, result in zip(tasks, results):
            assert result is not None
            funcname = func.__name__.split('_')[1:]
            funcname = '_'.join(funcname)
            parse_func = getattr(self, f'add_{funcname}')
            parse_func(result)

    # async def _fetch_data_from_api(self, tasks: List[Callable[..., Coroutine[Any, Any, Any]]]) -> List[Any]:
    #     results = await asyncio.gather(*[task() for task in tasks])
    #     return results
    # for func, result in zip(tasks, results):
    #     assert result is not None
    #     funcname = func.__name__.split('_')[1:]
    #     funcname = '_'.join(funcname)
    #     parse_func = getattr(self, f'add_{funcname}')
    #     parse_func(result)

    # def _add_to_file(self, data: Any, filename: str) -> None:
    #     with open(filename, 'w') as f:
    #         json.dump(data, f, indent=4)

    def clear(self) -> None:
        self._agents.clear()

    # agents

    @property
    def agents(self) -> List[Agent]:
        return list(self._agents.values())

    def get_agent(self, uuid: Optional[str]) -> Optional[Agent]:
        return self._agents.get(uuid)  # type: ignore

    def store_agent(self, data: agents.Agent) -> Agent:
        agent_id = data['uuid']
        self._agents[agent_id] = agent = Agent(state=self, data=data)
        return agent

    def add_agents(self, data: agents.Agents) -> None:
        agent_data = data['data']
        for agent in agent_data:
            existing = self.get_agent(agent['uuid'])
            if existing is None:
                self.store_agent(agent)

    # buddies

    @property
    def buddies(self) -> List[Buddy]:
        return list(self._buddies.values())

    @property
    def buddy_levels(self) -> List[BuddyLevel]:
        return list(self._buddy_levels.values())

    def get_buddy(self, uuid: Optional[str]) -> Optional[Buddy]:
        return self._buddies.get(uuid)  # type: ignore

    def get_buddy_level(self, uuid: Optional[str]) -> Optional[BuddyLevel]:
        return self._buddy_levels.get(uuid)  # type: ignore

    def store_buddy(self, data: buddies.Buddy) -> Buddy:
        buddy_id = data['uuid']
        self._buddies[buddy_id] = buddy = Buddy(state=self, data=data)
        return buddy

    def store_buddy_level(self, data: buddies.BuddyLevel) -> BuddyLevel:
        buddy_level_id = data['uuid']
        self._buddy_levels[buddy_level_id] = buddy_level = BuddyLevel(state=self, data=data)
        return buddy_level

    def add_buddies(self, data: buddies.Buddies) -> None:
        buddy_data = data['data']
        for buddy in buddy_data:
            buddy_existing = self.get_buddy(buddy['uuid'])
            if buddy_existing is None:
                buddy_existing = self.store_buddy(buddy)
            for level in buddy['levels']:
                level_existing = self.get_buddy_level(level['uuid'])
                if level_existing is None:
                    level_existing = self.store_buddy_level(level)
                level_existing.buddy = buddy_existing

    # bundles
