import pandas as pd
import pytest
from zoi_calculator import compute_zois, activate_zois, ZoiWindow


def make_simple_timeseries():
    times = pd.date_range("2025-01-01", periods=5, freq="T")
    return pd.DataFrame({"low": [1, 2, 3, 2, 1], "high": [2, 3, 4, 3, 2]}, index=times)


def test_compute_zois_returns_windows():
    df = make_simple_timeseries()
    zois = compute_zois(df, lookback=3)
    assert isinstance(zois, list)
    assert all(isinstance(z, ZoiWindow) for z in zois)


def test_activate_zois_sets_active_flag():
    zois = [ZoiWindow(start=0, end=10), ZoiWindow(start=20, end=30)]
    activated = activate_zois(zois, timestamp=25)
    assert activated[1].activated is True
    assert activated[0].activated is False
