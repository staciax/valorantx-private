from typing import Optional, TypedDict


class PartialUser(TypedDict):
    puuid: str
    name: Optional[str]
    tag: Optional[str]
    region: Optional[str]
