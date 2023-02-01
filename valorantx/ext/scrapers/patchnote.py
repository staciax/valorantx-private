from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Optional, TypeVar

if TYPE_CHECKING:
    from ...client import Client
    from typing_extensions import Self

from bs4 import BeautifulSoup, FeatureNotFound

# fmt: off
__all__ = (
    'PatchNote',
)
# fmt: on

ClientT = TypeVar('ClientT', bound='Client')


class PatchNote(Generic[ClientT]):
    def __init__(self, title: Optional[str], banner_url: Optional[str]) -> None:
        self.title: Optional[str] = title
        self.banner_url: Optional[str] = banner_url

    def __repr__(self) -> str:
        return f'<PatchNote title={self.title!r}> banner_url={self.banner_url!r}>'

    def get_highlight_banner(self) -> Optional[str]:
        return self.banner_url

    @staticmethod
    def to_soup(text: str) -> BeautifulSoup:
        # lxml is faster than html.parser
        try:
            # try to use lxml
            soup = BeautifulSoup(text, 'lxml')
        except FeatureNotFound:
            # fallback to html.parser
            soup = BeautifulSoup(text, 'html.parser')
        return soup

    @staticmethod
    def get_title(soup: BeautifulSoup) -> Optional[str]:
        soup_title = soup.find('title')
        if soup_title is not None:
            return soup_title.text
        return None

    @staticmethod
    def get_banner_url(soup: BeautifulSoup) -> Optional[str]:
        banners = soup.find_all('img')
        for banner in banners:
            if 'src' in banner.attrs:
                if 'Highlights' in banner['src']:
                    return banner['src']
        return None

    @classmethod
    async def fetch_from_url(cls, client: ClientT, url: str) -> Self:
        text = await client.http.text_from_url(url)

        soup = cls.to_soup(text)
        title = cls.get_title(soup)
        banner_url = cls.get_banner_url(soup)

        return cls(title, banner_url)

    @classmethod
    def from_text(cls, text: str) -> Self:
        soup = cls.to_soup(text)
        title = cls.get_title(soup)
        banner_url = cls.get_banner_url(soup)
        return cls(title, banner_url)
