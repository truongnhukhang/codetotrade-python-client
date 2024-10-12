import datetime
from typing import Dict
from coin_algorithm.domain.bar import Bar
from coin_algorithm.domain.base_bot import BaseBot
from coin_algorithm.domain.trade_metadata import TradeMetadata


class SimpleBot(BaseBot):
    def is_close_current_position(self,idx: int) -> bool:
        pass

    def __init__(self):
        super().__init__()
        self.tp = 0.1
        self.sl = 0.1
        self.name = "SimpleBot"

    def init(self, config: Dict[str, str]) -> None:
        self.tp = float(config.get("tp", 0.1))
        self.sl = float(config.get("sl", 0.1))
        return super().init(config)

    def is_buy(self, idx: int) -> bool:
        current_bar: Bar = self.bar_series.bars[idx]
        start_time = current_bar.start_time
        # convert start_time to datetime
        # hint: use datetime.fromtimestamp
        minute = datetime.datetime.fromtimestamp(start_time/1000.0).minute
        # get the minutes of the start_time
        # hint: use start_time.minute
        return minute % 3 == 0

    def is_sell(self, idx: int) -> bool:
        current_bar: Bar = self.bar_series.bars[idx]
        start_time = current_bar.start_time
        # convert start_time to datetime
        # hint: use datetime.fromtimestamp
        minute = datetime.datetime.fromtimestamp(start_time/1000.0).minute
        # get the minutes of the start_time
        # hint: use start_time.minute
        return minute % 2 == 0

    def buy(self, idx: int) -> TradeMetadata:
        current_bar: Bar = self.bar_series.bars[idx]
        return TradeMetadata(
            current_bar.close,
            0.01,
            take_profit_price=current_bar.close + current_bar.close * self.tp,
            stop_loss_price=current_bar.close - current_bar.close * self.sl,
            trade_log="SimpleBot Buy",
        )

    def sell(self, idx: int) -> TradeMetadata:
        current_bar: Bar = self.bar_series.bars[idx]
        return TradeMetadata(
            current_bar.close,
            0.01,
            take_profit_price=current_bar.close - current_bar.close * self.tp,
            stop_loss_price=current_bar.close + current_bar.close * self.sl,
            trade_log="SimpleBot Buy",
        )
