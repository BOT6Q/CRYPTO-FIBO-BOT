# tests/test_pattern1.py

import pandas as pd
import pytest
from pattern_detector import detect_pattern1, PatternResult

def make_synthetic_df():
    """8‐bar minute timestamps with a fakeout above zoi_end then rejection below zoi_start."""
    times = pd.date_range("2025-01-01", periods=8, freq="T")
    data = {
        "ts":    times,
        "open":  [100]*8,
        "high":  [100, 110, 130, 120, 125, 110, 100,  90],
        "low":   [100]*8,
        "close": [100, 115, 118, 115, 105, 108,  98,  88],
        "vol":   [1]*8,
    }
    return pd.DataFrame(data)

def test_pattern1_detects_basic_fakeout():
    df = make_synthetic_df()
    # bar[2].high = 130 >= zoi_end (125), then bar[4].close = 105 < zoi_start (110) → should trigger
    res = detect_pattern1(df, zoi_start=110, zoi_end=125)

    # core API
    assert isinstance(res, PatternResult)
    assert res.triggered is True

    # “short”‐fakeout is reported as direction="down"
    assert res.direction == "down"

    # stop_loss is the high of the rejection bar (bar index=4)
    assert res.stop_loss == pytest.approx(df["high"].iloc[4])

def test_pattern1_triggers_on_synthetic():
    df = make_synthetic_df()

    # same exact params, still fires
    res = detect_pattern1(df, zoi_start=110, zoi_end=125)

    assert isinstance(res, PatternResult)
    assert res.triggered is True
