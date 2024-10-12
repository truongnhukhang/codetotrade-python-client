from coin_algorithm.domain.bot_order_type import BotOrderType


class BotConfig:
    def __init__(
        self,
        bot_order_type=BotOrderType.MARKET,
        is_enable_close_mode=False,
        init_bar=0,
        init_balance=0.0,
        maker_fee=0.0,
        taker_fee=0.0,
    ):
        self.bot_order_type = bot_order_type
        self.is_enable_close_mode = is_enable_close_mode
        self.init_bar = init_bar
        self.init_balance = init_balance
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
