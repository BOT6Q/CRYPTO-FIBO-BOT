import os
import ccxt
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime


def fetch_and_save(
    symbol: str,
    timeframe: str,
    limit: int = 1000,
    filename: str = "your_crypto_data.csv",
):
    """
    Fetch OHLCV via CCXT and save as CSV with datetime index.
    """
    load_dotenv()
    name = os.getenv("EXCHANGE")
    key = os.getenv("API_KEY")
    secret = os.getenv("API_SECRET")
    ex = getattr(ccxt, name)(
        {
            "apiKey": key,
            "secret": secret,
            "enableRateLimit": True,
        }
    )

    ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("datetime", inplace=True)
    df.to_csv(filename)
    print(f"Saved {len(df)} bars to {filename}")


if __name__ == "__main__":
    fetch_and_save(os.getenv("SYMBOL", "BTC/USDT"), "15m", limit=2000)
