import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

import logging

from coin_algorithm.server import binance_server, back_test_server

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    back_test_server.serve(port='8888', bot_module='bot.my_ta_bot', bot_class='MyTABot')
    binance_server.serve(port='8888', bot_module='bot.my_simple_bot', bot_class='SimpleBot',
                         api_key='',
                         secret_key='',
                         is_test_net=True)
