import os, sys
import ccxt
from dotenv import load_dotenv

def connect():
    """
    Connect to a centralized exchange via CCXT using credentials from .env.
    """
    load_dotenv()
    name   = os.getenv("EXCHANGE")
    key    = os.getenv("API_KEY")
    secret = os.getenv("API_SECRET")
    symbol = os.getenv("SYMBOL")

    if not all([name, key, secret, symbol]):
        print("Error: EXCHANGE, API_KEY, API_SECRET, SYMBOL must be set in .env")
        sys.exit(1)

    exchange_cls = getattr(ccxt, name)
    ex = exchange_cls({
        "apiKey": key,
        "secret": secret,
        "enableRateLimit": True,
    })
    return ex

if __name__ == "__main__":
    ex = connect()
    bars = ex.fetch_ohlcv(os.getenv("SYMBOL"), "15m", limit=int(os.getenv("DATALOAD_LIMIT", "1000")))
    print("Latest 5 candles:", bars[-5:])
