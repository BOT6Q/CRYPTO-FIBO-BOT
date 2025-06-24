def calculate_position_size(balance: float, risk_pct: float, entry: float, sl: float) -> float:
    """
    Given an account balance, the fraction to risk per trade, an entry price and a stop-loss level,
    return how many units we should buy/sell to risk exactly `risk_pct` of `balance`.

    Raises ValueError if entry == sl (zero risk distance).
    """
    if entry == sl:
        raise ValueError("entry price and stop-loss level must differ to compute a position size")

    risk_amount = balance * risk_pct
    # distance per unit
    distance = abs(entry - sl)
    position_size = risk_amount / distance
    return position_size
