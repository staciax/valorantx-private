from __future__ import annotations
from .abc import Messageable
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import Client
    from . message import Message

class Context(Messageable):

    def __init__(self, message: Message, client: Client, **attrs) -> None:
        self.message: Message = message
        
        # self.channel: Channel = message.channel
        # self.author: Union[Chatter, PartialChatter] = message.author

        self.prefix: Optional[str] = attrs.get('prefix')
        self.client = client

        # self.command: Optional[Command] = attrs.get("command")
        # if self.command:
            # self.cog: Optional[Cog] = self.command.cog
        # self.args: Optional[list] = attrs.get("args")
        # self.kwargs: Optional[dict] = attrs.get("kwargs")

        # self.view: Optional[StringParser] = attrs.get("view")
        # self.is_valid: bool = attrs.get("valid")

        # self.bot: Bot = bot
        # self._ws = self.author._ws