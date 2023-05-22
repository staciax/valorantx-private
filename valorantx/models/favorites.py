from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..types.favorites import Favorite as FavoritePayload, Favorites as FavoritesPayload
    from ..valorant_api_cache import CacheState


__all__ = (
    'Favorites',
    'Favorite',
)


class Favorites:
    def __init__(self, state: CacheState, data: FavoritesPayload) -> None:
        self._state: CacheState = state
        self.subject: str = data['Subject']
        self.favorited_content: Dict[str, Favorite] = {
            favorite['ItemID']: Favorite(favorite) for favorite in data['FavoritedContent'].values()
        }


class Favorite:
    def __init__(self, data: FavoritePayload) -> None:
        self.favorite_id: str = data['FavoriteID']
        self.item_id: str = data['ItemID']
