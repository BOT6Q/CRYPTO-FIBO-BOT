# create_tests.py
import os

files = {
    # 1) pytest.ini
    "pytest.ini": """\
[pytest]
minversion = 6.0
testpaths = tests
python_files = test_*.py
""",
    # 2) tests/__init__.py (empty marker)
    "tests/__init__.py": "",
    # 3) tests/test_pattern1.py
    "tests/test_pattern1.py": """\
import pandas as pd
import pytest
from pattern_detector import detect_pattern1, PatternResult

def make_synthetic_df():
    times = pd.date_range("2025-01-01 00:00", periods=8, freq="T")
    data = {"high":[1,2,6,3,2,1,1,1],"close":[1,1,1,3,2,1,1,1]}
    return pd.DataFrame(data, index=times)

def test_pattern1_detects_basic_fakeout():
    df = pd.DataFrame({"high":[1,2,1],"close":[1,1,0.5]},
                      index=pd.date_range("2025-01-01",periods=3,freq="T"))
    res = detect_pattern1(df, zoi_start=1, zoi_end=1.5)
    assert isinstance(res, PatternResult)
    assert res.triggered is True

def test_pattern1_triggers_on_synthetic():
    df = make_synthetic_df()
    res = detect_pattern1(df, zoi_start=4, zoi_end=5)
    assert isinstance(res, PatternResult)
    assert res.triggered is True
""",
    # 4) tests/test_risk.py
    "tests/test_risk.py": """\
import pytest
from risk_manager import calculate_position_size

def test_calculate_position_size_returns_positive():
    size = calculate_position_size(balance=1000, risk_pct=0.01, entry=100, sl=90)
    assert size == pytest.approx(1.0)

def test_calculate_position_size_error_on_equal_prices():
    with pytest.raises(ValueError):
        calculate_position_size(balance=1000, risk_pct=0.01, entry=100, sl=100)
""",
    # 5) tests/test_zoi.py
    "tests/test_zoi.py": """\
import pandas as pd
import pytest
from zoi_calculator import compute_zois, activate_zois, ZoiWindow

def make_simple_timeseries():
    times = pd.date_range("2025-01-01", periods=5, freq="T")
    return pd.DataFrame({"low":[1,2,3,2,1],"high":[2,3,4,3,2]}, index=times)

def test_compute_zois_returns_windows():
    df = make_simple_timeseries()
    zois = compute_zois(df, lookback=3)
    assert isinstance(zois, list)
    assert all(isinstance(z, ZoiWindow) for z in zois)

def test_activate_zois_sets_active_flag():
    zois = [ZoiWindow(start=0,end=10), ZoiWindow(start=20,end=30)]
    activated = activate_zois(zois, timestamp=25)
    assert activated[1].activated is True
    assert activated[0].activated is False
""",
}

for path, content in files.items():
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        f.write(content)

print("✅ pytest scaffolding created. Now run `pytest -q`")
