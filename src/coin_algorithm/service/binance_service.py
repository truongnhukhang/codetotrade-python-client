import asyncio
import json
import logging
import queue
import time
import uuid
from typing import Dict, List

from google.protobuf.json_format import ParseDict

from coin_algorithm.domain.bar import Bar
from coin_algorithm.domain.bar_series import BarSeries
from coin_algorithm.domain.base_bot import BaseBot
from coin_algorithm.domain.bot_config import BotConfig
from coin_algorithm.domain.coin_info import CoinInfo
from coin_algorithm.service.back_test_service import BackTestService
from coin_algorithm.service.exchange.binance.binance_future_connector import BinanceFutureConnector
from coin_algorithm.service.grpc import coin_service_pb2
from coin_algorithm.service.grpc.coin_service_pb2_grpc import CoinAlgorithmServiceServicer

logger = logging.getLogger(__name__)


class BinanceService(CoinAlgorithmServiceServicer):

    def __init__(self, bot_module, bot_class: str, api_key: str, api_secret: str, is_test_net: bool):
        self.bot_module = bot_module
        self.bot_class = bot_class
        self.api_key = api_key
        self.api_secret = api_secret
        self.is_test_net = is_test_net
        self.account_connector = BinanceFutureConnector(api_key, api_secret, is_test_net)
        self.exchange_connector = BinanceFutureConnector(api_key, api_secret, is_test_net)
        self.bot_map: Dict[str, BaseBot] = {}
        self.queue = queue.Queue()
        self.last_ping = int(time.time() * 1000)
        self.exchange_connector.start()

    def CreateOnlineRun(self, request, context):
        try:
            online_id = str(uuid.uuid4())

            # Set all fields of back_test_data from request
            coin_info = CoinInfo(
                request.symbol,
                request.pricePrecision,
                request.quantityPrecision,
                request.tickSize
            )

            main_candles = self.exchange_connector.get_recent_candle(
                request.symbol,
                BinanceFutureConnector.duration_to_string(request.mainInterval),
                request.initBar
            )
            bar_series = BarSeries(
                symbol=request.symbol,
                bars=Bar.convert_candles_to_bars(main_candles),
                duration=int(main_candles[0].duration),
            )

            other_candles = {}
            btc_doom_candles = {}
            other_bar_series = {}
            btc_dom_bar_series = {}
            for interval in request.otherIntervals:
                candles = self.exchange_connector.get_recent_candle(
                    request.symbol,
                    BinanceFutureConnector.duration_to_string(interval),
                    request.initBar
                )
                bar_series = BarSeries(
                    symbol=request.symbol,
                    bars=Bar.convert_candles_to_bars(candles),
                    duration=int(candles[0].duration),
                )
                other_bar_series[interval] = bar_series
                other_candles[interval] = coin_service_pb2.Candles(candles=candles)

            for interval in request.btcDomIntervals:
                candles = self.exchange_connector.get_recent_candle(
                    "BTCDOMUSDT",
                    BinanceFutureConnector.duration_to_string(interval),
                    request.initBar
                )
                bar_series = BarSeries(
                    symbol=request.symbol,
                    bars=Bar.convert_candles_to_bars(candles),
                    duration=int(candles[0].duration),
                )
                btc_dom_bar_series[interval] = bar_series
                btc_doom_candles[interval] = coin_service_pb2.Candles(candles=candles)

            bot_config = BotConfig(
                request.botOrderType,
                request.isEnableCloseMode,
                request.initBar,
                request.initBalance,
                request.makerFee,
                request.takerFee
            )

            # Create bot instance
            base_bot = BackTestService.dynamic_class_instantiation(self.bot_module, self.bot_class)
            base_bot.coin_info = coin_info
            base_bot.bar_series = bar_series
            base_bot.btc_dom_bar_series = btc_dom_bar_series
            base_bot.other_bar_series = other_bar_series
            base_bot.bot_config = bot_config
            base_bot.init(request.config)

            self.bot_map[online_id] = base_bot

            response = coin_service_pb2.CreateOnlineResponse(
                onlineId=online_id,
                candles=coin_service_pb2.Candles(candles=main_candles),
                candleMap=other_candles,
                btcDomCandleMap=btc_doom_candles
            )
            return response
        except Exception as e:
            raise RuntimeError(e)

    def GetTradeMetadata(self, request, context):
        try:
            online_id = request.onlineId
            base_bot = self.bot_map.get(online_id)
            trade_type = request.tradeType
            trade_metadata = None

            if trade_type == 1:
                trade_metadata = base_bot.buy(len(base_bot.bar_series.bars) - 1)
            elif trade_type == 2:
                trade_metadata = base_bot.sell(len(base_bot.bar_series.bars) - 1)

            proto_trade_metadata = ParseDict(trade_metadata.to_proto_dict(), coin_service_pb2.TradeMetadata())
            response = coin_service_pb2.GetTradeMetadataResponse(tradeMetadata=proto_trade_metadata,
                                                                 onlineId=online_id)
            return response
        except Exception as e:
            raise RuntimeError(e)

    def StreamCandle(self, request, context):
        try:
            last_ping = int(time.time() * 1000)
            online_id = request.onlineId
            base_bot = self.bot_map.get(online_id)
            bar_series = base_bot.bar_series
            other_bar_series = base_bot.other_bar_series
            btc_dom_bar_series = base_bot.btc_dom_bar_series
            symbol = base_bot.coin_info.symbol
            durations = [d for d in other_bar_series.keys()]
            durations.append(bar_series.duration)
            symbol_durations: Dict[str, List[int]] = {}
            symbol_durations[symbol] = durations
            symbol_durations["btcdomusdt"] = [d for d in btc_dom_bar_series.keys()]
            self.exchange_connector.subscribe_candle_event(
                symbol_durations,
                on_message=lambda _, message: self.on_message(_, message, online_id),
                on_error=None,
                on_close=None
            )
            while True:
                res = self.queue.get()
                logger.info(f"Sending candle: {res}")
                yield res
        except Exception as e:
            context.send_error(e)

    def on_message(self, _, message, online_id):
        base_bot = self.bot_map.get(online_id)
        bar_series = base_bot.bar_series
        other_bar_series = base_bot.other_bar_series
        candle = BinanceFutureConnector.from_candlestick_event(message)
        if candle and candle.startTime != 0:
            self.update_bar_series(bar_series, candle)
            for key, value in other_bar_series.items():
                self.update_bar_series(value, candle)
            if (time.time() * 1000) - self.last_ping > 5000:
                last_bar = bar_series.get_last_bar()
                logger.info(f"Last bar time: {last_bar.end_time}, close price: {last_bar.close}")
                self.last_ping = int(time.time() * 1000)
            self.queue.put(coin_service_pb2.StreamCandleResponse(candle=candle))

    def update_bar_series(self, bar_series: BarSeries, candle):
        # Check if candle duration matches bar_series duration
        if candle and candle.startTime != 0 and bar_series.duration == candle.duration:
            is_replace = bar_series.get_last_bar().in_period(candle.startTime)
            bar_series.add_bar(
                Bar(
                    start_time=candle.startTime,
                    end_time=candle.endTime,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume
                ),
                is_replace
            )

    def GetSignal(self, request, context):
        online_id = request.onlineId
        idx = request.idx
        base_bot = self.bot_map.get(online_id)
        response = coin_service_pb2.GetSignalResponse()
        signal = coin_service_pb2.Signal(
            time=base_bot.bar_series.bars[idx].start_time,
            isBuy=base_bot.is_buy(idx),
            isSell=base_bot.is_sell(idx),
            isCloseBuy=base_bot.is_close_buy_position(idx),
            isCloseSell=base_bot.is_close_sell_position(idx)
        )
        response.signal.CopyFrom(signal)
        return response

    def GetOrderStatus(self, request, context):
        order_id = request.orderId
        symbol = request.symbol
        payload = ""
        order_status_response = coin_service_pb2.GetOrderStatusResponse()
        order_status_response.isSuccess = True
        status = coin_service_pb2.OrderStatus.NEW

        try:
            rs = self.account_connector.get_order_status(symbol, order_id)
            payload = json.dumps(rs)
            if rs.get("status").lower() != "new":
                status = coin_service_pb2.OrderStatus.FILLED
        except json.JSONDecodeError:
            order_status_response.isSuccess = False

        order_status_response.payload = payload
        order_status_response.status = status
        return order_status_response

    def CreateOrder(self, request, context):
        response = coin_service_pb2.CreateOrderResponse()
        try:
            order_id = request.orderId
            symbol = request.symbol
            price = request.price
            quantity = request.quantity
            side = request.side
            order_type = request.type
            rs = None
            if order_type == coin_service_pb2.OrderType.MARKET:
                rs = self.place_market_order(symbol, quantity, False, order_id, side)
            elif order_type == coin_service_pb2.OrderType.LIMIT:
                rs = self.place_limit_order(symbol, price, quantity, False, order_id, side)
            elif order_type == coin_service_pb2.OrderType.SL_MARKET:
                rs = self.place_stop_loss_order(symbol, price, quantity, False, order_id, side)
            elif order_type == coin_service_pb2.OrderType.TP_MARKET:
                rs = self.place_take_profit_order(symbol, price, quantity, False, order_id, side)

            response.isSuccess = True
            payload = json.dumps(rs)
            status = rs.get("status")
            executed_price = rs.get("avgPrice")
            response.executedPrice = executed_price
            response.payload = payload
            response.status = status
            response.orderId = rs.get("clientOrderId")
        except Exception as e:
            response.isSuccess = False
            response.payload = str(e)
        finally:
            return response

    def CancelOrder(self, request, context):
        payload = ""
        response = coin_service_pb2.CancelOrderResponse()
        try:
            order_id = request.orderId
            symbol = request.symbol
            rs = self.account_connector.cancel_order(symbol, order_id)
            response.isSuccess = True
            payload = json.dumps(rs)
            response.payload = payload
        except Exception as e:
            response.isSuccess = False
        finally:
            return response

    def place_market_order(self, symbol, quantity, is_test, order_id, side):
        if side == coin_service_pb2.OrderSide.BUY:
            return self.account_connector.place_market_buy_order(symbol, quantity, is_test, order_id)
        else:
            return self.account_connector.place_market_sell_order(symbol, quantity, is_test, order_id)

    def place_limit_order(self, symbol, price, quantity, is_test, order_id, side):
        if side == coin_service_pb2.OrderSide.BUY:
            return self.account_connector.place_limit_buy_order(symbol, quantity, price, is_test, order_id)
        else:
            return self.account_connector.place_limit_sell_order(symbol, quantity, price, is_test, order_id)

    def place_stop_loss_order(self, symbol, price, quantity, is_test, order_id, side):
        if side == coin_service_pb2.OrderSide.BUY:
            return self.account_connector.place_buy_stop_loss_order(symbol, quantity, price, is_test, order_id)
        else:
            return self.account_connector.place_sell_stop_loss_order(symbol, quantity, price, is_test, order_id)

    def place_take_profit_order(self, symbol, price, quantity, is_test, order_id, side):
        if side == coin_service_pb2.OrderSide.BUY:
            return self.account_connector.place_buy_take_profit_order(symbol, quantity, price, is_test, order_id)
        else:
            return self.account_connector.place_sell_take_profit_order(symbol, quantity, price, is_test, order_id)
