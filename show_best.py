import pandas as pd
import matplotlib.pyplot as plt


def main():
    # Load results
    df = pd.read_csv("opt_results.csv")

    # Find the best by Sharpe
    best = df.loc[df["sharpe"].idxmax()]

    # Print summary
    print(
        f"Best params: risk={best.risk}, zoi_start={best.zoi_start}, zoi_end={best.zoi_end}"
    )
    print(
        f"Sharpe: {best.sharpe:.2f}   P&L: {best.pnl:.2f}   Max drawdown: {best.max_drawdown:.2f}%"
    )

    # OPTIONAL: plot cumulative P&L across all runs
    df["cum_pnl"] = df["pnl"].cumsum()
    plt.plot(df["cum_pnl"])
    plt.title("Cumulative P&L Across All Runs")
    plt.xlabel("Run #")
    plt.ylabel("Cumulative P&L")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
