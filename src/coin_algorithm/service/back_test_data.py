from abc import ABC
from typing import Dict

from coin_algorithm.domain.bar_series import BarSeries
from coin_algorithm.domain.bot_config import BotConfig
from coin_algorithm.domain.coin_info import CoinInfo


class BackTestData(ABC):
    def __init__(
            self,
            bar_series: BarSeries,
            other_bar_series: Dict[int, BarSeries],
            btd_dom_bar_series: Dict[int, BarSeries],
            coin_info: CoinInfo,
            bot_config: BotConfig,
    ):
        self.bar_series = bar_series
        self.btc_dom_bar_series = btd_dom_bar_series
        self.other_bar_series = other_bar_series
        self.coin_info = coin_info
        self.bot_config = bot_config
