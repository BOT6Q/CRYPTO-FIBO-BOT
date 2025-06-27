import pandas as pd
import pytest
from pattern_detector import detect_pattern1, PatternResult


def make_synthetic_df():
    times = pd.date_range("2025-01-01 00:00", periods=8, freq="T")
    data = {"high": [1, 2, 6, 3, 2, 1, 1, 1], "close": [1, 1, 1, 3, 2, 1, 1, 1]}
    return pd.DataFrame(data, index=times)


def test_pattern1_detects_basic_fakeout():
    df = pd.DataFrame(
        {"high": [1, 2, 1], "close": [1, 1, 0.5]},
        index=pd.date_range("2025-01-01", periods=3, freq="T"),
    )
    res = detect_pattern1(df, zoi_start=1, zoi_end=1.5)
    assert isinstance(res, PatternResult)
    assert res.triggered is True


def test_pattern1_triggers_on_synthetic():
    df = make_synthetic_df()
    res = detect_pattern1(df, zoi_start=4, zoi_end=5)
    assert isinstance(res, PatternResult)
    assert res.triggered is True
