import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

import logging

from coin_algorithm.server import binance_server

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    # back_test_server.serve(port='8888', bot_module='bot.my_ta_bot', bot_class='MyTABot')
    binance_server.serve(port='8888', bot_module='bot.my_simple_bot', bot_class='SimpleBot',
                         api_key='199aa7dccca9992236c1af0f3f8c81813ef7bfc726cd7bf22457f07b77bc199c',
                         secret_key='f7427c38051d677dd3f94b6ab1321d9675ee541665fc22494f426c3eb318acbe',
                         is_test_net=True)
