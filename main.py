import os, time, logging
import pandas as pd
from dotenv import load_dotenv

from data_ingestion import connect
from zoi_calculator   import compute_zois, activate_zois
from pattern_detector import detect_pattern1
from risk_manager     import calculate_position_size
from ai_scoring       import trap_score, sentiment_score
from execution        import CCXTExecutor

def main():
    load_dotenv()
    symbol   = os.getenv("SYMBOL")
    exchange = connect()
    executor = CCXTExecutor()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s")

    while True:
        # 1) fetch recent bars
        bars = exchange.fetch_ohlcv(symbol, "15m", limit=200)
        df   = pd.DataFrame(bars, columns=["timestamp","open","high","low","close","volume"])
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("datetime", inplace=True)

        # 2) compute ZOIs
        z15  = compute_zois(df, lookback=100)
        active = activate_zois(z15, df["close"].iloc[-1])

        # 3) detect pattern
        pr = detect_pattern1(df, active[-1].start, active[-1].end)
        if pr.triggered:
            entry = df["close"].iloc[-1]
            sl    = pr.stop_loss
            size  = calculate_position_size(exchange.fetch_balance()["free"]["USDT"], 0.01, entry, sl)

            # 4) optional AI filter
            score = trap_score({"entry":entry,"sl":sl})
            if score > 0.5:
                order = executor.place_order(symbol, "sell", size)
                logging.info(f"Placed order: {order}")

        time.sleep(60)

if __name__ == "__main__":
    main()
