from abc import ABC, abstractmethod
from coin_algorithm.domain.bar_series import BarSeries
from coin_algorithm.domain.bot_config import BotConfig
from coin_algorithm.domain.chart import Chart
from coin_algorithm.domain.coin_info import CoinInfo
from coin_algorithm.domain.time_travel import TimeTravel
from coin_algorithm.domain.trade_metadata import TradeMetadata

from typing import Dict, List


class BaseBot(ABC):
    def __init__(
            self, bar_series=BarSeries(), btc_dom_bar_series: Dict[int, BarSeries] = None,
            other_bar_series: Dict[int, BarSeries] = None,
            chart_list: [Chart] = None, bot_config: BotConfig = BotConfig(), coin_info: CoinInfo = CoinInfo()
    ):
        if btc_dom_bar_series is None:
            self.btc_dom_bar_series: Dict[int, BarSeries] = {}
        if chart_list is None:
            self.chart_list = []
        if other_bar_series is None:
            self.other_bar_series: Dict[int, BarSeries] = {}
        self.bar_series = bar_series
        self.coin_info = coin_info
        self.bot_config = bot_config

    @abstractmethod
    def init(self, config: Dict[str, str]) -> None:
        pass

    @abstractmethod
    def is_buy(self, idx: int) -> bool:
        pass

    @abstractmethod
    def is_sell(self, idx: int) -> bool:
        pass

    @abstractmethod
    def buy(self, idx: int) -> TradeMetadata:
        pass

    @abstractmethod
    def sell(self, idx: int) -> TradeMetadata:
        pass

    @abstractmethod
    def is_close_current_position(self, idx: int) -> bool:
        pass

    def get_chart_list(self) -> List[Chart]:
        return self.chart_list

    @staticmethod
    def get_index_of_bar_series_by_start_time(bar_series: BarSeries, start_time: int) -> int:
        max_len = len(bar_series.bars)-1
        min_len = 0
        while min_len <= max_len:
            mid = int(min_len + (max_len - min_len) // 2)
            if bar_series.bars[mid].start_time <= start_time <= bar_series.bars[mid].end_time:
                return mid
            if bar_series.bars[mid].end_time < start_time:
                min_len = mid + 1
            if bar_series.bars[mid].start_time > start_time:
                max_len = mid - 1
        return -1

    def time_travel(self) -> TimeTravel:
        time_travel = TimeTravel([], [])
        bars = self.bar_series.bars
        buysell = [0] * len(bars)
        metadata = [TradeMetadata()] * len(bars)
        for i in range(0, len(bars)):
            if self.is_buy(i):
                buysell[i] = 1
                metadata[i] = self.buy(i)
            elif self.is_sell(i):
                buysell[i] = 2
                metadata[i] = self.sell(i)
            elif self.bot_config.is_enable_close_mode and self.is_close_current_position(i):
                buysell[i] = 3
                metadata[i] = TradeMetadata()
            else:
                buysell[i] = 0
                metadata[i] = TradeMetadata()

        time_travel.buy_sell = buysell
        time_travel.metadata = metadata
        return time_travel
