import pytest
from risk_manager import calculate_position_size


def test_calculate_position_size_returns_positive():
    size = calculate_position_size(balance=1000, risk_pct=0.01, entry=100, sl=90)
    assert size == pytest.approx(1.0)


def test_calculate_position_size_error_on_equal_prices():
    with pytest.raises(ValueError):
        calculate_position_size(balance=1000, risk_pct=0.01, entry=100, sl=100)
