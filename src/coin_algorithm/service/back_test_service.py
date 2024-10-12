import uuid
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
from typing import Dict

from coin_algorithm.domain.bar import Bar
from coin_algorithm.domain.bar_series import BarSeries
from coin_algorithm.domain.base_bot import BaseBot
from coin_algorithm.domain.bot_config import BotConfig
from coin_algorithm.domain.coin_info import CoinInfo
from coin_algorithm.service.back_test_data import BackTestData
from coin_algorithm.service.grpc import coin_service_pb2
from coin_algorithm.service.grpc.coin_service_pb2_grpc import CoinAlgorithmServiceServicer


class BackTestService(CoinAlgorithmServiceServicer):
    def __init__(self, bot_module, bot_class: str):
        self.bot_module = bot_module
        self.bot_class = bot_class
        self.back_test_map: Dict[str, BackTestData] = {}

    def CreateBackTest(self, request, context):
        # Generate a unique ID for the backtest
        uuid_str = str(uuid.uuid4())
        # Convert request to dict
        # hint : use MessageToDict
        request_dict = MessageToDict(
            request,
            always_print_fields_with_no_presence=True,
            preserving_proto_field_name=True,
        )
        # Create CoinInfo instance
        coin_info = CoinInfo(
            symbol=request_dict["symbol"],
            price_precision=request_dict["pricePrecision"],
            quantity_precision=request_dict["quantityPrecision"],
            tick_size=request_dict["tickSize"],
        )

        # Create BarSeries instances
        bar_series = BarSeries(
            symbol=request_dict["symbol"],
            bars=Bar.convert_candle_dicts_to_bars(request_dict["candles"]["candles"]),
            duration=int(request_dict["candles"]["candles"][0]["duration"]),
        )

        other_bar_series = {
            int(key): BarSeries(
                symbol=request.symbol,
                bars=Bar.convert_candle_dicts_to_bars(value['candles']),
                duration=int(value['candles'][0]['duration']),
            )
            for key, value in request_dict['candleMap'].items()
        }

        btc_dom_bar_series = {
            int(key): BarSeries(
                symbol=request.symbol,
                bars=Bar.convert_candle_dicts_to_bars(value['candles']),
                duration=int(value['candles'][0]['duration']),
            )
            for key, value in request_dict['btcDomCandleMap'].items()
        }

        # Create BotConfig instance
        bot_config = BotConfig(
            bot_order_type=request_dict['botOrderType'],
            is_enable_close_mode=request_dict['isEnableCloseMode'],
            init_bar=request_dict['initBar'],
            init_balance=request_dict['initBalance'],
            maker_fee=request_dict['makerFee'],
            taker_fee=request_dict['takerFee'],
        )
        # Create backTestData
        back_test_data = BackTestData(
            bar_series=bar_series,
            other_bar_series=other_bar_series,
            btd_dom_bar_series=btc_dom_bar_series,
            coin_info=coin_info,
            bot_config=bot_config,
        )
        self.back_test_map[uuid_str] = back_test_data
        return ParseDict(
            {"backTestId": uuid_str}, coin_service_pb2.CreateBackTestResponse()
        )

    def GetTimeTravel(self, request, context):
        time_travel_request = MessageToDict(
            request,
            preserving_proto_field_name=True,
            always_print_fields_with_no_presence=True,
        )
        back_test_id = time_travel_request["backTestId"]
        config = time_travel_request["config"]
        # init bot from botPath
        base_bot: BaseBot = self.dynamic_class_instantiation(
            self.bot_module,
            self.bot_class,

        )
        base_bot.bar_series = self.back_test_map[back_test_id].bar_series
        base_bot.other_bar_series = self.back_test_map[back_test_id].other_bar_series
        base_bot.btc_dom_bar_series = self.back_test_map[back_test_id].btc_dom_bar_series
        base_bot.coin_info = self.back_test_map[back_test_id].coin_info
        base_bot.bot_config = self.back_test_map[back_test_id].bot_config
        base_bot.init(config)

        time_travel_res = base_bot.time_travel()
        response_dict = time_travel_res.to_proto_dict()
        chart_list = base_bot.get_chart_list()
        for chart in chart_list:
            for plot in chart.plot_list:
                if plot.bar_series.duration != base_bot.bar_series.duration:
                    base_bars = base_bot.bar_series.bars
                    new_indicator_values = [
                        plot.indicator_values[
                            base_bot.get_index_of_bar_series_by_start_time(plot.bar_series, bar.start_time)]
                        for bar in base_bars
                    ]
                    plot.indicator_values = new_indicator_values
        response_dict["chartList"] = {"charts": [c.to_proto_dict() for c in base_bot.get_chart_list()]}
        return ParseDict(
            response_dict,
            coin_service_pb2.GetTimeTravelResponse(),
        )

    @staticmethod
    def dynamic_class_instantiation(module_name: str, class_name: str, *args, **kwargs):
        # Import the module dynamically
        module = __import__(module_name, fromlist=[class_name])
        # Get the class from the module
        cls = getattr(module, class_name)
        # Instantiate the class with the provided arguments
        instance = cls(*args, **kwargs)
        return instance
