def calculate_position_size(
    balance: float,
    risk_pct: float,
    entry: float,
    sl: float,
) -> float:
    """
    How many units to buy/sell so that
    risking (entry - sl) per unit = risk_pct * balance.

    Raises ValueError if entry == sl.
    """
    if entry == sl:
        raise ValueError("Entry and stop-loss prices are equal; zero risk per unit.")
    risk_amount = balance * risk_pct
    unit_risk = abs(entry - sl)
    return risk_amount / unit_risk
