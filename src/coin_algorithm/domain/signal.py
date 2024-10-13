class Signal:
    def __init__(self, time: int = 0, is_buy: bool = False, is_sell: bool = False, is_close_buy: bool = False,
                 is_close_sell: bool = False):
        self.time = time
        self.is_buy = is_buy
        self.is_sell = is_sell
        self.is_close_buy = is_close_buy
        self.is_close_sell = is_close_sell

    def to_proto_dict(self):
        return {
            "time": self.time,
            "isBuy": self.is_buy,
            "isSell": self.is_sell,
            "isCloseBuy": self.is_close_buy,
            "isCloseSell": self.is_close_sell,
        }
