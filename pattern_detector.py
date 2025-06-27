from dataclasses import dataclass
from typing import Optional


@dataclass
class PatternResult:
    triggered: bool
    direction: Optional[str]
    stop_loss: Optional[float]


def detect_pattern1(df, *, zoi_start: float, zoi_end: float) -> PatternResult:
    """
    A “fake-out” short:
      1. bar.high >= zoi_end
      2. immediately next bar’s close < zoi_start

    Returns PatternResult(triggered, direction, stop_loss) where:
      • triggered=False if no setup
      • direction="down" on trigger
      • stop_loss = high of the breakout bar
    """
    highs = df["high"]
    closes = df["close"]

    for i, h in enumerate(highs):
        if h >= zoi_end:
            # check very next bar
            j = i + 1
            if j < len(df) and closes.iloc[j] < zoi_start:
                return PatternResult(
                    triggered=True,
                    direction="down",
                    stop_loss=float(highs.iloc[i]),
                )
            # if breakout happens but next-bar condition fails, keep looking
    return PatternResult(triggered=False, direction=None, stop_loss=None)
