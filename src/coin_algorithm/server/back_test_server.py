import logging
from concurrent import futures

import grpc

from coin_algorithm.service.back_test_service import BackTestService
from coin_algorithm.service.grpc import coin_service_pb2_grpc

MAX_MESSAGE_LENGTH = 500 * 1024 * 1024
logger = logging.getLogger(__name__)


def serve(port, bot_module, bot_class, option=None) -> None:
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
        BackTestService(bot_module, bot_class), server
    )
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()
