__all__ = ('_Cost',)


class _Cost:
    def __init__(self) -> None:
        self._cost: int = 0

    @property
    def cost(self) -> int:
        return self._cost

    @cost.setter
    def cost(self, cost: int) -> None:
        self._cost = cost

    @property
    def price(self) -> int:
        """:class:`int`: alias for :attr:`cost`"""
        return self.cost

    @price.setter
    def price(self, price: int) -> None:
        self.cost = price
