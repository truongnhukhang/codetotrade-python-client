from typing import List

from coin_algorithm.domain.bar_series import BarSeries


class Plot:
    def __init__(
            self,
            name,
            color="#000000",
            indicator_values:List[float]=None,
            bar_series:BarSeries=None,
            price_precision=0,
            style="LINE",
    ):
        self.name = name
        self.color = color
        self.indicator_values = indicator_values if indicator_values is not None else []
        self.bar_series:BarSeries = bar_series if bar_series is not None else []
        self.price_precision = price_precision
        self.style = style

    def to_proto_dict(self):
        return {
            "name": self.name,
            "color": self.color,
            "valueList": self.indicator_values,
            "pricePrecision": self.price_precision,
            "style": self.style,
        }

    def with_color(self, color):
        self.color = color
        return self

    def with_indicator(self, indicator):
        self.indicator = indicator
        return self

    def with_price_precision(self, price_precision):
        self.price_precision = price_precision
        return self

    def with_style(self, style):
        self.style = style
        return self

    def with_indicator_values(self, indicator_values):
        self.indicator_values = indicator_values
        return self
