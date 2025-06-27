from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ZoiWindow:
    start: float
    end: float
    activated: bool = False

    def replace(self, activated: bool) -> "ZoiWindow":
        return ZoiWindow(self.start, self.end, activated)


def compute_zois(df, lookback: int) -> List[ZoiWindow]:
    """
    Slide a window of `lookback` bars over df, building a ZoiWindow
    for each slice: (low, high).
    """
    if lookback <= 0 or lookback > len(df):
        raise ValueError("lookback must be between 1 and len(df)")
    zois: List[ZoiWindow] = []
    for i in range(lookback, len(df) + 1):
        window = df.iloc[i - lookback : i]
        hi = float(window["high"].max())
        lo = float(window["low"].min())
        zois.append(ZoiWindow(start=lo, end=hi))
    return zois


def activate_zois(zois: List[ZoiWindow], timestamp: float) -> List[ZoiWindow]:
    """
    Given a list of ZoiWindow and a numeric timestamp,
    return a new list where exactly the windows containing
    `timestamp` have activated=True.
    """
    activated = []
    for z in zois:
        is_active = (z.start <= timestamp) and (timestamp <= z.end)
        activated.append(z.replace(is_active))
    return activated
