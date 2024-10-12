class Bar:
    def __init__(self, open=0.0, high=0.0, low=0.0, close=0.0, volume=0.0, start_time=0, end_time=0):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.start_time = start_time
        self.end_time = end_time
        
    @staticmethod   
    def convert_candle_dicts_to_bars(candles_dict):
        bars_list = []
        for c in candles_dict:
            bar = Bar(
                open=float(c['open']),
                high=float(c['high']),
                low=float(c['low']),
                close=float(c['close']),
                volume=float(c['volume']),
                start_time=int(c['startTime']),
                end_time=int(c['endTime'])
            )
            bars_list.append(bar)
        return bars_list

    @staticmethod
    def convert_candles_to_bars(candles):
        bars_list = []
        for c in candles:
            bar = Bar(
                open=float(c.open),
                high=float(c.high),
                low=float(c.low),
                close=float(c.close),
                volume=float(c.volume),
                start_time=int(c.startTime),
                end_time=int(c.endTime)
            )
            bars_list.append(bar)
        return bars_list

    def in_period(self, time):
        return self.start_time < time < self.end_time