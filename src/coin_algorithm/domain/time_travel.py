from typing import List

from coin_algorithm.domain.signal import Signal
from coin_algorithm.domain.trade_metadata import TradeMetadata


class TimeTravel:
    def __init__(self, signal: List[Signal], metadata=List[TradeMetadata]):
        if signal is None:
            signal = []
        if metadata is None:
            metadata = []
        self.signal = signal
        self.metadata = metadata

    def to_proto_dict(self):
        return {
            "signal": [signal.to_proto_dict() for signal in self.signal],
            "tradeMetadata": [metadata.to_proto_dict() for metadata in self.metadata],
        }
