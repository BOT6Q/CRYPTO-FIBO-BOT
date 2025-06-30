import csv
import backtrader as bt
from execution import (
    YourFiboStrategy,
)  # ← point this at your actual strategy file & class


def run_backtest(risk, zoi_start, zoi_end, profit_rr=3):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)

    # Add your strategy with its parameters
    cerebro.addstrategy(
        YourFiboStrategy,
        risk=risk,
        zoi_start=zoi_start,
        zoi_end=zoi_end,
        profit_rr=profit_rr,
    )

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.Sharpe, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    # Optional: SQN
    # cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    strat = cerebro.run()[0]

    # Compute results
    pnl = cerebro.broker.getvalue() - 100000
    sharpe_ratio = strat.analyzers.sharpe.get_analysis().get("sharperatio", None)
    dd = strat.analyzers.drawdown.get_analysis().max.drawdown

    return pnl, sharpe_ratio, dd


def main():
    # Parameter grid
    grid = [
        (r, zs, ze)
        for r in [0.0025, 0.005, 0.01, 0.02]
        for zs in [40, 50, 60, 75]
        for ze in [20, 25, 30, 35]
    ]

    # Write CSV header
    with open("opt_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["risk", "zoi_start", "zoi_end", "pnl", "sharpe", "max_drawdown"]
        )

        # Sweep
        for risk, zs, ze in grid:
            print(f"▶ risk={risk}, zoi_start={zs}, zoi_end={ze}")
            pnl, sharpe, dd = run_backtest(risk, zs, ze)
            writer.writerow([risk, zs, ze, pnl, sharpe, dd])

    print("✅ opt_results.csv written.")


if __name__ == "__main__":
    main()
