class CoinInfo:
    def __init__(self, symbol="", price_precision=0, quantity_precision=0, tick_size=0):
        self.symbol = symbol
        self.price_precision = price_precision
        self.quantity_precision = quantity_precision
        self.tick_size = tick_size
