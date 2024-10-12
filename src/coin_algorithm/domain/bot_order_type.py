from enum import Enum

class BotOrderType(Enum):
    MARKET = 0
    LIMIT_ORDER = 1

    def __init__(self, value):
        self._value_ = value

    @property
    def value(self):
        return self._value_
