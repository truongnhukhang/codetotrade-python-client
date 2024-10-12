from typing import List
from coin_algorithm.domain.bar import Bar


class BarSeries(object):
    def __init__(self, symbol="", bars:List[Bar]=None, duration=5):
        if bars is None:
            bars = []
        self.symbol = symbol
        self.bars = bars
        self.closes = [bar.close for bar in bars]
        self.opens = [bar.open for bar in bars]
        self.highs = [bar.high for bar in bars]
        self.lows = [bar.low for bar in bars]
        self.volume = [bar.volume for bar in bars]
        self.start_time = [bar.start_time for bar in bars]
        self.end_time = [bar.end_time for bar in bars]
        self.duration = duration

    def get_first_bar(self) -> Bar:
        return self.bars[0]

    def get_last_bar(self) -> Bar:
        return self.bars[-1]

    def get_bar_count(self) -> int:
        return len(self.bars)

    def add_bar(self, bar: Bar, is_replace=False):
        if is_replace:
            self.bars[-1] = bar
            self.closes[-1] = bar.close
            self.opens[-1] = bar.open
            self.highs[-1] = bar.high
            self.lows[-1] = bar.low
            self.volume[-1] = bar.volume
            self.start_time[-1] = bar.start_time
            self.end_time[-1] = bar.end_time
        else:
            self.bars.append(bar)
