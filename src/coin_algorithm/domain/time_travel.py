from typing import List

from coin_algorithm.domain.trade_metadata import TradeMetadata


class TimeTravel:
    def __init__(self, buy_sell: List[int], metadata=List[TradeMetadata]):
        if buy_sell is None:
            buy_sell = []
        if metadata is None:
            metadata = []
        self.buy_sell = buy_sell
        self.metadata = metadata

    def to_proto_dict(self):
        return {
            "buySell": self.buy_sell,
            "tradeMetadata": [metadata.to_proto_dict() for metadata in self.metadata],
        }
