import pandas as pd
import matplotlib.pyplot as plt
from backtest_opt import run_backtest, INITIAL_CASH, CSV_PATH


def main():
    # 1. Load grid results
    df = pd.read_csv("opt_results.csv")

    # 2. Pick the row with highest Sharpe
    best = df.loc[df["sharpe"].idxmax()]

    print("🏆 Best parameter set:")
    print(f"  • risk_pct    = {best.risk_pct}")
    print(f"  • zoi_start   = {best.zoi_start}")
    print(f"  • zoi_end     = {best.zoi_end}")
    print()
    print("📊 Metrics:")
    print(f"  • PnL          = {best.pnl:.2f}")
    print(f"  • Sharpe       = {best.sharpe:.2f}")
    print(f"  • Max Drawdown = {best.max_drawdown:.2f}%")

    # 3. (Optional) re-run that backtest to get the equity curve
    pnl_series = []
    cash = INITIAL_CASH

    # A very simple equity‐curve re-simulation:
    # we step bar by bar, record broker value from cerebro
    import backtrader as bt
    import pandas as pd

    class EQC(bt.Strategy):
        def __init__(self):
            self.eq = []

        def next(self):
            self.eq.append(self.broker.getvalue())

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(INITIAL_CASH)
    cerebro.broker.setcommission(commission=0.0005)

    data = pd.read_csv(CSV_PATH, parse_dates=["datetime"], index_col="datetime")
    cerebro.adddata(bt.feeds.PandasData(dataname=data))

    cerebro.addstrategy(
        EQC,
        risk_pct=best.risk_pct,
        zoi_start=best.zoi_start,
        zoi_end=best.zoi_end,
        profit_rr=3.0,
        lookback=100,
    )

    cerebro.run()
    eq_curve = cerebro.runstrats[0][0].eq  # extract the stored equity list

    # 4. Plot it
    plt.figure(figsize=(10, 4))
    plt.plot(eq_curve)
    plt.title("Equity Curve for Best Run")
    plt.ylabel("Account Value")
    plt.xlabel("Bar #")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
