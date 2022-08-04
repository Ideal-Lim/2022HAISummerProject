from hai_stock import OrderTypes, HAIStock

import json


if __name__ == '__main__':
    with open('config.json', 'rt') as f:
        CONFIG = json.load(f)

    api = HAIStock(CONFIG['server'], CONFIG['token'])

    api.send_order(OrderTypes.BUY, 'TQQQ', 1000, 3100)
