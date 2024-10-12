class TradeMetadata:
    def __init__(
        self,
        price=0.0,
        amount=0.0,
        take_profit_price=0.0,
        stop_loss_price=0.0,
        trade_log="",
        waiting_minutes=0,
    ):
        self.price = price
        self.amount = amount
        self.take_profit_price = take_profit_price
        self.stop_loss_price = stop_loss_price
        self.trade_log = trade_log
        self.waiting_minutes = waiting_minutes

    def to_proto_dict(self):
        return {
            "price": self.price,
            "amount": self.amount,
            "takeProfitPrice": self.take_profit_price,
            "takeStopLossPrice": self.stop_loss_price,
            "tradeLog": self.trade_log,
            "waitingMinutes": self.waiting_minutes,
        }
