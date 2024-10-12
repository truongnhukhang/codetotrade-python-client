from concurrent import futures

import grpc

from coin_algorithm.service.binance_service import BinanceService
from coin_algorithm.service.grpc import coin_service_pb2_grpc

MAX_MESSAGE_LENGTH = 500 * 1024 * 1024

import logging

logger = logging.getLogger(__name__)


def serve(port, bot_module, bot_class, api_key, secret_key, is_test_net, option=None) -> None:
    logger.log(logging.INFO, f"Starting server on port {port} with bot_module {bot_module} and bot_class {bot_class}")
    if option is None:
        option = [
            ("grpc.max_send_message_length", MAX_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
            ("grpc.max_metadata_size ", MAX_MESSAGE_LENGTH),
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.keepalive_time_ms", 10000),
            ("grpc.http2.max_ping_strikes", 0),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.http2.min_ping_interval_without_data_ms", 10000),
        ]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=option)
    coin_service_pb2_grpc.add_CoinAlgorithmServiceServicer_to_server(
        BinanceService(bot_module, bot_class, api_key, secret_key, is_test_net), server
    )
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()
