# Coin Algorithm Python Client

This is the `codetotrade.app` Python client, which provides tools and functionalities to interact with the `codetotrade.app` platform.

## Installation

To install the client, you can use `pip`:
```sh
pip install coin-algorithm==1.4
```
## Usage

### Create your bot 

#### Create new python file (ex : bot/my_test_bot.py) and Implement the BaseBot class

```python
from typing import Dict
from coin_algorithm.domain.base_bot import BaseBot
from coin_algorithm.domain.trade_metadata import TradeMetadata
class MyTestBot(BaseBot):
    def init(self, config: Dict[str, str]) -> None:
        pass

    def is_buy(self, idx: int) -> bool:
        pass

    def is_sell(self, idx: int) -> bool:
        pass

    def buy(self, idx: int) -> TradeMetadata:
        pass

    def sell(self, idx: int) -> TradeMetadata:
        pass

```
### Run your bot

There are 2 Params to indicate where your bot is located.
- bot_module : The path to the bot file without the extension (ex : bot.my_test_bot)
- bot_class : The class name of the bot (ex : MyTestBot)

**Run back test for your bot**

```python
import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)
from coin_algorithm.server import back_test_server
import logging

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    back_test_server.serve(port='8888', bot_module='bot.my_test_bot', bot_class='MyTestBot')
```

**Run exchange trade for your bot**

```python
import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

import logging

from coin_algorithm.server import binance_server

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    binance_server.serve(port='8888', bot_module='bot.my_test_bot', bot_class='MyTestBot',
                         api_key='',
                         secret_key='',
                         is_test_net=True)
```
