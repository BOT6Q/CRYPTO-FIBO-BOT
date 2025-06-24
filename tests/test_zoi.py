import pandas as pd
import pytest
from zoi_calculator import compute_zois, activate_zois, ZoiWindow

def make_simple_timeseries():
    # 5 bars, ascending close prices
    times = pd.date_range("2025-01-01", periods=5, freq="T")
    df = pd.DataFrame({"close": [100, 102, 105, 107, 110]}, index=times)
    return df

def test_compute_zois_returns_list_of_windows():
    df = make_simple_timeseries()
    zois = compute_zois(df, lookback=3)
    assert isinstance(zois, list)
    assert all(isinstance(z, ZoiWindow) for z in zois)

def test_activate_zois_sets_active_flag():
    # stub ZoiWindow-like class
    class Z:
        def __init__(self, start, end):
            self.start = start
            self.end = end
            self.activated = False
        def replace(self, activated):
            z = Z(self.start, self.end)
            z.activated = activated
            return z

    zois = [Z(0,10), Z(20,30)]
    # timestamp=25 falls into the second window
    activated = activate_zois(zois, timestamp=25)
    assert activated[0].activated is False
    assert activated[1].activated is True
