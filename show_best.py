import pandas as pd


def show_best():
    df = pd.read_csv("opt_results.csv")
    best = df.loc[df["sharpe"].idxmax()]

    print(
        f"Best params: risk={best.risk}, zoi_start={best.zoi_start}, zoi_end={best.zoi_end}"
    )
    print(
        f"Sharpe: {best.sharpe:.2f} | P&L: {best.pnl:.2f} | Max Drawdown: {best.max_drawdown:.2f}"
    )


if __name__ == "__main__":
    show_best()
