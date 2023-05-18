from typing import Dict, TypedDict


class Favorite(TypedDict):
    FavoriteID: str
    ItemID: str


class Favorites(TypedDict):
    Subject: str
    FavoritedContent: Dict[str, Favorite]
