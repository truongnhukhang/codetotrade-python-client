import json
import logging
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from time import sleep
from typing import Dict, Any, List
from uuid import uuid4

from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from coin_algorithm.service.grpc import coin_service_pb2
import sched, time

logger = logging.getLogger(__name__)


class BinanceFutureConnector(object):
    MAX_SIZE = 1000  # Example value, set according to your requirements

    def __init__(self, api_key, api_secret, testnet=False):
        self.start_time = time.time()
        self.executor_service = ThreadPoolExecutor(max_workers=1)
        self.api_key = api_key
        self.api_secret = api_secret
        self.test_net = testnet
        self.ws_client_map: Dict[str, Dict[str, UMFuturesWebsocketClient]] = {}
        self.maintainer = sched.scheduler(time.time, time.sleep)
        if testnet:
            self.client = UMFutures(base_url='https://testnet.binancefuture.com', key=api_key,
                                    secret=api_secret)
        else:
            self.client = UMFutures(key=api_key, secret=api_secret)

    def start(self):
        self.executor_service.submit(self.maintain_ws_client)

    def stop(self):
        self.executor_service.shutdown()

    def maintain_ws_client(self):
        while True:
            # if self.start_time + 2hours < current time then restart the websocket client
            if self.start_time + 2 * 60 * 60 < time.time():
                self.start_time = time.time()
                for stream_id, ws_client_map in self.ws_client_map.items():
                    for streams_hash, ws_client in ws_client_map.items():
                        logger.info(f"UNSUBSCRIBING {streams_hash} with id {stream_id}")
                        ws_client.unsubscribe(streams_hash.split(","), stream_id)
                        logger.info(f"SUBSCRIBING {streams_hash} with id {stream_id}")
                        ws_client.subscribe(streams_hash.split(","), stream_id)
            else:
                sleep(60)

    def create_ws_client(self, is_combined, on_message, on_close, on_error) -> UMFuturesWebsocketClient:
        if self.test_net:
            return UMFuturesWebsocketClient(stream_url='wss://stream.binancefuture.com', is_combined=is_combined
                                            , on_message=on_message, on_close=on_close, on_error=on_error)
        else:
            return UMFuturesWebsocketClient(is_combined=is_combined
                                            , on_message=on_message, on_close=on_close, on_error=on_error)

    def default_market_order(self, client_id: str) -> OrderedDict:
        params = OrderedDict()
        params["positionSide"] = "BOTH"
        params["type"] = "MARKET"
        params["newClientOrderId"] = client_id
        params["newOrderRespType"] = "RESULT"
        return params

    def default_limit_order(self, client_id: str) -> OrderedDict:
        params = OrderedDict()
        params["positionSide"] = "BOTH"
        params["type"] = "LIMIT"
        params["newClientOrderId"] = client_id
        params["newOrderRespType"] = "RESULT"
        return params

    def default_reduce_only_order(self, client_id: str) -> OrderedDict:
        params = self.default_market_order(client_id)
        params["reduceOnly"] = "true"
        return params

    def place_market_buy_order(self, symbol: str, quantity: str, is_test_order: bool, client_id: str) -> Dict[
        str, Any]:
        params = self.default_market_order(client_id)
        params["symbol"] = symbol
        params["side"] = "BUY"
        params["quantity"] = quantity
        if is_test_order:
            return self.client.new_order_test(**params)
        else:
            return self.client.new_order(**params)

    def place_limit_buy_order(self, symbol: str, quantity: str, price: str, is_test_order: bool, client_id: str) -> \
            Dict[str, Any]:
        params = self.default_limit_order(client_id)
        params["symbol"] = symbol
        params["side"] = "BUY"
        params["quantity"] = quantity
        params["price"] = price
        params["timeInForce"] = "GTC"
        if is_test_order:
            return self.client.new_order_test(**params)
        else:
            return self.client.new_order(**params)

    def place_limit_sell_order(self, symbol: str, quantity: str, price: str, is_test_order: bool, client_id: str) -> \
            Dict[str, Any]:
        params = self.default_limit_order(client_id)
        params["symbol"] = symbol
        params["side"] = "SELL"
        params["quantity"] = quantity
        params["price"] = price
        params["timeInForce"] = "GTC"
        if is_test_order:
            return self.client.new_order_test(**params)
        else:
            return self.client.new_order(**params)

    def place_market_sell_order(self, symbol: str, quantity: str, is_test_order: bool, client_id: str) -> Dict[
        str, Any]:
        params = self.default_market_order(client_id)
        params["symbol"] = symbol
        params["side"] = "SELL"
        params["quantity"] = quantity
        if is_test_order:
            return self.client.new_order_test(**params)
        else:
            return self.client.new_order(**params)

    def place_buy_take_profit_order(self, symbol: str, quantity: str, price: str, is_test_order: bool,
                                    client_id: str) -> Dict[str, Any]:
        params = self.default_reduce_only_order(client_id)
        params["type"] = "TAKE_PROFIT_MARKET"
        params["symbol"] = symbol
        params["side"] = "BUY"
        params["quantity"] = quantity
        params["stopPrice"] = price
        if is_test_order:
            return self.client.new_order_test(**params)
        else:
            return self.client.new_order(**params)

    def place_buy_stop_loss_order(self, symbol: str, quantity: str, price: str, is_test_order: bool,
                                  client_id: str) -> \
            Dict[str, Any]:
        params = self.default_reduce_only_order(client_id)
        params["type"] = "STOP_MARKET"
        params["symbol"] = symbol
        params["side"] = "BUY"
        params["quantity"] = quantity
        params["stopPrice"] = price
        if is_test_order:
            return self.client.new_order_test(**params)
        else:
            return self.client.new_order(**params)

    def place_sell_take_profit_order(self, symbol: str, quantity: str, price: str, is_test_order: bool,
                                     client_id: str) -> Dict[str, Any]:
        params = self.default_reduce_only_order(client_id)
        params["type"] = "TAKE_PROFIT_MARKET"
        params["symbol"] = symbol
        params["side"] = "SELL"
        params["quantity"] = quantity
        params["stopPrice"] = price
        if is_test_order:
            return self.client.new_order_test(**params)
        else:
            return self.client.new_order(**params)

    def place_sell_stop_loss_order(self, symbol: str, quantity: str, price: str, is_test_order: bool,
                                   client_id: str) -> \
            Dict[str, Any]:
        params = self.default_reduce_only_order(client_id)
        params["type"] = "STOP_MARKET"
        params["symbol"] = symbol
        params["side"] = "SELL"
        params["quantity"] = quantity
        params["stopPrice"] = price
        if is_test_order:
            return self.client.new_order_test(**params)
        else:
            return self.client.new_order(**params)

    def cancel_all_open_orders(self, symbol: str) -> str:
        params = OrderedDict()
        params["symbol"] = symbol
        return self.client.cancel_open_orders(symbol)

    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        return self.client.cancel_order(symbol=symbol, origClientOrderId=order_id)

    @staticmethod
    def duration_to_string(duration: int) -> str:
        duration_map = {
            1: "1m",
            3: "3m",
            5: "5m",
            15: "15m",
            30: "30m",
            60: "1h",
            120: "2h",
            180: "3h",
            240: "4h",
            360: "6h",
            480: "8h",
            720: "12h",
            1440: "1d",
            1440 * 3: "3d",
            1440 * 7: "1w",
            1440 * 30: "1mo"
        }
        return duration_map.get(duration, "5m")

    @staticmethod
    def from_string(interval: str) -> timedelta:
        interval_map = {
            "1m": timedelta(minutes=1),
            "3m": timedelta(minutes=3),
            "5m": timedelta(minutes=5),
            "15m": timedelta(minutes=15),
            "30m": timedelta(minutes=30),
            "1h": timedelta(hours=1),
            "2h": timedelta(hours=2),
            "3h": timedelta(hours=3),
            "4h": timedelta(hours=4),
            "6h": timedelta(hours=6),
            "8h": timedelta(hours=8),
            "12h": timedelta(hours=12),
            "1d": timedelta(days=1),
            "3d": timedelta(days=3),
            "1w": timedelta(weeks=1),
            "1mo": timedelta(days=30)
        }
        return interval_map.get(interval, timedelta(minutes=5))

    def get_recent_candle(self, symbol: str, interval: str, limit: int) -> List[coin_service_pb2.Candle]:
        if limit < 0:
            return []

        fetch_size = min(limit, self.MAX_SIZE)
        raw_klines = self.client.klines(symbol=symbol, interval=interval, limit=fetch_size)

        candles = []

        for kline in raw_klines:
            try:
                c = coin_service_pb2.Candle(
                    startTime=int(kline[0]),
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5]),
                    endTime=int(kline[6]),
                    duration=int(self.from_string(interval).total_seconds() // 60)
                )
                candles.append(c)
            except Exception as e:
                print(f"Error parsing candlestick: {e} - {kline}")
        if limit > self.MAX_SIZE:
            candles.extend(self.get_recent_candle(symbol, interval, limit - self.MAX_SIZE))

        return candles

    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        return self.client.query_order(symbol=symbol, origClientOrderId=order_id)

    def subscribe_candle_event(self, symbol_intervals_map: Dict[str, List[int]], on_message, on_error,
                               on_close) -> None:
        streams = []
        for symbol, durations in symbol_intervals_map.items():
            for duration in durations:
                streams.append(f"{symbol.lower()}@kline_{self.duration_to_string(duration)}")
        ws_client = self.create_ws_client(True, on_message, on_close, on_error)
        stream_id = str(uuid4())
        ws_client.subscribe(streams, stream_id)
        # convert streams to hashable string
        streams_hash = ",".join(streams)
        logger.info(f"Subscribed to {streams} with id {stream_id}")
        self.ws_client_map[stream_id] = {streams_hash: ws_client}

    @staticmethod
    def from_candlestick_event(event_str: str) -> coin_service_pb2.Candle:
        try:
            root = json.loads(event_str)
            data = root["data"]
            kline = data["k"]
            return coin_service_pb2.Candle(
                startTime=int(kline["t"]),
                open=float(kline["o"]),
                high=float(kline["h"]),
                low=float(kline["l"]),
                close=float(kline["c"]),
                volume=float(kline["v"]),
                endTime=int(kline["T"]),
                duration=int(BinanceFutureConnector.from_string(kline["i"]).total_seconds() // 60),
                isCloseCandle=kline["x"],
                symbol=kline["s"]
            )
        except Exception as e:
            print(f"Error parsing candlestick event: {e}")
            return None
