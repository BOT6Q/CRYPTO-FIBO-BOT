# pattern_detector.py

from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass
class PatternResult:
    triggered: bool
    direction: Optional[str] = None
    stop_loss: Optional[float] = None

def detect_pattern1(df: pd.DataFrame, zoi_start: float, zoi_end: float) -> PatternResult:
    """
    A 'fakeout' short pattern:
      • bar[2].high ≥ zoi_end  AND  bar[4].close < zoi_start
      ⇒ trigger a short (down) entry.
    Returns
      PatternResult(triggered, direction, stop_loss)
    """
    # Need at least 5 bars to look at index 2 and 4
    if len(df) < 5:
        return PatternResult(triggered=False)

    highs = df["high"].values
    closes = df["close"].values

    # Short fake‐out: blow past the top of the zone, then reject back below
    if highs[2] >= zoi_end and closes[4] < zoi_start:
        stop_loss = float(df["high"].iloc[4])  # high of the rejection bar
        return PatternResult(triggered=True, direction="down", stop_loss=stop_loss)

    return PatternResult(triggered=False)
