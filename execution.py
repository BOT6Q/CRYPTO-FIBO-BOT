import os
import ccxt
from dotenv import load_dotenv

# —— Centralized via CCXT ——
class CCXTExecutor:
    def __init__(self):
        load_dotenv()
        name   = os.getenv("EXCHANGE")
        key    = os.getenv("API_KEY")
        secret = os.getenv("API_SECRET")
        self.ex = getattr(ccxt, name)({
            "apiKey": key,
            "secret": secret,
            "enableRateLimit": True,
        })

    def place_order(self, symbol: str, side: str, amount: float, price=None):
        """
        side: 'buy' or 'sell'; amount: base currency units.
        """
        params = {}
        if price:
            return self.ex.create_limit_order(symbol, side, amount, price, params)
        else:
            return self.ex.create_market_order(symbol, side, amount, params)

# —— Decentralized GMX stub ——
# from web3 import Web3
# def open_position(...): ...
# def close_position(...): ...
