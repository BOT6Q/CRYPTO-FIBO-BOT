import pytest
from risk_manager import calculate_position_size

def test_risk_size_basic():
    # 1% of 1000 = 10 risked, price diff = 10−9 = 1 ⇒ size = 10/1 = 10 units
    size = calculate_position_size(balance=1000, risk_pct=0.01, entry=10, sl=9)
    assert pytest.approx(size) == 10

def test_risk_size_equal_entry_sl_raises():
    with pytest.raises(ValueError):
        calculate_position_size(balance=500, risk_pct=0.02, entry=10, sl=10)
