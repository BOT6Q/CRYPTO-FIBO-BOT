import pandas as pd

REQUIRED_COLS = ["datetime", "open", "high", "low", "close", "volume"]


def load_and_validate_csv(path):
    df = pd.read_csv(path, parse_dates=["datetime"])
    if list(df.columns)[:6] != REQUIRED_COLS:
        raise ValueError(f"{path} must have columns {REQUIRED_COLS} in that order")
    df.set_index("datetime", inplace=True)
    return df
