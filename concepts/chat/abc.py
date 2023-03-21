import abc

class Messageable(abc.ABC):

    __slots__ = ()

    # @abc.abstractmethod
    # def _fetch_channel(self):
    #     raise NotImplementedError

    # @abc.abstractmethod
    # def _fetch_websocket(self):
    #     raise NotImplementedError

    # @abc.abstractmethod
    # def _fetch_message(self):
    #     raise NotImplementedError

    # @abc.abstractmethod
    # def _bot_is_mod(self):
    #     raise NotImplementedError

    # def check_bucket(self, channel):
    #     mod = self._bot_is_mod()

    #     if mod:
    #         bucket = limiter.get_bucket(channel=channel, method="mod")
    #     else:
    #         bucket = limiter.get_bucket(channel=channel, method="irc")
    #     now = time.time()
    #     bucket.update()

    #     if bucket.limited:
    #         raise IRCCooldownError(
    #             f"IRC Message rate limit reached for channel <{channel}>."
    #             f" Please try again in {bucket._reset - now:.2f}s"
    #         )

    # def check_content(self, content: str):
    #     if len(content) > 500:
    #         raise InvalidContent("Content must not exceed 500 characters.")

    # async def send(self, content: str):
    #     """|coro|


    #     Send a message to the destination associated with the dataclass.

    #     Destination will either be a channel or user.

    #     Parameters
    #     ------------
    #     content: str
    #         The content you wish to send as a message. The content must be a string.

    #     Raises
    #     --------
    #     InvalidContent
    #         Invalid content.
    #     """
    #     entity = self._fetch_channel()
    #     ws = self._fetch_websocket()

    #     self.check_content(content)
    #     self.check_bucket(channel=entity.name)

    #     try:
    #         name = entity.channel.name
    #     except AttributeError:
    #         name = entity.name
    #     if entity.__messageable_channel__:
    #         await ws.send(f"PRIVMSG #{name} :{content}\r\n")
    #     else:
    #         await ws.send(f"PRIVMSG #jtv :/w {entity.name} {content}\r\n")
